"""ALG-01 … ALG-10 a T-MVP-01 … 04 (spec. kap. 14.1, 26.1)."""

from __future__ import annotations

import math
import time

import pytest

from grid_arranger.core import EPSILON, arrange_to_grid
from grid_arranger.core.collision import find_spacing_conflicts
from grid_arranger.domain import Align, GridError, Item, Rect

from .helpers import mixed_items, request, scattered_items

ABS = 1e-9  # numerická přesnost výpočtu; geometrická tolerance je EPSILON


def lefts_tops(layout):
    return sorted({round(p.target_bounds.left, 9) for p in layout.placements}), sorted(
        {round(p.target_bounds.top, 9) for p in layout.placements}
    )


# --- ALG-01 / T-MVP-01: referenční příklad 512 × 123 mm -------------------------------------


def test_alg01_reference_example_512x123():
    items = scattered_items(10)
    lay = arrange_to_grid(items, request(items, columns=5))

    lefts, tops = lefts_tops(lay)
    assert lefts == [10, 113, 216, 319, 422]
    assert tops == [20, 83]
    g = lay.grid_bounds
    assert (g.width, g.height) == pytest.approx((512, 123), abs=ABS)
    assert (g.right, g.bottom) == pytest.approx((522, 143), abs=ABS)
    assert (lay.columns, lay.rows) == (5, 2)
    assert len(lay.placements) == 10  # nikoli 20 — nic se nekopíruje
    assert {p.item_id for p in lay.placements} == {i.id for i in items}
    assert lay.uniform_size


def test_alg01_row_major_order_left_to_right_top_to_bottom():
    items = scattered_items(10)
    lay = arrange_to_grid(items, request(items, columns=5))
    for p in lay.placements:
        assert (p.row, p.column) == divmod(p.index, 5)
        assert p.target_bounds.left == pytest.approx(10 + p.column * 103, abs=ABS)
        assert p.target_bounds.top == pytest.approx(20 + p.row * 63, abs=ABS)


def test_dx_dy_move_old_bounds_onto_target():
    items = scattered_items(10)
    lay = arrange_to_grid(items, request(items, columns=5))
    for p in lay.placements:
        moved = p.old_bounds.translated(p.dx, p.dy)
        assert moved.left == pytest.approx(p.target_bounds.left, abs=ABS)
        assert moved.top == pytest.approx(p.target_bounds.top, abs=ABS)
        assert moved.width == pytest.approx(p.old_bounds.width, abs=ABS)  # rozměr výrobku se nemění


# --- ALG-02, ALG-03 / T-MVP-02 -------------------------------------------------------------


def test_alg02_single_item_more_columns_than_items():
    items = scattered_items(1)
    lay = arrange_to_grid(items, request(items, columns=5))
    assert (lay.columns, lay.rows, len(lay.placements)) == (1, 1, 1)
    assert (lay.grid_bounds.width, lay.grid_bounds.height) == pytest.approx((100, 60))


def test_alg03_partial_last_row_starts_left():
    items = scattered_items(7)
    lay = arrange_to_grid(items, request(items, columns=3))
    assert (lay.columns, lay.rows) == (3, 3)
    last = [p for p in lay.placements if p.row == 2]
    assert len(last) == 1 and last[0].column == 0
    assert last[0].target_bounds.left == pytest.approx(10)
    assert len(lay.placements) == 7


def test_more_columns_than_items_width_uses_occupied_columns():
    items = scattered_items(3)
    lay = arrange_to_grid(items, request(items, columns=5))
    assert lay.columns == 3
    assert lay.grid_bounds.width == pytest.approx(3 * 100 + 2 * 3)


# --- ALG-04: různé rozměry (adaptivní mřížka) ------------------------------------------------


def test_alg04_mixed_sizes_column_width_and_row_height_are_maxima():
    items = [
        Item("a", Rect.from_xywh(0, 0, 100, 60)),
        Item("b", Rect.from_xywh(0, 0, 80, 50)),
        Item("c", Rect.from_xywh(0, 0, 120, 40)),
        Item("d", Rect.from_xywh(0, 0, 90, 70)),
    ]
    lay = arrange_to_grid(items, request(items, columns=2, gap=(5, 4), start=(0, 0)))
    assert lay.column_widths == (120, 90)  # max(a,c), max(b,d)
    assert lay.row_heights == (60, 70)  # max(a,b), max(c,d)
    tb = {p.item_id: p.target_bounds for p in lay.placements}
    assert (tb["a"].left, tb["a"].top) == (0, 0)
    assert (tb["b"].left, tb["b"].top) == (125, 0)
    assert (tb["c"].left, tb["c"].top) == (0, 64)
    assert (tb["d"].left, tb["d"].top) == (125, 64)
    assert (lay.grid_bounds.width, lay.grid_bounds.height) == (215, 134)
    assert not lay.uniform_size


