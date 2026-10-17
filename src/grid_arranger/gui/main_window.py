"""Hlavní okno (MVP-06; spec. kap. 12.2, 12.3). Bez geometrické logiky — vše počítá `application`."""

from __future__ import annotations

from pathlib import Path

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QEvent, QSize, QStandardPaths, Qt, QUrl, qVersion
from PySide6.QtGui import QAction, QActionGroup, QDesktopServices, QKeySequence, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from ..adapters.lightburn.read import LoadedProject, load_project
from ..adapters.lightburn.render import ProjectRenderer
from ..adapters.lightburn.write import next_output_path
from ..application.arrange_job import ArrangeParams, MaterialInput, Plan, check_output_path, execute, make_plan, material_to_core
from ..core.collision import Severity, usable_area
from ..core.order import default_order, deselect, move_down, move_up, select, swap
from ..domain.errors import GridError
from ..version import display_version
from . import icons
from .i18n import NATIVE_NAMES, LocaleManager
from .messages import issue_text, message
from .preview import PreviewView
from .settings import PROTOCOL_MODES, BoardPreset, UserSettings
from .theme import THEMES, apply_theme
from .updates_ui import UpdateController

ANCHOR_KEYS = ("origin", "center", "manual", "selection")
FILL_KEYS = ("origin", "reading")


def _dspin(minimum: float, maximum: float, value: float, decimals: int = 2) -> QDoubleSpinBox:
    s = QDoubleSpinBox()
    s.setRange(minimum, maximum)
    s.setDecimals(decimals)
    s.setValue(value)
    s.setSuffix(" mm")
    s.setKeyboardTracking(False)  # přepočet až po dopsání hodnoty
    s.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
    return s


