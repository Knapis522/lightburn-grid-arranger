"""Chyby jádra se stabilními kódy.

Kód chyby (`code`) je stabilní a nepřekládá se; lokalizovanou větu sestaví až UI
z kódu a parametrů (spec. kap. 36.4). Text výjimky slouží jen pro vývojáře a logy.
"""

from __future__ import annotations

from typing import Any


class GridError(ValueError):
    """Neplatný vstup jádra. Výpočet ani zápis nesmí pokračovat."""

    def __init__(self, code: str, message: str, **params: Any) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.params = params
