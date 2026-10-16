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
