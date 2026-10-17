"""Ovládací prvky levého panelu: sbalitelné sekce a pole délky s jednotkami mm / palce.

Všechny délky se v aplikaci počítají v milimetrech (stejně jako v souboru ``.lbrn2``). Palce jsou
jen zobrazení: :class:`LengthSpin` drží přesnou hodnotu v mm a při přepnutí jednotek ji jen
převede pro zobrazení, takže opakované přepínání hodnotu nemění (žádné zaokrouhlovací posuny).
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractSpinBox, QDoubleSpinBox, QFrame, QSizePolicy, QToolButton, QVBoxLayout, QWidget

MM_PER_INCH = 25.4


@dataclass(frozen=True, slots=True)
class Unit:
    key: str
    suffix: str
    factor: float  # mm v jedné jednotce
    decimals: int

    def to_display(self, mm: float) -> float:
        return mm / self.factor

    def to_mm(self, value: float) -> float:
        return value * self.factor


MM = Unit("mm", "mm", 1.0, 2)
INCH = Unit("in", "in", MM_PER_INCH, 3)  # 0,001 in = 0,0254 mm
UNITS = {u.key: u for u in (MM, INCH)}


class LengthSpin(QDoubleSpinBox):
    """Délka v mm zobrazená v aktuálních jednotkách. ``mm()`` / ``set_mm()`` pracují vždy v mm."""

    mmChanged = Signal(float)

    def __init__(self, minimum_mm: float, maximum_mm: float, value_mm: float, unit: Unit = MM) -> None:
        super().__init__()
        self._min_mm, self._max_mm = minimum_mm, maximum_mm
        self._mm = value_mm
        self._unit = unit
        self._internal = False
        self.setKeyboardTracking(False)  # přepočet až po dopsání hodnoty
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.valueChanged.connect(self._on_value_changed)
        self.set_unit(unit)

    def _on_value_changed(self, value: float) -> None:
        if self._internal:
            return
        self._mm = self._unit.to_mm(value)
        self.mmChanged.emit(self._mm)

    def _show(self) -> None:
        self._internal = True
        try:
            self.setDecimals(self._unit.decimals)
            self.setRange(self._unit.to_display(self._min_mm), self._unit.to_display(self._max_mm))
            self.setSuffix(" " + self._unit.suffix)
            self.setValue(self._unit.to_display(self._mm))
        finally:
            self._internal = False

    def set_unit(self, unit: Unit) -> None:
        self._unit = unit
        self._show()
        # pole pro čísla do 0000,00 (resp. 000,000 in) + jednotka — ne zbytečně široké
        fm = self.fontMetrics()
        self.setFixedWidth(fm.horizontalAdvance("0000,000 " + unit.suffix) + 16)

    def unit(self) -> Unit:
        return self._unit

    def mm(self) -> float:
        return self._mm

    def set_mm(self, value_mm: float, emit: bool = True) -> None:
        self._mm = min(max(value_mm, self._min_mm), self._max_mm)
        self._show()
        if emit:
            self.mmChanged.emit(self._mm)


class Section(QWidget):
    """Sekce levého panelu s výraznou, ale klidnou hlavičkou; kliknutím na hlavičku se sbalí/rozbalí."""

    expandedChanged = Signal(bool)

    def __init__(self, key: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.key = key
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.header = QToolButton()
        self.header.setObjectName("sectionHeader")
        self.header.setCheckable(True)
        self.header.setChecked(True)
        self.header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.header.setArrowType(Qt.ArrowType.DownArrow)
        self.header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.toggled.connect(self.setExpanded)
        self.body = QFrame()
        self.body.setObjectName("sectionBody")
        lay.addWidget(self.header)
        lay.addWidget(self.body)

    def setTitle(self, text: str) -> None:  # noqa: N802 — stejné API jako QGroupBox
        self.header.setText(text)

    def title(self) -> str:
        return self.header.text()

    def isExpanded(self) -> bool:  # noqa: N802
        return self.body.isVisibleTo(self)

    def setExpanded(self, expanded: bool) -> None:  # noqa: N802
        self.header.blockSignals(True)
        self.header.setChecked(expanded)
        self.header.blockSignals(False)
        self.header.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.body.setVisible(expanded)
        self.expandedChanged.emit(expanded)


def section_stylesheet(window: str, text: str, mid: str, accent: str, header_bg: str, body_bg: str) -> str:
    """Hlavička: tučný text, jemné pozadí a úzký barevný proužek vlevo; tělo: jemný rámeček."""
    return f"""
QToolButton#sectionHeader {{
    font-weight: 600;
    color: {text};
    background: {header_bg};
    border: none;
    border-left: 3px solid {accent};
    border-radius: 3px;
    padding: 5px 6px;
    margin-top: 8px;
    text-align: left;
}}
QToolButton#sectionHeader:hover {{ background: {mid}; }}
QFrame#sectionBody {{
    background: {body_bg};
    border: 1px solid {mid};
    border-top: none;
    border-bottom-left-radius: 4px;
    border-bottom-right-radius: 4px;
}}
"""
