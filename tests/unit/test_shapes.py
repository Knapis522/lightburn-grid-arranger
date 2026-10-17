"""Nativní tvary LightBurnu (Ellipse / Rect / Polygon) — rozměry, AABB a ekvivalentní cesta."""

from __future__ import annotations

import math

import pytest

from grid_arranger.adapters.lightburn import geometry as geo
from grid_arranger.adapters.lightburn import shapes
from grid_arranger.adapters.lightburn.coords import Orientation
from grid_arranger.adapters.lightburn.render import Stroke, _path_ops, stroke_points


def rot(deg: float, e: float = 0.0, f: float = 0.0) -> geo.Affine:
    r = math.radians(deg)
    return (math.cos(r), math.sin(r), -math.sin(r), math.cos(r), e, f)


def curve_bbox(native: shapes.Native, m: geo.Affine) -> geo.BBox:
    verts, prims = shapes.native_path(native)
    o = Orientation(False, True)  # sx = sy = 1: jádro = soubor — jen pro rozvinutí křivek
    pts = stroke_points([Stroke("0", _path_ops(verts, prims, m, o))], 0.0005)
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def test_parse_native_reads_dimensions():
    assert shapes.parse_native({"Type": "Ellipse", "Rx": "20", "Ry": "15.000008"}) == shapes.Native("Ellipse", rx=20, ry=15.000008)
    assert shapes.parse_native({"Type": "Rect", "W": "59.999996", "H": "40", "Cr": "0"}).w == pytest.approx(59.999996)
    assert shapes.parse_native({"Type": "Polygon", "Rx": "30.5", "Ry": "30.5", "N": "6"}).n == 6


@pytest.mark.parametrize("attrs", [
    {"Type": "Ellipse", "Rx": "20"},
    {"Type": "Ellipse", "Rx": "0", "Ry": "5"},
    {"Type": "Ellipse", "Rx": "nan", "Ry": "5"},
    {"Type": "Ellipse", "Rx": "abc", "Ry": "5"},
    {"Type": "Rect", "W": "10", "H": "-1", "Cr": "0"},
    {"Type": "Rect", "W": "10", "H": "5", "Cr": "-1"},
    {"Type": "Polygon", "Rx": "5", "Ry": "5", "N": "2"},
    {"Type": "Polygon", "Rx": "5", "Ry": "5", "N": "5.5"},
    {"Type": "Polygon", "Rx": "5", "Ry": "5", "N": "100000"},
])
def test_parse_native_rejects_bad_dimensions(attrs):
    with pytest.raises(geo.GeometryError):
        shapes.parse_native(attrs)


def test_unknown_attributes_are_reported():
    assert shapes.unknown_attrs({"Type": "Ellipse", "CutIndex": "0", "Rx": "1", "Ry": "1"}) == []
    assert shapes.unknown_attrs({"Type": "Ellipse", "CutIndex": "0", "Rx": "1", "Ry": "1", "StartAngle": "0"}) == ["StartAngle"]
    assert shapes.unknown_attrs({"Type": "Rect", "W": "1", "H": "1", "Cr": "0", "N": "6"}) == ["N"]


def poly_world(native, m):
    verts, _ = shapes.native_path(native)
    return [geo.apply(m, v.x, v.y) for v in verts]


@pytest.mark.parametrize("n, rx, ry, lightburn", [
    # vrcholy z LightBurnu (KAL-02: nativní tvar → Convert to Path), místní souřadnice
    (3, 20, 20, [(17.320509, 9.999999), (0, -20), (-17.320503, 10.000008)]),
    (4, 20, 20, [(14.142136, 14.142136), (14.142136, -14.142136), (-14.142138, -14.142133), (-14.142131, 14.14214)]),
    (5, 20, 20, [(11.755705, 16.18034), (19.02113, -6.1803408), (0, -20), (-19.021132, -6.1803331), (-11.755706, 16.18034)]),
    (5, 25, 14, [(14.694632, 11.326238), (23.776413, -4.3262386), (0, -14), (-23.776415, -4.3262329), (-14.694633, 11.326237)]),
    (6, 20, 20, [(10, 17.320507), (20, 0), (9.9999962, -17.320511), (-10.000004, -17.320505), (-20, 0), (-9.9999952, 17.320511)]),
])
def test_polygon_vertices_match_lightburn(n, rx, ry, lightburn):
    ours = poly_world(shapes.Native("Polygon", rx=rx, ry=ry, n=n), geo.IDENTITY)
    assert len(ours) == n
    for p in lightburn:  # stejná množina vrcholů (LightBurn začíná jinde a jde opačně)
        assert min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in ours) < 1e-4