class MainWindow(QMainWindow):
    def __init__(self, settings: UserSettings, locale: LocaleManager) -> None:
        super().__init__()
        self.settings = settings
        self.locale_mgr = locale
        self.project: LoadedProject | None = None
        self.order: tuple[str, ...] = ()
        self.plan: Plan | None = None
        self.plan_error: GridError | None = None
        self._rebuilding = False
        self.updates = UpdateController(self, settings)
        self._build_ui()
        self.retranslate()
        self._apply_number_locale()
        self.spin_start_x.setEnabled(False)
        self.spin_start_y.setEnabled(False)
        self._apply_theme(self.settings.theme())
        QApplication.styleHints().colorSchemeChanged.connect(self._on_system_scheme_changed)
        self.recompute()

    # ====================================================================== stavba UI
    def _build_ui(self) -> None:
        self.resize(1280, 820)
        # --- menu
        self.act_open = QAction(self)
        self.act_open.setShortcut(QKeySequence.StandardKey.Open)
        self.act_open.triggered.connect(lambda: self.open_project())
        self.act_save = QAction(self)
        self.act_save.setShortcut(QKeySequence.StandardKey.Save)
        self.act_save.triggered.connect(lambda: self.save_new_project())
        self.act_quit = QAction(self)
        self.act_quit.triggered.connect(self.close)
        self.act_help = QAction(self)
        self.act_help.setShortcut(QKeySequence(Qt.Key.Key_F1))
        self.act_help.triggered.connect(lambda: self.show_help())
        self.act_about = QAction(self)
        self.act_about.triggered.connect(self.show_about)
        self.lang_group = QActionGroup(self)
        self.lang_actions: dict[str, QAction] = {}
        for key in ("auto", "cs", "en"):
            a = QAction(self, checkable=True)
            a.setData(key)
            a.triggered.connect(lambda _=False, k=key: self.set_language(k))
            self.lang_group.addAction(a)
            self.lang_actions[key] = a
        self.lang_actions[self.settings.language()].setChecked(True)
        self.theme_group = QActionGroup(self)
        self.theme_actions: dict[str, QAction] = {}
        for key in THEMES:
            a = QAction(self, checkable=True)
            a.triggered.connect(lambda _=False, k=key: self.set_theme(k))
            self.theme_group.addAction(a)
            self.theme_actions[key] = a
        self.theme_actions[self.settings.theme()].setChecked(True)
        self.act_update_auto = QAction(self, checkable=True)
        self.act_update_auto.setChecked(self.settings.update_auto())
        self.act_update_auto.toggled.connect(self.settings.set_update_auto)
        self.act_update_pre = QAction(self, checkable=True)
        self.act_update_pre.setChecked(self.settings.update_prerelease())
        self.act_update_pre.toggled.connect(self.settings.set_update_prerelease)
        self.protocol_group = QActionGroup(self)
        self.protocol_actions: dict[str, QAction] = {}
        for key in PROTOCOL_MODES:
            a = QAction(self, checkable=True)
            a.triggered.connect(lambda _=False, k=key: self.settings.set_protocol_mode(k))
            self.protocol_group.addAction(a)
            self.protocol_actions[key] = a
        self.protocol_actions[self.settings.protocol_mode()].setChecked(True)
        self.act_open_protocols = QAction(self)
        self.act_open_protocols.triggered.connect(self.open_protocol_folder)
        self.act_check_updates = QAction(self)
        self.act_check_updates.triggered.connect(lambda: self.updates.check(manual=True))

        mb = self.menuBar()
        self.menu_file = mb.addMenu("")
        self.menu_file.addActions([self.act_open, self.act_save])
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.act_quit)
        self.menu_settings = mb.addMenu("")
        self.menu_lang = self.menu_settings.addMenu("")
        self.menu_lang.addActions(list(self.lang_actions.values()))
        self.menu_theme = self.menu_settings.addMenu("")
        self.menu_theme.addActions(list(self.theme_actions.values()))
        self.menu_protocol = self.menu_settings.addMenu("")
        self.menu_protocol.addActions(list(self.protocol_actions.values()))
        self.menu_protocol.addSeparator()
        self.menu_protocol.addAction(self.act_open_protocols)
        self.menu_updates = self.menu_settings.addMenu("")
        self.menu_updates.addActions([self.act_update_auto, self.act_update_pre])
        self.menu_help = mb.addMenu("")
        self.menu_help.addActions([self.act_help, self.act_check_updates, self.act_about])

        # --- nástrojová lišta (ikony; další funkce: nová akce + ikona v gui/icons.py)
        self.toolbar = QToolBar(self)
        self.toolbar.setObjectName("mainToolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.toolbar.addActions([self.act_open, self.act_save])
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.act_help)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self._toolbar_icons = {self.act_open: "open", self.act_save: "save_new", self.act_help: "help"}

        # --- levý panel
        left = QWidget()
        lv = QVBoxLayout(left)

        self.box_project = QGroupBox()
        pv = QVBoxLayout(self.box_project)
        # otevření a uložení je na nástrojové liště (a v menu Soubor); zde jen údaje o projektu
        self.lbl_file = QLabel()
        self.lbl_file.setWordWrap(True)
        pv.addWidget(self.lbl_file)
        self.lbl_device = QLabel()
        self.lbl_device.setWordWrap(True)
        pv.addWidget(self.lbl_device)
        lv.addWidget(self.box_project)

        self.box_items = QGroupBox()
        iv = QVBoxLayout(self.box_items)
        self.list_items = QListWidget()
        self.list_items.setMinimumHeight(180)
        self.list_items.itemChanged.connect(self._on_item_changed)
        iv.addWidget(self.list_items)
        g = QGridLayout()
        self.btn_up, self.btn_down, self.btn_reset = QPushButton(), QPushButton(), QPushButton()
        self.btn_all, self.btn_none = QPushButton(), QPushButton()
        self.btn_up.clicked.connect(lambda: self._move(-1))
        self.btn_down.clicked.connect(lambda: self._move(1))
        self.btn_reset.clicked.connect(self._reset_order)
        self.btn_all.clicked.connect(self._select_all)
        self.btn_none.clicked.connect(self._select_none)
        g.addWidget(self.btn_up, 0, 0)
        g.addWidget(self.btn_down, 0, 1)
        g.addWidget(self.btn_reset, 0, 2)
        g.addWidget(self.btn_all, 1, 0)
        g.addWidget(self.btn_none, 1, 1)
        iv.addLayout(g)
        self.lbl_count = QLabel()
        iv.addWidget(self.lbl_count)
        lv.addWidget(self.box_items)

        self.box_grid = QGroupBox()
        self.form_grid = QFormLayout(self.box_grid)
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 1000)
        self.spin_cols.setValue(3)
        self.spin_cols.setKeyboardTracking(False)
        self.spin_gap_x = _dspin(0, 1000, 3.0)
        self.spin_gap_y = _dspin(0, 1000, 3.0)
        self.combo_fill = QComboBox()
        self.lbls_grid = self._rows(self.form_grid, (self.spin_cols, self.spin_gap_x, self.spin_gap_y, self.combo_fill))
        lv.addWidget(self.box_grid)

        self.box_place = QGroupBox()
        self.form_place = QFormLayout(self.box_place)
        self.combo_anchor = QComboBox()
        self.spin_start_x = _dspin(-100000, 100000, 5.0)
        self.spin_start_y = _dspin(-100000, 100000, 5.0)
        self.lbls_place = self._rows(self.form_place, (self.combo_anchor, self.spin_start_x, self.spin_start_y))
        lv.addWidget(self.box_place)

        self.box_board = QGroupBox()
        self.form_board = QFormLayout(self.box_board)
        self.spin_bw = _dspin(0, 100000, 700.0)
        self.spin_bh = _dspin(0, 100000, 500.0)
        self.spin_bx = _dspin(-100000, 100000, 0.0)
        self.spin_by = _dspin(-100000, 100000, 0.0)
        self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb = (_dspin(0, 10000, 5.0) for _ in range(4))
        self.lbls_board = self._rows(self.form_board, (self.spin_bw, self.spin_bh, self.spin_bx, self.spin_by,
                                                       self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb))
        self.btn_board_default = QPushButton()
        self.btn_board_default.clicked.connect(self.save_board_default)
        self.form_board.addRow(self.btn_board_default)
        lv.addWidget(self.box_board)
        lv.addStretch(1)

        for w in (self.spin_cols, self.spin_gap_x, self.spin_gap_y, self.spin_start_x, self.spin_start_y,
                  self.spin_bw, self.spin_bh, self.spin_bx, self.spin_by, self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb):
            w.valueChanged.connect(self.recompute)
        self.combo_fill.currentIndexChanged.connect(self.recompute)
        self.combo_anchor.currentIndexChanged.connect(self._on_anchor_changed)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left)
        scroll.setMinimumWidth(380)

        # --- pravý panel
        right = QWidget()
        rv = QVBoxLayout(right)
        self.preview = PreviewView()
        self.preview.itemDropped.connect(self._on_item_dropped)
        rv.addWidget(self.preview, 1)
        bar = QHBoxLayout()
        self.lbl_summary = QLabel()
        self.lbl_summary.setWordWrap(True)
        self.btn_fit = QPushButton()
        self.btn_fit.clicked.connect(self.preview.fit)
        self.chk_art = QCheckBox()
        self.chk_art.setChecked(True)
        self.chk_art.toggled.connect(lambda _: self.recompute())
        bar.addWidget(self.lbl_summary, 1)
        bar.addWidget(self.chk_art)
        bar.addWidget(self.btn_fit)
        rv.addLayout(bar)
        self.list_issues = QListWidget()
        self.list_issues.setMaximumHeight(150)
        rv.addWidget(self.list_issues)

        split = QSplitter()
        split.addWidget(scroll)
        split.addWidget(right)
        split.setStretchFactor(1, 1)
        self.setCentralWidget(split)

    @staticmethod
    def _rows(form: QFormLayout, widgets) -> list[QLabel]:
        labels = []
        for w in widgets:
            lbl = QLabel()
            lbl.setBuddy(w)
            form.addRow(lbl, w)
            labels.append(lbl)
        return labels

    # ====================================================================== texty
    def retranslate(self) -> None:
        self._update_title()
        self.menu_file.setTitle(self.tr("&File"))
        self.act_open.setText(self.tr("&Open project…"))
        self.act_save.setText(self.tr("&Save as new project…"))
        self.act_quit.setText(self.tr("&Quit"))
        self.menu_settings.setTitle(self.tr("&Settings"))
        self.menu_lang.setTitle(self.tr("&Language"))
        self.lang_actions["auto"].setText(self.tr("Automatic (system)"))
        for k in ("cs", "en"):
            self.lang_actions[k].setText(NATIVE_NAMES[k])  # vlastní název jazyka (kap. 36.2)
        self.menu_theme.setTitle(self.tr("&Appearance"))
        self.theme_actions["auto"].setText(self.tr("Automatic (system)"))
        self.theme_actions["light"].setText(self.tr("Light"))
        self.theme_actions["dark"].setText(self.tr("Dark"))
        self.menu_protocol.setTitle(self.tr("Save &protocol"))
        self.protocol_actions["none"].setText(self.tr("Do not save"))
        self.protocol_actions["beside"].setText(self.tr("Next to the saved project"))
        self.protocol_actions["appdata"].setText(self.tr("In the application's protocol folder"))
        self.act_open_protocols.setText(self.tr("Open protocol folder"))
        self.menu_updates.setTitle(self.tr("&Updates"))
        self.act_update_auto.setText(self.tr("Check for updates &automatically"))
        self.act_update_pre.setText(self.tr("Include &pre-release versions"))
        self.menu_help.setTitle(self.tr("&Help"))
        self.act_help.setText(self.tr("User &guide"))
        self.act_check_updates.setText(self.tr("Check for &updates…"))
        self.act_about.setText(self.tr("&About"))
        self.toolbar.setWindowTitle(self.tr("Toolbar"))
        for act in self._toolbar_icons:
            tip = act.text().replace("&", "").rstrip("…")
            keys = act.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
            act.setToolTip(f"{tip} ({keys})" if keys else tip)

        self.box_project.setTitle(self.tr("Project"))
        self.box_items.setTitle(self.tr("Items (groups)"))
        self.btn_up.setText(self.tr("Up"))
        self.btn_down.setText(self.tr("Down"))
        self.btn_reset.setText(self.tr("Default order"))
        self.btn_all.setText(self.tr("Select all"))
        self.btn_none.setText(self.tr("Select none"))

        self.box_grid.setTitle(self.tr("Grid"))
        labels = [self.tr("Columns:"), self.tr("Gap X:"), self.tr("Gap Y:"), self.tr("Fill order:")]
        for lbl, t in zip(self.lbls_grid, labels):
            lbl.setText(t)
        self._fill_combo(self.combo_fill, FILL_KEYS, [self.tr("From the laser origin"), self.tr("Reading order (from top left)")])

        self.box_place.setTitle(self.tr("Placement"))
        labels = [self.tr("Place grid:"), self.tr("Corner X:"), self.tr("Corner Y:")]
        for lbl, t in zip(self.lbls_place, labels):
            lbl.setText(t)
        self._fill_combo(self.combo_anchor, ANCHOR_KEYS, [
            self.tr("In the board corner at the laser origin"),
            self.tr("In the centre of the board"),
            self.tr("Manually (LightBurn coordinates)"),
            self.tr("At the original position of the items"),
        ])
        tip = self.tr("Position of the grid corner nearest to the laser origin, in LightBurn X/Y coordinates.")
        self.spin_start_x.setToolTip(tip)
        self.spin_start_y.setToolTip(tip)

        self.box_board.setTitle(self.tr("Board"))
        labels = [self.tr("Width:"), self.tr("Height:"), self.tr("Board corner X:"), self.tr("Board corner Y:"),
                  self.tr("Margin left:"), self.tr("Margin right:"), self.tr("Margin top:"), self.tr("Margin bottom:")]
        for lbl, t in zip(self.lbls_board, labels):
            lbl.setText(t)
        self.btn_board_default.setText(self.tr("Save as default for this laser"))
        self.btn_fit.setText(self.tr("Fit view"))
        self.chk_art.setText(self.tr("Show artwork"))
        self._update_project_labels()
        self._rebuild_item_list()
        self._refresh_issue_texts()

    def _fill_combo(self, combo: QComboBox, keys: tuple[str, ...], texts: list[str]) -> None:
        current = combo.currentData() or keys[0]
        combo.blockSignals(True)
        combo.clear()
        for k, t in zip(keys, texts):
            combo.addItem(t, k)
        combo.setCurrentIndex(keys.index(current))
        combo.blockSignals(False)

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate()
        super().changeEvent(event)

    def _apply_number_locale(self) -> None:
        loc = self.locale_mgr.qlocale()
        for w in self.findChildren(QDoubleSpinBox) + self.findChildren(QSpinBox):
            w.setLocale(loc)

    def _origin_text(self) -> str:
        o = self.project.info.orientation.origin if self.project else ""
        return {
            "top_right": self.tr("top right"),
            "top_left": self.tr("top left"),
        }.get(o, o)

    def app_title(self) -> str:
        return self.tr("Grid Arranger for LightBurn")

    def _update_title(self) -> None:
        """Jako v LightBurnu: název aplikace a verze, za pomlčkou otevřený projekt."""
        title = f"{self.app_title()} {display_version()}"
        if self.project is not None:
            title += f" - {self.project.info.path.name}"
        self.setWindowTitle(title)

    def _refresh_icons(self) -> None:
        color = QApplication.palette().color(QPalette.ColorRole.WindowText).name()
        for act, name in self._toolbar_icons.items():
            act.setIcon(icons.icon(name, color))

    def _update_project_labels(self) -> None:
        self._update_title()
        if self.project is None:
            self.lbl_file.setText(self.tr("No project open. Save the project in LightBurn first, then open the saved .lbrn2 file."))
            self.lbl_device.setText("")
            return
        i = self.project.info
        self.lbl_file.setText(f"<b>{i.path.name}</b>")
        self.lbl_device.setText(
            self.tr("Saved for laser: {device}, origin {origin} (LightBurn {version}).").format(
                device=i.device_name or "?", origin=self._origin_text(), version=i.app_version)
            + "<br>"
            + self.tr("After switching the laser in LightBurn, save the project again and reopen it here.")
        )

    # ====================================================================== projekt
    def open_project(self, path: str | Path | None = None) -> bool:
        if path is None:
            path, _ = QFileDialog.getOpenFileName(
                self, self.tr("Open LightBurn project"), "",
                self.tr("LightBurn project (*.lbrn2);;All files (*)"))
            if not path:
                return False
        try:
            project = load_project(path)
        except GridError as e:
            self._error(message(e.code, **e.params))
            return False
        self.project = project
        self.renderer = ProjectRenderer(project)
        self.preview.clear_cache()
        self._refit = True
        self.order = default_order(it for it in project.items if it.supported)
        preset = self.settings.board_for(project.info.device_name)
        if preset is not None:
            self._set_board(preset)
        self._update_project_labels()
        self._rebuild_item_list()
        self.recompute()
        return True

    def _set_board(self, p: BoardPreset) -> None:
        widgets = (self.spin_bw, self.spin_bh, self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb)
        for w in widgets:
            w.blockSignals(True)
        self.spin_bw.setValue(p.width)
        self.spin_bh.setValue(p.height)
        for w, v in zip(widgets[2:], p.margins):
            w.setValue(v)
        for w in widgets:
            w.blockSignals(False)

    def save_board_default(self) -> None:
        if self.project is None:
            return
        preset = BoardPreset(self.spin_bw.value(), self.spin_bh.value(),
                             (self.spin_ml.value(), self.spin_mr.value(), self.spin_mt.value(), self.spin_mb.value()))
        self.settings.set_board_for(self.project.info.device_name, preset)
        self.statusBar().showMessage(self.tr("Board saved as default for {device}.").format(device=self.project.info.device_name), 5000)

    # ====================================================================== seznam výrobků
    def _rebuild_item_list(self, keep: str | None = None) -> None:
        cur = keep or (self.list_items.currentItem().data(Qt.ItemDataRole.UserRole) if self.list_items.currentItem() else None)
        self._rebuilding = True
        self.list_items.clear()
        if self.project is None:
            self.lbl_count.setText("")
            self._rebuilding = False
            return
        items = {it.id: it for it in self.project.items}
        rows = [items[i] for i in self.order]
        rows += [it for it in self.project.items if it.supported and it.id not in self.order]
        rows += [it for it in self.project.items if not it.supported]
        for it in rows:
            selected = it.id in self.order
            num = f"{self.order.index(it.id) + 1}. " if selected else ""
            if it.supported:
                b = it.file_bbox
                size = self.tr("{w} × {h} mm").format(w=self.locale_mgr.qlocale().toString(b[2] - b[0], "f", 1),
                                                    h=self.locale_mgr.qlocale().toString(b[3] - b[1], "f", 1))
                text = f"{num}{it.id}  {it.label}  —  {size}"
            else:
                text = f"{it.id}  {it.label}  —  " + self.tr("cannot be moved")
            if it.warnings:
                text += "  ⚠"
            li = QListWidgetItem(text)
            li.setData(Qt.ItemDataRole.UserRole, it.id)
            tips = [message(r.code, **r.params) for r in it.reasons] + [message(w.code, **w.params) for w in it.warnings]
            if it.outline_layer:
                tips.insert(0, self.tr("Outline layer: {layer}").format(layer=it.outline_layer))
            li.setToolTip("\n".join(tips))
            if it.supported:
                li.setFlags(li.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                li.setCheckState(Qt.CheckState.Checked if selected else Qt.CheckState.Unchecked)
            else:
                li.setFlags(li.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self.list_items.addItem(li)
            if it.id == cur:
                self.list_items.setCurrentItem(li)
        n_sup = sum(1 for it in self.project.items if it.supported)
        self.lbl_count.setText(
            self.tr("Selected %n item(s)", "", len(self.order)) + " / " + self.tr("supported: {s}, total: {t}").format(s=n_sup, t=len(self.project.items)))
        self._rebuilding = False

    def _on_item_changed(self, li: QListWidgetItem) -> None:
        if self._rebuilding:
            return
        iid = li.data(Qt.ItemDataRole.UserRole)
        checked = li.checkState() == Qt.CheckState.Checked
        if checked and iid not in self.order:
            self.order = select(self.order, iid)
        elif not checked and iid in self.order:
            self.order = deselect(self.order, iid)
        self._rebuild_item_list(keep=iid)
        self.recompute()

    def current_id(self) -> str | None:
        li = self.list_items.currentItem()
        return li.data(Qt.ItemDataRole.UserRole) if li else None

    def _move(self, step: int) -> None:
        iid = self.current_id()
        if iid is None or iid not in self.order:
            return
        self.order = move_up(self.order, iid) if step < 0 else move_down(self.order, iid)
        self._rebuild_item_list(keep=iid)
        self.recompute()

    def _on_item_dropped(self, item_id: str, target_id: str) -> None:
        """Přetažení v náhledu: přetažený a cílový výrobek si prohodí místa (rozhodnutí vlastníka)."""
        if item_id in self.order and target_id in self.order:
            self.order = swap(self.order, item_id, target_id)
            self._rebuild_item_list(keep=item_id)
        self.recompute()

    def _reset_order(self) -> None:
        if self.project:
            sel = set(self.order)
            self.order = default_order(it for it in self.project.items if it.id in sel)
            self._rebuild_item_list()
            self.recompute()

    def _select_all(self) -> None:
        if self.project:
            self.order = self.order + tuple(it.id for it in self.project.items if it.supported and it.id not in self.order)
            self._rebuild_item_list()
            self.recompute()

    def _select_none(self) -> None:
        self.order = ()
        self._rebuild_item_list()
        self.recompute()

    def _on_anchor_changed(self) -> None:
        manual = self.combo_anchor.currentData() == "manual"
        self.spin_start_x.setEnabled(manual)
        self.spin_start_y.setEnabled(manual)
        self.recompute()

    # ====================================================================== výpočet a náhled
    def params(self) -> ArrangeParams:
        material = MaterialInput(self.spin_bw.value(), self.spin_bh.value(), self.spin_bx.value(), self.spin_by.value(),
                                 self.spin_ml.value(), self.spin_mr.value(), self.spin_mt.value(), self.spin_mb.value())
        return ArrangeParams(
            columns=self.spin_cols.value(),
            gap_x=self.spin_gap_x.value(),
            gap_y=self.spin_gap_y.value(),
            material=material,
            order=self.order,
            anchor=self.combo_anchor.currentData() or "origin",
            start=(self.spin_start_x.value(), self.spin_start_y.value()),
            fill=self.combo_fill.currentData() or "origin",
        )

    def recompute(self) -> None:
        self.plan, self.plan_error = None, None
        if self.project is None:
            self.preview.clear()
            self._refresh_issue_texts()
            return
        p = self.params()
        try:
            self.plan = make_plan(self.project, p)
        except GridError as e:
            self.plan_error = e
        self._draw()
        self._refresh_issue_texts()

    def _draw(self) -> None:
        from ..domain.models import Rect

        proj = self.project
        o = proj.info.orientation
        board = usable = None
        if self.spin_bw.value() > 0 and self.spin_bh.value() > 0:
            spec = material_to_core(proj, self.params().material)
            board = Rect(spec.board_left, spec.board_top, spec.board_left + spec.board_width, spec.board_top + spec.board_height)
            usable, _ = usable_area(spec)
        sel = set(self.order)
        show = self.chk_art.isChecked()
        obstacles = [(ob.id, ob.bounds, self.renderer.strokes(ob.id) if show else [])
                     for ob in proj.obstacles_for(sel) if ob.bounds is not None]
        problems: set[str] = set()
        if self.plan is not None:
            items = [(pl.item_id, pl.index + 1, pl.target_bounds, self.renderer.strokes(pl.item_id) if show else [], pl.dx, pl.dy)
                     for pl in self.plan.layout.placements]
            for i in self.plan.report.errors:
                problems.update(i.item_ids)
        else:
            items = [(i, n + 1, proj.item(i).screen_bounds, self.renderer.strokes(i) if show else [], 0.0, 0.0)
                     for n, i in enumerate(self.order) if proj.item(i).screen_bounds]
        refit, self._refit = getattr(self, "_refit", False), False
        self.preview.draw(board, usable, o.to_screen_point(0.0, 0.0), obstacles, items, problems, show_art=show, refit=refit)

    def _refresh_issue_texts(self) -> None:
        if not hasattr(self, "list_issues"):
            return
        self.list_issues.clear()
        can_save = False
        if self.locale_mgr.missing_catalog:
            self.list_issues.addItem("⚠ " + self.tr("Translation catalogue is missing; showing English."))
        if self.project is None:
            self.lbl_summary.setText("")
        elif self.plan_error is not None:
            self.lbl_summary.setText(self.tr("The grid cannot be calculated."))
            self.list_issues.addItem("✖ " + message(self.plan_error.code, **self.plan_error.params))
        elif self.plan is not None:
            lay = self.plan.layout
            loc = self.locale_mgr.qlocale()
            cx, cy = self.plan.origin_corner_lightburn
            self.lbl_summary.setText(
                self.tr("Grid {c} × {r}: {w} × {h} mm. Corner at the origin side: X {x}, Y {y}.").format(
                    c=lay.columns, r=lay.rows, w=loc.toString(lay.grid_bounds.width, "f", 2),
                    h=loc.toString(lay.grid_bounds.height, "f", 2), x=loc.toString(cx, "f", 2), y=loc.toString(cy, "f", 2)))
            for i in self.plan.report.errors:
                self.list_issues.addItem("✖ " + issue_text(i.code, i.item_ids, i.params))
            for i in self.plan.report.warnings:
                self.list_issues.addItem("⚠ " + issue_text(i.code, i.item_ids, i.params))
            for iid in self.order:
                for w in self.project.item(iid).warnings:
                    self.list_issues.addItem(f"⚠ {iid}: " + message(w.code, **w.params))
            can_save = self.plan.report.can_save
            if can_save and not self.plan.report.errors:
                self.list_issues.insertItem(0, "✔ " + self.tr("The layout passed all checks."))
        self.act_save.setEnabled(can_save)

    # ====================================================================== uložení
    def save_new_project(self, confirm: bool = True) -> Path | None:
        if self.plan is None or not self.plan.report.can_save:
            return None
        src = self.project.info.path
        target: Path | None = next_output_path(src)  # návrh: puvodni__grid_NNN.lbrn2 vedle originálu
        while confirm:
            target = self._ask_save_path(target)
            if target is None:
                return None
            try:
                target = check_output_path(target, src, self._protocol_target())
                break
            except GridError as e:  # existující soubor nebo originál: nic nepřepsat, nabídnout znovu
                self._error(message(e.code, **e.params) + "\n\n" + self.tr("Choose another name or folder."))
        try:
            res = execute(self.plan, output=target, protocol=self._protocol_target())
        except GridError as e:
            self._error(message(e.code, **e.params))
            return None
        text = self.tr("Saved:\n{out}").format(out=res.output)
        if res.protocol is not None:
            text += "\n\n" + self.tr("Protocol:\n{proto}").format(proto=res.protocol)
        self._info(text + "\n\n" + self.tr("Open the file in LightBurn via File → Open and check the layers, "
                                           "Preview and the position on the machine before cutting."))
        return res.output

    # ====================================================================== protokol
    @staticmethod
    def protocol_folder() -> Path:
        """Složka protokolů v profilu uživatele (Windows: %LOCALAPPDATA%\\GridArranger\\GridArranger\\protocols)."""
        return Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)) / "protocols"

    def _protocol_target(self) -> str | Path:
        mode = self.settings.protocol_mode()
        return self.protocol_folder() if mode == "appdata" else mode

    def open_protocol_folder(self) -> None:
        folder = self.protocol_folder()
        folder.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    # ====================================================================== jazyk, nápověda
    def set_language(self, key: str) -> None:
        self.settings.set_language(key)
        self.locale_mgr.apply(key)
        self.lang_actions[key].setChecked(True)
        self._apply_number_locale()
        self.retranslate()
        self.recompute()
        if getattr(self, "_help", None) is not None:
            self._help.set_language(self.locale_mgr.current)

    def set_theme(self, key: str) -> None:
        self.settings.set_theme(key)
        self.theme_actions[key].setChecked(True)
        self._apply_theme(key)
        if self.project is not None:
            self.recompute()

    def _apply_theme(self, key: str) -> None:
        # Náhled desky zůstává vždy světlý (i v tmavém vzhledu) — rozhodnutí vlastníka.
        self._theme_busy = True
        try:
            self.is_dark = apply_theme(QApplication.instance(), key)
            self._refresh_icons()  # barva ikon podle vzhledu
        finally:
            self._theme_busy = False

    def _on_system_scheme_changed(self, *_args) -> None:
        if self.settings.theme() == "auto" and not getattr(self, "_theme_busy", False):
            self._apply_theme("auto")

    def show_help(self, topic: str = "index") -> None:
        from .help import HelpWindow

        if getattr(self, "_help", None) is None:
            self._help = HelpWindow(self.locale_mgr.current, self)
        self._help.open_topic(topic)
        self._help.show()
        self._help.raise_()

    def show_about(self) -> None:
        QMessageBox.about(
            self, self.tr("About"),
            self.tr("<b>Grid Arranger for LightBurn</b> {version}<br><br>Moves existing groups of a LightBurn project "
                    "into an exact grid and saves a new .lbrn2 file.<br><br>Unofficial tool — not a product of LightBurn "
                    "Software. Always check the result in LightBurn before cutting.").format(version=display_version())
            + f"<br><br><small>Qt {qVersion()} · PySide6 {pyside_version} · {QApplication.style().name()}</small>")

    # ====================================================================== dialogy (v testech nahraditelné)
    def _ask_save_path(self, proposal: Path) -> Path | None:
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("Save as new project"), str(proposal), self.tr("LightBurn project (*.lbrn2)"),
            options=QFileDialog.Option.DontConfirmOverwrite)  # přepsání odmítneme sami s vysvětlením
        return Path(path) if path else None

    def _ask(self, text: str) -> bool:
        return QMessageBox.question(self, self.app_title(), text) == QMessageBox.StandardButton.Yes

    def _info(self, text: str) -> None:
        QMessageBox.information(self, self.app_title(), text)

    def _error(self, text: str) -> None:
        QMessageBox.critical(self, self.app_title(), text)

    # pro testy
    def issues(self) -> list[str]:
        return [self.list_issues.item(i).text() for i in range(self.list_issues.count())]