@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("columns", [1, 2, 3, 7])
def test_alg04_mixed_sizes_never_violate_minimum_gap(seed, columns):
    items = mixed_items(25, seed=seed)
    lay = arrange_to_grid(items, request(items, columns=columns, gap=(2.5, 1.25)))
    boxes = [(p.item_id, p.target_bounds) for p in lay.placements]
    assert find_spacing_conflicts(boxes, 2.5, 1.25, EPSILON) == []
    for p in lay.placements:  # každý výrobek leží uvnitř mřížky
        g, t = lay.grid_bounds, p.target_bounds
        assert g.left - ABS <= t.left and t.right <= g.right + ABS
        assert g.top - ABS <= t.top and t.bottom <= g.bottom + ABS


def test_center_alignment_inside_cell():
    items = [Item("big", Rect.from_xywh(0, 0, 100, 60)), Item("small", Rect.from_xywh(0, 0, 40, 20))]
    lay = arrange_to_grid(items, request(items, columns=1, start=(0, 0), align_x=Align.CENTER, align_y=Align.CENTER))
    s = lay.placement_for("small").target_bounds
    assert s.left == pytest.approx(30)  # (100 − 40) / 2
    assert s.top == pytest.approx(63)  # druhý řádek, výška 20 = výška řádku


# --- ALG-05 / T-MVP-03: neplatné vstupy -----------------------------------------------------


@pytest.mark.parametrize(
    "kw, code",
    [
        ({"columns": 0}, "invalid_columns"),
        ({"columns": -1}, "invalid_columns"),
        ({"columns": 2.0}, "invalid_columns"),
        ({"columns": True}, "invalid_columns"),
        ({"columns": 3, "gap": (-1, 3)}, "invalid_gap"),
        ({"columns": 3, "gap": (3, math.nan)}, "invalid_gap"),
        ({"columns": 3, "gap": (math.inf, 3)}, "invalid_gap"),
        ({"columns": 3, "start": (math.nan, 0)}, "invalid_start"),
        ({"columns": 3, "start": (0, -math.inf)}, "invalid_start"),
    ],
)
def test_alg05_invalid_parameters_are_rejected(kw, code):
    items = scattered_items(5)
    with pytest.raises(GridError) as e:
        arrange_to_grid(items, request(items, **kw))
    assert e.value.code == code


@pytest.mark.parametrize("bad", [(math.nan, 0, 1, 1), (0, 0, math.inf, 1), (10, 0, 5, 1)])
def test_alg05_malformed_bounds_rejected(bad):
    with pytest.raises(GridError) as e:
        Rect(*bad)
    assert e.value.code == "invalid_bounds"


def test_degenerate_item_rejected():
    items = [Item("flat", Rect(0, 0, 100, 0))]
    with pytest.raises(GridError) as e:
        arrange_to_grid(items, request(items, columns=1))
    assert e.value.code == "degenerate_item"


def test_t_mvp06_empty_selection_rejected():
    items = scattered_items(3)
    with pytest.raises(GridError) as e:
        arrange_to_grid(items, request(items, columns=3, order=()))
    assert e.value.code == "empty_selection"


# --- ALG-06: změna pořadí -------------------------------------------------------------------


def test_alg06_reordering_changes_only_positions_not_identity():
    items = scattered_items(6)
    a = arrange_to_grid(items, request(items, columns=3))
    rev = tuple(reversed([i.id for i in items]))
    b = arrange_to_grid(items, request(items, columns=3, order=rev))
    assert {p.item_id for p in a.placements} == {p.item_id for p in b.placements}
    assert a.placement_for("g0").target_bounds == b.placement_for("g5").target_bounds
    assert b.placement_for("g0").index == 5


# --- ALG-07 / T-MVP-04: idempotence ---------------------------------------------------------


@pytest.mark.parametrize("make", [scattered_items, mixed_items])
def test_alg07_idempotent_on_already_arranged_layout(make):
    items = make(9)
    req = request(items, columns=4)
    first = arrange_to_grid(items, req)
    moved = [Item(p.item_id, p.target_bounds) for p in first.placements]
    second = arrange_to_grid(moved, req)
    for p, q in zip(second.placements, first.placements):
        assert abs(p.dx) <= EPSILON and abs(p.dy) <= EPSILON
        assert p.target_bounds.left == pytest.approx(q.target_bounds.left, abs=EPSILON)
        assert p.target_bounds.top == pytest.approx(q.target_bounds.top, abs=EPSILON)


