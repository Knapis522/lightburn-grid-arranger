"""Geometrie pro náhled (adapters/lightburn/render.py)."""

from __future__ import annotations

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.adapters.lightburn.render import ProjectRenderer

from .lbrn2_builder import Group, Path, Text, card, project, rect


def ops_of(p, sid="G1"):
    return [s.ops for s in ProjectRenderer(p).strokes(sid)]


def test_line_closed_rect_in_screen_coords(write_project):
    p = load_project(write_project(project([Group([rect(0, 0, 100, 60)], xform=(1, 0, 0, 1, 10, 20))], mirror_x=False)))
    (ops,) = ops_of(p)
    assert ops[0] == ("M", (10.0, 20.0))
    assert [o[0] for o in ops] == ["M", "L", "L", "L", "Z"]
    assert ops[2] == ("L", (110.0, 80.0))


def test_mirror_x_flips_screen_x(write_project):
    p = load_project(write_project(project([Group([rect(0, 0, 100, 60)], xform=(1, 0, 0, 1, 10, 20))], mirror_x=True)))
    (ops,) = ops_of(p)
    assert ops[0] == ("M", (-10.0, 20.0))


def test_bezier_uses_c0_of_start_and_c1_of_end(write_project):
    path = Path([(0, 0), (10, 0)], prims="B0 1", bezier_ctrl=True)  # c0 = (x+1, y), c1 = (x−1, y)
    p = load_project(write_project(project([Group([rect(-5, -5, 30, 10), path])], mirror_x=False)))
    strokes = ProjectRenderer(p).strokes("G1")
    curve = strokes[1].ops
    assert curve[0] == ("M", (0.0, 0.0))
    assert curve[1] == ("C", (1.0, 0.0), (9.0, 0.0), (10.0, 0.0))


def test_text_uses_backup_path_world_transform(write_project):
    g = Group([rect(0, 0, 100, 60), Text("A", (5, 5, 20, 10))], xform=(1, 0, 0, 1, 200, 300))
    p = load_project(write_project(project([g], mirror_x=False)))
    strokes = ProjectRenderer(p).strokes("G1")
    text = strokes[1]
    assert text.cut == "1"
    assert text.ops[0] == ("M", (205.0, 305.0))


def test_strokes_cover_outline_bounds(write_project):
    p = load_project(write_project(project([card(30, 40)])))
    it = p.items[0]
    pts = [pt for s in ProjectRenderer(p).strokes("G1") for op in s.ops for pt in op[1:]]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    b = it.screen_bounds
    assert min(xs) == pytest.approx(b.left) and max(xs) == pytest.approx(b.right)
    assert min(ys) == pytest.approx(b.top) and max(ys) == pytest.approx(b.bottom)


def test_unknown_id_gives_no_strokes(write_project):
    p = load_project(write_project(project([card(0, 0)])))
    assert ProjectRenderer(p).strokes("nope") == []
