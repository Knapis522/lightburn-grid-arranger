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

Očekávaný výsledek: všechny testy `passed`. Testy jádra nepotřebují LightBurn ani žádný `.lbrn2`.

## Testovací data

- Automatické testy: jen syntetická data (`tests/unit/helpers.py`, později `tests/fixtures/synthetic/`).
- Reálné projekty: mimo Git v `..\lightburn-grid-arranger-data\`.
- Diagnostické prototypy KAL-00: `tools/kal00/` (nejsou součástí aplikace).

## Pravidla

- Každá změna kódu ve stejném commitu aktualizuje testy a dotčenou dokumentaci (DOC-01, spec. kap. 37.3).
- `domain/` a `core/` nesmí importovat Qt ani adaptér.
- Commit zprávy začínat ID požadavku (`CORE-00: …`, `MVP-04: …`).
