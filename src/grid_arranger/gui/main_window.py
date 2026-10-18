"""Hlavní okno (MVP-06; spec. kap. 12.2, 12.3). Bez geometrické logiky — vše počítá `application`."""

from __future__ import annotations

from dataclasses import replace
from html import escape
from pathlib import Path

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QByteArray, QEvent, QItemSelectionModel, QSize, QStandardPaths, Qt, QUrl, qVersion
from PySide6.QtGui import QAction, QDesktopServices, QKeySequence, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QAbstractItemView,
    QDoubleSpinBox,
    QFileDialog,
    QInputDialog,
    QGridLayout,
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
from ..application.arrange_job import (
    ROTATION_MODES, ArrangeParams, ItemGeometry, MaterialInput, Plan, check_output_path, execute, make_plan, material_to_core,
    normalize_angle,
)
from ..core.collision import usable_area
from ..core.order import default_order, deselect, move_down, move_up, select, swap
from ..domain.errors import GridError
from ..version import display_version
from . import icons
from .i18n import LocaleManager
from .messages import issue_text, message
from .history import History
from .preview import PreviewView
from .settings import BoardPreset, UserSettings
from .theme import apply_theme
from .toolbar import ReorderableToolBar, separator
from .widgets import UNITS, LengthSpin, Section, Unit, section_stylesheet
from .updates_ui import UpdateController

