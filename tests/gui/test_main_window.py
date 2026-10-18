"""MVP-06 (GUI-00) — obsluha okna nad syntetickými projekty (offscreen)."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from tests.integration.lbrn2_builder import Group, card, project, rect


def write(tmp_path, data, name="karty.lbrn2"):
    p = tmp_path / name
    p.write_bytes(data)
    return p


def four(mirror_x=True):
    return project([card(10, 20, text="A"), card(300, 400, text="B"), card(-50, 700, 80, 50, text="C"), card(900, -100, text="D")], mirror_x=mirror_x)


def test_open_project_lists_items_and_laser(make_window, tmp_path):
    w = make_window("en")
    assert w.open_project(write(tmp_path, four()))
    assert w.list_items.count() == 4
    assert w.order == ("G1", "G2", "G3", "G4")
    assert "Syntetický laser" in w.lbl_device.text() and "top right" in w.lbl_device.text()
    assert w.act_save.isEnabled()


def test_save_disabled_without_project(make_window):
    w = make_window("en")
    assert not w.act_save.isEnabled()
    assert w.save_new_project(confirm=False) is None


def test_t_mvp05_09_uncheck_and_recheck_goes_to_end(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    li = next(w.list_items.item(i) for i in range(w.list_items.count()) if w.list_items.item(i).data(Qt.ItemDataRole.UserRole) == "G2")
    li.setCheckState(Qt.CheckState.Unchecked)
    assert w.order == ("G1", "G3", "G4")
    assert {p.item_id for p in w.plan.layout.placements} == {"G1", "G3", "G4"}
    li = next(w.list_items.item(i) for i in range(w.list_items.count()) if w.list_items.item(i).data(Qt.ItemDataRole.UserRole) == "G2")
    li.setCheckState(Qt.CheckState.Checked)
    assert w.order == ("G1", "G3", "G4", "G2")


def test_t_mvp08_10_move_and_reset_order(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    w.list_items.setCurrentRow(3)  # G4
    for _ in range(3):
        w._move(-1)
    assert w.order == ("G4", "G1", "G2", "G3")
    assert w.plan.layout.placements[0].item_id == "G4"
    w._reset_order()
    assert w.order == ("G1", "G2", "G3", "G4")


def test_t_mvp06_empty_selection_blocks_save(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    w._select_none()
    assert not w.act_save.isEnabled()
    assert any("Select at least one item" in t for t in w.issues())
    w._select_all()
    assert w.act_save.isEnabled() and len(w.order) == 4


def test_t_mvp11_overrun_blocks_save_and_names_item(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    w.spin_bw.setValue(150)
    assert not w.act_save.isEnabled()
    assert any("extends beyond the usable board area" in t for t in w.issues())


def test_blocked_item_is_disabled_with_reason(make_window, tmp_path):
    w = make_window("en")
    bad = Group([rect(0, 0, 100, 60, prims="L0 1L1 2L2 3")])
    w.open_project(write(tmp_path, project([card(10, 20), bad])))
    li = w.list_items.item(w.list_items.count() - 1)
    assert not (li.flags() & Qt.ItemFlag.ItemIsEnabled)
    assert "No closed cut outline" in li.toolTip()
    assert w.order == ("G1",)


def test_save_creates_new_file_and_reports(make_window, tmp_path):
    w = make_window("en")
    src = write(tmp_path, four())
    before = src.read_bytes()
    out = w.save_new_project(confirm=False)
    assert out is None  # žádný projekt
    w.open_project(src)
    out = w.save_new_project(confirm=True)
    assert out is not None and out.name == "karty__grid_001.lbrn2" and out.exists()
    assert src.read_bytes() == before
    kinds = [k for k, _ in w._dialogs]
    assert kinds == ["save_as", "info"]
    assert w._dialogs[0][1] == str(tmp_path / "karty__grid_001.lbrn2")  # návrh názvu vedle originálu
    assert "File → Open" in w._dialogs[-1][1]


def test_legacy_file_shows_localized_error(make_window, tmp_path):
    w = make_window("cs")
    assert not w.open_project(write(tmp_path, b"x", name="stary.lbrn"))
    assert w._dialogs[-1] == ("error", "Tato aplikace podporuje pouze projekty .lbrn2. Uložte projekt v LightBurnu ve formátu .lbrn2.")


def test_manual_anchor_enables_corner_fields(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    assert not w.spin_start_x.isEnabled()
    w.combo_anchor.setCurrentIndex(w.combo_anchor.findData("manual"))
    assert w.spin_start_x.isEnabled()
    w.spin_start_x.setValue(20)
    w.spin_start_y.setValue(30)
    assert w.plan.origin_corner_lightburn == (20, 30)


def test_board_prefill_and_save_default_per_laser(make_window, tmp_path, settings):
    from grid_arranger.gui.settings import BoardPreset

    settings.set_board_for("Syntetický laser", BoardPreset(640, 420, (2, 3, 4, 5)))
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    assert (w.spin_bw.value(), w.spin_bh.value(), w.spin_ml.value(), w.spin_mb.value()) == (640, 420, 2, 5)
    w.spin_bw.setValue(800)
    w.save_board_default()
    assert settings.board_for("Syntetický laser").width == 800


def test_owner_default_boards():
    from grid_arranger.gui.settings import DEFAULT_BOARDS

    assert DEFAULT_BOARDS["Červený Ruida 6445S"] == (700.0, 500.0)
    assert DEFAULT_BOARDS["Modrý Ruida 643XG"] == (500.0, 400.0)


def test_corrupt_board_setting_is_ignored(settings):
    settings._s.setValue("boards/X/width", "abc")
    settings._s.setValue("boards/X/height", "1")
    assert settings.board_for("X") is None


def _center(w, iid):
    return w.preview._rects[iid].center()


def test_drag_in_preview_moves_item_to_target_place(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    v = w.preview
    assert v.start_drag(_center(w, "G4"))
    v.drag_to(_center(w, "G2"))
    assert v._drop_marker.isVisible()
    v.finish_drag(_center(w, "G2"))
    assert w.order == ("G1", "G4", "G3", "G2")  # G4 a G2 si prohodily místa, ostatní zůstaly
    rows = [w.list_items.item(i).data(Qt.ItemDataRole.UserRole) for i in range(4)]
    assert rows == ["G1", "G4", "G3", "G2"]  # seznam se přečísloval
    assert w.plan.layout.placement_for("G4").index == 1
    assert w.plan.layout.placement_for("G2").index == 3


def test_drag_to_empty_space_restores_position(make_window, tmp_path):
    from PySide6.QtCore import QPointF

    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    v = w.preview
    before = [g.pos() for g in v._graphics["G1"]]
    v.start_drag(_center(w, "G1"))
    v.drag_to(QPointF(-5000, -5000))
    v.finish_drag(QPointF(-5000, -5000))
    assert [g.pos() for g in v._graphics["G1"]] == before
    assert w.order == ("G1", "G2", "G3", "G4")


def test_drag_with_real_mouse_events(make_window, tmp_path):
    from PySide6.QtCore import QEvent, QPointF
    from PySide6.QtGui import QMouseEvent

    w = make_window("en")
    w.resize(1200, 800)
    w.show()
    w.open_project(write(tmp_path, four()))
    v = w.preview
    v.fit()

    def ev(kind, scene_pt, buttons):
        local = QPointF(v.mapFromScene(scene_pt))
        return QMouseEvent(kind, local, v.viewport().mapToGlobal(local), Qt.MouseButton.LeftButton, buttons, Qt.KeyboardModifier.NoModifier)

    a, b = _center(w, "G3"), _center(w, "G1")
    v.mousePressEvent(ev(QEvent.Type.MouseButtonPress, a, Qt.MouseButton.LeftButton))
    v.mouseMoveEvent(ev(QEvent.Type.MouseMove, b, Qt.MouseButton.LeftButton))
    v.mouseReleaseEvent(ev(QEvent.Type.MouseButtonRelease, b, Qt.MouseButton.NoButton))
    assert w.order == ("G3", "G2", "G1", "G4")
    assert v.dragMode() == v.DragMode.ScrollHandDrag


def test_theme_dark_light_and_persistence(make_window, settings, qapp):
    from PySide6.QtGui import QPalette

    w = make_window("en")
    try:
        w.set_theme("dark")
        assert settings.theme() == "dark" and w.theme_actions["dark"].isChecked() and w.is_dark
        assert qapp.palette().color(QPalette.ColorRole.Window).lightness() < 80  # tmavé ovládání
        assert w.preview.backgroundBrush().color().lightness() > 200  # náhled desky zůstává světlý
        w.set_theme("light")
        assert not w.is_dark
        for role in (QPalette.ColorRole.Window, QPalette.ColorRole.Base, QPalette.ColorRole.Button):
            assert qapp.palette().color(role).lightness() > 200  # celá aplikace světlá
        assert qapp.palette().color(QPalette.ColorRole.Text).lightness() < 50
        w.set_theme("auto")
        assert settings.theme() == "auto"
    finally:
        w.set_theme("light")
        settings.set_theme("auto")


def test_invalid_theme_setting_falls_back(settings):
    import pytest

    settings._s.setValue("ui/theme", "neon")
    assert settings.theme() == "auto"
    with pytest.raises(ValueError):
        settings.set_theme("neon")


def _wheel(view, delta):
    from PySide6.QtCore import QPoint, QPointF
    from PySide6.QtGui import QWheelEvent

    c = QPointF(view.viewport().rect().center())
    ev = QWheelEvent(c, QPointF(view.viewport().mapToGlobal(c.toPoint())), QPoint(0, 0), QPoint(0, delta),
                     Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
    view.wheelEvent(ev)


def test_zoom_is_proportional_and_limited(make_window, tmp_path):
    w = make_window("en")
    w.resize(1200, 800)
    w.show()
    w.open_project(write(tmp_path, four()))
    v = w.preview
    v.fit()
    base = v.transform().m11()
    _wheel(v, 120)
    assert v.transform().m11() / base == pytest.approx(1.0015 ** 120, rel=1e-6)  # jeden zub ≈ 20 %
    v.fit()
    _wheel(v, 8)  # touchpad: malý krok = malá změna
    assert 1.0 < v.transform().m11() / base < 1.02
    for _ in range(200):
        _wheel(v, 120)
    assert v.transform().m11() / base == pytest.approx(v.MAX_ZOOM, rel=1e-6)
    for _ in range(400):
        _wheel(v, -120)
    assert v.transform().m11() / base == pytest.approx(v.MIN_ZOOM, rel=1e-6)


def test_scene_rect_does_not_grow_after_drag_far_away(make_window, tmp_path):
    from PySide6.QtCore import QPointF

    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    v = w.preview
    before = v.sceneRect()
    v.start_drag(_center(w, "G1"))
    v.drag_to(QPointF(-50000, -50000))
    v.finish_drag(QPointF(-50000, -50000))
    w.recompute()
    assert v.sceneRect() == before


def test_parameter_change_keeps_user_zoom(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    v = w.preview
    _wheel(v, 360)
    z = v.transform().m11()
    w.spin_gap_x.setValue(7)
    assert v.transform().m11() == pytest.approx(z)


def test_title_shows_project_like_lightburn(make_window, tmp_path):
    from grid_arranger.version import display_version

    w = make_window("en")
    assert w.windowTitle() == f"Grid Arranger for LightBurn {display_version()}"
    w.open_project(write(tmp_path, four(), name="Zakázka 12.lbrn2"))
    assert w.windowTitle() == f"Grid Arranger for LightBurn {display_version()} - Zakázka 12.lbrn2"
    w.set_language("cs")
    assert w.windowTitle().endswith(" - Zakázka 12.lbrn2")  # přepnutí jazyka název neztratí
    assert w.app_title() == "Grid Arranger for LightBurn"


def test_toolbar_open_save_help_with_icons(make_window, tmp_path):
    w = make_window("en")
    acts = [a for a in w.toolbar.actions() if not a.isSeparator()]
    assert acts == [w.act_open, w.act_save, w.act_open_in_lb, w.act_undo, w.act_redo, w.act_duplicate, w.act_fit,
                    w.act_help]
    assert w.act_fit.toolTip().startswith("Fit view (Ctrl+0)\n")
    assert all(not a.icon().isNull() for a in acts)
    assert w.act_open.toolTip().startswith("Open project (Ctrl+O)")
    assert not w.act_save.isEnabled()  # bez projektu nelze uložit — i na liště
    w.open_project(write(tmp_path, four()))
    assert w.act_save.isEnabled()


def test_toolbar_icons_follow_theme(make_window, settings):
    from PySide6.QtGui import QColor

    def darkest_pixel_lightness(act):
        img = act.icon().pixmap(24, 24).toImage()
        vals = [QColor(img.pixel(x, y)).lightness() for x in range(24) for y in range(24) if QColor.fromRgba(img.pixel(x, y)).alpha() > 200]
        return min(vals), max(vals)

    w = make_window("en")
    try:
        w.set_theme("light")
        assert darkest_pixel_lightness(w.act_open)[1] < 60  # tmavé ikony na světlé liště
        w.set_theme("dark")
        assert darkest_pixel_lightness(w.act_open)[0] > 180  # světlé ikony na tmavé liště
    finally:
        w.set_theme("light")
        settings.set_theme("auto")


def test_save_to_chosen_folder_and_name(make_window, tmp_path):
    w = make_window("en")
    src = write(tmp_path, four())
    before = src.read_bytes()
    w.open_project(src)
    other = tmp_path / "zakazky"
    other.mkdir()
    w._save_answers = [other / "Deska 1"]  # bez přípony → doplní se .lbrn2
    out = w.save_new_project()
    assert out == other / "Deska 1.lbrn2" and out.exists()
    assert not list(other.glob("*.json"))  # výchozí: protokol se neukládá
    assert "Protocol" not in w._dialogs[-1][1]
    assert src.read_bytes() == before


def test_save_never_overwrites_and_asks_again(make_window, tmp_path):
    w = make_window("en")
    src = write(tmp_path, four())
    before = src.read_bytes()
    w.open_project(src)
    existing = tmp_path / "hotovo.lbrn2"
    existing.write_bytes(b"keep me")
    w._save_answers = [existing, src, tmp_path / "novy.lbrn2"]
    out = w.save_new_project()
    assert out == tmp_path / "novy.lbrn2"
    assert existing.read_bytes() == b"keep me" and src.read_bytes() == before
    kinds = [k for k, _ in w._dialogs]
    assert kinds == ["save_as", "error", "save_as", "error", "save_as", "info"]
    assert "never overwrites" in w._dialogs[1][1] and "overwrite the original" in w._dialogs[3][1]


def test_save_cancelled_writes_nothing(make_window, tmp_path):
    w = make_window("en")
    src = write(tmp_path, four())
    w.open_project(src)
    w._ask_save_path = lambda proposal: None
    assert w.save_new_project() is None
    assert not list(tmp_path.glob("*__grid_*")) and not list(tmp_path.glob("*.json"))


def test_protocol_modes(make_window, tmp_path, monkeypatch):
    from grid_arranger.gui.main_window import MainWindow

    w = make_window("en")
    assert w.settings.protocol_mode() == "none" and w.protocol_actions["none"].isChecked()
    src = write(tmp_path, four())
    w.open_project(src)

    w.protocol_actions["beside"].trigger()
    assert w.settings.protocol_mode() == "beside"
    out = w.save_new_project()
    assert out.with_suffix(".json").exists() and "Protocol" in w._dialogs[-1][1]
    clash = tmp_path / "jiny.lbrn2"
    clash.with_suffix(".json").write_text("{}")
    w._save_answers = [clash, tmp_path / "treti.lbrn2"]
    assert w.save_new_project() == tmp_path / "treti.lbrn2"  # existující protokol se nepřepíše → jiný název
    assert clash.with_suffix(".json").read_text() == "{}"

    folder = tmp_path / "appdata" / "protocols"
    monkeypatch.setattr(MainWindow, "protocol_folder", staticmethod(lambda: folder))
    w.protocol_actions["appdata"].trigger()
    w._save_answers = [tmp_path / "a.lbrn2"]
    w.save_new_project()
    (tmp_path / "x").mkdir()
    w._save_answers = [tmp_path / "x" / "a.lbrn2"]  # stejný název z jiné složky → a_2.json, nic se nepřepíše
    w.save_new_project()
    assert sorted(p.name for p in folder.iterdir()) == ["a.json", "a_2.json"]
    assert not (tmp_path / "a.json").exists()


def test_invalid_protocol_setting_falls_back(settings):
    settings._s.setValue("save/protocol", "everywhere")
    assert settings.protocol_mode() == "none"
    with pytest.raises(ValueError):
        settings.set_protocol_mode("everywhere")


def test_units_inches_display_only_no_drift(make_window, tmp_path, settings):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    before = w.params()
    w.unit_actions["in"].trigger()
    assert settings.units() == "in"
    assert w.spin_bw.suffix() == " in" and w.spin_bw.value() == pytest.approx(700 / 25.4, abs=0.0005)
    assert " in." in w.lbl_summary.text() and " in" in w.list_items.item(0).text()
    assert w.params() == before  # výpočet dál v mm, přepnutí nic nezmění
    w.spin_gap_x.setValue(0.25)  # uživatel zadá palce
    assert w.spin_gap_x.mm() == pytest.approx(6.35) and w.params().gap_x == pytest.approx(6.35)
    for _ in range(5):  # opakované přepínání nemění hodnoty (žádné zaokrouhlovací posuny)
        w.set_units("mm")
        w.set_units("in")
    assert w.spin_gap_x.mm() == pytest.approx(6.35) and w.spin_bw.mm() == 700
    w.set_units("mm")
    assert w.spin_gap_x.value() == pytest.approx(6.35) and w.spin_bw.suffix() == " mm"
    settings.set_units("mm")


def test_saved_board_and_preset_stay_in_mm_with_inches(make_window, tmp_path, settings):
    from grid_arranger.gui.settings import BoardPreset

    settings.set_board_for("Syntetický laser", BoardPreset(508, 254, (5, 5, 5, 5)))
    settings.set_units("in")
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    assert w.spin_bw.value() == pytest.approx(20.0) and w.spin_bw.mm() == 508
    w.save_board_default()
    assert settings.board_for("Syntetický laser").width == 508
    settings.set_units("mm")


def test_compact_fields_and_collapsible_sections(make_window, settings):
    w = make_window("en")
    # pole na 0000,00 mm, ne přes celou šířku — měřeno písmem systému (Windows má jiné písmo a DPI než Linux)
    for sp in w.length_spins:
        assert sp.width() <= sp.fontMetrics().horizontalAdvance("0000,000 mm") + 16
        assert sp.width() < w._left_scroll.minimumWidth() / 2
    assert w.spin_gap_y.parentWidget() is w.spin_gap_x.parentWidget()  # Mezera X a Y na jednom řádku
    assert w._left_scroll.horizontalScrollBarPolicy() == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    assert w.box_board.title() == "Board"
    w.box_items.header.click()
    assert not w.box_items.isExpanded() and settings.section_expanded("items") is False
    w2 = make_window("en")
    assert not w2.box_items.isExpanded()  # stav sekce se pamatuje
    w2.box_items.header.click()
    assert w2.box_items.isExpanded() and settings.section_expanded("items") is True


def test_corner_fields_follow_computed_corner_and_manual_keeps_it(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    assert (w.spin_start_x.mm(), w.spin_start_y.mm()) == pytest.approx(w.plan.origin_corner_lightburn)
    w.spin_ml.setValue(15)
    w.spin_mt.setValue(15)
    w.spin_mr.setValue(15)
    corner = w.plan.origin_corner_lightburn
    assert (w.spin_start_x.mm(), w.spin_start_y.mm()) == pytest.approx(corner)  # zašedlá pole se aktualizují
    w.combo_anchor.setCurrentIndex(w.combo_anchor.findData("center"))
    assert (w.spin_start_x.mm(), w.spin_start_y.mm()) == pytest.approx(w.plan.origin_corner_lightburn)
    center = w.plan.origin_corner_lightburn
    w.combo_anchor.setCurrentIndex(w.combo_anchor.findData("manual"))
    assert w.plan.origin_corner_lightburn == pytest.approx(center)  # přepnutí na Ručně mřížku neposune
    w.spin_ml.setValue(30)
    assert w.plan.origin_corner_lightburn == pytest.approx(center)  # v režimu Ručně platí zadaný roh
    w.spin_start_x.setValue(center[0] + 10)
    assert w.plan.origin_corner_lightburn[0] == pytest.approx(center[0] + 10)


def test_rotation_combo_exceptions_and_list_markers(make_window, tmp_path, settings):
    from tests.integration.test_rotation_plan import tilted

    assert settings.rotation_mode() == "any"  # výchozí volba vlastníka
    w = make_window("en")
    w.open_project(write(tmp_path, project([tilted(0, 0), tilted(300, 0)])))
    assert w.combo_rotation.currentData() == "any"
    assert set(w.plan.rotations) == {"G1", "G2"}
    assert "↻" in w.list_items.item(0).text() or "↺" in w.list_items.item(0).text()
    w.list_items.setCurrentRow(1)
    assert w.btn_norotate.isEnabled() and not w.btn_norotate.isChecked()
    w.btn_norotate.click()
    assert w.manual_angles == {"G2": 0.0} and "G2" not in w.plan.rotations and "(no rotation)" in w.list_items.item(1).text()
    w.combo_rotation.setCurrentIndex(w.combo_rotation.findData("none"))
    assert settings.rotation_mode() == "none" and w.plan.rotations == {}
    settings.set_rotation_mode("any")


def _row(w, iid):
    from PySide6.QtCore import Qt

    return next(w.list_items.item(i) for i in range(w.list_items.count())
                if w.list_items.item(i).data(Qt.ItemDataRole.UserRole) == iid)


def test_click_in_preview_selects_item_and_ctrl_adds(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, project([card(0, 0), card(200, 0), card(0, 200)])))
    w.preview.itemClicked.emit("G2", False)
    assert w.selected_ids() == {"G2"} and w.preview.selection() == {"G2"}
    w.preview.itemClicked.emit("G3", True)
    assert w.selected_ids() == {"G2", "G3"} and w.preview.selection() == {"G2", "G3"}
    w.preview.itemClicked.emit("G2", True)  # Ctrl+klik na vybraný = odebrat
    assert w.selected_ids() == {"G3"}
    w.recompute()  # překreslení výběr zachová
    assert w.preview.selection() == {"G3"}
    from PySide6.QtTest import QTest

    w.show()
    w.activateWindow()
    QTest.qWaitForWindowActive(w, 1000)
    w.preview.setFocus()
    QTest.keyClick(w.preview, Qt.Key.Key_Escape)  # Esc zruší výběr
    assert w.selected_ids() == set() and w.preview.selection() == set()
    assert not w.spin_angle.isEnabled()


def test_click_without_moving_is_selection_not_swap(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, project([card(0, 0), card(200, 0)])))
    order = w.order
    clicked = []
    w.preview.itemClicked.connect(lambda i, a: clicked.append(i))
    r = w.preview._rects["G1"]
    w.preview.start_drag(r.center())
    w.preview.drag_to(r.center())
    w.preview.finish_drag(r.center())
    assert clicked == ["G1"] and w.order == order


def test_manual_angle_buttons_and_auto(make_window, tmp_path):
    from tests.integration.test_rotation_plan import tilted

    w = make_window("en")
    w.combo_rotation.setCurrentIndex(w.combo_rotation.findData("none"))
    w.open_project(write(tmp_path, project([tilted(0, 0), tilted(300, 0), tilted(0, 300)])))
    assert w.plan.rotations == {} and not w.spin_angle.isEnabled()
    w.preview.itemClicked.emit("G1", False)
    w.preview.itemClicked.emit("G3", True)
    assert w.spin_angle.isEnabled() and not w.btn_rot_auto.isEnabled()
    w.btn_rot_cw.click()  # ruční úhel platí i v režimu Nenatáčet
    assert w.plan.rotations == {"G1": 90.0, "G3": 90.0} and w.plan.manual == {"G1", "G3"}
    assert "(manual)" in _row(w, "G1").text() and "(manual)" not in _row(w, "G2").text()
    w.btn_rot_ccw.click()
    w.btn_rot_ccw.click()
    assert w.plan.rotations == {"G1": -90.0, "G3": -90.0}
    w.spin_angle.setValue(-30.0)
    assert w.plan.rotations == {"G1": -30.0, "G3": -30.0} and w.plan.report.can_save
    w.btn_rot_auto.click()
    assert w.manual_angles == {} and w.plan.rotations == {}
    w.btn_rot_ccw.click()
    w.btn_rot_ccw.click()
    w.btn_rot_ccw.click()  # −270° → +90°
    assert w.plan.rotations == {"G1": 90.0, "G3": 90.0}
    w.combo_rotation.setCurrentIndex(w.combo_rotation.findData("any"))


def test_manual_angle_survives_auto_mode_and_is_saved(make_window, tmp_path):
    from grid_arranger.adapters.lightburn.read import load_project

    from tests.integration.test_rotation_plan import tilted

    w = make_window("en")
    w.combo_rotation.setCurrentIndex(w.combo_rotation.findData("any"))
    w.open_project(write(tmp_path, project([tilted(0, 0), tilted(300, 0)])))
    auto = dict(w.plan.rotations)
    w.preview.itemClicked.emit("G2", False)
    w.spin_angle.setValue(auto["G2"] + 180.0 if auto["G2"] <= 0 else auto["G2"] - 180.0)  # otočit vzhůru nohama
    assert w.plan.rotations["G1"] == pytest.approx(auto["G1"])
    assert abs(w.plan.rotations["G2"] - auto["G2"]) == pytest.approx(180.0)
    out = tmp_path / "manual.lbrn2"
    w._save_answers = [out]
    w.save_new_project()
    assert out.exists() and all(it.supported for it in load_project(out).items)


def test_rotated_items_drawn_rotated_in_preview(make_window, tmp_path):
    from tests.integration.test_rotation_plan import tilted

    w = make_window("en")
    w.open_project(write(tmp_path, project([tilted(0, 0)])))
    art = [g for g in w.preview._graphics["G1"] if g.rotation() != 0]
    assert art and art[0].rotation() == pytest.approx(w.plan.rotations["G1"])


def test_fit_on_toolbar_and_artwork_toggle_in_items_header(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    v = w.preview
    v.fit()
    base = v.transform().m11()
    _wheel(v, 360)
    assert v.transform().m11() != pytest.approx(base)
    w.act_fit.trigger()
    assert v.transform().m11() == pytest.approx(base)  # Přizpůsobit z lišty
    assert w.chk_art.parentWidget() is w.box_items.header_bar  # přepínač v hlavičce sekce Výrobky
    w.box_items.setExpanded(False)
    assert w.chk_art.isVisibleTo(w.box_items)  # zůstává vidět i u sbalené sekce
    w.chk_art.setChecked(False)
    assert all(len(g) == 2 for g in w.preview._graphics.values())  # jen obdélník + popisek, bez kresby


def test_check_for_updates_is_also_in_settings_menu(make_window):
    w = make_window("en")
    assert w.act_check_updates in w.menu_updates.actions()
    assert w.act_check_updates in w.menu_help.actions()


def test_copy_paste_and_duplicate_dialog_fill_the_board(make_window, tmp_path):
    from grid_arranger.adapters.lightburn.read import load_project

    w = make_window("en")
    w.combo_rotation.setCurrentIndex(w.combo_rotation.findData("none"))
    w.open_project(write(tmp_path, project([card(0, 0), card(200, 0)])))
    assert not w.act_paste.isEnabled()
    w.preview.itemClicked.emit("G2", False)
    w.act_copy.trigger()
    w.act_paste.trigger()
    assert w.copies == {"G2+1": "G2"} and w.order == ("G1", "G2", "G2+1")
    assert w.selected_ids() == {"G2+1"} and "(copy of G2)" in _row(w, "G2+1").text()
    w._ask_int = lambda *a: 3
    w.preview.itemClicked.emit("G1", False)
    w.act_duplicate.trigger()
    assert w.order == ("G1", "G2", "G2+1", "G1+1", "G1+2", "G1+3")
    assert len(w.plan.layout.placements) == 6 and w.plan.report.can_save
    # odebrat: Delete na vybrané kopii; odškrtnutí kopie ji také odebere
    w._select_ids({"G1+2"})
    w.act_remove_copies.trigger()
    assert "G1+2" not in w.copies and "G1+2" not in w.order
    _row(w, "G1+3").setCheckState(Qt.CheckState.Unchecked)
    assert set(w.copies) == {"G2+1", "G1+1"}
    out = tmp_path / "copies.lbrn2"
    w._save_answers = [out]
    w.save_new_project()
    q = load_project(out)
    assert len(q.items) == 4 and all(it.supported for it in q.items)


def test_copy_inherits_manual_angle_and_new_project_clears_copies(make_window, tmp_path):
    from tests.integration.test_rotation_plan import tilted

    w = make_window("en")
    w.open_project(write(tmp_path, project([tilted(0, 0), tilted(300, 0)])))
    w.preview.itemClicked.emit("G1", False)
    w.spin_angle.setValue(15.0)
    w.act_copy.trigger()
    w.act_paste.trigger()
    assert w.manual_angles["G1+1"] == 15.0 and w.plan.rotations["G1+1"] == 15.0
    w.open_project(write(tmp_path, project([tilted(0, 0)]), "other.lbrn2"))
    assert w.copies == {} and not w.act_paste.isEnabled()


def test_window_size_maximized_state_and_splitter_are_remembered(make_window, settings):
    w = make_window("en")
    w.resize(760, 560)  # offscreen obrazovka má 800 × 600
    w.show()
    w.splitter.setSizes([250, 650])
    w.close()
    geometry = settings.window_geometry()
    assert geometry and settings.window_splitter()
    w2 = make_window("en")
    w2.restore_window_state()
    assert (w2.width(), w2.height()) == (w.width(), w.height())
    w2.show()
    w2.showMaximized()
    w2.close()
    w3 = make_window("en")
    w3.restore_window_state()
    assert w3.windowState() & Qt.WindowState.WindowMaximized


def test_open_saved_project_in_lightburn(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, project([card(0, 0), card(200, 0)])))
    assert not w.act_open_in_lb.isEnabled()
    out = tmp_path / "a.lbrn2"
    w._save_answers = [out]
    w.save_new_project()
    assert w._opened == [] and w.act_open_in_lb.isEnabled()  # v hlášení zvoleno Zavřít
    w.act_open_in_lb.trigger()
    assert w._opened == [out]
    out2 = tmp_path / "b.lbrn2"
    w._save_answers = [out2]
    w._open_in_lb_answer = True  # v hlášení zvoleno Otevřít v LightBurnu
    w.save_new_project()
    assert w._opened[-1] == out2 and w.last_saved == out2
    w._open_file = lambda path: False  # .lbrn2 bez přiřazeného programu
    assert not w.open_in_lightburn() and w._dialogs[-1][0] == "error"
    out2.unlink()
    assert not w.open_in_lightburn() and "not found" in w._dialogs[-1][1]


def test_title_shows_saved_copy_and_original_stays_open(make_window, tmp_path):
    w = make_window("en")
    src = write(tmp_path, four())
    w.open_project(src)
    out = w.save_new_project(confirm=False)
    assert w.project.info.path == src  # dál se pracuje s originálem
    assert w.windowTitle().endswith(f"- {src.name} (last saved as {out.name})")
    assert out.name in w.lbl_file.text() and "next save creates another file" in w.lbl_file.text()
    assert w.save_new_project(confirm=False).name == "karty__grid_002.lbrn2"
    w.open_project(src)  # nově otevřený projekt: žádné „naposledy uloženo“
    assert w.windowTitle().endswith(f"- {src.name}") and w.last_saved is None and not w.act_open_in_lb.isEnabled()


def test_continue_with_saved_file(make_window, tmp_path):
    w = make_window("en")
    src = write(tmp_path, four())
    before = src.read_bytes()
    w.open_project(src)
    w.add_copies([w.order[0]], 2)
    w._switch_answer = True  # v hlášení zaškrtnuto „Pokračovat s uloženým souborem“
    out = w.save_new_project(confirm=False)
    assert w.project.info.path == out and w.last_saved == out and w.act_open_in_lb.isEnabled()
    assert w.windowTitle().endswith(f"- {out.name}") and "last saved" not in w.windowTitle()
    assert w.copies == {} and len(w.order) == 6  # kopie jsou teď v souboru napevno
    assert not w.act_undo.isEnabled()
    assert src.read_bytes() == before
    w._switch_answer = False
    assert w.save_new_project(confirm=False).name == "karty__grid_002.lbrn2"  # řada originálu, ne __grid_001__grid_001


def test_undo_redo_of_layout_changes(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, project([card(0, 0), card(200, 0), card(0, 200)])))
    assert not w.act_undo.isEnabled() and not w.act_redo.isEnabled()
    w.spin_cols.setValue(1)
    w.spin_gap_x.set_mm(10.0)
    w.preview.itemClicked.emit("G2", False)
    w._ask_int = lambda *a: 2
    w.act_duplicate.trigger()
    assert w.order == ("G1", "G2", "G3", "G2+1", "G2+2")
    w.act_undo.trigger()  # kopie zpět
    assert w.order == ("G1", "G2", "G3") and w.copies == {} and w.act_redo.isEnabled()
    w.act_undo.trigger()
    assert w.spin_gap_x.mm() == 3.0 and w.spin_cols.value() == 1
    w.act_undo.trigger()
    assert w.spin_cols.value() == 3 and not w.act_undo.isEnabled()
    w.act_redo.trigger()
    w.act_redo.trigger()
    w.act_redo.trigger()
    assert w.order[-2:] == ("G2+1", "G2+2") and w.spin_gap_x.mm() == 10.0 and not w.act_redo.isEnabled()
    assert len(w.plan.layout.placements) == 5
    w.act_undo.trigger()
    w.spin_cols.setValue(2)  # nová změna zahodí kroky vpřed
    assert not w.act_redo.isEnabled()


def test_toolbar_can_be_rearranged_and_order_is_remembered(make_window, settings):
    w = make_window("en")
    assert w.toolbar.order()[:3] == ["open", "save", "open_in_lightburn"]
    assert w.toolbar.move_action("help", "open")
    assert w.toolbar.order()[0] == "help" and settings.toolbar_order()[0] == "help"
    w2 = make_window("en")
    assert w2.toolbar.order() == w.toolbar.order()
    w2.reset_toolbar()
    assert w2.toolbar.order() == w2.TOOLBAR_DEFAULT and settings.toolbar_order() == []
    assert not w2.toolbar.move_action("help", "help")
