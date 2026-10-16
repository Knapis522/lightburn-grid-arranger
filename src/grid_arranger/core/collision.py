"""Kontrola materiálu, okrajů, mezer a kolizí (MVP-04; spec. kap. 21.4).

Pravidlo odstupu (spec. v1.9): dvojice obdélníků je v pořádku, pokud je jejich
vodorovná vzdálenost ≥ ``gap_x − ε`` **nebo** svislá vzdálenost ≥ ``gap_y − ε``.
Pokud jsou obě vzdálenosti záporné (víc než ε), jde o překryv.
Stejné pravidlo platí mezi přesouvanými výrobky i vůči nepřesouvaným překážkám.

Validátor nic neopravuje: neposouvá, neškáluje ani neodstraňuje (kap. 21.4).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..domain.models import LayoutResult, MaterialSpec, Obstacle, Rect, _finite
from .tolerance import EPSILON


class Severity(Enum):
    ERROR = "error"  # blokuje uložení
    WARNING = "warning"  # uložení dovoleno, uživatel musí vidět upozornění


@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    severity: Severity
    item_ids: tuple[str, ...] = ()
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ValidationReport:
    issues: tuple[Issue, ...]

    @property
    def errors(self) -> tuple[Issue, ...]:
        return tuple(i for i in self.issues if i.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Issue, ...]:
        return tuple(i for i in self.issues if i.severity is Severity.WARNING)

    @property
    def can_save(self) -> bool:
        return not self.errors

    def codes(self) -> set[str]:
        return {i.code for i in self.issues}


def _separation(a: Rect, b: Rect) -> tuple[float, float]:
    sx = max(b.left - a.right, a.left - b.right)
    sy = max(b.top - a.bottom, a.top - b.bottom)
    return sx, sy


def classify_pair(a: Rect, b: Rect, gap_x: float, gap_y: float, eps: float = EPSILON) -> str | None:
    """Vrátí ``None`` (v pořádku), ``"overlap"`` nebo ``"gap"`` (porušená mezera)."""
    sx, sy = _separation(a, b)
    if sx >= gap_x - eps or sy >= gap_y - eps:
        return None
    if sx < -eps and sy < -eps:
        return "overlap"
    return "gap"


def find_spacing_conflicts(
    boxes: Sequence[tuple[str, Rect]], gap_x: float, gap_y: float, eps: float = EPSILON
) -> list[tuple[str, str, str]]:
    """Najde všechny dvojice porušující mezeru. Zametání podle X: O(n log n + k)."""
    ordered = sorted(boxes, key=lambda b: (b[1].left, b[0]))
    out: list[tuple[str, str, str]] = []
    for i, (ida, a) in enumerate(ordered):
        reach = a.right + gap_x - eps
        for idb, b in ordered[i + 1 :]:
            if b.left >= reach:
                break  # všechny další jsou vodorovně dost daleko
            kind = classify_pair(a, b, gap_x, gap_y, eps)
            if kind:
                out.append((ida, idb, kind))
    return out


def usable_area(m: MaterialSpec) -> tuple[Rect | None, list[Issue]]:
    """Využitelná plocha materiálu po odečtení okrajů, nebo chyby zadání."""
    issues: list[Issue] = []
    if not _finite(m.board_left, m.board_top, m.board_width, m.board_height) or m.board_width <= 0 or m.board_height <= 0:
        issues.append(Issue("invalid_material", Severity.ERROR, params={"width": m.board_width, "height": m.board_height}))
        return None, issues
    margins = (m.margin_left, m.margin_right, m.margin_top, m.margin_bottom)
    if not _finite(*margins) or any(v < 0 for v in margins):
        issues.append(Issue("invalid_margin", Severity.ERROR, params={"margins": margins}))
        return None, issues
    left = m.board_left + m.margin_left
    top = m.board_top + m.margin_top
    right = m.board_left + m.board_width - m.margin_right
    bottom = m.board_top + m.board_height - m.margin_bottom
    if right <= left or bottom <= top:
        issues.append(Issue("margins_exceed_material", Severity.ERROR, params={"margins": margins}))
        return None, issues
    return Rect(left, top, right, bottom), issues


def validate_layout(
    layout: LayoutResult,
    gap_x: float,
    gap_y: float,
    material: MaterialSpec | None,
    obstacles: Iterable[Obstacle] = (),
    eps: float = EPSILON,
) -> ValidationReport:
    """Úplná kontrola rozložení před uložením. ``can_save`` je True jen bez chyb."""
    issues: list[Issue] = []
    placed = [(p.item_id, p.target_bounds) for p in layout.placements]

    # 1) Materiál a okraje
    if material is None:
        issues.append(Issue("material_missing", Severity.ERROR))
    else:
        area, mat_issues = usable_area(material)
        issues.extend(mat_issues)
        if area is not None:
            for item_id, r in placed:
                over = {
                    "left": area.left - r.left,
                    "top": area.top - r.top,
                    "right": r.right - area.right,
                    "bottom": r.bottom - area.bottom,
                }
                exceeded = {k: v for k, v in over.items() if v > eps}
                if exceeded:
                    issues.append(Issue("outside_material", Severity.ERROR, (item_id,), {"overhang_mm": exceeded}))

    # 2) Mezery mezi přesouvanými výrobky
    for a, b, kind in find_spacing_conflicts(placed, gap_x, gap_y, eps):
        code = "items_overlap" if kind == "overlap" else "gap_violation"
        issues.append(Issue(code, Severity.ERROR, (a, b)))

    # 3) Nepřesouvané překážky
    for ob in obstacles:
        if ob.bounds is None:
            issues.append(Issue("obstacle_unmeasurable", Severity.ERROR, (ob.id,), {"label": ob.label}))
            continue
        for item_id, r in placed:
            kind = classify_pair(r, ob.bounds, gap_x, gap_y, eps)
            if kind:
                code = "obstacle_overlap" if kind == "overlap" else "obstacle_gap_violation"
                issues.append(Issue(code, Severity.ERROR, (item_id, ob.id), {"label": ob.label}))

    # 4) Upozornění
    if gap_x == 0 or gap_y == 0:
        issues.append(Issue("zero_gap", Severity.WARNING, params={"gap_x": gap_x, "gap_y": gap_y}))
    if not layout.uniform_size:
        issues.append(Issue("minimum_gap_only", Severity.WARNING))

    return ValidationReport(tuple(issues))
