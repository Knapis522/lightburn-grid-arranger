"""Uživatelské nastavení (spec. kap. 36.3, v1.10 kap. 12.3).

Ukládá se přes ``QSettings`` (Windows: registr uživatele), tedy mimo složku
aplikace — přežije přesun i výměnu ZIPu. Nic z toho se nezapisuje do `.lbrn2`.

* ``ui/language`` — ``auto`` | ``cs`` | ``en``
* ``boards/<laser>/…`` — výchozí deska pro laser podle ``DeviceName`` z projektu
* ``profiles/<název>/…`` — profily rozložení (spec. v1.24): sloupce, mezery, plnění, natočení, umístění
* ``lasers/<laser>/…`` — katalog laserů (spec. v1.23): název jako v LightBurnu a roh počátku;
  deska laseru je v ``boards/<laser>``. Lasery z otevřených projektů se přidávají samy.
* ``layout/rotation`` — natočení výrobků: ``any`` (výchozí, rozhodnutí vlastníka) | ``90`` | ``none``
* ``ui/units`` — ``mm`` (výchozí) | ``in`` — jen zobrazení, výpočty a soubor jsou vždy v mm
* ``ui/sections/<klíč>`` — sbalené/rozbalené sekce panelu nastavení rozložení
* ``ui/panel_side`` — panel nastavení rozložení ``left`` (výchozí) | ``right`` od náhledu
* ``save/protocol`` — protokol uložení: ``none`` (výchozí) | ``beside`` | ``appdata``
* ``updates/…`` — automatická kontrola aktualizací, předběžné verze, přeskočená verze, čas poslední kontroly
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from PySide6.QtCore import QByteArray, QSettings

ORGANIZATION = "GridArranger"
APPLICATION = "GridArranger"
LANGUAGES = ("auto", "cs", "en", "de", "sk", "pl", "fr", "es", "it")
THEMES = ("auto", "light", "dark")
PROTOCOL_MODES = ("none", "beside", "appdata")
UNSELECTED_POLICIES = ("omit", "keep")
BOARD_MODES = ("sequential", "even", "product", "none")  # když se nevejde (spec. v1.29)
BOARD_OUTPUTS = ("pages", "files")  # desky jako stránky jednoho projektu / samostatné soubory  # nezaškrtnuté objekty: vynechat z výstupu / ponechat na místě (spec. v1.27)
UNIT_KEYS = ("mm", "in")
PANEL_SIDES = ("left", "right")
ORIGINS = ("top_left", "top_right", "bottom_left", "bottom_right")
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


@dataclass(frozen=True, slots=True)
class LaserProfile:
    """Laser v katalogu: ``name`` = ``DeviceName`` v LightBurnu, ``origin`` = roh počátku (``ORIGINS``)."""

    name: str
    origin: str
    board: BoardPreset | None = None


def _bool(value: object, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in ("true", "1", "false", "0"):
        return value.lower() in ("true", "1")
    if isinstance(value, int):
        return bool(value)
    return default


def _safe(device: str) -> str:
    # QSettings klíče: lomítka a zpětná lomítka nahradit, aby nevznikly podskupiny
    return device.replace("/", "_").replace("\\", "_")


def _key(device: str) -> str:
    return "boards/" + _safe(device)


def _laser_key(device: str) -> str:
    return "lasers/" + _safe(device)


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

    def remove_board_for(self, device: str) -> None:
        self._s.remove(_key(device))
        self._s.sync()

    # --- profily rozložení (spec. v1.24) ---------------------------------------------------------
    def profiles(self) -> list[str]:
        self._s.beginGroup("profiles")
        keys = self._s.childGroups()
        self._s.endGroup()
        names = [str(self._s.value(f"profiles/{k}/name", "") or "") for k in keys]
        return sorted((n for n in names if n and self.profile(n) is not None), key=str.casefold)

    def profile(self, name: str) -> dict | None:
        raw = self._s.value(f"profiles/{_safe(name)}/data")
        try:
            data = json.loads(str(raw)) if raw else None
        except ValueError:
            return None  # poškozený záznam
        return data if isinstance(data, dict) else None

    def set_profile(self, name: str, data: dict) -> None:
        if not name.strip():
            raise ValueError(name)
        self._s.setValue(f"profiles/{_safe(name)}/name", name)
        self._s.setValue(f"profiles/{_safe(name)}/data", json.dumps(data, sort_keys=True))
        self._s.sync()

    def remove_profile(self, name: str) -> None:
        self._s.remove(f"profiles/{_safe(name)}")
        self._s.sync()

    # --- katalog laserů (spec. v1.23) ------------------------------------------------------------
    def lasers(self) -> list[LaserProfile]:
        out = []
        self._s.beginGroup("lasers")
        keys = self._s.childGroups()
        self._s.endGroup()
        for k in keys:
            name = str(self._s.value(f"lasers/{k}/name", "") or "")
            origin = str(self._s.value(f"lasers/{k}/origin", ""))
            if name and origin in ORIGINS:
                out.append(LaserProfile(name, origin, self.board_for(name)))
        return sorted(out, key=lambda p: p.name.casefold())

    def laser(self, name: str) -> LaserProfile | None:
        return next((p for p in self.lasers() if p.name == name), None)

    def remember_laser(self, name: str, origin: str) -> None:
        """Laser z otevřeného projektu: přidá ho do katalogu, případně opraví roh počátku podle projektu."""
        if not name or origin not in ORIGINS:
            return
        known = self.laser(name)
        if known is None or known.origin != origin:
            self._s.setValue(_laser_key(name) + "/name", name)
            self._s.setValue(_laser_key(name) + "/origin", origin)
            self._s.sync()

    def set_lasers(self, profiles: list[LaserProfile]) -> None:
        """Nahradí celý katalog (okno Nastavení → Lasery); desky odebraných laserů smaže."""
        keep = {p.name for p in profiles}
        for old in self.lasers():
            if old.name not in keep:
                self._s.remove(_laser_key(old.name))
                self._s.remove(_key(old.name))
        for p in profiles:
            if p.origin not in ORIGINS or not p.name:
                raise ValueError(p)
            self._s.setValue(_laser_key(p.name) + "/name", p.name)
            self._s.setValue(_laser_key(p.name) + "/origin", p.origin)
            if p.board is not None:
                self.set_board_for(p.name, p.board)
        self._s.sync()

    # --- aktualizace (spec. v1.11 kap. 32) ---------------------------------------------------
    def update_auto(self) -> bool:
        """Automaticky kontrolovat při každém spuštění. Výchozí: ano."""
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

    # --- více desek (spec. v1.29) ---------------------------------------------------------------
    def board_mode(self) -> str:
        v = str(self._s.value("boards/mode", "sequential"))
        return v if v in BOARD_MODES else "sequential"

    def set_board_mode(self, value: str) -> None:
        if value not in BOARD_MODES:
            raise ValueError(value)
        self._s.setValue("boards/mode", value)
        self._s.sync()

    def board_fill(self) -> bool:
        return str(self._s.value("boards/fill", "false")).lower() == "true"

    def set_board_fill(self, on: bool) -> None:
        self._s.setValue("boards/fill", "true" if on else "false")
        self._s.sync()

    def board_limit(self) -> int:
        """Upozornění nad tento počet desek; 0 = vypnuto."""
        try:
            return max(0, int(self._s.value("boards/limit", 10)))
        except (TypeError, ValueError):
            return 10

    def set_board_limit(self, n: int) -> None:
        self._s.setValue("boards/limit", max(0, int(n)))
        self._s.sync()

    def board_output(self) -> str:
        v = str(self._s.value("boards/output", "pages"))
        return v if v in BOARD_OUTPUTS else "pages"

    def set_board_output(self, value: str) -> None:
        if value not in BOARD_OUTPUTS:
            raise ValueError(value)
        self._s.setValue("boards/output", value)
        self._s.sync()

    # --- názvy výrobků (jen v aplikaci, podle obsahu souboru) ---------------------------------------
    def item_labels(self, sha256: str) -> dict[str, str]:
        import json

        try:
            data = json.loads(str(self._s.value(f"labels/{sha256}", "{}")))
        except ValueError:
            return {}
        return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}

    def set_item_labels(self, sha256: str, labels: dict[str, str]) -> None:
        import json

        key = f"labels/{sha256}"
        if labels:
            self._s.setValue(key, json.dumps(labels, ensure_ascii=False))
        else:
            self._s.remove(key)
        self._s.sync()

    def unselected_policy(self) -> str:
        """Co s objekty, které se nerozmisťují: ``omit`` (výchozí, rozhodnutí vlastníka 2026-10-18) nebo ``keep``."""
        v = str(self._s.value("save/unselected", "omit"))
        return v if v in UNSELECTED_POLICIES else "omit"

    def set_unselected_policy(self, value: str) -> None:
        if value not in UNSELECTED_POLICIES:
            raise ValueError(value)
        self._s.setValue("save/unselected", value)
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

    # --- strana panelu nastavení rozložení ----------------------------------------------------------
    def panel_side(self) -> str:
        v = str(self._s.value("ui/panel_side", "left"))
        return v if v in PANEL_SIDES else "left"

    def set_panel_side(self, value: str) -> None:
        if value not in PANEL_SIDES:
            raise ValueError(value)
        self._s.setValue("ui/panel_side", value)
        self._s.sync()

    # --- poslední složka s projekty ----------------------------------------------------------------
    def last_open_dir(self) -> str:
        """Složka naposledy otevřeného projektu (dialog Otevřít v ní začne); prázdné, pokud už neexistuje."""
        from pathlib import Path

        v = str(self._s.value("files/last_open_dir", "") or "")
        return v if v and Path(v).is_dir() else ""

    def set_last_open_dir(self, folder: str) -> None:
        self._s.setValue("files/last_open_dir", str(folder))
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
