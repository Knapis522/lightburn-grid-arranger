"""Zápis nového `.lbrn2` cíleným přepisem bajtových úseků (ADR-0002; spec. kap. 9.2, 9.4).

Mění se výhradně obsah ``<XForm>…</XForm>``:

1. nejvyšší skupiny každého přesouvaného výrobku,
2. ``BackupPath`` každého textu v jejím podstromu (je ve světových souřadnicích; KAL-00).

Oba se násobí zleva stejnou afinní transformací výrobku ``T`` (posun, od v1.13 i natočení):
``XForm' = T ∘ XForm``. Čistý posun mění jen ``e, f`` a lineární část nechává bajtově beze změny.

Ostatní bajty souboru zůstávají identické. Výstup se nikdy nezapisuje přes
existující soubor ani přes originál.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from ...domain.errors import GridError
from . import geometry as geo
from .read import LoadedProject
from .xmltree import Node

MAX_OUTPUT_INDEX = 999


@dataclass(frozen=True, slots=True)
class PatchOp:
    start: int
    end: int
    old: bytes
    new: bytes
    item_id: str
    role: str  # "group" | "text_backup"


def _xform_node(shape: Node) -> Node:
    x = shape.find("XForm")
    if x is None or x.content_start is None or x.content_end is None:
        raise GridError("missing_xform", "Tvar nemá zapisovatelný XForm.", shape=shape.attrs.get("Type"))
    return x


def as_affine(move: tuple[float, ...]) -> geo.Affine:
    """``(dx, dy)`` → čistý posun; šestice → afinní transformace (souřadnice souboru)."""
    if len(move) == 2:
        return (1.0, 0.0, 0.0, 1.0, float(move[0]), float(move[1]))
    if len(move) == 6:
        return tuple(float(v) for v in move)  # type: ignore[return-value]
    raise GridError("bad_transform", "Neplatná transformace výrobku.")


def is_translation(t: geo.Affine) -> bool:
    return t[:4] == (1.0, 0.0, 0.0, 1.0)


def _transformed(data: bytes, x: Node, t: geo.Affine) -> tuple[bytes, bytes]:
    old = data[x.content_start : x.content_end]
    try:
        vals = geo.parse_xform(old.decode("ascii"))
    except (UnicodeDecodeError, geo.GeometryError) as e:
        raise GridError("bad_xform", "Nečitelný XForm.", detail=str(e)) from None
    if is_translation(t):  # posun: lineární část ponechat bajtově beze změny
        tokens = old.decode("ascii").split()
        new = " ".join(tokens[:4] + [geo.fmt_num(vals[4] + t[4]), geo.fmt_num(vals[5] + t[5])])
    else:
        new = " ".join(geo.fmt_num(v) for v in geo.compose(t, vals))
    return old, new.encode("ascii")


def plan_patches(project: LoadedProject, moves_file: dict[str, tuple[float, ...]]) -> list[PatchOp]:
    """Přepisy pro výrobky ``{item_id: (dx, dy) | (a, b, c, d, e, f)}`` v souřadnicích **souboru**."""
    ops: list[PatchOp] = []
    for item_id, move in moves_file.items():
        t = as_affine(move)
        it = project.item(item_id)
        if not it.supported:
            raise GridError("item_not_supported", "Výrobek nelze přesunout.", item_id=item_id)
        x = _xform_node(it.node)
        old, new = _transformed(project.data, x, t)
        ops.append(PatchOp(x.content_start, x.content_end, old, new, item_id, "group"))
        for n in it.node.iter():
            if n.tag == "Shape" and n.attrs.get("Type") == "Text":
                bp = n.find("BackupPath")
                if bp is not None:
                    bx = _xform_node(bp)
                    old, new = _transformed(project.data, bx, t)
                    ops.append(PatchOp(bx.content_start, bx.content_end, old, new, item_id, "text_backup"))
    ops.sort(key=lambda o: o.start)
    for a, b in zip(ops, ops[1:]):
        if b.start < a.end:
            raise GridError("overlapping_patch", "Interní chyba: překrývající se přepisy.")
    return ops


def apply_patches(data: bytes, ops: list[PatchOp]) -> bytes:
    out = bytearray()
    last = 0
    for op in ops:
        if data[op.start : op.end] != op.old:
            raise GridError("patch_mismatch", "Zdrojová data neodpovídají plánu přepisu.")
        out += data[last : op.start] + op.new
        last = op.end
    out += data[last:]
    return bytes(out)


def next_output_path(source: Path, out_dir: Path | None = None) -> Path:
    """``puvodni__grid_001.lbrn2``, ``…_002``, … — první neexistující (spec. kap. 9.4)."""
    folder = out_dir or source.parent
    stem = source.stem
    for i in range(1, MAX_OUTPUT_INDEX + 1):
        cand = folder / f"{stem}__grid_{i:03d}.lbrn2"
        if not cand.exists() and not cand.with_suffix(".json").exists():
            return cand
    raise GridError("no_free_output_name", "Není volný název výstupního souboru.")


def _publish_no_overwrite(tmp: Path, final: Path) -> None:
    """Zveřejní hotový dočasný soubor pod konečným jménem; existující soubor nikdy nepřepíše.

    Po úspěšném zveřejnění už nesmí selhat: úklid dočasného souboru je jen best-effort.
    """
    if os.name == "nt":
        os.rename(tmp, final)  # na Windows selže, pokud cíl existuje
    else:
        os.link(tmp, final)  # selže, pokud cíl existuje (POSIX rename by přepsal)
        try:
            os.unlink(tmp)
        except OSError:
            pass  # výstup je zveřejněn; dočasný soubor zůstal (např. složka bez práva mazat)


def write_new_file(final: Path, data: bytes, forbidden: Path | None = None) -> Path:
    """Zapíše ``data`` do dočasného souboru ve stejné složce a atomicky jej zveřejní."""
    if final.exists():
        raise GridError("output_exists", "Výstupní soubor už existuje.", path=str(final))
    if forbidden is not None and final.resolve() == forbidden.resolve():
        raise GridError("would_overwrite_source", "Výstup by přepsal originál.")
    tmp = final.with_name(f".{final.name}.tmp-{os.getpid()}")
    try:
        with open(tmp, "xb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        _publish_no_overwrite(tmp, final)
    except FileExistsError:
        raise GridError("output_exists", "Výstupní soubor už existuje.", path=str(final)) from None
    except OSError as e:
        raise GridError("write_failed", "Zápis výstupu selhal.", detail=str(e)) from None
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
    return final
