"""Natočení pro úsporu materiálu — čistá geometrie (spec. v1.13 kap. 7.6)."""

import math

import pytest

from grid_arranger.core.rotation import convex_hull, min_area_angle, rotate_point, rotated_bounds


def tilted_rect(w, h, deg, cx=0.0, cy=0.0):
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    return [rotate_point((x + cx, y + cy), deg, cx, cy) for x, y in pts]


@pytest.mark.parametrize("deg", [30.0, -30.0, 12.5, 44.0, -44.0, 60.0, 135.0])
def test_tilted_rectangle_is_straightened(deg):
    pts = tilted_rect(100, 40, deg)
    a = min_area_angle(pts)
    r = rotated_bounds(pts, a)
    assert sorted((round(r.width, 6), round(r.height, 6))) == [40.0, 100.0]
    assert -45 < a <= 45


def test_axis_aligned_and_symmetric_shapes_are_not_rotated():
    assert min_area_angle(tilted_rect(100, 40, 0)) == 0.0
    assert min_area_angle(tilted_rect(50, 50, 0)) == 0.0
    circle = [(math.cos(t) * 20, math.sin(t) * 20) for t in (i * 2 * math.pi / 360 for i in range(360))]
    assert min_area_angle(circle) == 0.0  # kruh: žádná úspora → nenatáčet
    slightly = tilted_rect(100, 40, 0.3)  # nepatrně nakřivo: vyrovná se (úspora 1,5 %)
    assert min_area_angle(slightly) == pytest.approx(-0.3)
    almost = tilted_rect(100, 40, 0.05)  # úspora pod 0,5 % → nechat být
    assert min_area_angle(almost) == 0.0


def test_irregular_shape_gets_smaller_box():
    # trojúhelník „šikmo“ — nejmenší obdélník má stranu na nejdelší hraně
    pts = [(0, 0), (100, 60), (20, 70)]
    a = min_area_angle(pts)
    assert a != 0.0
    r0, r = rotated_bounds(pts, 0), rotated_bounds(pts, a)
    assert r.width * r.height < r0.width * r0.height * 0.995


def test_convex_hull_and_rotation_about_center():
    assert sorted(convex_hull([(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)])) == [(0, 0), (0, 1), (1, 0), (1, 1)]
    x, y = rotate_point((2, 1), 90, 1, 1)
    assert (round(x, 9), round(y, 9)) == (1.0, 2.0)  # kladně = po směru hodin při ose Y dolů