ANCHOR_KEYS = ("origin", "center", "manual", "selection")
FILL_KEYS = ("origin", "reading")


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
        self._geometry = None
        self.manual_angles: dict[str, float] = {}
        self.copies: dict[str, str] = {}
        """Kopie výrobků ``{id kopie: zdroj}`` v pořadí vytvoření (spec. v1.16)."""
        self._clipboard: list[str] = []
        self.history = History()
        self._restoring = False
        self.last_saved: Path | None = None
        """Naposledy uložený projekt (pro Otevřít v LightBurnu)."""
        self._open_file = lambda path: QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        """Ruční natočení výrobků (°, po směru hodin); 0 = nenatáčet."""
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
        # Nastavení aplikace: modální okno se stránkami (gui/settings_dialog.py), ne dlouhé menu
        self.act_settings = QAction(self)
        self.act_settings.setShortcut(QKeySequence("Ctrl+,"))
        self.act_settings.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.act_settings.triggered.connect(lambda: self.show_settings())
        self.act_settings_menu = QAction(self)  # v liště menu jen text (ikona je na nástrojové liště)
        self.act_settings_menu.triggered.connect(lambda: self.show_settings())
        self.act_check_updates = QAction(self)
        self.act_check_updates.triggered.connect(lambda: self.updates.check(manual=True))
        # Krok zpět / vpřed (rozložení v aplikaci, ne projekt LightBurnu)
        self.act_undo = QAction(self)
        self.act_undo.setShortcut(QKeySequence(QKeySequence.StandardKey.Undo))
        self.act_undo.triggered.connect(self.undo)
        self.act_redo = QAction(self)
        self.act_redo.setShortcuts([QKeySequence("Ctrl+Y"), QKeySequence("Ctrl+Shift+Z")])
        self.act_redo.triggered.connect(self.redo)
        for a in (self.act_undo, self.act_redo):
            a.setEnabled(False)
            a.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        # Otevřít uložený projekt v LightBurnu (program přiřazený k .lbrn2 = jako dvojklik v Průzkumníku)
        self.act_open_in_lb = QAction(self)
        self.act_open_in_lb.setShortcut(QKeySequence("Ctrl+L"))
        self.act_open_in_lb.setEnabled(False)
        self.act_open_in_lb.triggered.connect(lambda: self.open_in_lightburn())
        # Úpravy: kopie výrobků (Ctrl+C / Ctrl+V, Vytvořit kopie… Ctrl+D jako v LightBurnu), Esc = zrušit výběr
        self.act_copy = QAction(self)
        self.act_copy.setShortcut(QKeySequence(QKeySequence.StandardKey.Copy))
        self.act_copy.triggered.connect(self.copy_selection)
        self.act_paste = QAction(self)
        self.act_paste.setShortcut(QKeySequence(QKeySequence.StandardKey.Paste))
        self.act_paste.triggered.connect(self.paste_copies)
        self.act_duplicate = QAction(self)
        self.act_duplicate.setShortcut(QKeySequence("Ctrl+D"))
        self.act_duplicate.triggered.connect(self.duplicate_dialog)
        self.act_remove_copies = QAction(self)
        self.act_remove_copies.setShortcut(QKeySequence(QKeySequence.StandardKey.Delete))
        self.act_remove_copies.triggered.connect(self.remove_selected_copies)
        for a in (self.act_copy, self.act_paste, self.act_duplicate, self.act_remove_copies):
            a.setShortcutContext(Qt.ShortcutContext.WindowShortcut)

        mb = self.menuBar()
        self.menu_file = mb.addMenu("")
        self.menu_file.addActions([self.act_open, self.act_save, self.act_open_in_lb])
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.act_quit)
        self.menu_edit = mb.addMenu("")
        self.menu_edit.addActions([self.act_undo, self.act_redo])
        self.menu_edit.addSeparator()
        self.menu_edit.addActions([self.act_copy, self.act_paste, self.act_duplicate, self.act_remove_copies])
        self.menu_edit.addSeparator()
        mb.addAction(self.act_settings_menu)  # položka lišty menu otevře rovnou okno Nastavení
        self.menu_help = mb.addMenu("")
        self.menu_help.addActions([self.act_help, self.act_check_updates, self.act_about])

        # --- nástrojová lišta (ikony; další funkce: nová akce + ikona v gui/icons.py)
        self.toolbar = ReorderableToolBar(self)  # ikony lze přeuspořádat tažením (pořadí se pamatuje)
        self.toolbar.setObjectName("mainToolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(24, 24))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.act_fit = QAction(self)
        self.act_fit.setShortcut(QKeySequence("Ctrl+0"))
        self._toolbar_icons = {self.act_open: "open", self.act_save: "save_new", self.act_open_in_lb: "send",
                               self.act_undo: "undo", self.act_redo: "redo", self.act_duplicate: "copies",
                               self.act_fit: "fit", self.act_settings: "settings", self.act_help: "help"}
        keys = {self.act_open: "open", self.act_save: "save", self.act_open_in_lb: "open_in_lightburn",
                self.act_undo: "undo", self.act_redo: "redo", self.act_duplicate: "copies", self.act_fit: "fit",
                self.act_settings: "settings", self.act_help: "help"}
        for a, k in keys.items():
            a.setObjectName(k)
        self.TOOLBAR_DEFAULT = ["open", "save", "open_in_lightburn", "sep1", "undo", "redo", "sep2", "copies", "fit",
                                "sep3", "settings", "help"]
        by_key = {k: a for a, k in keys.items()}
        for k in self.TOOLBAR_DEFAULT:
            self.toolbar.addAction(by_key[k] if k in by_key else separator(self, k))
        saved = self.settings.toolbar_order()
        if saved:
            self.toolbar.set_order(saved)
        self.toolbar.orderChanged.connect(self.settings.set_toolbar_order)
        self.toolbar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.toolbar.customContextMenuRequested.connect(self._toolbar_menu)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        # Esc = zrušit výběr výrobků (v seznamu i v náhledu)
        self.act_clear_selection = QAction(self)
        self.act_clear_selection.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.act_clear_selection.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
        self.act_clear_selection.triggered.connect(self.clear_selection)
        self.addAction(self.act_clear_selection)
        self.menu_edit.addAction(self.act_clear_selection)

        # --- levý panel: sbalitelné sekce (stav se pamatuje), kompaktní mřížka polí
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setSpacing(2)
        unit = UNITS[self.settings.units()]

        def section(key: str) -> tuple[Section, QWidget]:
            sec = Section(key)
            sec.setExpanded(self.settings.section_expanded(key))
            sec.expandedChanged.connect(lambda on, k=key: self.settings.set_section_expanded(k, on))
            lv.addWidget(sec)
            return sec, sec.body

        def length(lo: float, hi: float, value: float) -> LengthSpin:
            return LengthSpin(lo, hi, value, unit)

        self.box_project, body = section("project")
        pv = QVBoxLayout(body)
        # otevření a uložení je na nástrojové liště (a v menu Soubor); zde jen údaje o projektu
        self.lbl_file = QLabel()
        self.lbl_file.setWordWrap(True)
        pv.addWidget(self.lbl_file)
        self.lbl_device = QLabel()
        self.lbl_device.setWordWrap(True)
        pv.addWidget(self.lbl_device)

        self.box_items, body = section("items")
        iv = QVBoxLayout(body)
        self.list_items = QListWidget()
        self.list_items.setMinimumHeight(180)
        self.list_items.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_items.itemChanged.connect(self._on_item_changed)
        self.list_items.itemSelectionChanged.connect(self._on_list_selection)
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
        self.btn_norotate = QPushButton()
        self.btn_norotate.setCheckable(True)
        self.btn_norotate.toggled.connect(self._toggle_no_rotate)
        g.addWidget(self.btn_norotate, 1, 2)
        # ruční natočení vybraných výrobků (výběr v seznamu nebo kliknutím v náhledu)
        self.lbl_angle = QLabel()
        self.spin_angle = QDoubleSpinBox()
        self.spin_angle.setRange(-180.0, 180.0)
        self.spin_angle.setDecimals(1)
        self.spin_angle.setSingleStep(1.0)
        self.spin_angle.setWrapping(True)
        self.spin_angle.setSuffix(" °")
        self.spin_angle.setKeyboardTracking(False)
        self.spin_angle.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.spin_angle.valueChanged.connect(self._on_angle_edited)
        self.btn_rot_ccw, self.btn_rot_cw, self.btn_rot_auto = QPushButton("↺ 90°"), QPushButton("↻ 90°"), QPushButton()
        self.btn_rot_ccw.clicked.connect(lambda: self._turn_selected(-90.0))
        self.btn_rot_cw.clicked.connect(lambda: self._turn_selected(90.0))
        self.btn_rot_auto.clicked.connect(self._auto_selected)
        g.addWidget(self.btn_rot_ccw, 2, 0)
        g.addWidget(self.btn_rot_cw, 2, 1)
        g.addWidget(self.btn_rot_auto, 2, 2)
        iv.addLayout(g)
        rot = QHBoxLayout()
        rot.addWidget(self.lbl_angle)
        rot.addWidget(self.spin_angle)
        rot.addStretch(1)
        iv.addLayout(rot)
        self.lbl_count = QLabel()
        iv.addWidget(self.lbl_count)
        self.chk_art = QCheckBox()  # v hlavičce sekce Výrobky (vykreslení motivů v náhledu)
        self.chk_art.setChecked(True)
        self.chk_art.toggled.connect(lambda _: self.recompute())
        self.box_items.add_header_widget(self.chk_art)

        # Mřížka: Sloupce | Mezera X, Y | Pořadí plnění
        self.box_grid, body = section("grid")
        gg = self._grid_layout(body)
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(1, 1000)
        self.spin_cols.setValue(3)
        self.spin_cols.setKeyboardTracking(False)
        self.spin_cols.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.spin_cols.setFixedWidth(self.spin_cols.fontMetrics().horizontalAdvance("0000") + 36)
        self.spin_gap_x = length(0, 1000, 3.0)
        self.spin_gap_y = length(0, 1000, 3.0)
        self.combo_fill = QComboBox()
        self.combo_rotation = QComboBox()
        self.lbls_grid = [
            self._cell(gg, 0, 0, self.spin_cols),
            self._cell(gg, 1, 0, self.spin_gap_x), self._cell(gg, 1, 2, self.spin_gap_y),
            self._cell(gg, 2, 0, self.combo_fill, span=3),
            self._cell(gg, 3, 0, self.combo_rotation, span=3),
        ]

        # Umístění: způsob | Roh X, Y
        self.box_place, body = section("placement")
        gp = self._grid_layout(body)
        self.combo_anchor = QComboBox()
        self.spin_start_x = length(-100000, 100000, 5.0)
        self.spin_start_y = length(-100000, 100000, 5.0)
        self.lbls_place = [
            self._cell(gp, 0, 0, self.combo_anchor, span=3),
            self._cell(gp, 1, 0, self.spin_start_x), self._cell(gp, 1, 2, self.spin_start_y),
        ]

        # Deska: Šířka, Výška | Roh X, Y | Okraje L, P | H, D
        self.box_board, body = section("board")
        gb = self._grid_layout(body)
        self.spin_bw = length(0, 100000, 700.0)
        self.spin_bh = length(0, 100000, 500.0)
        self.spin_bx = length(-100000, 100000, 0.0)
        self.spin_by = length(-100000, 100000, 0.0)
        self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb = (length(0, 10000, 5.0) for _ in range(4))
        self.lbls_board = [
            self._cell(gb, 0, 0, self.spin_bw), self._cell(gb, 0, 2, self.spin_bh),
            self._cell(gb, 1, 0, self.spin_bx), self._cell(gb, 1, 2, self.spin_by),
            self._cell(gb, 2, 0, self.spin_ml), self._cell(gb, 2, 2, self.spin_mr),
            self._cell(gb, 3, 0, self.spin_mt), self._cell(gb, 3, 2, self.spin_mb),
        ]
        self.btn_board_default = QPushButton()
        self.btn_board_default.clicked.connect(self.save_board_default)
        gb.addWidget(self.btn_board_default, 4, 0, 1, 4)
        lv.addStretch(1)

        self.length_spins = (self.spin_gap_x, self.spin_gap_y, self.spin_start_x, self.spin_start_y,
                             self.spin_bw, self.spin_bh, self.spin_bx, self.spin_by,
                             self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb)
        self.spin_cols.valueChanged.connect(self.recompute)
        for w in self.length_spins:
            w.mmChanged.connect(self.recompute)
        self.combo_fill.currentIndexChanged.connect(self.recompute)
        self.combo_rotation.currentIndexChanged.connect(self._on_rotation_changed)
        self.combo_anchor.currentIndexChanged.connect(self._on_anchor_changed)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._left_scroll, self._left_widget = scroll, left

        # --- pravý panel
        right = QWidget()
        rv = QVBoxLayout(right)
        self.preview = PreviewView()
        self.preview.itemDropped.connect(self._on_item_dropped)
        self.preview.itemClicked.connect(self._on_preview_clicked)
        rv.addWidget(self.preview, 1)
        bar = QHBoxLayout()
        self.lbl_summary = QLabel()
        self.lbl_summary.setWordWrap(True)
        self.act_fit.triggered.connect(self.preview.fit)
        bar.addWidget(self.lbl_summary, 1)
        rv.addLayout(bar)
        self.list_issues = QListWidget()  # výsledek kontroly: výška podle počtu hlášení (viz _fit_issue_list)
        self.list_issues.setWordWrap(True)
        rv.addWidget(self.list_issues)

        split = QSplitter()
        split.addWidget(scroll)
        split.addWidget(right)
        split.setChildrenCollapsible(False)
        self.setCentralWidget(split)
        self.splitter = split
        self._preview_panel = right
        self._place_panel(self.settings.panel_side())

    @staticmethod
    def _grid_layout(body: QWidget) -> QGridLayout:
        g = QGridLayout(body)
        g.setHorizontalSpacing(8)
        g.setColumnStretch(4, 1)  # pole zůstanou úzká, volné místo vpravo
        return g

    @staticmethod
    def _cell(grid: QGridLayout, row: int, col: int, widget: QWidget, span: int = 1) -> QLabel:
        """Popisek + pole do mřížky (sloupce 0–1 a 2–3); vrací popisek kvůli překladu."""
        lbl = QLabel()
        lbl.setBuddy(widget)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        grid.addWidget(lbl, row, col)
        grid.addWidget(widget, row, col + 1, 1, span, Qt.AlignmentFlag.AlignLeft)
        return lbl

    # ====================================================================== texty
    def retranslate(self) -> None:
        self._update_title()
        self.menu_file.setTitle(self.tr("&File"))
        self.act_open.setText(self.tr("&Open project…"))
        self.act_save.setText(self.tr("&Save as new project…"))
        self.act_quit.setText(self.tr("&Quit"))
        self.act_open_in_lb.setText(self.tr("Open saved project in &LightBurn"))
        self.act_settings.setText(self.tr("&Settings"))
        self.act_settings_menu.setText(self.tr("&Settings"))
        self.menu_help.setTitle(self.tr("&Help"))
        self.act_help.setText(self.tr("User &guide"))
        self.act_check_updates.setText(self.tr("Check for &updates…"))
        self.act_about.setText(self.tr("&About"))
        self.act_fit.setText(self.tr("Fit view"))
        self.menu_edit.setTitle(self.tr("&Edit"))
        self.act_undo.setText(self.tr("&Undo"))
        self.act_redo.setText(self.tr("&Redo"))
        self.act_copy.setText(self.tr("&Copy items"))
        self.act_paste.setText(self.tr("&Paste copies"))
        self.act_duplicate.setText(self.tr("Create &copies…"))
        self.act_remove_copies.setText(self.tr("&Remove copies"))
        self.act_clear_selection.setText(self.tr("Clear &selection"))
        self.toolbar.setWindowTitle(self.tr("Toolbar"))
        for act in self._toolbar_icons:
            tip = act.text().replace("&", "").rstrip("…")
            keys = act.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
            act.setToolTip((f"{tip} ({keys})" if keys else tip) + "\n" + self.tr("Drag to rearrange the toolbar"))

        self.box_project.setTitle(self.tr("Project"))
        self.box_items.setTitle(self.tr("Items (groups)"))
        self.btn_up.setText(self.tr("Up"))
        self.btn_down.setText(self.tr("Down"))
        self.btn_reset.setText(self.tr("Default order"))
        self.btn_all.setText(self.tr("Select all"))
        self.btn_none.setText(self.tr("Select none"))

        self.box_grid.setTitle(self.tr("Grid"))
        labels = [self.tr("Columns:"), self.tr("Gap X:"), self.tr("Y:"), self.tr("Fill order:"), self.tr("Rotation:")]
        for lbl, t in zip(self.lbls_grid, labels):
            lbl.setText(t)
        if self.combo_rotation.count() == 0:  # první naplnění: uložená volba
            self.combo_rotation.addItem("", self.settings.rotation_mode())
        self._fill_combo(self.combo_rotation, ROTATION_MODES, [
            self.tr("Do not rotate"), self.tr("In 90° steps"), self.tr("Any angle (smallest area)")])
        self.combo_rotation.setToolTip(self.tr(
            "Rotate items to save material: each item is turned so that the rectangle around it is as small as possible, "
            "and the orientation giving the smallest grid is chosen. Exceptions: select an item and click “No rotation”."))
        self.btn_norotate.setText(self.tr("No rotation"))
        self.btn_norotate.setToolTip(self.tr("The selected items will never be rotated."))
        self.lbl_angle.setText(self.tr("Angle of selected:"))
        self.spin_angle.setToolTip(self.tr(
            "Rotation of the selected items in degrees (positive = clockwise). Select items in the list or by clicking "
            "them in the preview (Ctrl+click adds more). A manual angle is kept as entered."))
        self.btn_rot_ccw.setToolTip(self.tr("Rotate the selected items 90° anticlockwise"))
        self.btn_rot_cw.setToolTip(self.tr("Rotate the selected items 90° clockwise"))
        self.btn_rot_auto.setText(self.tr("Auto"))
        self.btn_rot_auto.setToolTip(self.tr("Remove the manual angle: the selected items are rotated automatically again"))
        self._fill_combo(self.combo_fill, FILL_KEYS, [self.tr("From the laser origin"), self.tr("Reading order (from top left)")])

        self.box_place.setTitle(self.tr("Placement"))
        labels = [self.tr("Place grid:"), self.tr("Corner X:"), self.tr("Y:")]
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
        labels = [self.tr("Width:"), self.tr("Height:"), self.tr("Board corner X:"), self.tr("Y:"),
                  self.tr("Margin left:"), self.tr("right:"), self.tr("Margin top:"), self.tr("bottom:")]
        for lbl, t in zip(self.lbls_board, labels):
            lbl.setText(t)
        self.btn_board_default.setText(self.tr("Save as default for this laser"))
        self.chk_art.setText(self.tr("Show artwork"))
        self._update_project_labels()
        self._rebuild_item_list()
        self._refresh_issue_texts()
        self._fit_left_panel()

    def _fit_left_panel(self) -> None:
        """Levý panel tak široký, aby se vešla pole vedle sebe (závisí na jazyku a jednotkách) — bez vodorovného posuvníku."""
        self._left_widget.ensurePolished()
        for w in self._left_widget.findChildren(QWidget):
            w.ensurePolished()
        self._left_widget.layout().invalidate()
        self._left_widget.layout().activate()
        need = max(self._left_widget.minimumSizeHint().width(), 340)
        self._left_scroll.setMinimumWidth(need + self._left_scroll.verticalScrollBar().sizeHint().width() + 8)

    def _fill_combo(self, combo: QComboBox, keys: tuple[str, ...], texts: list[str]) -> None:
        current = combo.currentData() or keys[0]
        combo.blockSignals(True)
        combo.clear()
        for k, t in zip(keys, texts):
            combo.addItem(t, k)
        combo.setCurrentIndex(keys.index(current))
        combo.blockSignals(False)

    def _place_panel(self, side: str) -> None:
        """Panel nastavení rozložení vlevo, nebo vpravo od náhledu; náhled zabírá volné místo."""
        sizes = self.splitter.sizes()
        want = 0 if side == "left" else 1
        if self.splitter.indexOf(self._left_scroll) != want:
            self.splitter.insertWidget(want, self._left_scroll)
            self.splitter.setSizes(list(reversed(sizes)))
        self.splitter.setStretchFactor(want, 0)
        self.splitter.setStretchFactor(1 - want, 1)

    def panel_side(self) -> str:
        return "left" if self.splitter.indexOf(self._left_scroll) == 0 else "right"

    def set_panel_side(self, side: str) -> None:
        self.settings.set_panel_side(side)
        self._place_panel(side)

    def restore_window_state(self) -> None:
        """Velikost, poloha a maximalizace okna z minulého spuštění (volat před ``show()``).
        Okno mimo připojené monitory Qt samo vrátí na obrazovku."""
        geometry = self.settings.window_geometry()
        if geometry:
            self.restoreGeometry(QByteArray(geometry))
        splitter = self.settings.window_splitter()
        if splitter:
            self.splitter.restoreState(QByteArray(splitter))

    def closeEvent(self, event) -> None:  # noqa: N802
        self.settings.set_window_state(bytes(self.saveGeometry()), bytes(self.splitter.saveState()))
        super().closeEvent(event)

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate()
        super().changeEvent(event)

    def _apply_number_locale(self) -> None:
        loc = self.locale_mgr.qlocale()
        for w in self.findChildren(QDoubleSpinBox) + self.findChildren(QSpinBox):
            w.setLocale(loc)

    @property
    def unit(self) -> Unit:
        return UNITS[self.settings.units()]

    def _len(self, mm: float, short: bool = False) -> str:
        """Délka v aktuálních jednotkách a formátu čísel jazyka (mm: 2 desetiny, palce: 3; ``short`` o jednu méně)."""
        u = self.unit
        return self.locale_mgr.qlocale().toString(u.to_display(mm), "f", u.decimals - (1 if short else 0))

    def set_units(self, key: str) -> None:
        """Milimetry / palce (jako v LightBurnu). Jen zobrazení — výpočet a soubor zůstávají v mm."""
        self.settings.set_units(key)
        for w in self.length_spins:
            w.set_unit(UNITS[key])
        self._rebuild_item_list()
        self._refresh_issue_texts()
        self._fit_left_panel()

    def _origin_text(self) -> str:
        o = self.project.info.orientation.origin if self.project else ""
        return {
            "top_right": self.tr("top right"),
            "top_left": self.tr("top left"),
            "bottom_left": self.tr("bottom left"),
            "bottom_right": self.tr("bottom right"),
        }.get(o, o)

    def app_title(self) -> str:
        return self.tr("Grid Arranger for LightBurn")

    def _update_title(self) -> None:
        """Jako v LightBurnu: název aplikace a verze, za pomlčkou otevřený projekt."""
        title = f"{self.app_title()} {display_version()}"
        if self.project is not None:
            title += f" - {self.project.info.path.name}"
            saved = self._saved_elsewhere()
            if saved is not None:  # uloženo do nového souboru, ale dál se pracuje s otevřeným projektem
                title += " " + self.tr("(last saved as {name})").format(name=saved.name)
        self.setWindowTitle(title)

    def _saved_elsewhere(self) -> Path | None:
        """Naposledy uložený soubor, pokud to není právě otevřený projekt."""
        if self.project is None or self.last_saved is None or self.last_saved == self.project.info.path:
            return None
        return self.last_saved

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
        text = f"<b>{escape(i.path.name)}</b>"
        saved = self._saved_elsewhere()
        if saved is not None:
            text += "<br>" + self.tr("Last saved as <b>{name}</b>. You keep arranging the project opened above; "
                                     "the next save creates another file.").format(name=escape(saved.name))
        self.lbl_file.setText(text)
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
        self.last_saved = None
        self.act_open_in_lb.setEnabled(False)
        self.renderer = ProjectRenderer(project)
        self._geometry = ItemGeometry(project)
        self.manual_angles = {}
        self.copies = {}
        self._clipboard = []
        self.history = History()  # krok zpět jen v rámci otevřeného projektu
        self.preview.set_selection(set())
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
        values = (p.width, p.height, *p.margins)
        for w, v in zip((self.spin_bw, self.spin_bh, self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb), values):
            w.set_mm(v, emit=False)

    def save_board_default(self) -> None:
        if self.project is None:
            return
        preset = BoardPreset(self.spin_bw.mm(), self.spin_bh.mm(),
                             (self.spin_ml.mm(), self.spin_mr.mm(), self.spin_mt.mm(), self.spin_mb.mm()))
        self.settings.set_board_for(self.project.info.device_name, preset)
        self.statusBar().showMessage(self.tr("Board saved as default for {device}.").format(device=self.project.info.device_name), 5000)

    # ====================================================================== seznam výrobků
    def _rebuild_item_list(self, keep: str | None = None) -> None:
        cur = keep or (self.list_items.currentItem().data(Qt.ItemDataRole.UserRole) if self.list_items.currentItem() else None)
        chosen = self.selected_ids() if keep is None else {keep}
        self._rebuilding = True
        self.list_items.blockSignals(True)
        self.list_items.clear()
        if self.project is None:
            self.lbl_count.setText("")
            self._rebuilding = False
            return
        items = {it.id: it for it in self.project.items} | {cid: self._lookup(cid) for cid in self.copies}
        rows = [items[i] for i in self.order]
        rows += [it for it in self.project.items if it.supported and it.id not in self.order]
        rows += [it for it in self.project.items if not it.supported]
        for it in rows:
            selected = it.id in self.order
            li = QListWidgetItem(self._item_text(it))
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
            li.setSelected(it.id in chosen)
        n_sup = sum(1 for it in self.project.items if it.supported)
        self.lbl_count.setText(
            self.tr("Selected %n item(s)", "", len(self.order)) + " / " + self.tr("supported: {s}, total: {t}").format(s=n_sup, t=len(self.project.items)))
        self.list_items.blockSignals(False)
        self._rebuilding = False
        self._on_list_selection()

    def _item_text(self, it) -> str:
        selected = it.id in self.order
        num = f"{self.order.index(it.id) + 1}. " if selected else ""
        if it.supported:
            b = it.file_bbox
            size = self.tr("{w} × {h} {unit}").format(w=self._len(b[2] - b[0], short=True), h=self._len(b[3] - b[1], short=True),
                                                    unit=self.unit.suffix)
            label = f"{it.label}  " + self.tr("(copy of {src})").format(src=self.copies[it.id]) if it.id in self.copies else it.label
            text = f"{num}{it.id}  {label}  —  {size}"
            angle = self.plan.rotations.get(it.id) if self.plan is not None else None
            manual = it.id in self.manual_angles
            if manual and not self.manual_angles[it.id]:
                text += "  " + self.tr("(no rotation)")
            elif angle:
                deg = self.locale_mgr.qlocale().toString(abs(angle), "f", 1).rstrip("0").rstrip(",.")
                text += f"  {'↻' if angle > 0 else '↺'} {deg}°"
                if manual:
                    text += " " + self.tr("(manual)")
        else:
            text = f"{it.id}  {it.label}  —  " + self.tr("cannot be moved")
        if it.warnings:
            text += "  ⚠"
        return text

    def _update_item_texts(self) -> None:
        """Po přepočtu jen obnoví texty (úhel natočení) bez přestavby seznamu."""
        if self.project is None:
            return
        self._rebuilding = True
        for i in range(self.list_items.count()):
            li = self.list_items.item(i)
            li.setText(self._item_text(self._lookup(li.data(Qt.ItemDataRole.UserRole))))
        self._rebuilding = False
        self._sync_no_rotate_button()

    def _current_item_id(self) -> str | None:
        li = self.list_items.currentItem()
        return li.data(Qt.ItemDataRole.UserRole) if li is not None else None

    def _lookup(self, iid: str):
        """Výrobek podle id — u kopie zdrojový výrobek s id kopie."""
        if iid in self.copies:
            return replace(self.project.item(self.copies[iid]), id=iid)
        return self.project.item(iid)

    def selected_ids(self) -> set[str]:
        return {li.data(Qt.ItemDataRole.UserRole) for li in self.list_items.selectedItems()}

    def _rotatable_selection(self) -> list[str]:
        """Vybrané výrobky, které se rozmisťují (jen ty lze natáčet)."""
        return [i for i in self.order if i in self.selected_ids()]

    def _effective_angle(self, iid: str) -> float:
        if iid in self.manual_angles:
            return self.manual_angles[iid]
        return self.plan.rotations.get(iid, 0.0) if self.plan is not None else 0.0

    def _on_list_selection(self) -> None:
        if self._rebuilding:
            return
        self.preview.set_selection(self.selected_ids() & set(self.order))
        self._sync_no_rotate_button()

    # --- krok zpět / vpřed ----------------------------------------------------------------------
    def _snapshot(self) -> tuple:
        manual = self.combo_anchor.currentData() == "manual"
        return (
            tuple(self.order), tuple(self.copies.items()), tuple(sorted(self.manual_angles.items())),
            self.spin_cols.value(), round(self.spin_gap_x.mm(), 6), round(self.spin_gap_y.mm(), 6),
            self.combo_fill.currentData(), self.combo_rotation.currentData(), self.combo_anchor.currentData(),
            (round(self.spin_start_x.mm(), 6), round(self.spin_start_y.mm(), 6)) if manual else None,
            tuple(round(w.mm(), 6) for w in (self.spin_bw, self.spin_bh, self.spin_bx, self.spin_by,
                                              self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb)),
        )

    def _record_history(self) -> None:
        if self._restoring or self.project is None:
            return
        self.history.push(self._snapshot())
        self._sync_history_actions()

    def _sync_history_actions(self) -> None:
        self.act_undo.setEnabled(self.history.can_undo())
        self.act_redo.setEnabled(self.history.can_redo())

    def _restore(self, state: tuple | None) -> None:
        if state is None:
            return
        order, copies, angles, cols, gx, gy, fill, rotation, anchor, start, board = state
        self._restoring = True
        try:
            self.order, self.copies, self.manual_angles = tuple(order), dict(copies), dict(angles)
            widgets = [self.spin_cols, self.combo_fill, self.combo_rotation, self.combo_anchor]
            for w in widgets:
                w.blockSignals(True)
            self.spin_cols.setValue(cols)
            for combo, data in ((self.combo_fill, fill), (self.combo_rotation, rotation), (self.combo_anchor, anchor)):
                i = combo.findData(data)
                if i >= 0:
                    combo.setCurrentIndex(i)
            for w in widgets:
                w.blockSignals(False)
            if rotation:
                self.settings.set_rotation_mode(rotation)
            self.spin_gap_x.set_mm(gx, emit=False)
            self.spin_gap_y.set_mm(gy, emit=False)
            for w, v in zip((self.spin_bw, self.spin_bh, self.spin_bx, self.spin_by,
                             self.spin_ml, self.spin_mr, self.spin_mt, self.spin_mb), board):
                w.set_mm(v, emit=False)
            is_manual = anchor == "manual"
            if is_manual and start is not None:
                self.spin_start_x.set_mm(start[0], emit=False)
                self.spin_start_y.set_mm(start[1], emit=False)
            self.spin_start_x.setEnabled(is_manual)
            self.spin_start_y.setEnabled(is_manual)
            self._rebuild_item_list()
            self.recompute()
        finally:
            self._restoring = False
        self._sync_history_actions()

    def undo(self) -> None:
        self._restore(self.history.undo())

    def redo(self) -> None:
        self._restore(self.history.redo())

    def _toolbar_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)
        reset = menu.addAction(self.tr("Restore default toolbar layout"))
        if menu.exec(self.toolbar.mapToGlobal(pos)) is reset:
            self.reset_toolbar()

    def reset_toolbar(self) -> None:
        self.toolbar.set_order(self.TOOLBAR_DEFAULT)
        self.settings.set_toolbar_order([])

    # --- kopie výrobků (spec. v1.16) --------------------------------------------------------------
    MAX_COPIES = 999

    def _new_copy_id(self, src: str) -> str:
        k = 1
        while f"{src}+{k}" in self.copies:
            k += 1
        return f"{src}+{k}"

    def add_copies(self, ids: list[str], count: int) -> list[str]:
        """Přidá ``count`` kopií každého výrobku z ``ids`` na konec pořadí; kopie převezme ruční úhel."""
        if self.project is None or count < 1:
            return []
        new: list[str] = []
        for iid in ids:
            src = self.copies.get(iid, iid)
            if src not in {it.id for it in self.project.items} or not self.project.item(src).supported:
                continue
            for _ in range(count):
                if len(self.copies) >= self.MAX_COPIES:
                    break
                cid = self._new_copy_id(src)
                self.copies[cid] = src
                if iid in self.manual_angles:
                    self.manual_angles[cid] = self.manual_angles[iid]
                new.append(cid)
        if new:
            self.order = self.order + tuple(new)
            self._rebuild_item_list()
            self._select_ids(set(new))
            self.recompute()
            self.statusBar().showMessage(self.tr("Added %n copies.", "", len(new)), 5000)
        return new

    def _select_ids(self, ids: set[str]) -> None:
        self.list_items.blockSignals(True)
        self.list_items.clearSelection()
        last = None
        for i in range(self.list_items.count()):
            li = self.list_items.item(i)
            if li.data(Qt.ItemDataRole.UserRole) in ids:
                li.setSelected(True)
                last = li
        if last is not None:
            self.list_items.setCurrentItem(last, QItemSelectionModel.SelectionFlag.NoUpdate)
            self.list_items.scrollToItem(last)
        self.list_items.blockSignals(False)
        self._on_list_selection()

    def copy_selection(self) -> None:
        ids = self._rotatable_selection()
        if ids:
            self._clipboard = ids
            self.statusBar().showMessage(self.tr("Copied %n item(s). Paste with Ctrl+V.", "", len(ids)), 5000)
            self._sync_no_rotate_button()

    def paste_copies(self) -> None:
        self.add_copies(list(self._clipboard), 1)

    def duplicate_dialog(self) -> None:
        ids = self._rotatable_selection()
        if not ids:
            self._info(self.tr("First select the items to copy — in the list or by clicking them in the preview."))
            return
        n = self._ask_int(self.tr("Create copies"),
                          self.tr("Number of copies of each selected item (%n selected):", "", len(ids)), 1, 1, self.MAX_COPIES)
        if n:
            self.add_copies(ids, n)

    def _ask_int(self, title: str, label: str, value: int, lo: int, hi: int) -> int | None:
        n, ok = QInputDialog.getInt(self, title, label, value, lo, hi)
        return n if ok else None

    def _remove_copies(self, ids: list[str]) -> None:
        gone = [i for i in ids if i in self.copies]
        if not gone:
            return
        for cid in gone:
            del self.copies[cid]
            self.manual_angles.pop(cid, None)
        self.order = tuple(i for i in self.order if i not in gone)
        self._clipboard = [i for i in self._clipboard if i not in gone]
        self._rebuild_item_list()
        self.recompute()

    def remove_selected_copies(self) -> None:
        self._remove_copies([i for i in self.order if i in self.selected_ids()])

    def clear_selection(self) -> None:
        self.list_items.clearSelection()
        self._on_list_selection()

    def _on_preview_clicked(self, iid: str, additive: bool) -> None:
        """Kliknutí na výrobek v náhledu = výběr v seznamu (Ctrl přidá / odebere)."""
        for i in range(self.list_items.count()):
            li = self.list_items.item(i)
            if li.data(Qt.ItemDataRole.UserRole) != iid:
                continue
            self.list_items.blockSignals(True)
            if additive:
                li.setSelected(not li.isSelected())
            else:
                self.list_items.clearSelection()
                li.setSelected(True)
            self.list_items.setCurrentItem(li, QItemSelectionModel.SelectionFlag.NoUpdate)
            self.list_items.blockSignals(False)
            self.list_items.scrollToItem(li)
            self._on_list_selection()
            return

    def _sync_no_rotate_button(self) -> None:
        ids = self._rotatable_selection()
        ok = bool(ids) and self.project is not None
        self.btn_norotate.blockSignals(True)
        self.btn_norotate.setEnabled(ok)
        self.btn_norotate.setChecked(ok and all(self.manual_angles.get(i) == 0.0 for i in ids))
        self.btn_norotate.blockSignals(False)
        for w in (self.spin_angle, self.btn_rot_ccw, self.btn_rot_cw):
            w.setEnabled(ok)
        self.btn_rot_auto.setEnabled(ok and any(i in self.manual_angles for i in ids))
        self.act_copy.setEnabled(ok)
        self.act_duplicate.setEnabled(self.project is not None)
        self.act_paste.setEnabled(self.project is not None and bool(self._clipboard))
        self.act_remove_copies.setEnabled(any(i in self.copies for i in ids))
        self.spin_angle.blockSignals(True)
        self.spin_angle.setValue(self._effective_angle(ids[0]) if ok else 0.0)
        self.spin_angle.blockSignals(False)

    def _set_manual(self, angles: dict[str, float]) -> None:
        for iid, a in angles.items():
            self.manual_angles[iid] = normalize_angle(round(a, 6))
        self.recompute()

    def _toggle_no_rotate(self, on: bool) -> None:
        ids = self._rotatable_selection()
        if not ids:
            return
        if on:
            self._set_manual({i: 0.0 for i in ids})
        else:
            for i in ids:
                self.manual_angles.pop(i, None)
            self.recompute()

    def _on_angle_edited(self, value: float) -> None:
        ids = self._rotatable_selection()
        if ids:
            self._set_manual({i: value for i in ids})

    def _turn_selected(self, step: float) -> None:
        ids = self._rotatable_selection()
        if ids:
            self._set_manual({i: self._effective_angle(i) + step for i in ids})

    def _auto_selected(self) -> None:
        for i in self._rotatable_selection():
            self.manual_angles.pop(i, None)
        self.recompute()

    def _on_rotation_changed(self) -> None:
        self.settings.set_rotation_mode(self.combo_rotation.currentData() or "any")
        self.recompute()

    def _on_item_changed(self, li: QListWidgetItem) -> None:
        if self._rebuilding:
            return
        iid = li.data(Qt.ItemDataRole.UserRole)
        checked = li.checkState() == Qt.CheckState.Checked
        if not checked and iid in self.copies:  # kopie bez zaškrtnutí nemá smysl → odebrat
            self._remove_copies([iid])
            return
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
            self.order = default_order(it for it in self.project.items if it.id in sel) + tuple(c for c in self.copies if c in sel)
            self._rebuild_item_list()
            self.recompute()

    def _select_all(self) -> None:
        if self.project:
            self.order = self.order + tuple(it.id for it in self.project.items if it.supported and it.id not in self.order)
            self._rebuild_item_list()
            self.recompute()

    def _select_none(self) -> None:
        self.order = ()
        for cid in self.copies:
            self.manual_angles.pop(cid, None)
        self.copies = {}
        self._rebuild_item_list()
        self.recompute()

    def _sync_corner_fields(self) -> None:
        """Mimo režim Ručně ukazují (zašedlá) pole Roh X/Y skutečně vypočtený roh mřížky u počátku.
        Po přepnutí na Ručně tak pole obsahují aktuální roh a mřížka se neposune."""
        if self.plan is None or self.combo_anchor.currentData() == "manual":
            return
        x, y = self.plan.origin_corner_lightburn
        self.spin_start_x.set_mm(x, emit=False)
        self.spin_start_y.set_mm(y, emit=False)

    def _on_anchor_changed(self) -> None:
        manual = self.combo_anchor.currentData() == "manual"
        self.spin_start_x.setEnabled(manual)
        self.spin_start_y.setEnabled(manual)
        self.recompute()

    # ====================================================================== výpočet a náhled
    def params(self) -> ArrangeParams:
        material = MaterialInput(self.spin_bw.mm(), self.spin_bh.mm(), self.spin_bx.mm(), self.spin_by.mm(),
                                 self.spin_ml.mm(), self.spin_mr.mm(), self.spin_mt.mm(), self.spin_mb.mm())
        return ArrangeParams(
            columns=self.spin_cols.value(),
            gap_x=self.spin_gap_x.mm(),
            gap_y=self.spin_gap_y.mm(),
            material=material,
            order=self.order,
            anchor=self.combo_anchor.currentData() or "origin",
            start=(self.spin_start_x.mm(), self.spin_start_y.mm()),
            fill=self.combo_fill.currentData() or "origin",
            rotation=self.combo_rotation.currentData() or "none",
            angles={k: v for k, v in self.manual_angles.items() if k in self.order},
            copies={k: v for k, v in self.copies.items() if k in self.order},
        )

    def recompute(self) -> None:
        self.plan, self.plan_error = None, None
        if self.project is None:
            self.preview.clear()
            self._refresh_issue_texts()
            return
        p = self.params()
        try:
            self.plan = make_plan(self.project, p, self._geometry)
        except GridError as e:
            self.plan_error = e
        self._sync_corner_fields()
        self._update_item_texts()
        self._draw()
        self._refresh_issue_texts()
        self._record_history()

    def _draw(self) -> None:
        from ..domain.models import Rect

        proj = self.project
        o = proj.info.orientation
        board = usable = None
        if self.spin_bw.mm() > 0 and self.spin_bh.mm() > 0:
            spec = material_to_core(proj, self.params().material)
            board = Rect(spec.board_left, spec.board_top, spec.board_left + spec.board_width, spec.board_top + spec.board_height)
            usable, _ = usable_area(spec)
        sel = set(self.order)
        show = self.chk_art.isChecked()
        obstacles = [(ob.id, ob.bounds, self.renderer.strokes(ob.id) if show else [])
                     for ob in proj.obstacles_for(sel) if ob.bounds is not None]
        problems: set[str] = set()
        if self.plan is not None:
            items = [(pl.item_id, pl.index + 1, pl.target_bounds, self.renderer.strokes(self.copies.get(pl.item_id, pl.item_id)) if show else [], pl.dx, pl.dy,
                      self.plan.rotations.get(pl.item_id, 0.0), self.plan.pivots.get(pl.item_id, (0.0, 0.0)))
                     for pl in self.plan.layout.placements]
            for i in self.plan.report.errors:
                problems.update(i.item_ids)
        else:
            items = [(i, n + 1, self._lookup(i).screen_bounds, self.renderer.strokes(self.copies.get(i, i)) if show else [], 0.0, 0.0)
                     for n, i in enumerate(self.order) if self._lookup(i).screen_bounds]
        refit, self._refit = getattr(self, "_refit", False), False
        self.preview.draw(board, usable, o.to_screen_point(0.0, 0.0), obstacles, items, problems, show_art=show, refit=refit)

    def _refresh_issue_texts(self) -> None:
        if not hasattr(self, "list_issues"):
            return
        self.list_issues.clear()
        can_save = False
        if self.locale_mgr.missing_catalog:
            self.list_issues.addItem("⚠ " + self.tr("Translation catalogue is missing; showing English."))
        if self.project is not None and not self.project.info.orientation.verified:
            self.list_issues.addItem("⚠ " + message("origin_unverified", origin=self._origin_text()))
        if self.project is None:
            self.lbl_summary.setText("")
        elif self.plan_error is not None:
            self.lbl_summary.setText(self.tr("The grid cannot be calculated."))
            self.list_issues.addItem("✖ " + message(self.plan_error.code, **self.plan_error.params))
        elif self.plan is not None:
            lay = self.plan.layout
            cx, cy = self.plan.origin_corner_lightburn
            self.lbl_summary.setText(
                self.tr("Grid {c} × {r}: {w} × {h} {unit}. Corner at the origin side: X {x}, Y {y}.").format(
                    c=lay.columns, r=lay.rows, w=self._len(lay.grid_bounds.width), h=self._len(lay.grid_bounds.height),
                    x=self._len(cx), y=self._len(cy), unit=self.unit.suffix))
            for i in self.plan.report.errors:
                self.list_issues.addItem("✖ " + issue_text(i.code, i.item_ids, i.params))
            for i in self.plan.report.warnings:
                self.list_issues.addItem("⚠ " + issue_text(i.code, i.item_ids, i.params))
            for iid in self.order:
                for w in self._lookup(iid).warnings:
                    self.list_issues.addItem(f"⚠ {iid}: " + message(w.code, **w.params))
            can_save = self.plan.report.can_save
            if can_save and not self.plan.report.errors:
                self.list_issues.insertItem(0, "✔ " + self.tr("The layout passed all checks."))
        self.act_save.setEnabled(can_save)
        self._fit_issue_list()

    ISSUE_ROWS_MAX = 6

    def _fit_issue_list(self) -> None:
        """Seznam hlášení jen tak vysoký, kolik má řádků (nejvýš ``ISSUE_ROWS_MAX``, pak posuvník);
        bez hlášení (žádný projekt) se skryje a místo dostane náhled."""
        lst = self.list_issues
        n = lst.count()
        lst.setVisible(n > 0)
        if n == 0:
            return
        rows = sum(lst.sizeHintForRow(i) if lst.sizeHintForRow(i) > 0 else lst.fontMetrics().height() + 2
                   for i in range(min(n, self.ISSUE_ROWS_MAX)))
        lst.setFixedHeight(rows + 2 * lst.frameWidth() + 2)

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
        self.last_saved = res.output
        self.act_open_in_lb.setEnabled(True)
        self._update_project_labels()
        text += "\n\n" + self.tr("Open it in LightBurn (button below, or File → Open — not Import) and check the layers, "
                                   "Preview and the position on the machine before cutting.")
        text += "\n\n" + self.tr("The original project stays open here. To continue arranging the saved file "
                                   "instead, tick the option below.")
        open_lb, switch = self._ask_after_save(text)
        if open_lb:
            self.open_in_lightburn(res.output)
        if switch:
            self.continue_with_saved(res.output)
        return res.output

    def _ask_after_save(self, text: str) -> tuple[bool, bool]:
        """Hlášení o uložení: (otevřít v LightBurnu, pokračovat v aplikaci s uloženým souborem)."""
        box = QMessageBox(QMessageBox.Icon.Information, self.app_title(), text, parent=self)
        open_btn = box.addButton(self.tr("Open in LightBurn"), QMessageBox.ButtonRole.AcceptRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.setDefaultButton(open_btn)
        chk = QCheckBox(self.tr("Continue working on the saved file here (instead of the original)"))
        box.setCheckBox(chk)
        box.exec()
        return box.clickedButton() is open_btn, chk.isChecked()

    def continue_with_saved(self, path: Path | None = None) -> bool:
        """Otevře uložený výstup místo originálu — jako „Uložit jako“: další úpravy vycházejí z něj
        (kopie a natočení jsou v něm už napevno). Originál zůstává beze změny."""
        path = Path(path or self.last_saved or "")
        if not self.open_project(path):
            return False
        self.last_saved = path  # Otevřít v LightBurnu (Ctrl+L) dál otevře tento soubor
        self.act_open_in_lb.setEnabled(True)
        self.statusBar().showMessage(self.tr("Now working on the saved file {name}. The original is unchanged.")
                                     .format(name=path.name), 8000)
        return True

    def open_in_lightburn(self, path: Path | None = None) -> bool:
        """Otevře uložený projekt programem přiřazeným k .lbrn2 (LightBurn) — jako dvojklik v Průzkumníku.
        Běžící LightBurn nahradí otevřený projekt; na neuložené změny se zeptá sám."""
        path = Path(path or self.last_saved or "")
        if not path.is_file():
            self._error(self.tr("The saved project was not found:\n{path}").format(path=path))
            return False
        if not self._open_file(path):
            self._error(self.tr("The project could not be opened. Check that .lbrn2 files are associated with "
                                "LightBurn (right-click a .lbrn2 file → Open with → LightBurn, \"Always\").\n\n{path}")
                        .format(path=path))
            return False
        self.statusBar().showMessage(self.tr("Opening in LightBurn: {name}").format(name=path.name), 5000)
        return True

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

    # ====================================================================== nastavení
    def show_settings(self, page: str = "general") -> None:
        """Modální okno Nastavení (OK / Zrušit / Použít)."""
        from .settings_dialog import SettingsDialog

        dlg = SettingsDialog(self)
        dlg.show_page(page)
        self._exec_dialog(dlg)

    def _exec_dialog(self, dlg) -> int:
        return dlg.exec()

    def apply_settings(self, values: dict) -> None:
        """Použije hodnoty z okna Nastavení; mění jen to, co se liší od uloženého."""
        s = self.settings
        if values["language"] != s.language():
            self.set_language(values["language"])
        if values["theme"] != s.theme():
            self.set_theme(values["theme"])
        if values["units"] != s.units():
            self.set_units(values["units"])
        if values["panel_side"] != s.panel_side():
            self.set_panel_side(values["panel_side"])
        if values["protocol"] != s.protocol_mode():
            s.set_protocol_mode(values["protocol"])
        if values["update_auto"] != s.update_auto():
            s.set_update_auto(values["update_auto"])
        if values["update_pre"] != s.update_prerelease():
            s.set_update_prerelease(values["update_pre"])

    # ====================================================================== jazyk, nápověda
    def set_language(self, key: str) -> None:
        self.settings.set_language(key)
        self.locale_mgr.apply(key)
        self._apply_number_locale()
        self.retranslate()
        self.recompute()
        if getattr(self, "_help", None) is not None:
            self._help.set_language(self.locale_mgr.current)

    def set_theme(self, key: str) -> None:
        self.settings.set_theme(key)
        self._apply_theme(key)
        if self.project is not None:
            self.recompute()

    def _apply_theme(self, key: str) -> None:
        # Náhled desky zůstává vždy světlý (i v tmavém vzhledu) — rozhodnutí vlastníka.
        self._theme_busy = True
        try:
            self.is_dark = apply_theme(QApplication.instance(), key)
            self._refresh_icons()  # barva ikon podle vzhledu
            self._apply_section_style()
        finally:
            self._theme_busy = False

    def _apply_section_style(self) -> None:
        pal = QApplication.palette()
        c = lambda role: pal.color(role)  # noqa: E731
        window, text = c(QPalette.ColorRole.Window), c(QPalette.ColorRole.WindowText)
        header_bg = window.darker(108) if not self.is_dark else window.lighter(135)
        body_bg = window.lighter(103) if not self.is_dark else window.lighter(112)
        self.centralWidget().setStyleSheet(section_stylesheet(
            window.name(), text.name(), c(QPalette.ColorRole.Mid).name() if self.is_dark else window.darker(118).name(),
            c(QPalette.ColorRole.Highlight).name(), header_bg.name(), body_bg.name()))
        self._fit_left_panel()  # tučné hlavičky mění potřebnou šířku

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
