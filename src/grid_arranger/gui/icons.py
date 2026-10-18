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
    # dva překryté výrobky se znaménkem plus = vytvořit kopie
    "copies": '<path d="M15.5 5.5V4.8A1.3 1.3 0 0 0 14.2 3.5H4.8A1.3 1.3 0 0 0 3.5 4.8v9.4a1.3 1.3 0 0 0 1.3 1.3h.7"/>'
              '<rect x="8.5" y="8.5" width="12" height="12" rx="1.3"/><path d="M14.5 11.5v6M11.5 14.5h6"/>',
    # dokument se šipkou ven = otevřít uložený projekt v jiné aplikaci (LightBurn); žádné cizí logo
    "send": '<path d="M13 4.5H6.5A1.5 1.5 0 0 0 5 6v12a1.5 1.5 0 0 0 1.5 1.5h11A1.5 1.5 0 0 0 19 18v-6.5"/>'
            '<path d="M15 3.5h5.5V9M20.5 3.5L11 13"/>',
    # zahnutá šipka doleva / doprava = krok zpět / krok vpřed
    "undo": '<path d="M9 14L4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
    "redo": '<path d="M15 14l5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/>',
    # deska plná výrobků = vyplnit desku kopiemi
    "fill": '<rect x="3.5" y="4.5" width="17" height="15" rx="1.3"/>'
            '<rect x="6" y="7" width="5" height="4" rx="0.5"/><rect x="13" y="7" width="5" height="4" rx="0.5"/>'
            '<rect x="6" y="13" width="5" height="4" rx="0.5"/><rect x="13" y="13" width="5" height="4" rx="0.5"/>',
    # ozubené kolo = nastavení
    "settings": '<circle cx="12" cy="12" r="3"/>'
                '<path d="M10.3 3.5h3.4l.5 2.4 1.6.9 2.3-.8 1.7 2.9-1.8 1.6v1.9l1.8 1.6-1.7 2.9-2.3-.8-1.6.9-.5 2.4h-3.4'
                'l-.5-2.4-1.6-.9-2.3.8-1.7-2.9 1.8-1.6v-1.9L3.9 8.9l1.7-2.9 2.3.8 1.6-.9z"/>',
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
