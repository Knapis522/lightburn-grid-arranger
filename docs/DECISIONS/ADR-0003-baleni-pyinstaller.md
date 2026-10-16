# ADR-0003: Balení aplikace nástrojem PyInstaller (přenosná složka)

**Stav:** přijato 2026-10-16, podmíněně — potvrdit po GH-05 (EXE na čistém Windows bez Pythonu).
**Souvisí:** spec. kap. 30 (distribuce), 34 (GH-05), 38 (HELP-01), 36.6 (T-I18N-16).

## Kontext

Specifikace požaduje offline Windows aplikaci bez nutnosti instalovat Python, nejprve jako přenosnou složku s `GridArranger.exe` a ZIP; nástroj „přednostně PyInstaller nebo `pyside6-deploy`, volbu uzamknout po experimentálním build testu“.

## Rozhodnutí

PyInstaller 6, režim **onedir** (složka `GridArranger/` s `GridArranger.exe` a `_internal/`), okenní aplikace bez konzole, bez UPX. Konfigurace v `packaging/GridArranger.spec`, sestavení výhradně přes `tools/build_exe.py`, které po zabalení spustí **samokontrolu přímo v zabalené aplikaci** (`--self-test`) a bez jejího úspěchu ZIP nevytvoří.

Důvody:

- PyInstaller má udržované hooky pro PySide6 a nepotřebuje překladač C (`pyside6-deploy` je postavený na Nuitce: pomalé sestavení, nutný MSVC).
- Onedir je spolehlivější a rychleji startuje než onefile (nerozbaluje se do `%TEMP%`, méně planých poplachů antiviru). Onefile/instalátor až po samostatném ověření (spec. kap. 30).
- Data (příručka, `.qm`, ikona) se přibalují na stejné relativní cesty jako ve zdrojích, kód je hledá přes `Path(__file__)` — žádná zvláštní větev pro zabalený běh.
- Zúžení Qt: vyřazeny pluginy a knihovny, které aplikace nepoužívá (Qml/Quick/VirtualKeyboard/Pdf/Network, softwarové OpenGL, katalogy Qt mimo 8 plánovaných jazyků). Případnou chybějící knihovnu odhalí samokontrola.

## Důsledky

- EXE pro Windows lze sestavit jen na Windows (PyInstaller neumí křížové sestavení); sestavuje vlastník na svém PC skriptem `tools\build_exe.bat`. Později lze doplnit GitHub Actions (`windows-latest`).
- Aplikace není podepsaná — Windows SmartScreen může varovat; podpis až před veřejnou distribucí.
- Před veřejným vydáním doplnit `THIRD_PARTY_NOTICES.md` (PySide6/Qt LGPLv3, Python) a ověřit licenční povinnosti (spec. kap. 30).
- Zkušební sestavení na Linuxu (2026-10-16, PyInstaller 6.22, PySide6 6.12, Python 3.13): samokontrola 5/5.
