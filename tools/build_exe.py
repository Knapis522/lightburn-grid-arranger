"""Sestavení přenosné aplikace GridArranger (GH-05; spec. kap. 30).

    python tools/build_exe.py                 # překlady → testy → PyInstaller → samokontrola → ZIP → instalátor
    python tools/build_exe.py --skip-tests    # bez pytest (jen pro rychlé zkoušky balení)
    python tools/build_exe.py --no-installer  # bez instalátoru (není-li nainstalovaný Inno Setup)

Vše pro jednu verzi vznikne pohromadě ve složce ``dist/v<verze>/`` (starší verze zůstanou vedle):
* ``GridArranger-Setup-v<verze>-win-x64.exe`` — instalátor (Inno Setup 6.3+), hlavní podoba distribuce,
* ``GridArranger-v<verze>-win-x64.zip`` — záložní přenosná verze,
* ``SHA256SUMS.txt`` — kontrolní součty instalátoru a ZIPu (přikládá se ke GitHub Release;
  podle něj aplikace ověřuje staženou aktualizaci),
* ``RELEASE_NOTES.md`` — kopie ``docs/releases/v<verze>.md`` (text pro GitHub Release),
* ``GridArranger/GridArranger.exe`` — rozbalená aplikace (spustitelná bez Pythonu),
* ``selftest-report.json`` — výsledek samokontroly zabalené aplikace.

PyInstaller sestavuje vždy pro systém, na kterém běží: ``.exe`` pro Windows vznikne jen na Windows.
Na Linuxu skript slouží ke zkoušce balení (vznikne linuxová složka a ZIP ``-linux-x64``).
Výstupy v ``build/`` a ``dist/`` jsou generované, do Gitu nepatří a při dalším sestavení se přepíší.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_ROOT = ROOT / "dist"
BUILD = ROOT / "build" / "pyinstaller"
# Výstupy každé verze pohromadě v dist/v<verze>/ (nastaví set_output_dir podle čísla verze)
DIST = DIST_ROOT / "dev"
APP_DIR = DIST / "GridArranger"


def set_output_dir(ver: str) -> None:
    global DIST, APP_DIR
    DIST = DIST_ROOT / f"v{ver}"
    APP_DIR = DIST / "GridArranger"
SPEC = ROOT / "packaging" / "GridArranger.spec"
ISS = ROOT / "packaging" / "GridArranger.iss"
IS_WINDOWS = sys.platform == "win32"

README = """Grid Arranger for LightBurn {version}
=====================================
Build: {build}

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


def tool_env() -> dict:
    """Prostředí pro podprocesy: nástroje z .venv/Scripts (pyside6-lrelease…) i bez aktivace .venv."""
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    return env


def run(cmd: list[str]) -> None:
    print("> " + " ".join(cmd), flush=True)
    if subprocess.run(cmd, cwd=ROOT, env=tool_env()).returncode != 0:
        sys.exit("\nKrok selhal — popis chyby je výše.")


def version() -> str:
    """Verze ve tvaru SemVer (``0.1.0-alpha.1``) — stejná jako Git tag bez ``v`` a název ZIPu."""
    sys.path.insert(0, str(ROOT / "src"))
    from grid_arranger.version import display_version

    return display_version()


def _commit_from_files(root: Path) -> str | None:
    """Commit z ``.git`` bez příkazu git (GitHub Desktop git do PATH nepřidává)."""
    git = root / ".git"
    try:
        head = (git / "HEAD").read_text(encoding="ascii").strip()
        if not head.startswith("ref: "):
            return head[:7]
        ref = head[5:]
        if (git / ref).is_file():
            return (git / ref).read_text(encoding="ascii").strip()[:7]
        for line in (git / "packed-refs").read_text(encoding="ascii").splitlines():
            if line.endswith(" " + ref):
                return line.split()[0][:7]
    except OSError:
        pass
    return None


def git_state(root: Path = ROOT) -> tuple[str | None, bool | None]:
    """(zkrácený commit, necommitnuté změny?) — ``None`` = nelze zjistit."""
    try:
        head = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=root, capture_output=True, text=True)
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=root, capture_output=True, text=True)
        if head.returncode == 0:
            return head.stdout.strip(), bool(dirty.stdout.strip())
    except OSError:
        pass
    return _commit_from_files(root), None


def self_test(exe: Path) -> dict:
    report = DIST / "selftest-report.json"
    if report.exists():
        report.unlink()
    env = tool_env()
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


def ensure_not_running() -> None:
    """Spuštěná aplikace z dist/ drží zamčené DLL a PyInstaller by spadl uprostřed — zjistit předem."""
    if not APP_DIR.exists():
        return
    probe = APP_DIR.with_name(APP_DIR.name + ".lockcheck")
    try:
        APP_DIR.rename(probe)  # na Windows selže, pokud je některý soubor ve složce otevřený
        probe.rename(APP_DIR)
    except OSError:
        sys.exit(f"Složku {APP_DIR} nelze přepsat — nejspíš z ní běží GridArranger.exe.\n"
                 "Zavřete všechna okna Grid Arrangeru (případně ve Správci úloh ukončete GridArranger.exe) a spusťte sestavení znovu.")


