"""Výběr jazyka a načítání překladů (MVP-07; spec. kap. 36).

Zdrojový jazyk je angličtina. Katalogy ``gridarranger_<kód>.qm`` se hledají ve složce
``translations`` vedle tohoto modulu (sestavují se z ``translations/*.ts`` příkazem
``python tools/build_translations.py``). Chybějící katalog nesmí shodit aplikaci —
použije se angličtina (T-I18N-12).

Kromě vlastního katalogu se načítá i katalog Qt ``qtbase_<kód>.qm`` (tlačítka Ano/Ne,
Storno, kontextová nabídka polí…) ze složky překladů Qt; v EXE ji přibalí PyInstaller.
Chybějící katalog Qt není chyba — tlačítka zůstanou anglicky.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QCoreApplication, QLibraryInfo, QLocale, QTranslator

SUPPORTED = ("cs", "en", "de", "sk", "pl", "fr", "es", "it")  # osm jazyků veřejné v1.0.0 (spec. kap. 36)
NATIVE_NAMES = {"cs": "Čeština", "en": "English", "de": "Deutsch", "sk": "Slovenčina", "pl": "Polski",
                "fr": "Français", "es": "Español", "it": "Italiano"}
_LOCALES = {
    "cs": (QLocale.Language.Czech, QLocale.Country.CzechRepublic),
    "en": (QLocale.Language.English, QLocale.Country.UnitedStates),
    "de": (QLocale.Language.German, QLocale.Country.Germany),
    "sk": (QLocale.Language.Slovak, QLocale.Country.Slovakia),
    "pl": (QLocale.Language.Polish, QLocale.Country.Poland),
    "fr": (QLocale.Language.French, QLocale.Country.France),
    "es": (QLocale.Language.Spanish, QLocale.Country.Spain),
    "it": (QLocale.Language.Italian, QLocale.Country.Italy),
}
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
    def __init__(self, app: QCoreApplication, qm_dir: Path | None = None) -> None:
        self._app = app
        self._qm_dir = qm_dir if qm_dir is not None else QM_DIR
        self._translator: QTranslator | None = None
        self._qt_translator: QTranslator | None = None
        self.current = "en"
        self.missing_catalog = False
        self.qt_catalog_loaded = False

    def resolve(self, setting: str) -> str:
        return detect_system_language() if setting == "auto" else (setting if setting in SUPPORTED else "en")

    def apply(self, setting: str) -> str:
        """Nastaví jazyk podle volby ``auto`` nebo kódu z ``SUPPORTED``; vrátí skutečně použitý jazyk."""
        lang = self.resolve(setting)
        for t in (self._translator, self._qt_translator):
            if t is not None:
                self._app.removeTranslator(t)
        self._translator = self._qt_translator = None
        self.missing_catalog = False
        self.qt_catalog_loaded = False
        tr = QTranslator(self._app)
        qm = self._qm_dir / f"gridarranger_{lang}.qm"
        if qm.exists() and tr.load(str(qm)):
            self._app.installTranslator(tr)
            self._translator = tr
        elif lang != "en":
            self.missing_catalog = True
            lang = "en"  # bezpečný fallback
        self.current = lang
        if lang != "en":
            qt = QTranslator(self._app)
            if qt.load(f"qtbase_{lang}", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
                self._app.installTranslator(qt)
                self._qt_translator = qt
                self.qt_catalog_loaded = True
        QLocale.setDefault(self.qlocale())
        return lang

    def qlocale(self) -> QLocale:
        return QLocale(*_LOCALES.get(self.current, _LOCALES["en"]))
