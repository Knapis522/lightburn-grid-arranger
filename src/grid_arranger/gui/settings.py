"""Uživatelské nastavení (spec. kap. 36.3, v1.10 kap. 12.3).

Ukládá se přes ``QSettings`` (Windows: registr uživatele), tedy mimo složku
aplikace — přežije přesun i výměnu ZIPu. Nic z toho se nezapisuje do `.lbrn2`.

* ``ui/language`` — ``auto`` | ``cs`` | ``en``
* ``boards/<laser>/…`` — výchozí deska pro laser podle ``DeviceName`` z projektu
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QSettings

ORGANIZATION = "GridArranger"
APPLICATION = "GridArranger"
LANGUAGES = ("auto", "cs", "en")
THEMES = ("auto", "light", "dark")

# Výchozí desky vlastníka (spec. v1.10). Před veřejným vydáním nahradit prázdným výchozím stavem.
DEFAULT_BOARDS: dict[str, tuple[float, float]] = {
    "Červený Ruida 6445S": (700.0, 500.0),
    "Modrý Ruida 643XG": (500.0, 400.0),
}
DEFAULT_MARGIN = 5.0


@dataclass(frozen=True, slots=True)
class BoardPreset:
    width: float
    height: float
    margins: tuple[float, float, float, float] = (DEFAULT_MARGIN,) * 4
    """Vlevo, vpravo, nahoře, dole (vizuálně na obrazovce)."""


def _key(device: str) -> str:
    # QSettings klíče: lomítka a zpětná lomítka nahradit, aby nevznikly podskupiny
    return "boards/" + device.replace("/", "_").replace("\\", "_")


class UserSettings:
    def __init__(self, qsettings: QSettings | None = None) -> None:
        self._s = qsettings or QSettings(ORGANIZATION, APPLICATION)

    # --- jazyk ---------------------------------------------------------------------------
    def language(self) -> str:
        v = str(self._s.value("ui/language", "auto"))
        return v if v in LANGUAGES else "auto"

    def set_language(self, value: str) -> None:
        if value not in LANGUAGES:
            raise ValueError(value)
        self._s.setValue("ui/language", value)
        self._s.sync()

    # --- vzhled ---------------------------------------------------------------------------
    def theme(self) -> str:
        v = str(self._s.value("ui/theme", "auto"))
        return v if v in THEMES else "auto"

    def set_theme(self, value: str) -> None:
        if value not in THEMES:
            raise ValueError(value)
        self._s.setValue("ui/theme", value)
        self._s.sync()

    # --- desky podle laseru ----------------------------------------------------------------
    def board_for(self, device: str) -> BoardPreset | None:
        k = _key(device)
        if self._s.contains(k + "/width"):
            try:
                w = float(self._s.value(k + "/width"))
                h = float(self._s.value(k + "/height"))
                m = tuple(float(self._s.value(f"{k}/margin_{s}", DEFAULT_MARGIN)) for s in ("left", "right", "top", "bottom"))
                if w <= 0 or h <= 0 or any(v < 0 for v in m):
                    return None
                return BoardPreset(w, h, m)  # type: ignore[arg-type]
            except (TypeError, ValueError):
                return None  # poškozený záznam: raději nic nepředvyplnit
        if device in DEFAULT_BOARDS:
            w, h = DEFAULT_BOARDS[device]
            return BoardPreset(w, h)
        return None

    def set_board_for(self, device: str, preset: BoardPreset) -> None:
        k = _key(device)
        self._s.setValue(k + "/width", preset.width)
        self._s.setValue(k + "/height", preset.height)
        for side, v in zip(("left", "right", "top", "bottom"), preset.margins):
            self._s.setValue(f"{k}/margin_{side}", v)
        self._s.sync()
