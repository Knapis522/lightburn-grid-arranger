"""Zápis nového `.lbrn2` cíleným přepisem bajtových úseků (ADR-0002; spec. kap. 9.2, 9.4).

Mění se výhradně obsah ``<XForm>…</XForm>``:

1. nejvyšší skupiny každého přesouvaného výrobku,
2. ``BackupPath`` každého textu v jejím podstromu (je ve světových souřadnicích; KAL-00).

Oba se násobí zleva stejnou afinní transformací výrobku ``T`` (posun, od v1.13 i natočení):
``XForm' = T ∘ XForm``. Čistý posun mění jen ``e, f`` a lineární část nechává bajtově beze změny.

Ostatní bajty souboru zůstávají identické. Výstup se nikdy nezapisuje přes
existující soubor ani přes originál.

**Kopie výrobků (spec. v1.16):** kopie je bajtová kopie elementu nejvyšší skupiny vložená za
poslední nejvyšší ``Shape`` dokumentu. V kopii se stejně jako u přesunu změní jen ``XForm``
skupiny a ``BackupPath`` textů (``T ∘ XForm``) a u cest se sdíleným seznamem vrcholů
(``VertID`` / ``PrimID``) se vynechá ``VertList`` / ``PrimList`` — kopie na ně odkazuje stejně,
jako to dělá LightBurn sám u opakovaných tvarů (ověřeno v KAL-02, Convert to Path).
"""

from __future__ import annotations

import os
import re
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
    role: str  # "group" | "text_backup" | "header"


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


HEADER_ATTRS = ("DeviceName", "MirrorX", "MirrorY")


def _xml_attr(value: str) -> bytes:
    return (value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            .encode("utf-8"))


def header_patches(project: LoadedProject, attrs: dict[str, str]) -> list[PatchOp]:
    """Přepis hodnot atributů hlavičky ``<LightBurnProject …>`` pro cílový laser (spec. v1.23).

    Dovoleny jsou jen ``HEADER_ATTRS``; každý musí v hlavičce existovat právě jednou."""
    ops: list[PatchOp] = []
    root = project.root
    if root.content_start is None:
        raise GridError("xml_malformed", "Projekt nemá obsah.")
    tag_start, tag_end = root.start, root.content_start
    tag = project.data[tag_start:tag_end]
    for name, value in attrs.items():
        if name not in HEADER_ATTRS:
            raise GridError("bad_header_change", "Nepovolená změna hlavičky projektu.", attr=name)
        found = list(re.finditer(rb'\s' + name.encode("ascii") + rb'="([^"]*)"', tag))
        if len(found) != 1:
            raise GridError("bad_header_change", "Atribut hlavičky nenalezen.", attr=name)
        m = found[0]
        start, end = tag_start + m.start(1), tag_start + m.end(1)
        ops.append(PatchOp(start, end, project.data[start:end], _xml_attr(value), "", "header"))
    return sorted(ops, key=lambda o: o.start)


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


# --- kopie výrobků ---------------------------------------------------------------------------


def _line_span(data: bytes, start: int, end: int) -> tuple[int, int]:
    """Rozšíří ``[start, end)`` na celé řádky, pokud je mimo něj na řádku jen odsazení."""
    ls = data.rfind(b"\n", 0, start) + 1
    le = data.find(b"\n", end)
    le = len(data) if le < 0 else le + 1
    if data[ls:start].strip() == b"" and data[end:le].strip() == b"":
        return ls, le
    return start, end


def element_end(data: bytes, node: Node) -> int:
    """Bajt za koncovým tagem elementu (``</Tag>`` nebo ``/>``)."""
    if node.content_end is None:
        close = data.find(b"/>", node.start)
        if close < 0:
            raise GridError("xml_malformed", "Neukončený element.")
        return close + 2
    tag = f"</{node.tag}>".encode("ascii")
    if data[node.content_end : node.content_end + len(tag)] != tag:
        raise GridError("xml_malformed", "Neočekávaný koncový tag.", tag=node.tag)
    return node.content_end + len(tag)


