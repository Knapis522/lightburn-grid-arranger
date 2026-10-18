"""Uživatelské nastavení (spec. kap. 36.3, v1.10 kap. 12.3).

Ukládá se přes ``QSettings`` (Windows: registr uživatele), tedy mimo složku
aplikace — přežije přesun i výměnu ZIPu. Nic z toho se nezapisuje do `.lbrn2`.

* ``ui/language`` — ``auto`` | ``cs`` | ``en``
* ``boards/<laser>/…`` — výchozí deska pro laser podle ``DeviceName`` z projektu
* ``layout/rotation`` — natočení výrobků: ``any`` (výchozí, rozhodnutí vlastníka) | ``90`` | ``none``
* ``ui/units`` — ``mm`` (výchozí) | ``in`` — jen zobrazení, výpočty a soubor jsou vždy v mm
* ``ui/sections/<klíč>`` — sbalené/rozbalené sekce levého panelu
* ``save/protocol`` — protokol uložení: ``none`` (výchozí) | ``beside`` | ``appdata``
* ``updates/…`` — automatická kontrola aktualizací, předběžné verze, přeskočená verze, čas poslední kontroly
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QByteArray, QSettings

ORGANIZATION = "GridArranger"
APPLICATION = "GridArranger"
LANGUAGES = ("auto", "cs", "en")
THEMES = ("auto", "light", "dark")
PROTOCOL_MODES = ("none", "beside", "appdata")
UNIT_KEYS = ("mm", "in")
ROTATION_KEYS = ("none", "90", "any")  # protokol uložení: vůbec / vedle výstupu / ve složce aplikace

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


def _bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in ("true", "1", "false", "0"):
        return value.lower() in ("true", "1")
    if isinstance(value, int):
        return bool(value)
    return default


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

    # --- aktualizace (spec. v1.11 kap. 32) ---------------------------------------------------
    def update_auto(self) -> bool:
        """Automaticky kontrolovat při spuštění (nejvýš jednou denně). Výchozí: ano."""
        return _bool(self._s.value("updates/auto", True), True)

    def set_update_auto(self, value: bool) -> None:
        self._s.setValue("updates/auto", bool(value))
        self._s.sync()

    def update_prerelease(self) -> bool:
        """Nabízet i předběžné verze. Výchozí: ano, pokud sama běžící verze je předběžná."""
        from ..updates import current_version

        return _bool(self._s.value("updates/prerelease", current_version().is_prerelease), current_version().is_prerelease)

    def set_update_prerelease(self, value: bool) -> None:
        self._s.setValue("updates/prerelease", bool(value))
        self._s.sync()

    def skipped_version(self) -> str:
        return str(self._s.value("updates/skipped", "") or "")

    def set_skipped_version(self, tag: str) -> None:
        self._s.setValue("updates/skipped", tag)
        self._s.sync()

    def last_update_check(self) -> str:
        return str(self._s.value("updates/last_check", "") or "")

    def set_last_update_check(self, iso: str) -> None:
        self._s.setValue("updates/last_check", iso)
        self._s.sync()

    # --- protokol uložení (spec. v1.12 kap. 9.4) -----------------------------------------------
    def protocol_mode(self) -> str:
        """Výchozí: protokol se neukládá (rozhodnutí vlastníka 2026-10-17)."""
        v = str(self._s.value("save/protocol", "none"))
        return v if v in PROTOCOL_MODES else "none"

    def set_protocol_mode(self, value: str) -> None:
        if value not in PROTOCOL_MODES:
            raise ValueError(value)
        self._s.setValue("save/protocol", value)
        self._s.sync()

    # --- jednotky a sekce panelu ---------------------------------------------------------------
    def units(self) -> str:
        v = str(self._s.value("ui/units", "mm"))
        return v if v in UNIT_KEYS else "mm"

    def set_units(self, value: str) -> None:
        if value not in UNIT_KEYS:
            raise ValueError(value)
        self._s.setValue("ui/units", value)
        self._s.sync()

    def section_expanded(self, key: str) -> bool:
        return _bool(self._s.value(f"ui/sections/{key}", True), True)

    def set_section_expanded(self, key: str, expanded: bool) -> None:
        self._s.setValue(f"ui/sections/{key}", bool(expanded))
        self._s.sync()

    # --- uspořádání nástrojové lišty --------------------------------------------------------------
    def toolbar_order(self) -> list[str]:
        v = self._s.value("ui/toolbar_order", "")
        return [k for k in str(v).split(",") if k] if v else []

    def set_toolbar_order(self, keys: list[str]) -> None:
        self._s.setValue("ui/toolbar_order", ",".join(keys))
        self._s.sync()

    # --- velikost a poloha okna (včetně maximalizace) a rozdělení panelů ---------------------------
    def window_geometry(self) -> bytes | None:
        v = self._s.value("ui/window_geometry")
        return bytes(v) if v else None

    def window_splitter(self) -> bytes | None:
        v = self._s.value("ui/window_splitter")
        return bytes(v) if v else None

    def set_window_state(self, geometry: bytes, splitter: bytes) -> None:
        self._s.setValue("ui/window_geometry", QByteArray(geometry))
        self._s.setValue("ui/window_splitter", QByteArray(splitter))
        self._s.sync()

    # --- natočení výrobků (spec. v1.13) ----------------------------------------------------------
    def rotation_mode(self) -> str:
        v = str(self._s.value("layout/rotation", "any"))
        return v if v in ROTATION_KEYS else "any"

    def set_rotation_mode(self, value: str) -> None:
        if value not in ROTATION_KEYS:
            raise ValueError(value)
        self._s.setValue("layout/rotation", value)
        self._s.sync()
