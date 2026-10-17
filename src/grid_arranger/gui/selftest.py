"""Samokontrola sestavené aplikace: ``GridArranger.exe --self-test report.json`` (GH-05, HELP-01, T-I18N-16).

Spouští ji ``tools/build_exe.py`` hned po sestavení a lze ji spustit i na cílovém počítači.
Ověří, že balíček obsahuje vše potřebné (překlady, příručku, ikonu, knihovny Qt) a že
celý řetězec načtení → rozložení → zápis → kontrola funguje v zabaleném prostředí.
Okno se nezobrazuje, uživatelské nastavení se nemění, nic se nezapisuje mimo dočasnou složku.
Výsledek se zapíše jako JSON (okenní EXE nemá konzoli); návratový kód 0 = vše v pořádku.
"""

from __future__ import annotations

import json
import platform
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Callable

from PySide6 import __version__ as pyside_version
from PySide6.QtCore import QCoreApplication, QSettings, qVersion

from ..version import __version__

# Minimální syntetický projekt (dvě karty 100 × 60 mm, počátek vpravo nahoře) — žádná zákaznická data.
_PROJECT = "\r\n".join([
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<LightBurnProject AppVersion="2.2.00" DeviceName="Self-test" FormatVersion="1" MaterialHeight="0" '
    'MirrorX="True" MirrorY="True" AskForSendName="True" CurrentPage="0" Page0Name="Page 1">',
    '    <Thumbnail Source="iVBORw0KGgoAAAANSUhEUg=="/>',
    '    <VariableText>',
    '        <Start Value="0"/>',
    '    </VariableText>',
    '    <CutSetting type="Cut">',
    '        <index Value="1"/>',
    '        <name Value="C01"/>',
    '    </CutSetting>',
    *[line for i, x in enumerate((0, 300)) for line in (
        '    <Shape Type="Group" CutIndex="0">',
        f'        <XForm>1 0 0 1 {x} 40</XForm>',
        '        <Children>',
        f'            <Shape Type="Path" CutIndex="1" VertID="{i + 1}" PrimID="{i + 1}">',
        '                <XForm>1 0 0 1 0 0</XForm>',
        '                <VertList>V0 0c0x1c1x1V100 0c0x1c1x1V100 60c0x1c1x1V0 60c0x1c1x1</VertList>',
        '                <PrimList>LineClosed</PrimList>',
        '            </Shape>',
        '        </Children>',
        '    </Shape>',
    )],
    '    <Notes ShowOnLoad="0" Notes=""/>',
    '</LightBurnProject>',
    '',
])


def _check_help() -> str:
    from .help import HELP_DIR, TOPICS

    missing = [f"{lang}/{t}.md" for lang in ("cs", "en") for t in TOPICS if not (HELP_DIR / lang / f"{t}.md").is_file()]
    if missing:
        raise AssertionError("missing help topics: " + ", ".join(missing))
    return f"{2 * len(TOPICS)} topics in {HELP_DIR}"


def _check_translations(app) -> str:
    from .i18n import LocaleManager

    lm = LocaleManager(app)
    try:
        if lm.apply("cs") != "cs" or lm.missing_catalog:
            raise AssertionError("gridarranger_cs.qm not loaded")
        if QCoreApplication.translate("MainWindow", "&File") == "&File":
            raise AssertionError("Czech catalog loaded but strings are not translated")
        if not lm.qt_catalog_loaded:
            raise AssertionError("qtbase_cs.qm (Qt dialog buttons) not found")
        return "cs + qtbase_cs loaded"
    finally:
        lm.apply("en")


def _check_window(app, settings_file: Path) -> str:
    from .help import HelpWindow
    from .i18n import LocaleManager
    from .main_window import MainWindow
    from .settings import UserSettings

    settings = UserSettings(QSettings(str(settings_file), QSettings.Format.IniFormat))
    lm = LocaleManager(app)
    lm.apply("cs")
    try:
        win = MainWindow(settings, lm)
        help_win = HelpWindow("cs", win)
        help_win.open_topic("index")
        title = help_win.windowTitle()
        help_win.close()
        win.close()
        return f"main window + help ({title!r})"
    finally:
        lm.apply("en")


def _check_icon(app) -> str:
    from .app import ICON_PATH

    if not ICON_PATH.is_file() or app.windowIcon().isNull():
        raise AssertionError(f"icon missing: {ICON_PATH}")
    return str(ICON_PATH.name)


def _check_roundtrip(work: Path) -> str:
    from ..application.arrange_job import ArrangeParams, MaterialInput, run

    src = work / "selftest.lbrn2"
    src.write_bytes(_PROJECT.encode("utf-8"))
    before = src.read_bytes()
    res = run(src, ArrangeParams(columns=2, gap_x=5, gap_y=5, material=MaterialInput(700, 500)), out_dir=work)
    if res.problems or res.output is None:
        raise AssertionError(f"arrange failed: {res.problems}")
    if src.read_bytes() != before:  # run() sám nezávisle ověří výstup (safety.verify)
        raise AssertionError("source file changed")
    return f"{res.output.name} ({len(res.plan.layout.placements)} items)"


def _check_https() -> str:
    """Kontrola aktualizací potřebuje HTTPS: modul ssl v balíčku a certifikáty systému (bez síťového spojení)."""
    import ssl
    import urllib.request  # noqa: F401 — musí být v balíčku

    certs = len(ssl.create_default_context().get_ca_certs())
    if sys.platform == "win32" and certs == 0:
        raise AssertionError("no CA certificates loaded from the Windows store")
    return f"{ssl.OPENSSL_VERSION}, {certs} CA certificates"


def run_self_test(app, report_path: str | Path) -> int:
    checks: list[dict] = []

    def check(name: str, fn: Callable[[], str]) -> None:
        try:
            checks.append({"name": name, "ok": True, "detail": fn()})
        except Exception as exc:  # noqa: BLE001 — chceme zaznamenat každou chybu
            checks.append({"name": name, "ok": False, "detail": f"{exc!r}", "traceback": traceback.format_exc()})

    with tempfile.TemporaryDirectory(prefix="gridarranger-selftest-") as tmp:
        work = Path(tmp)
        check("help", _check_help)
        check("translations", lambda: _check_translations(app))
        check("icon", lambda: _check_icon(app))
        check("window", lambda: _check_window(app, work / "settings.ini"))
        check("roundtrip", lambda: _check_roundtrip(work))
        check("https", _check_https)

    ok = all(c["ok"] for c in checks)
    report = {
        "ok": ok,
        "version": __version__,
        "qt": qVersion(),
        "pyside6": pyside_version,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "frozen": bool(getattr(sys, "frozen", False)),
        "executable": sys.executable,
        "checks": checks,
    }
    Path(report_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if ok else 1
