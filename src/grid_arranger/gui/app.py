"""Spuštění grafické aplikace: ``python -m grid_arranger.gui`` nebo ``GridArranger.exe``.

Argumenty: cesta k ``.lbrn2`` (otevře projekt, např. přetažením souboru na ikonu EXE),
``--self-test REPORT.json`` (samokontrola sestavení bez zobrazení okna, viz ``selftest.py``).
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .i18n import LocaleManager
from .main_window import MainWindow
from .settings import APPLICATION, ORGANIZATION, UserSettings

ICON_PATH = Path(__file__).with_name("resources") / "app_icon.png"


def _install_excepthook() -> None:
    """Neočekávaná chyba: vypsat do konzole a ukázat uživateli (nic se tiše neztratí)."""

    def hook(exc_type, exc, tb) -> None:
        detail = "".join(traceback.format_exception(exc_type, exc, tb))
        if sys.__stderr__ is not None:  # v okenním EXE konzole neexistuje
            sys.__stderr__.write(detail)
        box = QMessageBox(QMessageBox.Icon.Critical, "Grid Arranger for LightBurn",
                          QCoreApplication.translate("App", "An unexpected error occurred. Nothing was saved.\n\nPlease send the details below when reporting the problem."))
        box.setDetailedText(detail)
        box.exec()

    sys.excepthook = hook


def main(argv: list[str] | None = None) -> int:
    app = QApplication(argv if argv is not None else sys.argv)
    app.setOrganizationName(ORGANIZATION)
    app.setApplicationName(APPLICATION)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    args = app.arguments()[1:]
    if args[:1] == ["--self-test"]:
        from .selftest import run_self_test

        return run_self_test(app, args[1] if len(args) > 1 else "gridarranger-selftest.json")
    _install_excepthook()
    settings = UserSettings()
    locale = LocaleManager(app)
    locale.apply(settings.language())
    win = MainWindow(settings, locale)
    win.show()
    if args and args[0].lower().endswith((".lbrn2", ".lbrn")):
        win.open_project(args[0])
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
