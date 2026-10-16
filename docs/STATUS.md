# Stav projektu

**Aktualizováno:** 2026-10-16
**Verze specifikace:** 1.9 (`docs/specification.md`)
**Verze aplikace:** žádná (nic není implementováno)

> Tento soubor je hlavní předávací dokument. Při navázání práce: přečíst tento soubor → `ROADMAP.md` → relevantní kapitolu specifikace. Nepředpokládat, že funkce funguje jen proto, že existuje kód.

## Přehled

| Hotovo | Probíhá | Blokováno | Další |
|---|---|---|---|
| Specifikace v1.8; **GIT-00 splněno** (soukromý repozitář `Knapis522/lightburn-grid-arranger`, GH-01 + GH-02, commity `55ab47e`, `5e94c06`); **DOC-00 splněno** | KAL-00 splněno; CORE-00 a **ADAPT-00 implementováno a automaticky otestováno** (205 testů + 3 regresní na reálných souborech); vývojářská CLI; zkušební rozmístění V-001 do mřížky 3 × 3 | Ruční kontrola zkušebního výstupu v LightBurnu (T-MVP-26) | Testy zatím neběžely na Windows (chybí Python) | Po kontrole výstupu: GUI-00 (PySide6) + MVP-07 (cs/en) + HELP-01 |

## Implementováno / otestováno

| Požadavek | Implementováno | Otestováno | Akceptováno |
|---|---|---|---|
| MVP-01 mřížka (jádro, adaptivní) | ano (`core/grid_layout.py`) | ano — ALG-01…10, T-MVP-01…04 | ne (chybí adaptér a ověření v LightBurnu) |
| MVP-02/03 výběr a pořadí (jádro) | ano (`core/order.py`) | ano — T-MVP-05, 06, 08…10 | ne (chybí GUI) |
| MVP-04 materiál a kolize | ano (`core/collision.py`, překážky z adaptéru) | ano — T-MVP-11…18, LB-05 | ne (chybí GUI) |
| MVP-05 bezpečné uložení a validace | ano (`adapters/lightburn/write.py`, `safety/verify.py`, `application/arrange_job.py`) | ano — T-MVP-19…25, T-FMT-01…05, 07 | ne (čeká T-MVP-26 ruční kontrola v LightBurnu) |
| Formát `.lbrn2` (čtení, orientace) | ano (`adapters/lightburn/read.py`, `coords.py`) | ano — LB-01…06, 08, 10, 11 | částečně (V-001 ověřen v LightBurnu přes prototyp) |

## Otevřená rozhodnutí

- Žádná. Rozhodnutí z 16. 10. 2026 zapsána ve specifikaci v1.8 (kap. 28).
- Vývojové prostředí na Windows: Python 3.12+ zatím neověřen (potřebný pro vývoj a sestavení EXE, ne pro uživatele).

## Poslední ověřený stav / co zkusit dál

- Ověřeno: čtení struktury `.lbrn2` 2.2.00; převod souřadnic pro `MirrorX/MirrorY` True/True i False/True (přepnutí laseru mění jen příznak, ne souřadnice); přesun skupiny bajtovým patchem (2 řádky) odpovídá LightBurnu a výsledek se v LightBurnu otevřel správně.
- Prototypové skripty KAL-00 jsou v `tools/kal00/` (jen diagnostika, nejsou součástí aplikace); čistá implementace vznikne v ADAPT-00.
- CORE-00: testy prošly v pracovním prostředí (Linux, Python 3.12 a 3.13); kontrolní mutace výpočtu (poloviční mezery) byla testy zachycena (114 selhání). Na Windows zatím nespuštěno — postup v `docs/DEVELOPMENT.md`.
- ADAPT-00: zkušební výstup `test program …__grid_001.lbrn2` (9 kartiček, 3 sloupce, mezera 5 mm, změněno 18 řádků, kontrola prošla) je ve složce s daty; čeká na otevření v LightBurnu.
- Další bezpečný krok: otevřít zkušební výstup v LightBurnu (File → Open), zkontrolovat mřížku, texty, vrstvy, Preview; potom GUI-00.
