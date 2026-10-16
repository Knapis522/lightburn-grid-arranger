"""Deterministická adaptivní mřížka (MVP-01; spec. kap. 7.2–7.5, 21.1).

Šířka sloupce = největší šířka výrobku v daném sloupci, výška řádku = největší
výška v daném řádku. Pro výrobky stejných rozměrů je výsledek totožný s režimem A
(kap. 7.2) a mezera je přesná; pro různé rozměry je zaručena **minimální** mezera.

Funkce nic nekopíruje: každý vybraný výrobek dostane právě jedno umístění.
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from ..domain.errors import GridError
from ..domain.models import Align, Corner, GridRequest, Item, LayoutResult, Placement, Rect, _finite
from .collision import find_spacing_conflicts
from .order import validate_permutation
from .tolerance import EPSILON


def _validate_request(req: GridRequest) -> None:
    if isinstance(req.columns, bool) or not isinstance(req.columns, int) or req.columns < 1:
        raise GridError("invalid_columns", "Počet sloupců musí být celé číslo ≥ 1.", columns=req.columns)
    for name in ("gap_x", "gap_y"):
        v = getattr(req, name)
        if not _finite(v) or v < 0:
            raise GridError("invalid_gap", "Mezera musí být konečné číslo ≥ 0.", field=name, value=v)
    for name in ("start_x", "start_y"):
        v = getattr(req, name)
        if not _finite(v):
            raise GridError("invalid_start", "Počátek mřížky musí být konečné číslo.", field=name, value=v)
    if not isinstance(req.align_x, Align) or not isinstance(req.align_y, Align):
        raise GridError("invalid_alignment", "Neplatné zarovnání.")
    if not isinstance(req.fill_from, Corner):
        raise GridError("invalid_fill_corner", "Neplatný roh plnění.")


def _offset(cell: float, size: float, align: Align) -> float:
    if align is Align.START:
        return 0.0
    if align is Align.CENTER:
        return (cell - size) / 2.0
    return cell - size


def _starts(origin: float, sizes: list[float], gap: float) -> list[float]:
    # fsum = přesný součet; výsledek nezávisí na pořadí sčítání (determinismus, kap. 7.4).
    return [math.fsum([origin, *sizes[:j], gap * j]) for j in range(len(sizes))]


def arrange_to_grid(items: Iterable[Item], request: GridRequest) -> LayoutResult:
    """Vypočte cílové polohy vybraných výrobků v pořadí ``request.ordered_item_ids``.

    ``items`` může obsahovat i nevybrané výrobky; použijí se jen ty uvedené v pořadí.
    Při jakémkoli neplatném vstupu vyhodí :class:`GridError` a nevrátí žádný výsledek.
    """
    _validate_request(request)

    by_id: dict[str, Item] = {}
    for it in items:
        if it.id in by_id:
            raise GridError("duplicate_item", "Dva výrobky mají stejný identifikátor.", item_id=it.id)
        by_id[it.id] = it

    validate_permutation(request.ordered_item_ids, by_id)
    ordered = [by_id[i] for i in request.ordered_item_ids]
    for it in ordered:
        if it.bounds.width <= 0 or it.bounds.height <= 0:
            raise GridError("degenerate_item", "Výrobek má nulovou šířku nebo výšku.", item_id=it.id)

    n = len(ordered)
    cols = min(request.columns, n)  # bez fiktivních prázdných sloupců (kap. 7.2, 21.1)
    rows = math.ceil(n / cols)

    col_w = [max(ordered[i].bounds.width for i in range(j, n, cols)) for j in range(cols)]
    row_h = [max(it.bounds.height for it in ordered[r * cols : (r + 1) * cols]) for r in range(rows)]

    # Roh plnění: TOP_LEFT = čtení (1. sloupec vlevo); TOP_RIGHT = od počátku vpravo
    # (1. sloupec vpravo, řádky se plní doleva; zarovnání v buňce se zrcadlí k rohu plnění).
    from_right = request.fill_from is Corner.TOP_RIGHT
    vis_w = list(reversed(col_w)) if from_right else col_w
    align_x = {Align.START: Align.END, Align.END: Align.START}.get(request.align_x, request.align_x) if from_right else request.align_x
    xs = _starts(request.start_x, vis_w, request.gap_x)
    ys = _starts(request.start_y, row_h, request.gap_y)

    placements: list[Placement] = []
    for index, it in enumerate(ordered):
        r, c = divmod(index, cols)
        v = cols - 1 - c if from_right else c
        w, h = it.bounds.width, it.bounds.height
        left = xs[v] + _offset(vis_w[v], w, align_x)
        top = ys[r] + _offset(row_h[r], h, request.align_y)
        placements.append(
            Placement(
                item_id=it.id,
                index=index,
                row=r,
                column=c,
                old_bounds=it.bounds,
                target_bounds=Rect(left, top, left + w, top + h),
                dx=left - it.bounds.left,
                dy=top - it.bounds.top,
            )
        )

    grid = Rect(
        request.start_x,
        request.start_y,
        math.fsum([request.start_x, *col_w, request.gap_x * (cols - 1)]),
        math.fsum([request.start_y, *row_h, request.gap_y * (rows - 1)]),
    )
    w0, h0 = ordered[0].bounds.width, ordered[0].bounds.height
    uniform = all(abs(it.bounds.width - w0) <= EPSILON and abs(it.bounds.height - h0) <= EPSILON for it in ordered)

    # Pojistka dle pseudokódu kap. 7.5: výsledek algoritmu nesmí porušit mezery.
    conflicts = find_spacing_conflicts(
        [(p.item_id, p.target_bounds) for p in placements], request.gap_x, request.gap_y, EPSILON
    )
    if conflicts:
        raise GridError("internal_overlap", "Interní chyba: výpočet mřížky porušil mezeru.", pairs=conflicts)

    return LayoutResult(
        placements=tuple(placements),
        grid_bounds=grid,
        columns=cols,
        rows=rows,
        column_widths=tuple(col_w),
        row_heights=tuple(row_h),
        uniform_size=uniform,
    )
