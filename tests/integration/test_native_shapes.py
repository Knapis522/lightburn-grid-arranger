"""Nativní tvary LightBurnu ve výrobcích: čtení, náhled, přesun, natočení (spec. v1.14 kap. 5.3)."""

from __future__ import annotations

import math

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.adapters.lightburn.render import ProjectRenderer
from grid_arranger.application.arrange_job import ArrangeParams, MaterialInput, make_plan, run

from .lbrn2_builder import Group, Native, Text, ellipse, keyring, project


def write(tmp_path, data, name="t.lbrn2"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


def params(**kw):
    base = dict(columns=2, gap_x=5, gap_y=5, material=MaterialInput(700, 500))
    base.update(kw)
    return ArrangeParams(**base)


def rot(deg, e=0.0, f=0.0):
    r = math.radians(deg)
    return (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), e, f)


def codes(item):
    return [r.code for r in item.reasons]


@pytest.mark.parametrize("mirror_x", [True, False])
def test_keyring_with_nested_group_is_supported_and_arranged(tmp_path, mirror_x):
    src = write(tmp_path, project([keyring(100, 100), keyring(200, 100, text="K2"), keyring(300, 150, text="K3")],
                                  mirror_x=mirror_x))
    before = src.read_bytes()
    p = load_project(src)
    assert [it.supported for it in p.items] == [True, True, True]
    x0, y0, x1, y1 = p.items[0].file_bbox
    assert (x1 - x0, y1 - y0) == pytest.approx((40, 40))
    res = run(src, params(), out_dir=tmp_path)
    assert res.problems == [] and src.read_bytes() == before
    q = load_project(res.output)
    assert all(it.supported for it in q.items)
    changed = [a for a, b in zip(before.split(b"\r\n"), res.output.read_bytes().split(b"\r\n")) if a != b]
    assert len(changed) <= 6  # jen XForm nejvyšší skupiny a BackupPath textu; kruhy uvnitř beze změny
    assert not any(b"Ellipse" in line for line in changed)


def test_rect_and_hexagon_outlines(tmp_path):
    rect = Group([Native("Rect", {"W": 60, "H": 40, "Cr": 0}, xform=(1, 0, 0, 1, 510, 253)), Text("OB", (500, 248, 20, 10))])
    hexa = Group([Native("Polygon", {"Rx": 30.5, "Ry": 30.5, "N": 6}, xform=(-1, 0, 0, 1, 361.5, 342.5)),
                  Text("A1", (350, 338, 20, 10))])
    p = load_project(write(tmp_path, project([rect, hexa])))
    assert [it.supported for it in p.items] == [True, True]
    assert p.items[0].file_bbox == pytest.approx((480, 233, 540, 273))
    b = p.items[1].file_bbox
    assert (b[2] - b[0], b[3] - b[1]) == pytest.approx((61, 30.5 * math.sqrt(3)))


@pytest.mark.parametrize("shape, code", [
    (Native("Ellipse", {"Rx": 20, "Ry": 20, "Start": 0}), "unknown_shape_attribute"),
    (Native("Ellipse", {"Rx": 20}), "unreadable_shape"),
    (Native("Ellipse", {"Rx": 20, "Ry": 20}, children="<Extra/>"), "unknown_element"),
])
def test_unknown_native_shapes_are_blocked(tmp_path, shape, code):
    p = load_project(write(tmp_path, project([Group([shape, Text("X", (-5, -5, 10, 10))])])))
    assert not p.items[0].supported and code in codes(p.items[0])


