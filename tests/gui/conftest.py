from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(scope="session")
def qm_dir(tmp_path_factory) -> Path:
    """Sestaví .qm z translations/*.ts do dočasné složky (testy nezávisí na ručním buildu)."""
    out = tmp_path_factory.mktemp("qm")
    lrelease = shutil.which("pyside6-lrelease", path=str(Path(sys.executable).parent)) or shutil.which("pyside6-lrelease")
    if not lrelease:
        pytest.skip("pyside6-lrelease není k dispozici")
    for ts in (ROOT / "translations").glob("gridarranger_*.ts"):
        subprocess.run([lrelease, str(ts), "-qm", str(out / (ts.stem + ".qm"))], check=True, capture_output=True)
    return out


@pytest.fixture
def settings(tmp_path):
    from grid_arranger.gui.settings import UserSettings

    return UserSettings(QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat))


@pytest.fixture
def make_window(qapp, qm_dir, settings):
    from grid_arranger.gui.i18n import LocaleManager
    from grid_arranger.gui.main_window import MainWindow

    windows = []

    def _make(lang: str = "en"):
        lm = LocaleManager(qapp, qm_dir)
        lm.apply(lang)
        settings.set_language(lang)
        w = MainWindow(settings, lm)
        w._dialogs = []
        w._ask = lambda text: (w._dialogs.append(("ask", text)), True)[1]
        w._info = lambda text: w._dialogs.append(("info", text))
        w._error = lambda text: w._dialogs.append(("error", text))
        w._save_answers = []  # cesty, které „vybere“ uživatel v dialogu uložení; prázdné = přijme návrh

        def _ask_save_path(proposal):
            w._dialogs.append(("save_as", str(proposal)))
            return w._save_answers.pop(0) if w._save_answers else proposal

        w._ask_save_path = _ask_save_path
        windows.append((w, lm))
        return w

    yield _make
    for w, lm in windows:
        w.close()
        lm.apply("en")
