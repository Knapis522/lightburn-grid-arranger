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
- Commit zprávy začínat ID požadavku (`CORE-00: …`, `MVP-04: …`).
