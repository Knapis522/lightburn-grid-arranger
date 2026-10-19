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
        w._open_in_lb_answer = False  # tlačítko „Otevřít v LightBurnu“ v hlášení o uložení
        w._switch_answer = False  # zaškrtnuto „Pokračovat s uloženým souborem“
        w._ask_after_save = lambda text: (w._dialogs.append(("info", text)), (w._open_in_lb_answer, w._switch_answer))[1]
        w._unsaved_answers = []  # odpovědi na „neuložené změny“ (save/discard/cancel); prázdné = discard

        def _ask_unsaved(can_save):
            w._dialogs.append(("unsaved", can_save))
            return w._unsaved_answers.pop(0) if w._unsaved_answers else "discard"

        w._ask_unsaved = _ask_unsaved
        w._opened = []  # soubory „otevřené“ přiřazeným programem (LightBurn)
        w._open_file = lambda path: (w._opened.append(path), True)[1]
        windows.append((w, lm))
        return w

    yield _make
    from PySide6.QtCore import QCoreApplication, QEvent

    for w, lm in windows:
        w.close()
        w.deleteLater()  # okna se stylem by jinak zpomalovala další testy (přepínání vzhledu)
        lm.apply("en")
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
