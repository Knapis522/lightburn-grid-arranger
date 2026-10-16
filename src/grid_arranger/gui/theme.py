"""Světlý / tmavý vzhled aplikace (volba Nastavení → Vzhled).

* **Světlý** — celá aplikace světlá (i když má Windows tmavý režim).
* **Tmavý** — tmavé ovládací prvky, náhled desky zůstává světlý (rozhodnutí vlastníka 2026-10-16).
* **Automaticky** — podle nastavení Windows (sleduje i změnu za běhu).

Používá styl Fusion s explicitní paletou: výchozí paleta stylu se v novějším Qt řídí
tmavým režimem systému, proto se nikdy nepoužívá.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QGuiApplication, QPalette

THEMES = ("auto", "light", "dark")

_LIGHT = {
    "Window": "#efefef", "WindowText": "#000000", "Base": "#ffffff", "AlternateBase": "#f5f5f5",
    "ToolTipBase": "#ffffdc", "ToolTipText": "#000000", "Text": "#000000", "Button": "#efefef",
    "ButtonText": "#000000", "BrightText": "#d62728", "Link": "#0b5cad", "Highlight": "#308cc6",
    "HighlightedText": "#ffffff", "PlaceholderText": "#808080", "Light": "#ffffff", "Midlight": "#e3e3e3",
    "Mid": "#b8b8b8", "Dark": "#9f9f9f", "Shadow": "#767676",
}
_DARK = {
    "Window": "#2b2d30", "WindowText": "#e6e6e6", "Base": "#1e1f22", "AlternateBase": "#3c3f41",
    "ToolTipBase": "#3c3f41", "ToolTipText": "#e6e6e6", "Text": "#e6e6e6", "Button": "#3c3f41",
    "ButtonText": "#e6e6e6", "BrightText": "#ff6b6b", "Link": "#6ea8ff", "Highlight": "#3d6fb6",
    "HighlightedText": "#ffffff", "PlaceholderText": "#8a8a8a", "Light": "#4a4d50", "Midlight": "#404346",
    "Mid": "#33363a", "Dark": "#202225", "Shadow": "#141518",
}


def _palette(colors: dict[str, str], disabled: str) -> QPalette:
    p = QPalette()
    for name, value in colors.items():
        p.setColor(getattr(QPalette.ColorRole, name), QColor(value))
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText, QPalette.ColorRole.WindowText):
        p.setColor(QPalette.ColorGroup.Disabled, role, QColor(disabled))
    return p


def light_palette() -> QPalette:
    return _palette(_LIGHT, "#a0a0a0")


def dark_palette() -> QPalette:
    return _palette(_DARK, "#777777")


def _set_scheme(scheme) -> None:
    hints = QGuiApplication.styleHints()
    if hasattr(hints, "setColorScheme"):  # Qt ≥ 6.8: i titulek okna ve Windows
        hints.setColorScheme(scheme)


def system_is_dark() -> bool:
    return QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark


def apply_theme(app, mode: str) -> bool:
    """Nastaví vzhled; vrátí True, pokud je výsledný vzhled tmavý."""
    if mode not in THEMES:
        mode = "auto"
    if mode == "auto":
        _set_scheme(Qt.ColorScheme.Unknown)  # zpět na řízení systémem
        dark = system_is_dark()
    else:
        dark = mode == "dark"
        _set_scheme(Qt.ColorScheme.Dark if dark else Qt.ColorScheme.Light)
    app.setStyle("Fusion")
    app.setPalette(dark_palette() if dark else light_palette())
    return dark
