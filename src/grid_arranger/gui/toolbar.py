"""Nástrojová lišta, jejíž ikony (i oddělovače) lze přeuspořádat tažením myší.

Ikonu chytíte (stisk a podržení) a přetáhnete na nové místo; zelená svislá čára ukazuje, kam
se vloží. Obyčejné kliknutí funguje dál. Pořadí se ukládá jako seznam klíčů akcí
(``QAction.objectName()``), takže se po spuštění obnoví (``order()`` / ``set_order()``).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QMimeData, QObject, QPoint, Qt, Signal
from PySide6.QtGui import QAction, QColor, QDrag, QPainter, QPen
from PySide6.QtWidgets import QApplication, QToolBar, QToolButton, QWidget

MIME = "application/x-gridarranger-toolbar-action"


class ReorderableToolBar(QToolBar):
    orderChanged = Signal(list)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._press: tuple[QWidget, QPoint] | None = None
        self._drop_x: int | None = None

    # --- pořadí ----------------------------------------------------------------------------------
    def order(self) -> list[str]:
        return [a.objectName() for a in self.actions() if a.objectName()]

    def set_order(self, keys: list[str]) -> None:
        """Seřadí akce podle ``keys``; neznámé klíče přeskočí, akce bez klíče v seznamu dá na konec."""
        by_key = {a.objectName(): a for a in self.actions() if a.objectName()}
        wanted = [by_key[k] for k in keys if k in by_key]
        rest = [a for a in self.actions() if a not in wanted]
        for a in self.actions():
            self.removeAction(a)
        for a in wanted + rest:
            self.addAction(a)

    def move_action(self, key: str, before: str | None) -> bool:
        """Přesune akci ``key`` před akci ``before`` (``None`` = na konec)."""
        keys = self.order()
        if key not in keys or key == before:
            return False
        keys.remove(key)
        keys.insert(keys.index(before) if before in keys else len(keys), key)
        if keys == self.order():
            return False
        self.set_order(keys)
        self.orderChanged.emit(self.order())
        return True

    # --- tažení ----------------------------------------------------------------------------------
    def actionEvent(self, event) -> None:  # noqa: N802 (Qt API)
        super().actionEvent(event)
        if event.type() == QEvent.Type.ActionAdded:
            w = self.widgetForAction(event.action())
            if w is not None:
                w.installEventFilter(self)
                w.setProperty("toolbar_key", event.action().objectName())

    def eventFilter(self, obj: QObject, ev: QEvent) -> bool:  # noqa: N802
        t = ev.type()
        if t == QEvent.Type.MouseButtonPress and ev.button() == Qt.MouseButton.LeftButton:
            self._press = (obj, ev.position().toPoint())
        elif t == QEvent.Type.MouseMove and self._press is not None and self._press[0] is obj \
                and ev.buttons() & Qt.MouseButton.LeftButton:
            if (ev.position().toPoint() - self._press[1]).manhattanLength() >= QApplication.startDragDistance():
                self._start_drag(obj)
                return True
        elif t == QEvent.Type.MouseButtonRelease:
            self._press = None
        return super().eventFilter(obj, ev)

    def _start_drag(self, w: QWidget) -> None:
        key = w.property("toolbar_key")
        self._press = None
        if isinstance(w, QToolButton):
            w.setDown(False)
        if not key:
            return
        mime = QMimeData()
        mime.setData(MIME, str(key).encode("utf-8"))
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.setPixmap(w.grab())
        drag.setHotSpot(QPoint(w.width() // 2, w.height() // 2))
        drag.exec(Qt.DropAction.MoveAction)
        self._drop_x = None
        self.update()

    def _target(self, x: int) -> tuple[str | None, int]:
        """Klíč akce, před kterou se vloží, a x‑souřadnice čáry pro bod ``x``."""
        last_right = 0
        for a in self.actions():
            w = self.widgetForAction(a)
            if w is None or not w.isVisible():
                continue
            g = w.geometry()
            if x < g.center().x():
                return a.objectName() or None, g.left() - 1
            last_right = g.right() + 1
        return None, last_right

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasFormat(MIME):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasFormat(MIME):
            _, self._drop_x = self._target(event.position().toPoint().x())
            self.update()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:  # noqa: N802
        self._drop_x = None
        self.update()

    def dropEvent(self, event) -> None:  # noqa: N802
        if not event.mimeData().hasFormat(MIME):
            return
        key = bytes(event.mimeData().data(MIME)).decode("utf-8")
        before, _ = self._target(event.position().toPoint().x())
        self._drop_x = None
        self.move_action(key, before)
        event.acceptProposedAction()
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        if self._drop_x is not None:
            p = QPainter(self)
            p.setPen(QPen(QColor("#2a7d2a"), 3))
            p.drawLine(self._drop_x, 3, self._drop_x, self.height() - 3)
            p.end()


def separator(parent: QObject, key: str) -> QAction:
    """Oddělovač s klíčem (aby šel uložit i přesunout)."""
    a = QAction(parent)
    a.setSeparator(True)
    a.setObjectName(key)
    return a
