"""MVP-07: T-I18N-01 … 16 v rozsahu, který lze automatizovat (spec. kap. 36.6)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from PySide6.QtCore import QCoreApplication

from grid_arranger.gui.catalog_check import check_catalog
from grid_arranger.gui.i18n import LocaleManager, detect_system_language
from grid_arranger.gui.messages import TEMPLATES, message

from tests.integration.lbrn2_builder import card, project

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "langs, expected",
    [(["cs-CZ"], "cs"), (["cs"], "cs"), (["en-US"], "en"), (["en-GB"], "en"), (["fr-FR"], "en"),
     (["de-AT", "cs-CZ"], "cs"), ([], "en"), (["sk_SK", "en"], "en")],
)
def test_t_i18n01_02_auto_language(langs, expected):
    assert detect_system_language(langs) == expected


def test_t_i18n03_04_language_setting_persists(settings, tmp_path):
    from PySide6.QtCore import QSettings

    from grid_arranger.gui.settings import UserSettings

    assert settings.language() == "auto"
    for v in ("cs", "en", "auto"):
        settings.set_language(v)
        again = UserSettings(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))
        assert again.language() == v
    with pytest.raises(ValueError):
        settings.set_language("xx")


def test_t_i18n08_decimal_comma_and_point_same_value(make_window, tmp_path):
    values = []
    for lang, text in (("cs", "3,5"), ("en", "3.5")):
        w = make_window(lang)
        w.spin_gap_x.lineEdit().setText(text)
        w.spin_gap_x.interpretText()
        values.append(w.spin_gap_x.value())
    assert values == [3.5, 3.5]


def test_t_i18n09_switch_language_keeps_state(make_window, tmp_path):
    p = tmp_path / "k.lbrn2"
    p.write_bytes(project([card(0, 0), card(200, 0), card(400, 0)]))
    w = make_window("cs")
    w.open_project(p)
    w.list_items.setCurrentRow(2)
    w._move(-1)
    w.spin_cols.setValue(2)
    w.spin_gap_x.setValue(4.25)
    state = (w.order, w.spin_cols.value(), w.spin_gap_x.value(), w.plan.layout.grid_bounds)
    assert w.btn_save.text() == "Uložit jako nový projekt…"
    w.set_language("en")
    assert w.btn_save.text() == "Save as new project…"
    assert (w.order, w.spin_cols.value(), w.spin_gap_x.value(), w.plan.layout.grid_bounds) == state


def test_t_i18n10_identical_output_in_both_languages(make_window, tmp_path):
    outs = []
    data = project([card(0, 0), card(200, 0, text="Žluťoučký kůň"), card(400, 0)])  # stejný vstup pro oba jazyky
    for lang in ("cs", "en"):
        d = tmp_path / lang
        d.mkdir()
        p = d / "k.lbrn2"
        p.write_bytes(data)
        w = make_window(lang)
        w.open_project(p)
        w.spin_gap_x.setValue(2.5)
        outs.append(w.save_new_project(confirm=False).read_bytes())
    assert outs[0] == outs[1]


def test_t_i18n11_unicode_item_label_untouched(make_window, tmp_path):
    p = tmp_path / "k.lbrn2"
    p.write_bytes(project([card(0, 0, text="Příliš žluťoučký kůň ✓")]))
    w = make_window("en")
    w.open_project(p)
    assert "Příliš žluťoučký kůň ✓" in w.list_items.item(0).text()


def test_t_i18n12_missing_catalog_falls_back_to_english(qapp, tmp_path):
    lm = LocaleManager(qapp, tmp_path)  # prázdná složka bez .qm
    assert lm.apply("cs") == "en"
    assert lm.missing_catalog
    lm.apply("en")


@pytest.mark.parametrize("n, text", [(0, "Vybráno 0 výrobků"), (1, "Vybrán 1 výrobek"), (2, "Vybrány 2 výrobky"),
                                     (4, "Vybrány 4 výrobky"), (5, "Vybráno 5 výrobků"), (21, "Vybráno 21 výrobků")])
def test_t_i18n13_czech_plurals(qapp, qm_dir, n, text):
    lm = LocaleManager(qapp, qm_dir)
    lm.apply("cs")
    try:
        assert QCoreApplication.translate("MainWindow", "Selected %n item(s)", "", n) == text
    finally:
        lm.apply("en")


@pytest.mark.parametrize("n, text", [(1, "Selected 1 item"), (2, "Selected 2 items"), (0, "Selected 0 items")])
def test_english_plurals_need_en_catalog(qapp, qm_dir, n, text):
    lm = LocaleManager(qapp, qm_dir)
    lm.apply("en")
    assert QCoreApplication.translate("MainWindow", "Selected %n item(s)", "", n) == text


def test_t_i18n14_15_catalogs_complete_and_placeholders_match():
    assert check_catalog(ROOT / "translations" / "gridarranger_cs.ts", require_complete=True) == []
    assert check_catalog(ROOT / "translations" / "gridarranger_en.ts", require_complete=False) == []


def test_catalog_check_detects_missing_and_bad_placeholder(tmp_path):
    ts = tmp_path / "x.ts"
    ts.write_text(
        '<?xml version="1.0" encoding="utf-8"?><TS version="2.1" language="cs_CZ"><context><name>M</name>'
        '<message><source>Hello {a}</source><translation>Ahoj {b}</translation></message>'
        '<message><source>New critical warning</source><translation type="unfinished"></translation></message>'
        "</context></TS>", encoding="utf-8")
    problems = check_catalog(ts, require_complete=True)
    assert len(problems) == 2


def test_t_i18n07_every_error_code_has_a_message():
    """Každý kód chyby/upozornění z jádra, adaptéru a úlohy má lokalizovatelnou hlášku."""
    src = ROOT / "src" / "grid_arranger"
    codes: set[str] = set()
    for f in src.rglob("*.py"):
        if "gui" in f.parts:
            continue
        text = f.read_text(encoding="utf-8")
        codes |= set(re.findall(r'GridError\(\s*"([a-z_]+)"', text))
        codes |= set(re.findall(r'(?:Issue|Reason)\(\s*"([a-z_]+)"', text))
    codes.discard("patch_mismatch")  # interní pojistky — zobrazí se obecnou hláškou s kódem
    codes.discard("overlapping_patch")
    codes.discard("missing_xform")
    codes.discard("invalid_bounds")
    codes.discard("invalid_alignment")
    missing = sorted(c for c in codes if c not in TEMPLATES)
    assert missing == []


def test_unknown_code_has_safe_fallback(qapp):
    assert message("brand_new_code") == "Error brand_new_code"
    assert "?" in message("outside_material")  # chybějící parametr nevyvolá výjimku
