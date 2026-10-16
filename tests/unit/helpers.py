"""Pomocné funkce pro testy jádra — pouze syntetická data."""

from __future__ import annotations

import random

from grid_arranger.domain import GridRequest, Item, Rect


def scattered_items(n: int, w: float = 100.0, h: float = 60.0, seed: int = 1) -> list[Item]:
    """n výrobků stejné velikosti rozházených po ploše (jako v reálném projektu)."""
    rnd = random.Random(seed)
    return [
        Item(id=f"g{i}", bounds=Rect.from_xywh(rnd.uniform(-900, 900), rnd.uniform(-900, 900), w, h), source_order=i)
        for i in range(n)
    ]


def mixed_items(n: int, seed: int = 7) -> list[Item]:
    rnd = random.Random(seed)
    return [
        Item(
            id=f"m{i}",
            bounds=Rect.from_xywh(rnd.uniform(-500, 500), rnd.uniform(-500, 500), rnd.uniform(5, 250), rnd.uniform(5, 180)),
            source_order=i,
        )
        for i in range(n)
    ]


def request(items: list[Item], columns: int, gap=(3.0, 3.0), start=(10.0, 20.0), order=None, **kw) -> GridRequest:
    return GridRequest(
        ordered_item_ids=tuple(order if order is not None else (i.id for i in items)),
        columns=columns,
        gap_x=gap[0],
        gap_y=gap[1],
        start_x=start[0],
        start_y=start[1],
        **kw,
    )
