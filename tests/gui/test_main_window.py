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
    assert w.btn_save.isEnabled()


def test_save_disabled_without_project(make_window):
    w = make_window("en")
    assert not w.btn_save.isEnabled()
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
    assert not w.btn_save.isEnabled()
    assert any("Select at least one item" in t for t in w.issues())
    w._select_all()
    assert w.btn_save.isEnabled() and len(w.order) == 4


def test_t_mvp11_overrun_blocks_save_and_names_item(make_window, tmp_path):
    w = make_window("en")
    w.open_project(write(tmp_path, four()))
    w.spin_bw.setValue(150)
    assert not w.btn_save.isEnabled()
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
    assert kinds == ["ask", "info"]
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