def test_determinism_same_input_same_output():
    items = mixed_items(30)
    req = request(items, columns=6, gap=(0.125, 0.3))
    assert arrange_to_grid(items, req) == arrange_to_grid(items, req)


# --- ALG-08: velké N ------------------------------------------------------------------------


@pytest.mark.parametrize("columns", [1, 7, 32, 1000])
def test_alg08_thousand_items(columns):
    items = mixed_items(1000, seed=3)
    t0 = time.perf_counter()
    lay = arrange_to_grid(items, request(items, columns=columns))
    assert time.perf_counter() - t0 < 5
    ids = [p.item_id for p in lay.placements]
    assert len(ids) == 1000 and len(set(ids)) == 1000


# --- ALG-09: desetinné mezery ---------------------------------------------------------------


def test_alg09_fractional_gap_precision():
    items = scattered_items(40, w=12.345, h=6.789)
    lay = arrange_to_grid(items, request(items, columns=40, gap=(0.125, 0.125), start=(0.1, 0.2)))
    for p in lay.placements:
        expected = 0.1 + p.column * (12.345 + 0.125)
        assert abs(p.target_bounds.left - expected) < 1e-9
    assert lay.grid_bounds.width == pytest.approx(40 * 12.345 + 39 * 0.125, abs=1e-9)


# --- ALG-10: identifikátory -----------------------------------------------------------------


def test_alg10_duplicate_id_in_order():
    items = scattered_items(3)
    with pytest.raises(GridError) as e:
        arrange_to_grid(items, request(items, columns=2, order=("g0", "g1", "g0")))
    assert e.value.code == "duplicate_item"


def test_alg10_unknown_id_in_order():
    items = scattered_items(3)
    with pytest.raises(GridError) as e:
        arrange_to_grid(items, request(items, columns=2, order=("g0", "nope")))
    assert e.value.code == "unknown_item"


def test_alg10_duplicate_item_definition():
    items = scattered_items(2) + [Item("g0", Rect(0, 0, 1, 1))]
    with pytest.raises(GridError) as e:
        arrange_to_grid(items, request(items[:2], columns=2))
    assert e.value.code == "duplicate_item"


def test_unselected_items_get_no_placement():
    items = scattered_items(8)
    lay = arrange_to_grid(items, request(items, columns=3, order=("g2", "g5", "g7")))
    assert [p.item_id for p in lay.placements] == ["g2", "g5", "g7"]


# --- plnění od počátku vpravo (spec. v1.10) -------------------------------------------------


def test_fill_from_top_right_mirrors_columns():
    from grid_arranger.domain import Corner

    items = scattered_items(7)
    a = arrange_to_grid(items, request(items, columns=3))
    b = arrange_to_grid(items, request(items, columns=3, fill_from=Corner.TOP_RIGHT))
    assert a.grid_bounds == b.grid_bounds
    g = b.grid_bounds
    first = b.placement_for("g0").target_bounds
    assert first.right == pytest.approx(g.right) and first.top == pytest.approx(g.top)  # 1. kus vpravo nahoře
    last = b.placement_for("g6").target_bounds
    assert last.right == pytest.approx(g.right) and last.top == pytest.approx(20 + 2 * 63)  # neúplný řádek začíná vpravo
    for pa, pb in zip(a.placements, b.placements):  # zrcadlení v rámci mřížky
        assert pb.target_bounds.left == pytest.approx(g.left + g.right - pa.target_bounds.right)


def test_fill_from_top_right_mixed_sizes_aligned_toward_origin():
    from grid_arranger.domain import Corner

    items = [Item("wide", Rect.from_xywh(0, 0, 120, 40)), Item("narrow", Rect.from_xywh(0, 0, 80, 40)), Item("x", Rect.from_xywh(0, 0, 60, 40))]
    lay = arrange_to_grid(items, request(items, columns=2, gap=(5, 5), start=(0, 0), fill_from=Corner.TOP_RIGHT))
    # sloupec 1 (vpravo) = max(120, 60) = 120, sloupec 2 (vlevo) = 80; šířka 205
    assert lay.grid_bounds.width == pytest.approx(205)
    assert lay.placement_for("wide").target_bounds.right == pytest.approx(205)
    assert lay.placement_for("x").target_bounds.right == pytest.approx(205)  # menší kus přiléhá k rohu počátku
    assert lay.placement_for("narrow").target_bounds.left == pytest.approx(0)
