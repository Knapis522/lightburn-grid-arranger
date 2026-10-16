"""Výpočetní jádro: deterministická mřížka, pořadí a kontrola kolizí.

Nesmí importovat Qt ani nic z adaptéru LightBurnu (spec. kap. 7.5, 11).
"""

from .collision import Issue, Severity, ValidationReport, validate_layout
from .grid_layout import arrange_to_grid
from .tolerance import EPSILON
from .order import (
    default_order,
    move_down,
    move_to,
    move_up,
    select,
    deselect,
    swap,
    validate_permutation,
)

__all__ = [
    "EPSILON",
    "Issue",
    "Severity",
    "ValidationReport",
    "arrange_to_grid",
    "default_order",
    "deselect",
    "move_down",
    "move_to",
    "move_up",
    "select",
    "swap",
    "validate_layout",
    "validate_permutation",
]
