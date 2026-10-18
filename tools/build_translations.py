"""Aktualizace a sestavení překladů (spec. kap. 36.3, T-I18N-14).

    python tools/build_translations.py            # lupdate + kontrola + lrelease
    python tools/build_translations.py --no-update  # jen kontrola + lrelease

``translations/*.ts`` jsou zdroj (verzováno v Gitu, editace v Qt Linguist).
``src/grid_arranger/gui/translations/*.qm`` jsou výstup (negitují se, přibalí se do EXE).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TS_DIR = ROOT / "translations"
QM_DIR = ROOT / "src" / "grid_arranger" / "gui" / "translations"
SOURCES = sorted((ROOT / "src" / "grid_arranger" / "gui").glob("*.py"))
REQUIRED_COMPLETE = ("cs", "de", "sk", "pl", "fr", "es", "it")  # všech osm jazyků (en = zdroj)

sys.path.insert(0, str(ROOT / "src"))
from grid_arranger.gui.catalog_check import check_catalog  # noqa: E402


def _tool(name: str) -> str:
    # Nejdřív vedle běžícího Pythonu (.venv\Scripts) — funguje i bez aktivace .venv.
    exe = shutil.which(name, path=str(Path(sys.executable).parent)) or shutil.which(name)
    if not exe:
        sys.exit(f"Nástroj {name} nebyl nalezen — je nainstalovaný PySide6 a aktivní .venv?")
    return exe


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-update", action="store_true")
    a = ap.parse_args()
    ts_files = sorted(TS_DIR.glob("gridarranger_*.ts"))
    if not a.no_update:
        subprocess.run([_tool("pyside6-lupdate"), *map(str, SOURCES), "-ts", *map(str, ts_files)], check=True)
    failed = False
    for ts in ts_files:
        lang = ts.stem.split("_", 1)[1]
        problems = check_catalog(ts, require_complete=lang in REQUIRED_COMPLETE)
        for p in problems:
            print(f"{ts.name}: {p}")
        failed |= bool(problems)
    if failed:
        print("Překlady nejsou v pořádku — .qm nesestaveny.")
        return 1
    QM_DIR.mkdir(parents=True, exist_ok=True)
    for ts in ts_files:
        subprocess.run([_tool("pyside6-lrelease"), str(ts), "-qm", str(QM_DIR / (ts.stem + ".qm"))], check=True)
    print(f"Hotovo: {len(ts_files)} katalogů → {QM_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
