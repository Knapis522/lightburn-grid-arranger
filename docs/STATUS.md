# Stav projektu

**Aktualizováno:** 2026-10-16
**Verze specifikace:** 1.9 (`docs/specification.md`)
**Verze aplikace:** žádná (nic není implementováno)

> Tento soubor je hlavní předávací dokument. Při navázání práce: přečíst tento soubor → `ROADMAP.md` → relevantní kapitolu specifikace. Nepředpokládat, že funkce funguje jen proto, že existuje kód.

## Přehled

| Hotovo | Probíhá | Blokováno | Další |
|---|---|---|---|
| Specifikace v1.8; **GIT-00 splněno** (soukromý repozitář `Knapis522/lightburn-grid-arranger`, GH-01 + GH-02, commity `55ab47e`, `5e94c06`); **DOC-00 splněno** | **KAL-00 splněno** (LightBurn 2.2.00-RC-7; oba lasery; prototyp zápisu ověřen otevřením v LightBurnu); spec. v1.9 | — | — | CORE-00 (algoritmus mřížky + testy ALG-*), poté ADAPT-00 (čtečka, zápis, diff, negativní testy) |

## Implementováno / otestováno

| Požadavek | Implementováno | Otestováno | Akceptováno |
|---|---|---|---|
| — | — | — | — |

## Otevřená rozhodnutí

- Žádná. Rozhodnutí z 16. 10. 2026 zapsána ve specifikaci v1.8 (kap. 28).
- Vývojové prostředí na Windows: Python 3.12+ zatím neověřen (potřebný pro vývoj a sestavení EXE, ne pro uživatele).

## Poslední ověřený stav / co zkusit dál

- Ověřeno: čtení struktury `.lbrn2` 2.2.00; převod souřadnic pro `MirrorX/MirrorY` True/True i False/True (přepnutí laseru mění jen příznak, ne souřadnice); přesun skupiny bajtovým patchem (2 řádky) odpovídá LightBurnu a výsledek se v LightBurnu otevřel správně.
- Prototypové skripty KAL-00 jsou v `tools/kal00/` (jen diagnostika, nejsou součástí aplikace); čistá implementace vznikne v ADAPT-00.
- Další bezpečný krok: CORE-00 — `pyproject.toml`, `src/grid_arranger/domain` + `core`, pytest ALG-01…10 a T-MVP-01…04.
