# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller: přenosná složka GridArranger/ s GridArranger.exe (spec. kap. 30, ADR-0003).

Nespouštět přímo — použijte ``python tools/build_exe.py`` (sestaví překlady, spustí testy,
zabalí, provede samokontrolu a vytvoří ZIP).
"""

import re
import sys
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
SRC = ROOT / "src"
PKG = SRC / "grid_arranger"

sys.path.insert(0, str(SRC))
from grid_arranger.version import display_version  # noqa: E402

VERSION = display_version()  # SemVer, např. 0.1.0-alpha.1

# Data aplikace: příručka F1, překlady, ikona — na stejné relativní cesty jako ve zdrojích,
# aby je kód našel přes Path(__file__) i v zabalené podobě (HELP-01).
datas = []
for pattern in ("gui/help/*/*.md", "gui/translations/*.qm", "gui/resources/*.png"):
    for f in sorted(PKG.glob(pattern)):
        datas.append((str(f), str(f.parent.relative_to(SRC))))
if not any(d[0].endswith(".qm") for d in datas):
    raise SystemExit("Chybí .qm překlady — spusťte python tools/build_translations.py --no-update")

version_file = None
if sys.platform == "win32":
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
    )

    nums = tuple(int(n) for n in re.findall(r"\d+", VERSION)[:3]) + (0,)
    version_file = VSVersionInfo(
        ffi=FixedFileInfo(filevers=nums, prodvers=nums),
        kids=[
            StringFileInfo([StringTable("040904B0", [
                StringStruct("ProductName", "Grid Arranger for LightBurn"),
                StringStruct("FileDescription", "Grid Arranger for LightBurn (unofficial tool)"),
                StringStruct("FileVersion", VERSION),
                StringStruct("ProductVersion", VERSION),
                StringStruct("OriginalFilename", "GridArranger.exe"),
                StringStruct("InternalName", "GridArranger"),
            ])]),
            VarFileInfo([VarStruct("Translation", [0x0409, 1200])]),
        ],
    )

a = Analysis(
    [str(ROOT / "packaging" / "gridarranger_entry.py")],
    pathex=[str(SRC)],
    datas=datas,
    hiddenimports=["grid_arranger.gui.selftest"],
    excludes=["tkinter", "pytest", "PIL", "numpy", "setuptools"],
    noarchive=False,
)

# Zúžení balíčku: aplikace potřebuje jen QtCore/QtGui/QtWidgets. Pluginy níže by kvůli
# vlastním závislostem přitáhly Qml/Quick/VirtualKeyboard/Pdf/Network (desítky MB).
# Případnou chybějící knihovnu odhalí samokontrola v tools/build_exe.py.
QT_LANGS = ("cs", "en", "de", "sk", "pl", "fr", "es", "it")  # spec. kap. 36 — budoucí jazyky
DROP_PARTS = (
    "opengl32sw",  # softwarové OpenGL; náhled kreslí rastrově
    "Qt6Qml", "Qt6Quick", "Qt6VirtualKeyboard", "Qt6Pdf", "Qt6Network",
    "/platforminputcontexts/", "/networkinformation/", "/tls/", "/generic/", "/qpdf",
)


def _keep(dest: str) -> bool:
    d = "/" + dest.replace("\\", "/")
    if any(p in d for p in DROP_PARTS):
        return False
    if "/PySide6/" in d and "/translations/" in d and d.endswith(".qm"):  # jen katalogy Qt, ne vlastní
        name = d.rsplit("/", 1)[1]
        return name.startswith("qtbase_") and name[7:-3] in QT_LANGS
    return True


a.binaries = [b for b in a.binaries if _keep(b[0])]
a.datas = [d for d in a.datas if _keep(d[0])]
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="GridArranger",
    console=False,  # okenní aplikace bez černého okna konzole
    icon=str(ROOT / "packaging" / "GridArranger.ico"),
    version=version_file,
    upx=False,  # UPX zvyšuje riziko planých poplachů antiviru
)
coll = COLLECT(exe, a.binaries, a.datas, name="GridArranger", upx=False)
