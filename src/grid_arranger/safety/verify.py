"""Nezávislá kontrola výstupu před zveřejněním (MVP-05; spec. kap. 9.3, 14.3, 21.5).

Kontrola **nepoužívá plán přepisů** — oba soubory znovu rozparsuje a porovná:

1. Počet prvků ``XForm`` je stejný a soubory jsou bajtově shodné všude mimo obsah
   ``XForm`` (tím jsou prokazatelně beze změny tvary, texty, vrstvy, CutSetting…).
   Jedinou dovolenou výjimkou je nic — thumbnail se nemění.
2. Každý ``XForm`` je beze změny, kromě nejvyšší skupiny přesouvaného výrobku a
   ``BackupPath`` textů v ní; u nich musí výsledek přesně odpovídat ``T ∘ původní``
   (čistý posun: lineární část bajtově beze změny, ``e, f`` o plánovaný posun).
3. Výstup je znovu čitelný a struktura (tagy, atributy) je shodná.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..adapters.lightburn import geometry as geo
from ..adapters.lightburn.xmltree import Node, parse
from ..domain.errors import GridError

TOLERANCE = 1e-3  # mm; zápis na 8 platných číslic
LINEAR_TOLERANCE = 1e-6  # koeficienty natočení (bezrozměrné)


@dataclass(frozen=True, slots=True)
class _X:
    node: Node
    top_index: int | None  # pořadí nejvyšší Shape, pod kterou leží (1-based), jinak None
    role: str  # "group" | "text_backup" | "other"


def _collect(root: Node) -> list[_X]:
    out: list[_X] = []
    tops = {id(s): i for i, s in enumerate(root.findall("Shape"), start=1)}
    for n in root.iter():
        if n.tag != "XForm":
            continue
        owner = n.parent
        chain = [owner, *owner.ancestors()] if owner is not None else []
        top = next((tops[id(a)] for a in chain if id(a) in tops), None)
        if owner is not None and id(owner) in tops and owner.attrs.get("Type") == "Group":
            role = "group"
        elif owner is not None and owner.tag == "BackupPath" and owner.parent is not None and owner.parent.attrs.get("Type") == "Text":
            role = "text_backup"
        else:
            role = "other"
        out.append(_X(n, top, role))
    return out


def _masked(data: bytes, xs: list[_X]) -> bytes:
    parts, last = [], 0
    for x in sorted(xs, key=lambda x: x.node.content_start or 0):
        if x.node.content_start is None:
            continue
        parts.append(data[last : x.node.content_start])
        last = x.node.content_end
    parts.append(data[last:])
    return b"\x00".join(parts)


def _structure(root: Node) -> list[tuple[str, tuple]]:
    return [(n.tag, tuple(sorted(n.attrs.items()))) for n in root.iter()]


def _affine(move: tuple[float, ...]) -> tuple[float, ...]:
    return (1.0, 0.0, 0.0, 1.0, float(move[0]), float(move[1])) if len(move) == 2 else tuple(float(v) for v in move)


def verify_output(source: bytes, output: bytes, moves_file: dict[int, tuple[float, ...]]) -> list[str]:
    """Vrátí seznam nalezených problémů (prázdný = v pořádku).

    ``moves_file`` mapuje pořadí nejvyšší skupiny (1-based) na posun ``(dx, dy)`` nebo afinní
    transformaci ``(a, b, c, d, e, f)`` v souřadnicích souboru.
    """
    problems: list[str] = []
    try:
        r_src, r_out = parse(source), parse(output)
    except GridError as e:
        return [f"output_unreadable: {e}"]

    if _structure(r_src) != _structure(r_out):
        problems.append("structure_changed")

    xs_src, xs_out = _collect(r_src), _collect(r_out)
    if len(xs_src) != len(xs_out):
        return problems + ["xform_count_changed"]
    if _masked(source, xs_src) != _masked(output, xs_out):
        problems.append("bytes_outside_xform_changed")

    for a, b in zip(xs_src, xs_out):
        ta, tb = a.node.text, b.node.text
        move = moves_file.get(a.top_index) if a.top_index is not None else None
        allowed = move is not None and a.role in ("group", "text_backup")
        if not allowed:
            if ta != tb:
                problems.append(f"unexpected_xform_change: shape #{a.top_index} role={a.role}")
            continue
        try:
            va, vb = geo.parse_xform(ta), geo.parse_xform(tb)
        except geo.GeometryError:
            problems.append(f"unreadable_xform: shape #{a.top_index}")
            continue
        t = _affine(move)
        if t[:4] == (1.0, 0.0, 0.0, 1.0):
            if ta.split()[:4] != tb.split()[:4]:
                problems.append(f"linear_part_changed: shape #{a.top_index}")
        expected = geo.compose(t, va)  # type: ignore[arg-type]
        if any(abs(vb[i] - expected[i]) > LINEAR_TOLERANCE * max(1.0, abs(expected[i])) for i in range(4)):
            problems.append(f"wrong_rotation: shape #{a.top_index} role={a.role}")
        if abs(vb[4] - expected[4]) > TOLERANCE or abs(vb[5] - expected[5]) > TOLERANCE:
            problems.append(f"wrong_translation: shape #{a.top_index} role={a.role}")
    return problems
