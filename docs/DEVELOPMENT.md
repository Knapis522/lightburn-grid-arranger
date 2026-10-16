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
python -m grid_arranger arrange "..\lightburn-grid-arranger-data\projekt.lbrn2" --columns 3 --gap 5 --material 0 0 1300 900 --margin 5 --dry-run
```

- Souřadnice `--start X Y` (levý horní roh mřížky na obrazovce) a `--material X Y Š V` jsou **hodnoty z LightBurnu**.
- Bez `--start` začne mřížka v levém horním rohu vybraných výrobků.
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