@pytest.mark.parametrize("cr, corner", [(5, (20, -17)), (12, (13, -17)), (30, (8, -17))])
def test_rounded_rect_matches_lightburn_including_clamped_radius(cr, corner):
    # KAL-02: obdélník 50 × 34; poloměr větší než polovina výšky (30) LightBurn omezí na 17
    verts, _ = shapes.native_path(shapes.Native("Rect", w=50, h=34, cr=cr))
    assert any(abs(v.x - corner[0]) < 1e-6 and abs(v.y - corner[1]) < 1e-6 for v in verts)


@pytest.mark.parametrize("deg", [0.0, 25.0, 90.0])
def test_rounded_rect_bbox_is_exact(deg):
    n = shapes.Native("Rect", w=80, h=50, cr=10)
    exact = shapes.native_bbox(n, rot(deg, 5, 7))
    curve = curve_bbox(n, rot(deg, 5, 7))
    for a, b in zip(exact, curve):
        assert a == pytest.approx(b, abs=10 * 3e-4)


@pytest.mark.parametrize("deg", [0.0, 30.0, 90.0, -17.5])
def test_ellipse_bbox_is_exact_under_rotation(deg):
    n = shapes.Native("Ellipse", rx=30, ry=15)
    m = rot(deg, 100, 50)
    exact = shapes.native_bbox(n, m)
    curve = curve_bbox(n, m)
    # Bézierova aproximace čtvrtkruhu je o ≤ 0,03 % větší než elipsa
    for a, b in zip(exact, curve):
        assert a == pytest.approx(b, abs=30 * 3e-4)


def test_ellipse_rotated_30_matches_lightburn_e2():
    # Test_tvary_A „E2“: elipsa 60 × 30 natočená LightBurnem o 30° → AABB 54,08 × 39,69 mm
    x0, y0, x1, y1 = shapes.native_bbox(shapes.Native("Ellipse", rx=30, ry=15.000008), rot(30))
    assert x1 - x0 == pytest.approx(54.083, abs=1e-3) and y1 - y0 == pytest.approx(39.686, abs=1e-3)


def test_rect_is_centered_on_xform():
    assert shapes.native_bbox(shapes.Native("Rect", w=60, h=40), (1, 0, 0, 1, 510, 253)) == (480, 233, 540, 273)


def test_hexagon_has_points_left_and_right():
    # Test_tvary_A „A1“: Rx 30,5, N 6 → 61 × 52,83 mm (hrot vlevo a vpravo, rovná strana nahoře)
    x0, y0, x1, y1 = shapes.native_bbox(shapes.Native("Polygon", rx=30.5, ry=30.5, n=6), (-1, 0, 0, 1, 361.5, 342.5))
    assert (x0, x1) == pytest.approx((331, 392)) and y1 - y0 == pytest.approx(30.5 * math.sqrt(3))


def test_rounded_rect_path_matches_lightburn_conversion():
    # „Obdéln“ v Test_tvary_A: obdélník 80 × 50 s poloměrem 5 převedený v LightBurnu na křivky
    verts, prims = shapes.native_path(shapes.Native("Rect", w=80, h=50, cr=5))
    assert prims == "B0 1L1 2B2 3L3 4B4 5L5 6B6 7L7 0"
    assert (verts[0].x, verts[0].y, verts[0].c1) == (40, -20, None)
    assert verts[0].c0 == pytest.approx((40, -22.761424))
    assert (verts[1].x, verts[1].y, verts[1].c0) == (35, -25, None)
    assert verts[1].c1 == pytest.approx((37.761424, -25))
    assert verts[2].c0 == pytest.approx((-37.761424, -25))


def test_native_paths_are_closed():
    for n in (shapes.Native("Ellipse", rx=3, ry=4), shapes.Native("Rect", w=3, h=4), shapes.Native("Rect", w=3, h=4, cr=1),
              shapes.Native("Polygon", rx=3, ry=3, n=6)):
        verts, prims = shapes.native_path(n)
        assert geo.is_closed(prims, len(verts))


def test_vertlist_accepts_smooth_node_flag():
    # Test_klicenky: „S“ za vrcholem = hladký uzel (jen pro úpravy v LightBurnu)
    v = geo.parse_vertlist("V347 178c0x347c0y189.0457c1x347c1y168.51593SV327 198c0x1c1x1")
    assert [(p.x, p.y) for p in v] == [(347, 178), (327, 198)] and v[0].c0 == (347, 189.0457)
    with pytest.raises(geo.GeometryError):
        geo.parse_vertlist("V1 2X")
