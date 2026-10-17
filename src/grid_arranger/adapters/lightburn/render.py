"""Geometrie pro náhled: skutečné křivky výrobku v souřadnicích jádra (bez Qt).

Ověřeno na V-001 (LightBurn 2.2): Bézierův úsek ``B i j`` má řídicí body
``c0`` vrcholu *i* (odchozí) a ``c1`` vrcholu *j* (příchozí); chybějící řídicí bod
= vrchol sám. Slouží jen k vykreslení — zápis souboru ji nepoužívá.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import geometry as geo
from .coords import Orientation
from .read import LoadedProject, _Ctx, _xform
from .xmltree import Node

_PRIM = re.compile(r"([LB])(\d+) (\d+)")

Point = tuple[float, float]


@dataclass(slots=True)
class Stroke:
    """Jedna cesta: operace ``("M", p)``, ``("L", p)``, ``("C", c1, c2, p)``, ``("Z",)``."""

    cut: str
    ops: list[tuple] = field(default_factory=list)


def _path_ops(verts: list[geo.Vertex], prims: str | None, m: geo.Affine, o: Orientation) -> list[tuple]:
    def P(x: float, y: float) -> Point:
        fx, fy = geo.apply(m, x, y)
        return o.to_screen_point(fx, fy)

    pts = [P(v.x, v.y) for v in verts]
    t = (prims or "").strip()
    if t == "LineClosed" or not t:
        ops: list[tuple] = [("M", pts[0])] + [("L", p) for p in pts[1:]]
        if t == "LineClosed":
            ops.append(("Z",))
        return ops
    ops = []
    last_end: int | None = None
    start: int | None = None
    for kind, si, sj in _PRIM.findall(t):
        i, j = int(si), int(sj)
        if i >= len(verts) or j >= len(verts):
            continue
        if i != last_end:
            ops.append(("M", pts[i]))
            start = i
        if kind == "L":
            ops.append(("L", pts[j]))
        else:
            a, b = verts[i], verts[j]
            c1 = P(*a.c0) if a.c0 else pts[i]
            c2 = P(*b.c1) if b.c1 else pts[j]
            ops.append(("C", c1, c2, pts[j]))
        last_end = j
        if j == start:
            ops.append(("Z",))
            last_end = None
    return ops


def _walk(node: Node, parent: geo.Affine, ctx: _Ctx, o: Orientation, out: list[Stroke]) -> None:
    kind = node.attrs.get("Type", "")
    try:
        m = geo.compose(parent, _xform(node))
    except geo.GeometryError:
        return
    if kind == "Group":
        kids = node.find("Children")
        for c in kids.children if kids is not None else []:
            if c.tag == "Shape":
                _walk(c, m, ctx, o, out)
    elif kind == "Path":
        try:
            verts, prims = ctx.path_geometry(node)
            out.append(Stroke(node.attrs.get("CutIndex", ""), _path_ops(verts, prims, m, o)))
        except geo.GeometryError:
            pass
    elif kind == "Text":
        bp = node.find("BackupPath")
        if bp is not None:
            try:
                verts, prims = ctx.path_geometry(bp)
                out.append(Stroke(node.attrs.get("CutIndex", ""), _path_ops(verts, prims, _xform(bp), o)))
            except geo.GeometryError:
                pass


class ProjectRenderer:
    """Křivky výrobků a volných objektů v původní poloze (souřadnice jádra), s mezipamětí."""

    def __init__(self, project: LoadedProject) -> None:
        self.project = project
        self._ctx = _Ctx(project.root)
        self._cache: dict[str, list[Stroke]] = {}

    def strokes(self, shape_id: str) -> list[Stroke]:
        if shape_id not in self._cache:
            node = self._node(shape_id)
            out: list[Stroke] = []
            if node is not None:
                _walk(node, geo.IDENTITY, self._ctx, self.project.info.orientation, out)
            self._cache[shape_id] = out
        return self._cache[shape_id]

    def _node(self, shape_id: str) -> Node | None:
        for it in self.project.items:
            if it.id == shape_id:
                return it.node
        for ls in self.project.loose:
            if ls.id == shape_id:
                return ls.node
        return None


def _flatten_cubic(p0: Point, p1: Point, p2: Point, p3: Point, tol: float, out: list[Point], depth: int = 0) -> None:
    """Body na Bézierově křivce; mezi sousedními body se křivka neodchýlí o víc než ``tol``."""
    def dist(p: Point) -> float:
        dx, dy = p3[0] - p0[0], p3[1] - p0[1]
        n = (dx * dx + dy * dy) ** 0.5
        if n == 0:
            return ((p[0] - p0[0]) ** 2 + (p[1] - p0[1]) ** 2) ** 0.5
        return abs((p[0] - p0[0]) * dy - (p[1] - p0[1]) * dx) / n

    if depth > 18 or max(dist(p1), dist(p2)) <= tol:
        out.append(p3)
        return
    m01 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    m12 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
    m23 = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
    a = ((m01[0] + m12[0]) / 2, (m01[1] + m12[1]) / 2)
    b = ((m12[0] + m23[0]) / 2, (m12[1] + m23[1]) / 2)
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    _flatten_cubic(p0, m01, a, mid, tol, out, depth + 1)
    _flatten_cubic(mid, b, m23, p3, tol, out, depth + 1)


def stroke_points(strokes: list[Stroke], tol: float = 0.002) -> list[Point]:
    """Body všech křivek (Bézier rozvinutý s odchylkou ≤ ``tol`` mm) — pro výpočet natočení."""
    pts: list[Point] = []
    for st in strokes:
        cur: Point | None = None
        for op in st.ops:
            if op[0] in ("M", "L"):
                cur = op[1]
                pts.append(cur)
            elif op[0] == "C" and cur is not None:
                _flatten_cubic(cur, op[1], op[2], op[3], tol, pts)
                cur = op[3]
    return pts