def test_polygons_and_rounded_rects_are_supported(tmp_path):
    pent = Group([Native("Polygon", {"Rx": 20, "Ry": 20, "N": 5}, xform=(1, 0, 0, 1, 100, 100)), Text("P", (95, 95, 10, 10))])
    rounded = Group([Native("Rect", {"W": 60, "H": 40, "Cr": 5}, xform=(1, 0, 0, 1, 300, 100)), Text("R", (295, 95, 10, 10))])
    p = load_project(write(tmp_path, project([pent, rounded])))
    assert [it.supported for it in p.items] == [True, True]
    x0, y0, x1, y1 = p.items[0].file_bbox
    # pětiúhelník: vrchol v (0, −20), šířka 2·20·cos 18°, výška 20 + 20·cos 36°
    assert (x1 - x0, y0, y1) == pytest.approx((40 * math.cos(math.radians(18)), 80, 100 + 20 * math.cos(math.radians(36))))
    assert p.items[1].file_bbox == pytest.approx((270, 80, 330, 120))


def test_native_shapes_are_drawn_in_preview(tmp_path):
    p = load_project(write(tmp_path, project([keyring(100, 100)])))
    strokes = ProjectRenderer(p).strokes("G1")
    kinds = [op[0] for st in strokes for op in st.ops]
    assert kinds.count("C") >= 8 and kinds.count("Z") >= 2  # dvě elipsy po 4 Bézierových úsecích


def test_loose_native_shape_is_an_obstacle(tmp_path):
    p = load_project(write(tmp_path, project([keyring(100, 100), ellipse(400, 300, 10)])))
    assert p.loose[0].kind == "Ellipse" and p.loose[0].file_bbox == pytest.approx((390, 290, 410, 310))
    obstacle = p.obstacles_for({"G1"})[0]
    assert obstacle.bounds is not None


def test_rotated_ellipses_are_straightened_when_the_grid_gets_smaller(tmp_path):
    def tilted_ellipse(cx, cy):
        return Group([Native("Ellipse", {"Rx": 30, "Ry": 15}, xform=rot(30, cx, cy)), Text("E", (cx - 5, cy - 5, 10, 10))])

    src = write(tmp_path, project([tilted_ellipse(100, 100), tilted_ellipse(250, 100), tilted_ellipse(100, 250),
                                   tilted_ellipse(250, 250)]))
    p = load_project(src)
    plan = make_plan(p, params(rotation="any"))
    assert set(plan.rotations) == {"G1", "G2", "G3", "G4"}
    assert {round(abs(a), 6) for a in plan.rotations.values()} <= {30.0, 60.0}  # „hezký“ úhel, ne 29,6°
    for pl in plan.layout.placements:
        assert sorted((pl.target_bounds.width, pl.target_bounds.height)) == pytest.approx([30, 60], abs=0.02)
    res = run(src, params(rotation="any"), out_dir=tmp_path)
    assert res.problems == []
    q = load_project(res.output)
    for it in q.items:
        x0, y0, x1, y1 = it.file_bbox
        assert sorted((x1 - x0, y1 - y0)) == pytest.approx([30, 60], abs=1e-3)


def test_rotation_is_skipped_when_it_does_not_shrink_the_grid(tmp_path):
    fixed = Group([Native("Rect", {"W": 20, "H": 39.7, "Cr": 0}, xform=(1, 0, 0, 1, 100, 100)), Text("T", (95, 95, 10, 10))])
    tilted = Group([Native("Ellipse", {"Rx": 30, "Ry": 15}, xform=rot(30, 300, 100)), Text("E", (295, 95, 10, 10))])
    p = load_project(write(tmp_path, project([fixed, tilted])))
    plan = make_plan(p, params(columns=2, rotation="any", no_rotate=frozenset({"G1"})))
    # původně 79,1 × 39,7 mm; narovnaná elipsa 60 × 30 → 85 × 39,7; na výšku 30 × 60 → 55 × 60 — obojí větší
    assert plan.rotations == {}


def test_round_items_are_not_turned_by_90(tmp_path):
    src = write(tmp_path, project([keyring(100, 100), keyring(200, 100), keyring(300, 100),
                                   Group([Native("Rect", {"W": 40, "H": 20, "Cr": 0}, xform=(1, 0, 0, 1, 100, 300)),
                                          Text("R", (95, 295, 10, 10))])]))
    plan = make_plan(load_project(src), params(columns=1, rotation="90"))
    assert not {"G1", "G2", "G3"} & set(plan.rotations)
