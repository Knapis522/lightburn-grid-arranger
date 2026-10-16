"""MVP-02/03: výběr a ruční pořadí — T-MVP-05, 06, 08, 09, 10 (spec. kap. 21.2, 21.3, 26.1)."""

from __future__ import annotations

import pytest

from grid_arranger.core import arrange_to_grid, default_order, deselect, move_down, move_up, select, validate_permutation
from grid_arranger.domain import GridError, Item, Rect

from .helpers import request, scattered_items


def items_in_reverse_document_order():
    # pořadí v seznamu ≠ pořadí v dokumentu → default_order musí řadit podle source_order
    return [Item(f"g{i}", Rect.from_xywh(i * 7, 0, 100, 60), source_order=i) for i in reversed(range(5))]


def test_default_order_is_document_order():
    assert default_order(items_in_reverse_document_order()) == ("g0", "g1", "g2", "g3", "g4")


def test_t_mvp05_only_selected_are_placed():
    items = scattered_items(8)
    lay = arrange_to_grid(items, request(items, columns=3, order=("g1", "g4", "g6")))
    assert {p.item_id for p in lay.placements} == {"g1", "g4", "g6"}


def test_t_mvp08_move_last_to_first_and_swap():
    order = ("a", "b", "c", "d")
    for _ in range(3):
        order = move_up(order, "d")
    assert order == ("d", "a", "b", "c")
    # prohodit první a poslední opakovanými kroky
    order = ("a", "b", "c", "d")
    order = move_down(move_down(move_down(order, "a"), "a"), "a")  # a na konec
    for _ in range(2):
        order = move_up(order, "d")
    order = move_up(order, "d")
    assert order == ("d", "b", "c", "a")


def test_t_mvp08_layout_follows_new_order():
    items = scattered_items(4)
    order = ("g3", "g1", "g2", "g0")
    lay = arrange_to_grid(items, request(items, columns=4, order=order))
    assert [p.item_id for p in sorted(lay.placements, key=lambda p: p.target_bounds.left)] == list(order)


def test_move_at_edges_is_noop():
    order = ("a", "b", "c")
    assert move_up(order, "a") == order
    assert move_down(order, "c") == order


def test_t_mvp09_deselect_and_reselect_goes_to_end_without_duplicates():
    order = ("a", "b", "c", "d")
    order = deselect(order, "b")
    assert order == ("a", "c", "d")
    order = select(order, "b")
    assert order == ("a", "c", "d", "b")
    with pytest.raises(GridError) as e:
        select(order, "b")
    assert e.value.code == "duplicate_item"
    validate_permutation(order, {"a", "b", "c", "d"})


def test_t_mvp10_reset_to_document_order():
    items = items_in_reverse_document_order()
    order = move_up(move_up(default_order(items), "g4"), "g4")
    assert order != default_order(items)
    assert default_order([i for i in items if i.id in order]) == ("g0", "g1", "g2", "g3", "g4")


def test_operations_on_unknown_item_fail():
    with pytest.raises(GridError):
        move_up(("a",), "x")
    with pytest.raises(GridError):
        deselect(("a",), "x")


def test_order_functions_do_not_mutate_input():
    order = ["a", "b", "c"]
    move_up(order, "b")
    assert order == ["a", "b", "c"]
