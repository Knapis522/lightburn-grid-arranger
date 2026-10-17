"""Náhled rozložení v souřadnicích jádra (mm, osa Y dolů) — spec. kap. 12.3.

Kreslí desku, využitelnou plochu, počátek laseru, nepřesouvané objekty (šedě)
a přesouvané výrobky v cílové poloze se skutečnými křivkami a textem
v barvách vrstev (přibližná paleta LightBurnu) a s pořadovým číslem.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsScene, QGraphicsSimpleTextItem, QGraphicsView

from ..adapters.lightburn.render import Stroke
from ..domain.models import Rect

# Výchozí barvy vrstev LightBurnu C00–C15 (přibližně); další vrstvy cyklicky.
LAYER_COLORS = [
    "#000000", "#0000FF", "#FF0000", "#00C000", "#C0C000", "#FF8000", "#00C0C0", "#FF00FF",
    "#B4B4B4", "#0000A0", "#A00000", "#00A000", "#A0A000", "#C08000", "#00A0FF", "#A000A0",
]


def layer_color(cut: str) -> QColor:
    try:
        return QColor(LAYER_COLORS[int(cut) % len(LAYER_COLORS)])
    except ValueError:
        return QColor("#000000")


LIGHT = {"bg": "#f4f4f2", "board": "#ffffff", "board_pen": "#555555", "usable": "#999999", "obst_pen": "#aaaaaa",
         "obst_fill": (150, 150, 150, 40), "obst_art": "#9a9a9a", "obst_text": "#777777", "item_fill": (70, 120, 200, 18),
         "item_pen": (70, 120, 200, 120), "item_text": "#1f3d7a", "origin": "#111111"}



def strokes_to_paths(strokes: list[Stroke]) -> dict[str, QPainterPath]:
    paths: dict[str, QPainterPath] = {}
    for s in strokes:
        p = paths.setdefault(s.cut, QPainterPath())
        for op in s.ops:
            k = op[0]
            if k == "M":
                p.moveTo(QPointF(*op[1]))
            elif k == "L":
                p.lineTo(QPointF(*op[1]))
            elif k == "C":
                p.cubicTo(QPointF(*op[1]), QPointF(*op[2]), QPointF(*op[3]))
            elif k == "Z":
                p.closeSubpath()
    return paths


class PreviewView(QGraphicsView):
    """Tažením výrobku na místo jiného výrobku vznikne signál ``itemDropped(přetažený, cílový)``.

    Tažení po prázdném místě posouvá pohled, kolečko myši přibližuje.
    """

    itemDropped = Signal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._content = QRectF()
        self._fit_scale = 1.0
        self._c = LIGHT  # náhled je vždy světlý (i v tmavém vzhledu aplikace)
        self.setBackgroundBrush(QColor(self._c["bg"]))
        self.scene().setBackgroundBrush(QColor(self._c["bg"]))
        self.setMinimumSize(360, 300)
        self._has_content = False
        self._paths: dict[str, dict[str, QPainterPath]] = {}
        self._user_zoomed = False
        self._graphics: dict[str, list[QGraphicsItem]] = {}
        self._rects: dict[str, QRectF] = {}
        self._drag: dict | None = None
        self._drop_marker: QGraphicsRectItem | None = None

    def clear_cache(self) -> None:
        self._paths.clear()

    def clear(self) -> None:
        self.scene().clear()
        self._has_content = False

    def _label(self, text: str, x: float, y: float, bold: bool = False, color: str = "#222", bg: bool = False) -> QGraphicsSimpleTextItem:
        t = QGraphicsSimpleTextItem(text)
        f = QFont()
        f.setPointSize(9)
        f.setBold(bold)
        t.setFont(f)
        t.setBrush(QColor(color))
        t.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        t.setPos(x, y)
        t.setZValue(10)
        self.scene().addItem(t)
        return t

    @staticmethod
    def _r(r: Rect) -> QRectF:
        return QRectF(r.left, r.top, r.width, r.height)

    def _add_art(self, item_id: str, strokes: list[Stroke], dx: float, dy: float, gray: bool,
                 angle: float = 0.0, pivot: tuple[float, float] = (0.0, 0.0)) -> list[QGraphicsItem]:
        if item_id not in self._paths:
            self._paths[item_id] = strokes_to_paths(strokes)
        out: list[QGraphicsItem] = []
        for cut, path in self._paths[item_id].items():
            gi = QGraphicsPathItem(path)
            c = QColor(self._c["obst_art"]) if gray else layer_color(cut)
            gi.setPen(QPen(c, 0))  # kosmetické pero: 1 px při každém přiblížení
            if angle:
                gi.setTransformOriginPoint(QPointF(*pivot))
                gi.setRotation(angle)  # kladně po směru hodin = stejně jako jádro
            gi.setPos(dx, dy)
            gi.setZValue(2)
            self.scene().addItem(gi)
            out.append(gi)
        return out

    def draw(
        self,
        board: Rect | None,
        usable: Rect | None,
        origin: tuple[float, float] | None,
        obstacles: list[tuple[str, Rect, list[Stroke]]],
        items: list[tuple],
        problem_ids: set[str],
        show_art: bool = True,
        refit: bool = False,
    ) -> None:
        """``items``: (id, pořadí, cílový obdélník, křivky v původní poloze, dx, dy[, úhel, (cx, cy)])."""
        s = self.scene()
        s.clear()
        self._graphics.clear()
        self._rects.clear()
        self._drag = None
        self._drop_marker = None
        if board is not None:
            s.addRect(self._r(board), QPen(QColor(self._c["board_pen"]), 0), QBrush(QColor(self._c["board"])))
        if usable is not None:
            s.addRect(self._r(usable), QPen(QColor(self._c["usable"]), 0, Qt.PenStyle.DashLine))
        for oid, r, strokes in obstacles:
            bad = oid in problem_ids
            s.addRect(self._r(r), QPen(QColor("#d62728") if bad else QColor(self._c["obst_pen"]), 0), QBrush(QColor(*self._c["obst_fill"])))
            if show_art and strokes:
                self._add_art(oid, strokes, 0.0, 0.0, gray=True)
            self._label(oid, r.left, r.top, color=self._c["obst_text"])
        for iid, num, r, strokes, dx, dy, *rot in items:
            angle, pivot = (rot[0], rot[1]) if rot else (0.0, (0.0, 0.0))
            bad = iid in problem_ids
            fill = QColor(214, 39, 40, 70) if bad else QColor(*self._c["item_fill"])
            rect_item = s.addRect(self._r(r), QPen(QColor("#d62728") if bad else QColor(*self._c["item_pen"]), 0), QBrush(fill))
            rect_item.setZValue(1)
            group: list[QGraphicsItem] = [rect_item]
            if show_art and strokes:
                group += self._add_art(iid, strokes, dx, dy, gray=False, angle=angle, pivot=pivot)
            group.append(self._label(f"{num}. {iid}" if num else iid, r.left + 1, r.top + 1, bold=True, color="#d62728" if bad else self._c["item_text"]))
            self._graphics[iid] = group
            self._rects[iid] = self._r(r)
        if origin is not None:
            ox, oy = origin
            d = 6.0
            oc = QColor(self._c["origin"])
            dot = s.addEllipse(QRectF(ox - d / 2, oy - d / 2, d, d), QPen(oc, 0), QBrush(oc))
            dot.setZValue(11)
            self._label("0,0", ox + 3, oy + 3, color=self._c["origin"])
        # Obsah = deska, výrobky, překážky a počátek (bez popisků, které mají pevnou velikost v pixelech).
        content = QRectF()
        for r in [board, usable, *[o[1] for o in obstacles], *[i[2] for i in items]]:
            if r is not None:
                content = content.united(self._r(r))
        for r in self._rects.values():
            content = content.united(r)
        if origin is not None:
            content = content.united(QRectF(origin[0] - 1, origin[1] - 1, 2, 2))
        self._content = content
        if not content.isEmpty():  # pevná oblast posouvání: obsah + polovina rozměru na každou stranu
            m = max(content.width(), content.height()) * 0.5
            s.setSceneRect(content.adjusted(-m, -m, m, m))
        first = not self._has_content
        self._has_content = True
        if refit or first:
            self.fit()

    def fit(self) -> None:
        self._user_zoomed = False
        r = self._content if not self._content.isEmpty() else self.scene().itemsBoundingRect()
        if not r.isEmpty():
            m = max(r.width(), r.height()) * 0.04 + 1
            self.fitInView(r.adjusted(-m, -m, m, m), Qt.AspectRatioMode.KeepAspectRatio)
            self._fit_scale = self.transform().m11()

    MIN_ZOOM = 0.5  # vůči „Přizpůsobit“
    MAX_ZOOM = 60.0

    def wheelEvent(self, event) -> None:  # noqa: N802 (Qt API)
        delta = event.angleDelta().y() or event.angleDelta().x()
        if not delta:
            return
        factor = 1.0015 ** delta  # jeden zub kolečka (120) ≈ 20 %; touchpad plynule
        cur = self.transform().m11()
        lo, hi = self._fit_scale * self.MIN_ZOOM, self._fit_scale * self.MAX_ZOOM
        new = min(max(cur * factor, lo), hi)
        if abs(new - cur) < 1e-9:
            return
        self._user_zoomed = True
        f = new / cur
        self.scale(f, f)
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:  # noqa: N802
        """Dvojklik do prázdného místa = Přizpůsobit."""
        if self.item_at(self.mapToScene(event.position().toPoint())) is None:
            self.fit()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._has_content and not self._user_zoomed:
            self.fit()

    # --- přetahování výrobků -------------------------------------------------------------------
    def item_at(self, scene_pos: QPointF, exclude: str | None = None) -> str | None:
        for iid, r in self._rects.items():
            if iid != exclude and r.contains(scene_pos):
                return iid
        return None

    def start_drag(self, scene_pos: QPointF) -> bool:
        iid = self.item_at(scene_pos)
        if iid is None:
            return False
        self._drag = {"id": iid, "start": scene_pos, "last": scene_pos}
        for g in self._graphics[iid]:
            g.setZValue(g.zValue() + 20)
            g.setOpacity(0.75)
        self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
        return True

    def drag_to(self, scene_pos: QPointF) -> None:
        d = self._drag
        if d is None:
            return
        delta = scene_pos - d["last"]
        for g in self._graphics[d["id"]]:
            g.moveBy(delta.x(), delta.y())
        d["last"] = scene_pos
        target = self.item_at(scene_pos, exclude=d["id"])
        if self._drop_marker is None:
            pen = QPen(QColor("#2a7d2a"), 3)
            pen.setCosmetic(True)  # 3 px na obrazovce, ne 3 mm
            self._drop_marker = self.scene().addRect(QRectF(), pen, QBrush(QColor(42, 125, 42, 40)))
            self._drop_marker.setZValue(30)
        self._drop_marker.setVisible(target is not None)
        if target is not None:
            self._drop_marker.setRect(self._rects[target])

    def finish_drag(self, scene_pos: QPointF) -> None:
        d, self._drag = self._drag, None
        self.viewport().unsetCursor()
        if d is None:
            return
        target = self.item_at(scene_pos, exclude=d["id"])
        if self._drop_marker is not None:
            self._drop_marker.setVisible(False)
        if target is None:  # vrátit na místo
            back = d["start"] - d["last"]
            for g in self._graphics[d["id"]]:
                g.moveBy(back.x(), back.y())
                g.setZValue(g.zValue() - 20)
                g.setOpacity(1.0)
            return
        self.itemDropped.emit(d["id"], target)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self.start_drag(self.mapToScene(event.position().toPoint())):
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag is not None:
            self.drag_to(self.mapToScene(event.position().toPoint()))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        if self._drag is not None and event.button() == Qt.MouseButton.LeftButton:
            self.finish_drag(self.mapToScene(event.position().toPoint()))
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            event.accept()
            return
        super().mouseReleaseEvent(event)
