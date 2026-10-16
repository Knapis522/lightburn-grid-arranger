"""Spuštění grafické aplikace: ``python -m grid_arranger.gui`` nebo ``GridArranger.exe``."""

from __future__ import annotations

import sys
import traceback

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication, QMessageBox

from .i18n import LocaleManager
from .main_window import MainWindow
from .settings import APPLICATION, ORGANIZATION, UserSettings


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
    _install_excepthook()
    settings = UserSettings()
    locale = LocaleManager(app)
    locale.apply(settings.language())
    win = MainWindow(settings, locale)
    win.show()
    args = app.arguments()[1:]
    if args and args[0].lower().endswith((".lbrn2", ".lbrn")):
        win.open_project(args[0])
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
