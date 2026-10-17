"""Geometrie `.lbrn2`: afinní transformace, seznamy vrcholů a primitiv, AABB.

Formát ověřený v KAL-00 (LightBurn 2.2.00, `docs/FORMAT_COMPATIBILITY.md`):

* ``XForm``: ``a b c d e f`` — ``x' = a·x + c·y + e``, ``y' = b·x + d·y + f``.
* ``VertList``: ``V<x> <y>`` a volitelně ``c0x<v>c0y<v>`` / ``c1x<v>c1y<v>``;
  samotné ``c0x1`` / ``c1x1`` znamená „bez řídicího bodu“. Za vrcholem může stát příznak
  ``S`` (hladký uzel, jen pro úpravy v LightBurnu — geometrii nemění; KAL-02).
* ``PrimList``: ``LineClosed`` nebo posloupnost ``L<i> <j>`` / ``B<i> <j>``.

AABB je **konzervativní**: obsahuje vrcholy i všechny řídicí body (konvexní obal
Bézierovy křivky), takže rozměr nikdy nepodhodnotí (spec. v1.9, kap. 5).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

Affine = tuple[float, float, float, float, float, float]
IDENTITY: Affine = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
BBox = tuple[float, float, float, float]  # minx, miny, maxx, maxy (souřadnice souboru)

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
_VERTEX = re.compile(rf"\s*({_NUM})\s+({_NUM})((?:c[01][xy]{_NUM})*)S?\s*$")
_CTRL = re.compile(rf"c([01])([xy])({_NUM})")
_PRIM = re.compile(r"([LB])(\d+) (\d+)")


class GeometryError(ValueError):
    """Geometrii nelze spolehlivě přečíst → objekt je nezměřitelný."""


def parse_xform(text: str) -> Affine:
    parts = text.split()
    if len(parts) != 6:
        raise GeometryError(f"XForm nemá 6 čísel: {text!r}")
    try:
        vals = tuple(float(v) for v in parts)
    except ValueError:
        raise GeometryError(f"XForm obsahuje nečíselnou hodnotu: {text!r}") from None
    if not all(math.isfinite(v) for v in vals):
        raise GeometryError(f"XForm obsahuje nekonečno/NaN: {text!r}")
    return vals  # type: ignore[return-value]


def compose(outer: Affine, inner: Affine) -> Affine:
    """``outer ∘ inner`` — nejdřív ``inner``, potom ``outer``."""
    a, b, c, d, e, f = outer
    a2, b2, c2, d2, e2, f2 = inner
    return (a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2, a * e2 + c * f2 + e, b * e2 + d * f2 + f)


def apply(m: Affine, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


@dataclass(frozen=True, slots=True)
class Vertex:
    x: float
    y: float
    c0: tuple[float, float] | None
    c1: tuple[float, float] | None


def parse_vertlist(text: str) -> list[Vertex]:
    chunks = text.split("V")
    if chunks[0].strip():
        raise GeometryError("VertList nezačíná vrcholem")
    out: list[Vertex] = []
    for chunk in chunks[1:]:
        m = _VERTEX.match(chunk)
        if not m:
            raise GeometryError(f"Nečitelný vrchol: {chunk[:40]!r}")
        ctrl: dict[str, float] = {}
        rest = m.group(3)
        consumed = 0
        for cm in _CTRL.finditer(rest):
            if cm.start() != consumed:
                raise GeometryError(f"Nečitelný řídicí bod: {rest[:40]!r}")
            ctrl[cm.group(1) + cm.group(2)] = float(cm.group(3))
            consumed = cm.end()
        if consumed != len(rest):
            raise GeometryError(f"Nečitelný řídicí bod: {rest[:40]!r}")
        c0 = (ctrl["0x"], ctrl["0y"]) if "0y" in ctrl else None
        c1 = (ctrl["1x"], ctrl["1y"]) if "1y" in ctrl else None
        v = Vertex(float(m.group(1)), float(m.group(2)), c0, c1)
        if not all(math.isfinite(t) for t in (v.x, v.y, *(c0 or ()), *(c1 or ()))):
            raise GeometryError("Vrchol obsahuje nekonečno/NaN")
        out.append(v)
    if not out:
        raise GeometryError("Prázdný VertList")
    return out


def is_closed(primlist: str | None, n_vertices: int) -> bool:
    """True, pokud primitiva tvoří jednu uzavřenou smyčku. Neznámý zápis → False."""
    if primlist is None:
        return False
    t = primlist.strip()
    if t == "LineClosed":
        return n_vertices >= 3
    prims = _PRIM.findall(t)
    if not prims or "".join(f"{k}{i} {j}" for k, i, j in prims) != t:
        return False
    idx = [(int(i), int(j)) for _, i, j in prims]
    if any(i >= n_vertices or j >= n_vertices for i, j in idx):
        return False
    chained = all(idx[k][1] == idx[k + 1][0] for k in range(len(idx) - 1))
    return chained and idx[-1][1] == idx[0][0]


def path_bbox(vertices: list[Vertex], m: Affine) -> BBox:
    pts = []
    for v in vertices:
        pts.append(apply(m, v.x, v.y))
        if v.c0:
            pts.append(apply(m, *v.c0))
        if v.c1:
            pts.append(apply(m, *v.c1))
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def union(boxes: list[BBox]) -> BBox:
    return (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def contains(outer: BBox, inner: BBox, eps: float) -> bool:
    return (
        inner[0] >= outer[0] - eps
        and inner[1] >= outer[1] - eps
        and inner[2] <= outer[2] + eps
        and inner[3] <= outer[3] + eps
    )


def fmt_num(v: float) -> str:
    """Číslo pro ``XForm``: 8 platných číslic, desetinná tečka, bez exponentu (KAL-00)."""
    if not math.isfinite(v):
        raise ValueError("Nelze zapsat nekonečno/NaN")
    if v == 0:
        return "0"
    s = format(v, ".8g")
    if "e" in s or "E" in s:
        exp = math.floor(math.log10(abs(v)))
        s = f"{v:.{max(0, 7 - exp)}f}"
        if "." in s:
            s = s.rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s
