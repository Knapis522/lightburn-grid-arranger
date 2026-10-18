"""Krok zpět / krok vpřed (Ctrl+Z / Ctrl+Y) pro rozložení v aplikaci.

Ukládá se celý stav nastavení (pořadí a výběr výrobků, kopie, ruční úhly, mřížka, umístění,
deska) jako neměnný snímek; nový snímek vznikne jen tehdy, když se stav opravdu změnil. Projekt
LightBurnu se tím nemění — týká se jen rozložení, které se teprve uloží.
"""

from __future__ import annotations

from typing import Any

MAX_STEPS = 200


class History:
    def __init__(self) -> None:
        self._states: list[Any] = []
        self._index = -1

    def reset(self, state: Any) -> None:
        self._states = [state]
        self._index = 0

    def push(self, state: Any) -> bool:
        """Zapamatuje nový stav (jen pokud se liší od aktuálního); kroky vpřed se zahodí."""
        if self._index >= 0 and self._states[self._index] == state:
            return False
        del self._states[self._index + 1 :]
        self._states.append(state)
        if len(self._states) > MAX_STEPS:
            del self._states[0]
        self._index = len(self._states) - 1
        return True

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return 0 <= self._index < len(self._states) - 1

    def undo(self) -> Any:
        if not self.can_undo():
            return None
        self._index -= 1
        return self._states[self._index]

    def redo(self) -> Any:
        if not self.can_redo():
            return None
        self._index += 1
        return self._states[self._index]
