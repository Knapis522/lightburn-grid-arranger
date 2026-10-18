"""Automatický počet sloupců podle šířky desky (spec. v1.24)."""

from __future__ import annotations

import pytest

from grid_arranger.adapters.lightburn.read import load_project
from grid_arranger.application.arrange_job import AUTO_COLUMNS, ArrangeParams, MaterialInput, make_plan
from grid_arranger.domain import GridError

from .lbrn2_builder import card, project


def cards(n, w=100, h=60):
    return project([card(i * 150, 0, w, h, text=f"K{i}") for i in range(n)])


@pytest.mark.parametrize("width, expected", [(700, 6), (500, 4), (330, 3), (215, 2), (110, 1), (50, 1)])
def test_auto_columns_fill_board_width(write_project, width, expected):
    # 10 kartiček 100 mm, mezera 3, okraje 5: (W − 10 + 3) // 103 sloupců
    p = load_project(write_project(cards(10)))
    plan = make_plan(p, ArrangeParams(AUTO_COLUMNS, 3, 3, MaterialInput(width, 2000)))
    assert plan.layout.columns == expected and plan.columns_auto
    if expected > 1 or width >= 110:
        assert plan.layout.grid_bounds.width <= width - 10 + 1e-6


def test_auto_columns_never_more_than_items(write_project):
    plan = make_plan(load_project(write_project(cards(3))), ArrangeParams(AUTO_COLUMNS, 3, 3, MaterialInput(1000, 500)))
    assert plan.layout.columns == 3 and plan.layout.rows == 1


def test_auto_columns_use_rotation_to_fit_more(write_project):
    # kartičky na výšku 60 × 100: po 90° se vejde víc sloupců jen tehdy, když se mřížka zmenší
    p = load_project(write_project(cards(8, 100, 60)))
    plan = make_plan(p, ArrangeParams(AUTO_COLUMNS, 3, 3, MaterialInput(400, 1000), rotation="90"))
    assert plan.layout.grid_bounds.width <= 390 + 1e-6 and plan.report.can_save


def test_auto_columns_need_board(write_project):
    with pytest.raises(GridError) as e:
        make_plan(load_project(write_project(cards(3))), ArrangeParams(AUTO_COLUMNS, 3, 3, None))
    assert e.value.code == "material_missing"
