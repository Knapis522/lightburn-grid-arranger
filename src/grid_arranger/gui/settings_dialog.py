"""Modální okno Nastavení (spec. v1.20).

Nastavení aplikace (ne rozložení) jsou rozdělená do stránek — vlevo seznam stránek, vpravo jejich
obsah — aby s přibývajícími volbami nevznikalo dlouhé menu. Změny se projeví tlačítkem **OK**
nebo **Použít**; **Zrušit** okno zavře beze změny. Nová volba = nové pole na příslušné stránce
(nebo nová stránka v ``_build``), hodnota v ``values()`` a její použití v ``MainWindow.apply_settings``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QRadioButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..version import display_version
from .i18n import NATIVE_NAMES
from .settings import LANGUAGES, ORIGINS, PANEL_SIDES, PROTOCOL_MODES, THEMES, UNIT_KEYS, BoardPreset, LaserProfile
from .widgets import UNITS, LengthSpin

if TYPE_CHECKING:
    from .main_window import MainWindow

PAGES = ("general", "lasers", "saving", "updates")


class SettingsDialog(QDialog):
    def __init__(self, win: MainWindow) -> None:
        super().__init__(win)
        self.win = win
        self.setModal(True)
        self._build()
        self.retranslate()
        self.load()
        self.resize(720, 440)

    # ====================================================================== stavba
    def _build(self) -> None:
        self.pages = QListWidget()
        self.pages.setMaximumWidth(180)
        self.stack = QStackedWidget()
        for _ in PAGES:
            self.pages.addItem("")
        self.pages.currentRowChanged.connect(self.stack.setCurrentIndex)

        # --- Obecné: jazyk, vzhled, jednotky, strana panelu
        general = QWidget()
        form = QFormLayout(general)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.FieldsStayAtSizeHint)
        self.combo_lang, self.combo_theme, self.combo_units, self.combo_panel = (QComboBox() for _ in range(4))
        for combo, keys in ((self.combo_lang, LANGUAGES), (self.combo_theme, THEMES), (self.combo_units, UNIT_KEYS),
                            (self.combo_panel, PANEL_SIDES)):
            for k in keys:
                combo.addItem("", k)
            combo.currentIndexChanged.connect(self._sync_buttons)
        self.lbls_general = [QLabel() for _ in range(4)]
        for lbl, combo in zip(self.lbls_general, (self.combo_lang, self.combo_theme, self.combo_units, self.combo_panel)):
            lbl.setBuddy(combo)
            form.addRow(lbl, combo)
        self.lbl_units_note = QLabel()
        self.lbl_units_note.setWordWrap(True)
        form.addRow(self.lbl_units_note)
        self.stack.addWidget(general)

        # --- Lasery: katalog (název jako v LightBurnu, roh počátku, deska s okraji)
        lasers = QWidget()
        lv = QVBoxLayout(lasers)
        self.lbl_lasers_note = QLabel()
        self.lbl_lasers_note.setWordWrap(True)
        lv.addWidget(self.lbl_lasers_note)
        self.list_lasers = QListWidget()
        self.list_lasers.itemDoubleClicked.connect(lambda _it: self.edit_laser())
        self.list_lasers.currentRowChanged.connect(lambda _r: self._sync_laser_buttons())
        lv.addWidget(self.list_lasers, 1)
        row = QHBoxLayout()
        self.btn_laser_add, self.btn_laser_edit, self.btn_laser_remove = QPushButton(), QPushButton(), QPushButton()
        self.btn_laser_add.clicked.connect(self.add_laser)
        self.btn_laser_edit.clicked.connect(self.edit_laser)
        self.btn_laser_remove.clicked.connect(self.remove_laser)
        for b in (self.btn_laser_add, self.btn_laser_edit, self.btn_laser_remove):
            row.addWidget(b)
        row.addStretch(1)
        lv.addLayout(row)
        self._lasers: list[LaserProfile] = []
        self.stack.addWidget(lasers)

        # --- Uložení: protokol
        saving = QWidget()
        sv = QVBoxLayout(saving)
        self.box_protocol = QGroupBox()
        pv = QVBoxLayout(self.box_protocol)
        self.protocol_group = QButtonGroup(self)
        self.protocol_radios: dict[str, QRadioButton] = {}
        for k in PROTOCOL_MODES:
            r = QRadioButton()
            self.protocol_group.addButton(r)
            self.protocol_radios[k] = r
            pv.addWidget(r)
            r.toggled.connect(self._sync_buttons)
        self.lbl_protocol_note = QLabel()
        self.lbl_protocol_note.setWordWrap(True)
        pv.addWidget(self.lbl_protocol_note)
        self.btn_protocols = QPushButton()
        self.btn_protocols.clicked.connect(self.win.open_protocol_folder)
        row = QHBoxLayout()
        row.addWidget(self.btn_protocols)
        row.addStretch(1)
        pv.addLayout(row)
        sv.addWidget(self.box_protocol)
        sv.addStretch(1)
        self.stack.addWidget(saving)

        # --- Aktualizace
        updates = QWidget()
        uv = QVBoxLayout(updates)
        self.chk_update_auto = QCheckBox()
        self.chk_update_pre = QCheckBox()
        for c in (self.chk_update_auto, self.chk_update_pre):
            c.toggled.connect(self._sync_buttons)
            uv.addWidget(c)
        self.lbl_version = QLabel()
        uv.addWidget(self.lbl_version)
        self.btn_check = QPushButton()
        self.btn_check.clicked.connect(self.check_updates)
        row = QHBoxLayout()
        row.addWidget(self.btn_check)
        row.addStretch(1)
        uv.addLayout(row)
        uv.addStretch(1)
        self.stack.addWidget(updates)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
                                        | QDialogButtonBox.StandardButton.Apply | QDialogButtonBox.StandardButton.Help)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply)
        self.buttons.helpRequested.connect(lambda: self.win.show_help("about"))

        body = QHBoxLayout()
        body.addWidget(self.pages)
        body.addWidget(self.stack, 1)
        main = QVBoxLayout(self)
        main.addLayout(body, 1)
        main.addWidget(self.buttons)
        self.pages.setCurrentRow(0)

    # ====================================================================== texty
    def retranslate(self) -> None:
        self.setWindowTitle(self.tr("Settings"))
        if getattr(self, "_applied", False):
            # po Použít už nejde nic „zrušit“ — použité změny platí; tlačítko jen zavře okno
            self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(self.tr("Close"))
        for i, t in enumerate((self.tr("General"), self.tr("Lasers"), self.tr("Saving"), self.tr("Updates"))):
            self.pages.item(i).setText(t)
        self.lbl_lasers_note.setText(self.tr(
            "Lasers you prepare projects for. Lasers from opened projects are added automatically. The name must "
            "match the device name in LightBurn; the board is offered when the laser is selected."))
        self.btn_laser_add.setText(self.tr("Add…"))
        self.btn_laser_edit.setText(self.tr("Edit…"))
        self.btn_laser_remove.setText(self.tr("Remove"))
        self._show_lasers()
        for lbl, t in zip(self.lbls_general, (self.tr("Language:"), self.tr("Appearance:"), self.tr("Units:"),
                                              self.tr("Layout panel:"))):
            lbl.setText(t)
        self._texts(self.combo_lang, [self.tr("Automatic (system)"), NATIVE_NAMES["cs"], NATIVE_NAMES["en"]])
        self._texts(self.combo_theme, [self.tr("Automatic (system)"), self.tr("Light"), self.tr("Dark")])
        self._texts(self.combo_units, [self.tr("Millimetres (mm)"), self.tr("Inches (in)")])
        self._texts(self.combo_panel, [self.tr("Left of the preview"), self.tr("Right of the preview")])
        self.combo_panel.setToolTip(self.tr("Side of the window with the Project, Items, Grid, Placement and Board sections."))
        self.lbl_units_note.setText(self.tr("Units change only how values are shown and entered; the calculation "
                                            "and the saved project always use millimetres."))
        self.box_protocol.setTitle(self.tr("Save protocol"))
        self.protocol_radios["none"].setText(self.tr("Do not save"))
        self.protocol_radios["beside"].setText(self.tr("Next to the saved project"))
        self.protocol_radios["appdata"].setText(self.tr("In the application's protocol folder"))
        self.lbl_protocol_note.setText(self.tr("A record (.json) of what the output was made from and how — useful "
                                               "for tracing or reporting a problem. It contains no artwork or texts."))
        self.btn_protocols.setText(self.tr("Open protocol folder"))
        self.chk_update_auto.setText(self.tr("Check for updates &automatically"))
        self.chk_update_pre.setText(self.tr("Include &pre-release versions"))
        self.lbl_version.setText(self.tr("Installed version: {version}").format(version=display_version()))
        self.btn_check.setText(self.tr("Check for &updates…"))

    @staticmethod
    def _texts(combo: QComboBox, texts: list[str]) -> None:
        for i, t in enumerate(texts):
            combo.setItemText(i, t)

    def changeEvent(self, event) -> None:  # noqa: N802
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslate()
        super().changeEvent(event)

    # ====================================================================== hodnoty
    def current(self) -> dict:
        s = self.win.settings
        return {"language": s.language(), "theme": s.theme(), "units": s.units(), "panel_side": s.panel_side(),
                "protocol": s.protocol_mode(), "update_auto": s.update_auto(), "update_pre": s.update_prerelease(),
                "lasers": tuple(s.lasers())}

    def load(self) -> None:
        v = self.current()
        for combo, key in ((self.combo_lang, "language"), (self.combo_theme, "theme"), (self.combo_units, "units"),
                           (self.combo_panel, "panel_side")):
            combo.setCurrentIndex(combo.findData(v[key]))
        self.protocol_radios[v["protocol"]].setChecked(True)
        self.chk_update_auto.setChecked(v["update_auto"])
        self.chk_update_pre.setChecked(v["update_pre"])
        self._lasers = list(v["lasers"])
        self._show_lasers()
        self._sync_buttons()

    def values(self) -> dict:
        protocol = next((k for k, r in self.protocol_radios.items() if r.isChecked()), PROTOCOL_MODES[0])
        return {"language": self.combo_lang.currentData(), "theme": self.combo_theme.currentData(),
                "units": self.combo_units.currentData(), "panel_side": self.combo_panel.currentData(),
                "protocol": protocol, "update_auto": self.chk_update_auto.isChecked(),
                "update_pre": self.chk_update_pre.isChecked(), "lasers": tuple(self._lasers)}

    def _sync_buttons(self, *_args) -> None:
        if not hasattr(self, "buttons"):
            return
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).setEnabled(self.values() != self.current())

    def apply(self) -> None:
        self.win.apply_settings(self.values())
        self._applied = True
        self.retranslate()  # po změně jazyka hned (událost LanguageChange přijde až později)
        self._sync_buttons()

    def accept(self) -> None:
        self.apply()
        super().accept()

    # ====================================================================== katalog laserů
    def origin_text(self, origin: str) -> str:
        return {"top_left": self.tr("top left"), "top_right": self.tr("top right"),
                "bottom_left": self.tr("bottom left"), "bottom_right": self.tr("bottom right")}.get(origin, origin)

    def _show_lasers(self) -> None:
        if not hasattr(self, "list_lasers"):
            return
        row = self.list_lasers.currentRow()
        self.list_lasers.clear()
        unit = UNITS[self.win.settings.units()]
        for p in self._lasers:
            text = f"{p.name} — " + self.tr("origin {origin}").format(origin=self.origin_text(p.origin))
            if p.board is not None:
                text += f", {self.win.locale_mgr.qlocale().toString(unit.to_display(p.board.width), 'f', unit.decimals - 1)} × " \
                        f"{self.win.locale_mgr.qlocale().toString(unit.to_display(p.board.height), 'f', unit.decimals - 1)} {unit.suffix}"
            self.list_lasers.addItem(text)
        self.list_lasers.setCurrentRow(min(row, self.list_lasers.count() - 1))
        self._sync_laser_buttons()

    def _sync_laser_buttons(self) -> None:
        has = 0 <= self.list_lasers.currentRow() < len(self._lasers)
        self.btn_laser_edit.setEnabled(has)
        self.btn_laser_remove.setEnabled(has)

    def _ask_laser(self, profile: LaserProfile | None) -> LaserProfile | None:
        dlg = LaserDialog(self, profile, UNITS[self.win.settings.units()], {p.name for p in self._lasers})
        return dlg.result_profile() if dlg.exec() == QDialog.DialogCode.Accepted else None

    def add_laser(self) -> None:
        p = self._ask_laser(None)
        if p is not None:
            self._lasers = sorted([*self._lasers, p], key=lambda x: x.name.casefold())
            self._show_lasers()
            self.list_lasers.setCurrentRow(self._lasers.index(p))
            self._sync_buttons()

    def edit_laser(self) -> None:
        r = self.list_lasers.currentRow()
        if not 0 <= r < len(self._lasers):
            return
        p = self._ask_laser(self._lasers[r])
        if p is not None:
            rest = [x for i, x in enumerate(self._lasers) if i != r]
            self._lasers = sorted([*rest, p], key=lambda x: x.name.casefold())
            self._show_lasers()
            self._sync_buttons()

    def remove_laser(self) -> None:
        r = self.list_lasers.currentRow()
        if 0 <= r < len(self._lasers):
            del self._lasers[r]
            self._show_lasers()
            self._sync_buttons()

    def check_updates(self) -> None:
        """Zkontrolovat aktualizace — s volbami zaškrtnutými v okně (nejdřív je použije)."""
        self.apply()
        self.win.updates.check(manual=True)

    def show_page(self, key: str) -> None:
        self.pages.setCurrentRow(PAGES.index(key))
        self.stack.setCurrentIndex(PAGES.index(key))
        self.pages.setFocus(Qt.FocusReason.OtherFocusReason)


class LaserDialog(QDialog):
    """Přidání / úprava laseru v katalogu: název (jako v LightBurnu), roh počátku, deska a okraje."""

    def __init__(self, parent: SettingsDialog, profile: LaserProfile | None, unit, taken: set[str]) -> None:
        super().__init__(parent)
        self.setModal(True)
        self._taken = taken - ({profile.name} if profile else set())
        board = profile.board if profile and profile.board else BoardPreset(600.0, 400.0)
        form = QFormLayout(self)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)  # název přes celou šířku
        self.edit_name = QLineEdit(profile.name if profile else "")
        # i delší názvy zařízení („Červený Ruida 6445S – dílna 2“) celé viditelné
        self.edit_name.setMinimumWidth(self.edit_name.fontMetrics().horizontalAdvance("M" * 24))
        self.combo_origin = QComboBox()
        for o in ORIGINS:
            self.combo_origin.addItem(parent.origin_text(o), o)
        self.combo_origin.setCurrentIndex(ORIGINS.index(profile.origin) if profile else 0)
        self.spins = [LengthSpin(1.0, 10000.0, board.width, unit), LengthSpin(1.0, 10000.0, board.height, unit)]
        self.spins += [LengthSpin(0.0, 1000.0, m, unit) for m in board.margins]
        labels = [self.tr("Name in LightBurn:"), self.tr("Laser origin:"), self.tr("Board width:"), self.tr("Board height:"),
                  self.tr("Margin left:"), self.tr("Margin right:"), self.tr("Margin top:"), self.tr("Margin bottom:")]
        for lbl, w in zip(labels, [self.edit_name, self.combo_origin, *self.spins]):
            form.addRow(lbl, w)
        self.lbl_error = QLabel()
        self.lbl_error.setStyleSheet("color: #b3261e")
        form.addRow(self.lbl_error)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        form.addRow(self.buttons)
        self.edit_name.textChanged.connect(self._validate)
        self.setWindowTitle(self.tr("Edit laser") if profile else self.tr("Add laser"))
        self.setMinimumWidth(520)
        self._validate()

    def _validate(self) -> None:
        name = self.edit_name.text().strip()
        err = ""
        if not name:
            err = self.tr("Enter the laser name as shown in LightBurn.")
        elif name in self._taken:
            err = self.tr("A laser with this name is already in the catalogue.")
        self.lbl_error.setText(err)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(not err)

    def result_profile(self) -> LaserProfile:
        mm = [s.mm() for s in self.spins]
        return LaserProfile(self.edit_name.text().strip(), self.combo_origin.currentData(),
                            BoardPreset(mm[0], mm[1], tuple(mm[2:])))  # type: ignore[arg-type]
