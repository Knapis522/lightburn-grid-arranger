# Vývoj

## Požadavky

- Windows 10/11 x64, **Python 3.12 nebo novější** (jen pro vývoj a sestavení; uživatelé aplikace Python nepotřebují).
- GitHub Desktop pro commit/push.

## První nastavení (jednou)

V příkazovém řádku (`cmd`) ve složce projektu:

```bat
cd %USERPROFILE%\Documents\Claude\Projects\lightburn-grid-arranger
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install -e .[dev]
```

Složka `.venv` je v `.gitignore` a do Gitu se nedostane.

Po změně závislostí (např. přidání PySide6) příkaz `python -m pip install -e .[dev]` zopakujte.

## Spuštění aplikace (okno)

```bat
.venv\Scripts\activate
python tools\build_translations.py --no-update
python -m grid_arranger.gui
```

- `build_translations.py` zkontroluje katalogy `translations\*.ts` a sestaví `.qm` (bez nich aplikace běží anglicky).
- Po změně textů v GUI spusťte `python tools\build_translations.py` (bez `--no-update`) — doplní nové texty do `.ts`; chybějící český překlad zastaví sestavení. Překlady se upravují v Qt Linguist (`pyside6-linguist translations\gridarranger_cs.ts`).
- Příručka (F1) je v `src\grid_arranger\gui\help\cs` a `…\en` (Markdown, stejná témata v obou jazycích).

## Spuštění testů

```bat
.venv\Scripts\activate
python -m pytest
```

Očekávaný výsledek: všechny testy `passed` (3 regresní testy na reálných souborech se bez nastavení přeskočí). Testy používají jen syntetické projekty generované v `tests/integration/lbrn2_builder.py`.

Regresní testy na skutečných projektech (mimo Git):

```bat
set GRID_ARRANGER_REAL_DATA=..\lightburn-grid-arranger-data
python -m pytest tests\integration\test_real_projects.py
```

## Sestavení GridArranger.exe, instalátoru a ZIPu

**Jednou předem:** nainstalovat Inno Setup 6.3+ (sestavuje instalátor):

```bat
winget install JRSoftware.InnoSetup
```

