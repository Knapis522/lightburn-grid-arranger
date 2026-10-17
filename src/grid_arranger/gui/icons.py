"""Vlastní jednobarevné ikony nástrojové lišty (SVG, barva podle vzhledu aplikace).

Ikony jsou nakreslené pro tuto aplikaci (žádná cizí grafika ani ikony LightBurnu). Barva se
dosazuje z palety, takže ve světlém i tmavém vzhledu zůstávají čitelné. Nová funkce na liště =
nový záznam v ``_PATHS`` (mřížka 24 × 24, tah 1,8 px, bez výplně).
"""

from __future__ import annotations

from PySide6.QtCore import QByteArray
from PySide6.QtGui import QIcon, QPixmap

_PATHS: dict[str, str] = {
    # složka s otevřeným víkem
    "open": '<path d="M3.5 18.5V6.5a1.5 1.5 0 0 1 1.5-1.5h3.6l2 2h6.9a1.5 1.5 0 0 1 1.5 1.5V10"/>'
            '<path d="M3.5 18.5l2.6-7.1a1.5 1.5 0 0 1 1.4-1h12.4a1 1 0 0 1 .95 1.32l-2.3 6.1a1.5 1.5 0 0 1-1.4.98H3.5z"/>',
    # disketa se znaménkem plus = uložit jako nový projekt
    "save_new": '<path d="M13 20H5.5A1.5 1.5 0 0 1 4 18.5v-13A1.5 1.5 0 0 1 5.5 4h10l4 4v4"/>'
                '<path d="M8 4v4.5h6.5V4"/><path d="M7.5 20v-5.5h5"/>'
                '<path d="M18 15v6M15 18h6"/>',
    # rohy výřezu kolem obdélníku = přizpůsobit náhled
    "fit": '<path d="M4 9V5.5A1.5 1.5 0 0 1 5.5 4H9M15 4h3.5A1.5 1.5 0 0 1 20 5.5V9M20 15v3.5a1.5 1.5 0 0 1-1.5 1.5H15M9 20H5.5A1.5 1.5 0 0 1 4 18.5V15"/>'
           '<rect x="8.5" y="9.5" width="7" height="5" rx="0.8"/>',
    # otazník v kruhu = příručka
    "help": '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.4a2.5 2.5 0 0 1 4.8 1c0 1.7-2.4 2.2-2.4 3.6"/>'
            '<path d="M12 17.2v.1"/>',
}

SIZES = (16, 20, 24, 32, 48, 64)


def svg(name: str, color: str, size: int = 24) -> bytes:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{_PATHS[name]}</svg>'
            ).encode("ascii")


def icon(name: str, color: str) -> QIcon:
    """Ikona v několika velikostech (ostrá i na displejích s vyšším rozlišením)."""
    ic = QIcon()
    for size in SIZES:
        pm = QPixmap()
        if pm.loadFromData(QByteArray(svg(name, color, size)), "SVG"):
            ic.addPixmap(pm)
    return ic


def names() -> tuple[str, ...]:
    return tuple(_PATHS)