def shared_geometry_children(group: Node) -> list[Node]:
    """``VertList`` / ``PrimList`` tvarů se sdíleným ID — v kopii se vynechají (odkaz na ID stačí)."""
    out = []
    for n in group.iter():
        if n.tag != "Shape":
            continue
        if "VertID" in n.attrs and (v := n.find("VertList")) is not None:
            out.append(v)
        if "PrimID" in n.attrs and (p := n.find("PrimList")) is not None:
            out.append(p)
    return out


def copy_block(project: LoadedProject, item_id: str, move: tuple[float, ...]) -> bytes:
    """Bajty kopie výrobku ``item_id`` po transformaci ``move`` (souřadnice souboru), včetně odsazení a konce řádku."""
    it = project.item(item_id)
    if not it.supported:
        raise GridError("item_not_supported", "Výrobek nelze kopírovat.", item_id=item_id)
    data, node = project.data, it.node
    start, end = _line_span(data, node.start, element_end(data, node))
    t = as_affine(move)
    edits: list[tuple[int, int, bytes]] = []  # (od, do, nahradit) — absolutní pozice v ``data``
    x = _xform_node(node)
    edits.append((x.content_start, x.content_end, _transformed(data, x, t)[1]))
    for n in node.iter():
        if n.tag == "Shape" and n.attrs.get("Type") == "Text" and (bp := n.find("BackupPath")) is not None:
            bx = _xform_node(bp)
            edits.append((bx.content_start, bx.content_end, _transformed(data, bx, t)[1]))
    for g in shared_geometry_children(node):
        a, b = _line_span(data, g.start, element_end(data, g))
        edits.append((a, b, b""))
    edits.sort()
    for (a1, b1, _), (a2, _b2, _) in zip(edits, edits[1:]):
        if a2 < b1:
            raise GridError("overlapping_patch", "Interní chyba: překrývající se úpravy kopie.")
    out, last = bytearray(), start
    for a, b, new in edits:
        out += data[last:a] + new
        last = b
    out += data[last:end]
    if not out.endswith(b"\n"):
        out += b"\r\n" if b"\r\n" in data else b"\n"
    return bytes(out)


def copies_insert_at(project: LoadedProject) -> int:
    """Kopie se vkládají za poslední nejvyšší ``Shape`` (pořadí původních výrobků se nemění)."""
    tops = project.root.findall("Shape")
    if not tops:
        raise GridError("empty_project", "Projekt nemá žádné tvary.")
    last = tops[-1]
    return _line_span(project.data, last.start, element_end(project.data, last))[1]


def apply_with_copies(project: LoadedProject, ops: list[PatchOp], copies: list[tuple[str, tuple[float, ...]]]) -> bytes:
    """Přepisy původních výrobků + vložené kopie ``[(zdrojový výrobek, transformace), …]``."""
    out = apply_patches(project.data, ops)
    if not copies:
        return out
    at = copies_insert_at(project)
    shift = sum(len(op.new) - len(op.old) for op in ops if op.start < at)
    block = b"".join(copy_block(project, src, move) for src, move in copies)
    pos = at + shift
    return out[:pos] + block + out[pos:]


def name_tag(text: str, limit: int = 30) -> str:
    """Krátká značka do názvu souboru (bez diakritiky a mezer): „Modrý Ruida 643XG“ → ``Modry_Ruida_643XG``."""
    import unicodedata

    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return "_".join(re.findall(r"[A-Za-z0-9]+", ascii_text))[:limit].strip("_")


def next_output_path(source: Path, out_dir: Path | None = None, tag: str = "") -> Path:
    """``puvodni__grid_001.lbrn2``, ``…_002``, … — první neexistující (spec. kap. 9.4).

    Je‑li zdrojem už uložený výstup (``puvodni__grid_001``), číslo se nepřidává podruhé, ale
    pokračuje se v řadě originálu (``puvodni__grid_002``). ``tag`` = značka cílového laseru
    (``puvodni__Modry_Ruida__grid_001``, spec. v1.23)."""
    folder = out_dir or source.parent
    stem = re.sub(r"__grid_\d{3}$", "", source.stem) or source.stem
    if tag and not stem.endswith(f"__{tag}"):
        stem = f"{stem}__{tag}"
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
