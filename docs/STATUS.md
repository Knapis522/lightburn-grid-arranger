# Stav projektu

**Aktualizováno:** 2026-10-16
**Verze specifikace:** 1.9 (`docs/specification.md`)
**Verze aplikace:** žádná (nic není implementováno)

> Tento soubor je hlavní předávací dokument. Při navázání práce: přečíst tento soubor → `ROADMAP.md` → relevantní kapitolu specifikace. Nepředpokládat, že funkce funguje jen proto, že existuje kód.

## Přehled

| Hotovo | Probíhá | Blokováno | Další |
|---|---|---|---|
| Specifikace v1.8; **GIT-00 splněno** (soukromý repozitář `Knapis522/lightburn-grid-arranger`, GH-01 + GH-02, commity `55ab47e`, `5e94c06`); **DOC-00 splněno** | **KAL-00 splněno** (LightBurn 2.2.00-RC-7; oba lasery); **CORE-00 implementováno a automaticky otestováno** (143 testů, Python 3.12 i 3.13); spec. v1.9 | — | Testy zatím neběžely na tvém Windows (chybí Python) | ADAPT-00: čtení `.lbrn2` → `Item`/`Obstacle`, převod souřadnic, bajtový zápis, diff, negativní testy |

## Implementováno / otestováno

| Požadavek | Implementováno | Otestováno | Akceptováno |
|---|---|---|---|
| MVP-01 mřížka (jádro, adaptivní) | ano (`core/grid_layout.py`) | ano — ALG-01…10, T-MVP-01…04 | ne (chybí adaptér a ověření v LightBurnu) |
| MVP-02/03 výběr a pořadí (jádro) | ano (`core/order.py`) | ano — T-MVP-05, 06, 08…10 | ne (chybí GUI) |
| MVP-04 materiál a kolize (jádro) | ano (`core/collision.py`) | ano — T-MVP-11…18 | ne (překážky z reálného souboru až v ADAPT-00) |

## Otevřená rozhodnutí

- Žádná. Rozhodnutí z 16. 10. 2026 zapsána ve specifikaci v1.8 (kap. 28).
- Vývojové prostředí na Windows: Python 3.12+ zatím neověřen (potřebný pro vývoj a sestavení EXE, ne pro uživatele).

## Poslední ověřený stav / co zkusit dál

- Ověřeno: čtení struktury `.lbrn2` 2.2.00; převod souřadnic pro `MirrorX/MirrorY` True/True i False/True (přepnutí laseru mění jen příznak, ne souřadnice); přesun skupiny bajtovým patchem (2 řádky) odpovídá LightBurnu a výsledek se v LightBurnu otevřel správně.
- Prototypové skripty KAL-00 jsou v `tools/kal00/` (jen diagnostika, nejsou součástí aplikace); čistá implementace vznikne v ADAPT-00.
- CORE-00: testy prošly v pracovním prostředí (Linux, Python 3.12 a 3.13); kontrolní mutace výpočtu (poloviční mezery) byla testy zachycena (114 selhání). Na Windows zatím nespuštěno — postup v `docs/DEVELOPMENT.md`.
- Další bezpečný krok: ADAPT-00 — `adapters/lightburn/read.py` (skupiny, obrysy, BackupPath, Mirror, DeviceName), převod souřadnic, `write.py` dle ADR-0002, `safety/verify.py`, testy na syntetických `.lbrn2`.
