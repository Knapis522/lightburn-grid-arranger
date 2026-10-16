"""Výběr jazyka a načítání překladů (MVP-07; spec. kap. 36).

Zdrojový jazyk je angličtina. Katalogy ``gridarranger_<kód>.qm`` se hledají ve složce
``translations`` vedle tohoto modulu (sestavují se z ``translations/*.ts`` příkazem
``python tools/build_translations.py``). Chybějící katalog nesmí shodit aplikaci —
použije se angličtina (T-I18N-12).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QCoreApplication, QLocale, QTranslator

SUPPORTED = ("cs", "en")  # interní MVP; veřejné v1.0.0: cs/en/de/sk/pl/fr/es/it
NATIVE_NAMES = {"cs": "Čeština", "en": "English"}
QM_DIR = Path(__file__).with_name("translations")


def detect_system_language(ui_languages: list[str] | None = None) -> str:
    """První podporovaný jazyk z preferencí systému (``de-AT`` → ``de``), jinak ``en``."""
    langs = ui_languages if ui_languages is not None else QLocale.system().uiLanguages()
    for tag in langs:
        base = tag.replace("_", "-").split("-")[0].lower()
        if base in SUPPORTED:
            return base
    return "en"


class LocaleManager:
    def __init__(self, app: QCoreApplication, qm_dir: Path = QM_DIR) -> None:
        self._app = app
        self._qm_dir = qm_dir
        self._translator: QTranslator | None = None
        self.current = "en"
        self.missing_catalog = False

    def resolve(self, setting: str) -> str:
        return detect_system_language() if setting == "auto" else (setting if setting in SUPPORTED else "en")

    def apply(self, setting: str) -> str:
        """Nastaví jazyk podle volby ``auto|cs|en``; vrátí skutečně použitý jazyk."""
        lang = self.resolve(setting)
        if self._translator is not None:
            self._app.removeTranslator(self._translator)
            self._translator = None
        self.missing_catalog = False
        tr = QTranslator(self._app)
        qm = self._qm_dir / f"gridarranger_{lang}.qm"
        if qm.exists() and tr.load(str(qm)):
            self._app.installTranslator(tr)
            self._translator = tr
        elif lang != "en":
            self.missing_catalog = True
            lang = "en"  # bezpečný fallback
        self.current = lang
        QLocale.setDefault(self.qlocale())
        return lang

    def qlocale(self) -> QLocale:
        return QLocale(QLocale.Language.Czech, QLocale.Country.CzechRepublic) if self.current == "cs" else QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