def find_iscc() -> Path | None:
    """Kompilátor Inno Setup: PATH nebo obvyklá místa instalace (i per-user instalace přes winget)."""
    import shutil

    found = shutil.which("ISCC") or shutil.which("iscc")
    if found:
        return Path(found)
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")):
        if base:
            p = Path(base) / "Inno Setup 6" / "ISCC.exe"
            if p.is_file():
                return p
    return None


def make_installer(iscc: Path, ver: str) -> Path:
    import re

    numeric = ".".join(re.findall(r"\d+", ver)[:3]) + ".0"
    target = DIST / f"GridArranger-Setup-v{ver}-win-x64.exe"
    if target.exists():
        target.unlink()
    run([str(iscc), "/Q", f"/DAppVersion={ver}", f"/DVersionNumeric={numeric}",
         f"/DSourceDir={APP_DIR}", f"/DOutputDir={DIST}", str(ISS)])
    if not target.is_file():
        sys.exit(f"Inno Setup nevytvořil {target.name}.")
    return target


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
    ap.add_argument("--no-installer", action="store_true", help="nevytvářet instalátor (jen ZIP)")
    a = ap.parse_args()
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("PyInstaller není nainstalovaný. V aktivním .venv spusťte: python -m pip install -e .[dev,build]")
    if not IS_WINDOWS:
        print("Upozornění: nejde o Windows — vznikne jen zkušební linuxové sestavení, ne GridArranger.exe.")
    ver = version()
    set_output_dir(ver)
    iscc = None
    if IS_WINDOWS and not a.no_installer:
        iscc = find_iscc()
        if iscc is None:
            sys.exit("Nebyl nalezen Inno Setup 6 (ISCC.exe), potřebný pro instalátor.\n"
                     "Nainstalujte ho jednou příkazem:  winget install JRSoftware.InnoSetup\n"
                     "nebo z https://jrsoftware.org/isdl.php  — případně sestavte jen ZIP: build_exe.bat --no-installer")

    step("1/6 Překlady")
    run([sys.executable, "tools/build_translations.py", "--no-update"])

    commit, dirty = git_state()
    build = f"commit {commit}" + (" + uncommitted changes" if dirty else "") if commit else "commit unknown"
    if dirty:
        print("Upozornění: v repozitáři jsou necommitnuté změny — ZIP nebude odpovídat žádnému commitu/tagu.\n"
              "            Pro vydání nejdřív commitněte a sestavte znovu.")
    elif dirty is None:
        print(f"Poznámka: sestavuje se z {build}; necommitnuté změny nelze ověřit (git není v PATH).\n"
              "          Pro vydání musí být v GitHub Desktop prázdný seznam Changes.")

    if a.skip_tests:
        step("2/6 Testy — přeskočeno (--skip-tests)")
    else:
        step("2/6 Testy")
        run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"])

    step("3/6 PyInstaller")
    ensure_not_running()
    run([sys.executable, "-m", "PyInstaller", str(SPEC), "--noconfirm", "--clean",
         "--distpath", str(DIST), "--workpath", str(BUILD)])
    enc = "utf-8-sig" if IS_WINDOWS else "utf-8"
    (APP_DIR / "README.txt").write_text(README.format(version=ver, build=build), encoding=enc)

    step("4/6 Samokontrola zabalené aplikace")
    exe = APP_DIR / ("GridArranger.exe" if IS_WINDOWS else "GridArranger")
    report = self_test(exe)
    notices = (ROOT / "packaging" / "THIRD_PARTY_NOTICES.txt").read_text(encoding="utf-8")
    (APP_DIR / "THIRD_PARTY_NOTICES.txt").write_text(
        notices.format(version=ver, python=report["python"], qt=report["qt"], pyside=report["pyside6"]), encoding=enc)
    (APP_DIR / "LICENSE.txt").write_text((ROOT / "LICENSE").read_text(encoding="utf-8"), encoding=enc)

    step("5/6 ZIP")
    z = make_zip(ver)
    artifacts = [z]
    if iscc is not None:
        step("6/6 Instalátor (Inno Setup)")
        artifacts.insert(0, make_installer(iscc, ver))
    else:
        step("6/6 Instalátor — přeskočeno" + (" (--no-installer)" if a.no_installer else " (jen na Windows)"))
    sums = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in artifacts}
    (DIST / "SHA256SUMS.txt").write_text("".join(f"{h}  {n}\n" for n, h in sums.items()), encoding="ascii")
    notes_src = ROOT / "docs" / "releases" / f"v{ver}.md"
    if notes_src.is_file():
        (DIST / "RELEASE_NOTES.md").write_text(notes_src.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        print(f"Upozornění: chybí popis vydání docs/releases/v{ver}.md (potřebný pro GitHub Release).")
    size = sum(f.stat().st_size for f in APP_DIR.rglob("*") if f.is_file())
    print(f"\nHotovo — Grid Arranger {ver} (Qt {report['qt']}, Python {report['python']})")
    print(f"  Složka verze: {DIST}")
    print(f"  Aplikace: {exe}  (složka {size / 1e6:.0f} MB)")
    print(f"  ZIP:      {z}  ({z.stat().st_size / 1e6:.0f} MB)")
    for f in artifacts[:-1]:
        print(f"  Instalátor: {f}  ({f.stat().st_size / 1e6:.0f} MB)")
    print(f"  SHA-256:  {DIST / 'SHA256SUMS.txt'} ({len(sums)} soubory)")
    print(f"  Sestaveno z: {build}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
