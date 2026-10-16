"""Doménový model jádra (spec. kap. 10, 25.1).

Všechny délky jsou v **mm** (`float`). Souřadnice jsou v **systému jádra**:
osa X doprava, **osa Y dolů**, ``top`` je horní hrana (spec. kap. 7.1).
Převod ze souřadnic souboru `.lbrn2` dělá výhradně adaptér.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from .errors import GridError


def _finite(*values: float) -> bool:
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in values)


@dataclass(frozen=True, slots=True)
class Rect:
    """Osově zarovnaný obdélník (AABB) v systému jádra."""

    left: float
    top: float
    right: float
    bottom: float

    def __post_init__(self) -> None:
        if not _finite(self.left, self.top, self.right, self.bottom):
            raise GridError("invalid_bounds", "Souřadnice obdélníku nejsou konečná čísla.", rect=repr(self))
        if self.right < self.left or self.bottom < self.top:
            raise GridError("invalid_bounds", "Obdélník má zápornou šířku nebo výšku.", rect=repr(self))

    @classmethod
    def from_xywh(cls, x: float, y: float, w: float, h: float) -> Rect:
        return cls(x, y, x + w, y + h)

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    def translated(self, dx: float, dy: float) -> Rect:
        return Rect(self.left + dx, self.top + dy, self.right + dx, self.bottom + dy)

    def union(self, other: Rect) -> Rect:
        return Rect(
            min(self.left, other.left),
            min(self.top, other.top),
            max(self.right, other.right),
            max(self.bottom, other.bottom),
        )


class Align(Enum):
    """Zarovnání výrobku uvnitř buňky adaptivní mřížky. MVP používá START (vlevo/nahoře)."""

    START = "start"
    CENTER = "center"
    END = "end"


@dataclass(frozen=True, slots=True)
class Item:
    """Výrobek = jedna nejvyšší skupina; ``bounds`` je AABB jejího řezného obrysu."""

    id: str
    bounds: Rect
    label: str = ""
    source_order: int = 0


@dataclass(frozen=True, slots=True)
class GridRequest:
    """Parametry mřížky (spec. kap. 7.1, 21.1).

    ``ordered_item_ids`` je uživatelem zobrazené pořadí **vybraných** výrobků;
    musí jít o permutaci bez duplicit (spec. kap. 6 bod 5).
    """

    ordered_item_ids: tuple[str, ...]
    columns: int
    gap_x: float
    gap_y: float
    start_x: float
    start_y: float
    align_x: Align = Align.START
    align_y: Align = Align.START


@dataclass(frozen=True, slots=True)
class Placement:
    item_id: str
    index: int
    row: int
    column: int
    old_bounds: Rect
    target_bounds: Rect
    dx: float
    dy: float


@dataclass(frozen=True, slots=True)
class LayoutResult:
    placements: tuple[Placement, ...]
    grid_bounds: Rect
    columns: int
    rows: int
    column_widths: tuple[float, ...]
    row_heights: tuple[float, ...]
    uniform_size: bool
    """True, pokud mají všechny výrobky stejné rozměry (v toleranci) → mezera je přesná, jinak jen minimální."""

    def placement_for(self, item_id: str) -> Placement:
        for p in self.placements:
            if p.item_id == item_id:
                return p
        raise KeyError(item_id)


@dataclass(frozen=True, slots=True)
class MaterialSpec:
    """Uživatelský obdélník materiálu a okraje (spec. kap. 21.4). Nejde o pracovní plochu laseru."""

    board_left: float
    board_top: float
    board_width: float
    board_height: float
    margin_left: float = 0.0
    margin_right: float = 0.0
    margin_top: float = 0.0
    margin_bottom: float = 0.0


@dataclass(frozen=True, slots=True)
class Obstacle:
    """Nepřesouvaný objekt. ``bounds=None`` znamená, že rozsah nelze spolehlivě určit → blokace."""

    id: str
    bounds: Rect | None
    label: str = ""
    kind: str = field(default="object")
