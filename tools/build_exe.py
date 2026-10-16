"""Sestavení přenosné aplikace GridArranger (GH-05; spec. kap. 30).

    python tools/build_exe.py               # překlady → testy → PyInstaller → samokontrola → ZIP
    python tools/build_exe.py --skip-tests  # bez pytest (jen pro rychlé zkoušky balení)

Na Windows vznikne:
* ``dist/GridArranger/GridArranger.exe`` (+ složka ``_internal`` s knihovnami) — spustitelné bez Pythonu,
* ``dist/GridArranger-v<verze>-win-x64.zip`` — totéž v jednom souboru k přenesení na jiný počítač,
* ``dist/selftest-report.json`` — výsledek samokontroly zabalené aplikace.

PyInstaller sestavuje vždy pro systém, na kterém běží: ``.exe`` pro Windows vznikne jen na Windows.
Na Linuxu skript slouží ke zkoušce balení (vznikne linuxová složka a ZIP ``-linux-x64``).
Výstupy v ``build/`` a ``dist/`` jsou generované, do Gitu nepatří a při dalším sestavení se přepíší.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BUILD = ROOT / "build" / "pyinstaller"
APP_DIR = DIST / "GridArranger"
SPEC = ROOT / "packaging" / "GridArranger.spec"
IS_WINDOWS = sys.platform == "win32"

README = """Grid Arranger for LightBurn {version}
=====================================

CZ: Spusťte GridArranger.exe. Python ani instalace nejsou potřeba.
    Celou složku GridArranger lze zkopírovat kamkoli (např. na plochu nebo na počítač u laseru);
    soubor GridArranger.exe musí zůstat vedle složky _internal.
    Windows může při prvním spuštění upozornit na neznámého vydavatele (aplikace není podepsaná):
    „Další informace“ → „Přesto spustit“.
    Nápověda: klávesa F1 v aplikaci. Kontrola instalace: GridArranger.exe --self-test report.json

EN: Run GridArranger.exe. No Python or installation needed.
    The whole GridArranger folder can be copied anywhere; keep GridArranger.exe next to _internal.
    Windows may warn about an unknown publisher (the app is not signed):
    "More info" → "Run anyway". Help: press F1 in the app.

Unofficial tool, not a product of LightBurn Software. The original project is never overwritten;
each arrangement is saved as a new file ...__grid_NNN.lbrn2.
"""


def step(title: str) -> None:
    print(f"\n=== {title} ===", flush=True)


def run(cmd: list[str], **kw) -> None:
    print("> " + " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ROOT, **kw)


def version() -> str:
    sys.path.insert(0, str(ROOT / "src"))
    from grid_arranger.version import __version__

    return __version__


def self_test(exe: Path) -> dict:
    report = DIST / "selftest-report.json"
    if report.exists():
        report.unlink()
    env = dict(os.environ)
    if not IS_WINDOWS and not env.get("DISPLAY") and not env.get("WAYLAND_DISPLAY"):
        env["QT_QPA_PLATFORM"] = "offscreen"  # zkouška balení na serveru bez obrazovky
    print(f"> {exe} --self-test {report}", flush=True)
    proc = subprocess.run([str(exe), "--self-test", str(report)], env=env, timeout=180)
    if not report.exists():
        sys.exit(f"Samokontrola nevytvořila report (návratový kód {proc.returncode}).")
    data = json.loads(report.read_text(encoding="utf-8"))
    for c in data["checks"]:
        print(f"  [{'OK' if c['ok'] else 'CHYBA'}] {c['name']}: {c['detail']}")
    if proc.returncode != 0 or not data["ok"] or not data["frozen"]:
        sys.exit(f"Samokontrola selhala — podrobnosti v {report}")
    return data


def make_zip(ver: str) -> Path:
    arch = "x64" if platform.machine().lower() in ("amd64", "x86_64") else platform.machine().lower()
    target = DIST / f"GridArranger-v{ver}-{'win' if IS_WINDOWS else 'linux'}-{arch}.zip"
    if target.exists():
        target.unlink()
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(APP_DIR.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(DIST))
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip-tests", action="store_true", help="nespouštět pytest")
    a = ap.parse_args()
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("PyInstaller není nainstalovaný. V aktivním .venv spusťte: python -m pip install -e .[dev,build]")
    if not IS_WINDOWS:
        print("Upozornění: nejde o Windows — vznikne jen zkušební linuxové sestavení, ne GridArranger.exe.")
    ver = version()

    step("1/5 Překlady")
    run([sys.executable, "tools/build_translations.py", "--no-update"])

    if a.skip_tests:
        step("2/5 Testy — přeskočeno (--skip-tests)")
    else:
        step("2/5 Testy")
        run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"])

    step("3/5 PyInstaller")
    run([sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm", "--clean",
         "--distpath", str(DIST), "--workpath", str(BUILD)])
    (APP_DIR / "README.txt").write_text(README.format(version=ver), encoding="utf-8-sig" if IS_WINDOWS else "utf-8")

    step("4/5 Samokontrola zabalené aplikace")
    exe = APP_DIR / ("GridArranger.exe" if IS_WINDOWS else "GridArranger")
    report = self_test(exe)

    step("5/5 ZIP")
    z = make_zip(ver)
    size = sum(f.stat().st_size for f in APP_DIR.rglob("*") if f.is_file())
    print(f"\nHotovo — Grid Arranger {ver} (Qt {report['qt']}, Python {report['python']})")
    print(f"  Aplikace: {exe}  (složka {size / 1e6:.0f} MB)")
    print(f"  ZIP:      {z}  ({z.stat().st_size / 1e6:.0f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
