"""GH-05 / HELP-01 / T-I18N-16: předpoklady sestavení EXE ověřitelné bez Windows."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QCoreApplication

ROOT = Path(__file__).resolve().parents[2]


def test_self_test_passes_and_writes_report(qapp, qm_dir, monkeypatch, tmp_path):
    import grid_arranger.gui.i18n as i18n
    from grid_arranger.gui.selftest import run_self_test

    monkeypatch.setattr(i18n, "QM_DIR", qm_dir)
    from grid_arranger.gui.app import ICON_PATH
    from PySide6.QtGui import QIcon

    qapp.setWindowIcon(QIcon(str(ICON_PATH)))
    report = tmp_path / "r.json"
    assert run_self_test(qapp, report) == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["ok"] and {c["name"] for c in data["checks"]} == {"help", "translations", "icon", "window", "roundtrip", "https"}
    assert QCoreApplication.translate("MainWindow", "&File") == "&File"  # self-test vrátil angličtinu


def test_self_test_reports_missing_translations(qapp, monkeypatch, tmp_path):
    import grid_arranger.gui.i18n as i18n
    from grid_arranger.gui.selftest import run_self_test

    monkeypatch.setattr(i18n, "QM_DIR", tmp_path / "none")
    report = tmp_path / "r.json"
    assert run_self_test(qapp, report) == 1
    data = json.loads(report.read_text(encoding="utf-8"))
    bad = [c for c in data["checks"] if not c["ok"]]
    assert [c["name"] for c in bad] == ["translations"]
    assert "gridarranger_cs.qm" in bad[0]["detail"]


def test_czech_also_loads_qt_dialog_catalog(qapp, qm_dir):
    from grid_arranger.gui.i18n import LocaleManager

    lm = LocaleManager(qapp, qm_dir)
    try:
        lm.apply("cs")
        assert lm.qt_catalog_loaded
        assert QCoreApplication.translate("QPlatformTheme", "&Yes") != "&Yes"  # tlačítka Ano/Ne česky
        lm.apply("en")
        assert not lm.qt_catalog_loaded
        assert QCoreApplication.translate("QPlatformTheme", "&Yes") == "&Yes"
    finally:
        lm.apply("en")


def test_bundle_inputs_exist():
    assert (ROOT / "packaging" / "GridArranger.spec").is_file()
    assert (ROOT / "packaging" / "GridArranger.ico").is_file()
    assert (ROOT / "src" / "grid_arranger" / "gui" / "resources" / "app_icon.png").is_file()


def test_installer_script_invariants():
    import re

    from grid_arranger.updates import SETUP_RE

    iss = (ROOT / "packaging" / "GridArranger.iss").read_text(encoding="utf-8-sig")
    assert "AppId={{8C6E2F3A-5B1D-4E7A-9C2F-3D8B6A1E4F70}" in iss  # nikdy neměnit — aktualizace přes starou verzi
    assert "PrivilegesRequired=lowest" in iss  # bez práv správce (spec. kap. 32)
    assert re.search(r"Check: WizardSilent", iss)  # po aktualizaci z aplikace znovu spustit
    assert 'Type: filesandordirs; Name: "{app}\\_internal"' in iss  # žádné zbytky staré verze
    name = re.search(r"OutputBaseFilename=(.+)", iss).group(1).strip().replace("{#AppVersion}", "0.1.0-alpha.2") + ".exe"
    assert SETUP_RE.match(name)  # aplikace najde instalátor ve vydání