(nebo instalátor z https://jrsoftware.org/isdl.php). Skript ho najde sám v obvyklých složkách.

**Sestavení:** dvojklik na `tools\build_exe.bat` (nebo totéž z příkazového řádku ve složce projektu). Skript:

1. doinstaluje do `.venv` PyInstaller (`pip install -e .[dev,build]`),
2. sestaví překlady `.qm`,
3. spustí všechny testy (selhání sestavení zastaví),
4. zabalí aplikaci podle `packaging\GridArranger.spec` (PyInstaller, složka, bez konzole),
5. spustí **samokontrolu** zabalené aplikace `GridArranger.exe --self-test` (příručka F1 cs/en, překlady včetně tlačítek Qt, ikona, okno, načtení → rozložení → zápis → kontrola na syntetickém projektu, HTTPS pro aktualizace),
6. vytvoří ZIP, **instalátor** (`packaging\GridArranger.iss`, Inno Setup) a `SHA256SUMS.txt`, otevře složku `dist`.

Výsledek — vše pro jednu verzi pohromadě ve složce s číslem verze:

```text
dist\v0.1.0-alpha.2\
    GridArranger-Setup-v0.1.0-alpha.2-win-x64.exe  ← instalátor (hlavní podoba)
    GridArranger-v0.1.0-alpha.2-win-x64.zip        ← záložní přenosná verze
    SHA256SUMS.txt                                 ← kontrolní součty obou (aplikace podle nich ověřuje aktualizace)
    RELEASE_NOTES.md                               ← text pro GitHub Release (kopie docs\releases\v<verze>.md)
    GridArranger\GridArranger.exe                  ← rozbalená aplikace (vedle musí zůstat _internal)
    selftest-report.json                           ← výsledek samokontroly
```

- `build\` a `dist\` jsou generované (v `.gitignore`). Složky starších verzí v `dist` zůstávají; sestavení stejné verze její složku přepíše. Z `dist\v…\GridArranger` aplikaci před dalším sestavením zavřete (zamčené soubory skript ohlásí). Instalátor ani ZIP se do Gitu nedávají; přikládají se ke GitHub Release.
- Bez Inno Setup: `tools\build_exe.bat --no-installer` (jen ZIP). Rychlá zkouška bez testů: `--skip-tests`.
- PyInstaller i Inno Setup sestavují jen na Windows (na Linuxu jde jen o zkoušku balení, bez instalátoru).
- Instalátor: instalace jen pro aktuálního uživatele do `%LOCALAPPDATA%\Programs\Grid Arranger`, bez práv správce; nová verze se instaluje přes starou, nastavení (registr) zůstává. `AppId` v `.iss` se nesmí nikdy změnit.
- Samokontrolu lze spustit i na cílovém počítači: `GridArranger.exe --self-test report.json`.
- Windows SmartScreen může nepodepsaný instalátor zablokovat: „Další informace → Přesto spustit“.
- Ikonu (`packaging\GridArranger.ico`, `src\grid_arranger\gui\resources\app_icon.png`) vytváří `tools\make_icon.py` (vyžaduje Pillow); běžně se negeneruje.
- Rozhodnutí: `docs/DECISIONS/ADR-0003-baleni-pyinstaller.md`, `ADR-0004-instalator-a-aktualizace.md`.

## Aktualizace aplikace

- Logika `src\grid_arranger\updates.py` (bez Qt), okna `gui\updates_ui.py`; zdroj GitHub Releases přes anonymní API — funguje až u **veřejného** repozitáře (do té doby ruční kontrola hlásí „žádná veřejná vydání“).
- Vydání musí obsahovat `GridArranger-Setup-v<verze>-win-x64.exe` a `SHA256SUMS.txt`, jinak aplikace nabídne jen stránku ke stažení.
- Nastavení → Aktualizace (automaticky / předběžné verze), Nápověda → Zkontrolovat aktualizace. Hodnoty v registru `HKCU\Software\GridArranger\GridArranger\updates`.

Vydání na GitHub (tag, Release, kontrolní součty): `docs/RELEASE_CHECKLIST.md`.

**Ruční test GH-05 / T-I18N-16 / HELP-01 / T-UPD-07** na počítači bez Pythonu: nainstalovat instalátorem → spustit → přepnout jazyk cs/en → F1 → otevřít reálný projekt → uložit `__grid_NNN` → otevřít v LightBurnu (File → Open). Výsledek zapsat do `docs/TEST_PLAN.md`.

## Vývojářská příkazová řádka

```bat
python -m grid_arranger info "..\lightburn-grid-arranger-data\projekt.lbrn2"
python -m grid_arranger arrange "..\lightburn-grid-arranger-data\projekt.lbrn2" --columns 3 --gap 5 --board 700 500 --dry-run
```

- `--board Š V` = deska u počátku laseru (`--board-at X Y` jiný roh desky), `--margin` výchozí 5 mm (jedna hodnota nebo L P H D).
- `--anchor origin` (výchozí: roh mřížky do rohu desky u počátku), `center`, `manual` (+ `--start X Y` = roh mřížky u počátku v souřadnicích LightBurnu), `selection` (původní poloha).
- `--fill origin` (výchozí: 1. výrobek v rohu počátku laseru) nebo `reading` (vlevo nahoře).
- `--order G3,G1,G2` = výběr a pořadí; bez něj všechny podporované v pořadí dokumentu.
- Bez `--dry-run` vznikne nový `…__grid_001.lbrn2` a protokol `.json` vedle originálu.

## Testovací data

- Automatické testy: jen syntetická data (`tests/unit/helpers.py`, později `tests/fixtures/synthetic/`).
- Reálné projekty: mimo Git v `..\lightburn-grid-arranger-data\`.
- Diagnostické prototypy KAL-00: `tools/kal00/` (nejsou součástí aplikace).

## Pravidla

- Každá změna kódu ve stejném commitu aktualizuje testy a dotčenou dokumentaci (DOC-01, spec. kap. 37.3).
- `domain/` a `core/` nesmí importovat Qt ani adaptér.
- Commit zprávy (Summary i Description v GitHub Desktop) psát **anglicky** a začínat ID požadavku (`CORE-00: …`, `EXE-00: …`).
