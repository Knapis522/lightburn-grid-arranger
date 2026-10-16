"""Výběr a ruční pořadí výrobků (MVP-02, MVP-03; spec. kap. 6, 21.2, 21.3).

Všechny funkce jsou čisté: vrací novou n-tici a nic nemění na místě.
Výběr a pořadí jsou dva různé údaje — pořadí obsahuje jen vybrané položky.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from ..domain.errors import GridError
from ..domain.models import Item


def default_order(items: Iterable[Item]) -> tuple[str, ...]:
    """Pořadí podle dokumentu (`source_order`), stabilně při shodě."""
    return tuple(i.id for i in sorted(items, key=lambda i: i.source_order))


def validate_permutation(order: Sequence[str], allowed_ids: Iterable[str]) -> None:
    """Ověří, že ``order`` je neprázdná permutace podmnožiny ``allowed_ids`` bez duplicit."""
    allowed = set(allowed_ids)
    if len(order) == 0:
        raise GridError("empty_selection", "Není vybrán žádný výrobek.")
    seen: set[str] = set()
    for item_id in order:
        if item_id in seen:
            raise GridError("duplicate_item", "Výrobek je v pořadí vícekrát.", item_id=item_id)
        if item_id not in allowed:
            raise GridError("unknown_item", "Pořadí obsahuje neznámý výrobek.", item_id=item_id)
        seen.add(item_id)


def _index(order: Sequence[str], item_id: str) -> int:
    try:
        return list(order).index(item_id)
    except ValueError:
        raise GridError("unknown_item", "Výrobek není ve vybraném pořadí.", item_id=item_id) from None


def move_up(order: Sequence[str], item_id: str) -> tuple[str, ...]:
    """Posune položku o jedno místo nahoru; první položka zůstane na místě."""
    i = _index(order, item_id)
    lst = list(order)
    if i > 0:
        lst[i - 1], lst[i] = lst[i], lst[i - 1]
    return tuple(lst)


def move_down(order: Sequence[str], item_id: str) -> tuple[str, ...]:
    """Posune položku o jedno místo dolů; poslední položka zůstane na místě."""
    i = _index(order, item_id)
    lst = list(order)
    if i < len(lst) - 1:
        lst[i + 1], lst[i] = lst[i], lst[i + 1]
    return tuple(lst)


def deselect(order: Sequence[str], item_id: str) -> tuple[str, ...]:
    """Odebere položku z výběru (identita výrobku tím nezaniká)."""
    _index(order, item_id)
    return tuple(i for i in order if i != item_id)


def select(order: Sequence[str], item_id: str) -> tuple[str, ...]:
    """Přidá položku do výběru. Deterministické pravidlo: **na konec** (spec. kap. 21.3)."""
    if item_id in order:
        raise GridError("duplicate_item", "Výrobek už je vybrán.", item_id=item_id)
    return tuple(order) + (item_id,)
