"""MVP-04: materiál, okraje, kolize — T-MVP-11 … 18 (spec. kap. 21.4, 26.1)."""

from __future__ import annotations

import pytest

from grid_arranger.core import Severity, arrange_to_grid, validate_layout
from grid_arranger.core.collision import classify_pair, find_spacing_conflicts
from grid_arranger.domain import Item, MaterialSpec, Obstacle, Rect

from .helpers import request, scattered_items

BOARD = MaterialSpec(0, 0, 600, 400, 5, 5, 5, 5)


def ref_layout(start=(10.0, 20.0), gap=(3.0, 3.0)):
    items = scattered_items(10)
    req = request(items, columns=5, gap=gap, start=start)
    return arrange_to_grid(items, req), req


def test_t_mvp12_reference_grid_fits_board():
    lay, req = ref_layout()
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD)
    assert rep.can_save, rep.issues


def test_t_mvp11_overhang_of_0_1_mm_blocks_and_identifies_item():
    # mřížka 512 mm široká; využitelná plocha končí na 595 → start 83,1 přesahuje o 0,1 mm
    lay, req = ref_layout(start=(83.1, 20))
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD)
    assert not rep.can_save
    errs = [i for i in rep.errors if i.code == "outside_material"]
    assert {e.item_ids[0] for e in errs} == {"g4", "g9"}  # poslední sloupec
    assert errs[0].params["overhang_mm"]["right"] == pytest.approx(0.1)


def test_within_epsilon_is_accepted():
    lay, req = ref_layout(start=(83.0005, 20))
    assert validate_layout(lay, req.gap_x, req.gap_y, BOARD).can_save


@pytest.mark.parametrize(
    "mat, code",
    [
        (MaterialSpec(0, 0, 0, 400), "invalid_material"),
        (MaterialSpec(0, 0, 600, -1), "invalid_material"),
        (MaterialSpec(0, 0, 600, 400, 300, 300), "margins_exceed_material"),
        (MaterialSpec(0, 0, 600, 400, 0, 0, 250, 150), "margins_exceed_material"),
        (MaterialSpec(0, 0, 600, 400, -1), "invalid_margin"),
        (None, "material_missing"),
    ],
)
def test_t_mvp13_invalid_material_blocks(mat, code):
    lay, req = ref_layout()
    rep = validate_layout(lay, req.gap_x, req.gap_y, mat)
    assert not rep.can_save
    assert code in rep.codes()


def test_t_mvp14_overlap_between_targets_identifies_pair():
    a, b = Rect(0, 0, 100, 60), Rect(50, 30, 150, 90)
    assert find_spacing_conflicts([("A", a), ("B", b)], 3, 3) == [("A", "B", "overlap")]


def test_gap_violation_is_distinguished_from_overlap():
    a, b = Rect(0, 0, 100, 60), Rect(101, 0, 201, 60)  # mezera 1 mm < 3 mm
    assert classify_pair(a, b, 3, 3) == "gap"
    assert classify_pair(a, Rect(103, 0, 203, 60), 3, 3) is None


def test_diagonal_neighbours_ok_if_either_axis_has_gap():
    a, b = Rect(0, 0, 100, 60), Rect(103, 63, 203, 123)
    assert classify_pair(a, b, 3, 3) is None


def test_t_mvp15_unselected_group_inside_grid_blocks():
    lay, req = ref_layout()
    obstacle = Obstacle("g_unselected", Rect(200, 50, 260, 90), label="nevybraná skupina")
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD, [obstacle])
    assert not rep.can_save
    hits = [i for i in rep.errors if i.code == "obstacle_overlap"]
    assert hits and all(i.item_ids[1] == "g_unselected" for i in hits)
    assert obstacle.bounds == Rect(200, 50, 260, 90)  # překážka se nikdy nemění


def test_t_mvp16_ungrouped_object_crossing_grid_blocks():
    lay, req = ref_layout()
    line = Obstacle("loose_line", Rect(0, 70, 600, 70.5), kind="path")
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD, [line])
    assert not rep.can_save


def test_obstacle_too_close_is_gap_violation():
    lay, req = ref_layout()
    near = Obstacle("near", Rect(523, 20, 540, 40))  # 1 mm vpravo od mřížky (pravá hrana 522)
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD, [near])
    assert "obstacle_gap_violation" in rep.codes()


def test_obstacle_far_away_is_fine():
    lay, req = ref_layout()
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD, [Obstacle("far", Rect(540, 300, 590, 390))])
    assert rep.can_save


def test_t_mvp17_unmeasurable_obstacle_blocks():
    lay, req = ref_layout()
    rep = validate_layout(lay, req.gap_x, req.gap_y, BOARD, [Obstacle("bitmap?", None)])
    assert not rep.can_save
    assert "obstacle_unmeasurable" in rep.codes()


def test_t_mvp18_zero_gap_touching_is_allowed_with_warning():
    lay, req = ref_layout(gap=(0.0, 0.0))
    rep = validate_layout(lay, 0.0, 0.0, BOARD)
    assert rep.can_save
    assert any(i.code == "zero_gap" and i.severity is Severity.WARNING for i in rep.issues)
    assert find_spacing_conflicts([(p.item_id, p.target_bounds) for p in lay.placements], 0, 0) == []


def test_mixed_sizes_produce_minimum_gap_warning():
    items = [Item("a", Rect.from_xywh(0, 0, 100, 60)), Item("b", Rect.from_xywh(0, 0, 80, 50))]
    lay = arrange_to_grid(items, request(items, columns=2))
    rep = validate_layout(lay, 3, 3, BOARD)
    assert rep.can_save and "minimum_gap_only" in rep.codes()
