# Stav projektu

**Aktualizováno:** 2026-10-17
**Verze specifikace:** 1.11 (`docs/specification.md`)
**Verze aplikace:** `0.1.0-alpha.1` — první interní předběžné vydání **zveřejněno** 2026-10-16 jako GitHub Pre-release (tag `v0.1.0-alpha.1`, commit `64a5d00`)

> Tento soubor je hlavní předávací dokument. Při navázání práce: přečíst tento soubor → `ROADMAP.md` → relevantní kapitolu specifikace. Nepředpokládat, že funkce funguje jen proto, že existuje kód.

## Přehled

| Hotovo | Probíhá | Blokováno | Další |
|---|---|---|---|
| GIT-00, DOC-00, KAL-00; CORE-00 a ADAPT-00 (T-MVP-26 ověřeno vlastníkem pro `__grid_001` i `__grid_002`); **GUI-00 ověřeno vlastníkem na Windows** (okno, motivy, prohození tažením, světlý/tmavý vzhled, zoom; 2026-10-16) | **EXE-00 / GH-05:** sestavení přenosné složky `GridArranger/` přes PyInstaller (`tools\build_exe.bat`) se samokontrolou; **sestaveno na Windows vlastníka** (samokontrola 5/5 v `GridArranger.exe`, ZIP 28 MB); 286 testů | — | Commit + vydání `v0.1.0-alpha.2` (instalátor, ZIP, SHA256SUMS); instalátor u laseru bez Pythonu (GH-05, T-I18N-16, HELP-01); pak ostrý provoz → MVP-ACCEPT |

## Implementováno / otestováno

| Požadavek | Implementováno | Otestováno | Akceptováno |
|---|---|---|---|
| MVP-01 mřížka (jádro, adaptivní) | ano (`core/grid_layout.py`) | ano — ALG-01…10, T-MVP-01…04 | ne (chybí adaptér a ověření v LightBurnu) |
| MVP-02/03 výběr a pořadí | ano (`core/order.py`, GUI: zaškrtávání, Nahoru/Dolů, přetažení v náhledu) | ano — T-MVP-05, 06, 08…10, testy GUI | ne (ruční test na Windows) |
| MVP-04 materiál a kolize | ano (`core/collision.py`, překážky z adaptéru) | ano — T-MVP-11…18, LB-05 | ne (chybí GUI) |
| MVP-06 okno (GUI) | ano (`gui/`); balení `packaging/`, `tools/build_exe.py` | ano — `tests/gui` (offscreen), samokontrola sestavení | ne (okno ověřeno vlastníkem; čeká EXE na PC bez Pythonu) |
| MVP-07 jazyk cs/en | ano (`gui/i18n.py`, `translations/`) | ano — T-I18N-01…04, 07…15 | ne (T-I18N-05, 06, 16 ruční / EXE) |
| MVP-08 příručka F1 cs/en | ano (`gui/help.py`, `gui/help/`) | ano — T-HELP-01…04, 09 | ne (T-HELP-05…08, 10 / EXE) |
| MVP-05 bezpečné uložení a validace | ano (`adapters/lightburn/write.py`, `safety/verify.py`, `application/arrange_job.py`) | ano — T-MVP-19…25, T-FMT-01…05, 07 | ne (čeká T-MVP-26 ruční kontrola v LightBurnu) |
| Formát `.lbrn2` (čtení, orientace) | ano (`adapters/lightburn/read.py`, `coords.py`) | ano — LB-01…06, 08, 10, 11 | částečně (V-001 ověřen v LightBurnu přes prototyp) |

## Otevřená rozhodnutí

- Žádná. Rozhodnutí z 16. 10. 2026 zapsána ve specifikaci v1.8 (kap. 28).
- Balicí nástroj: zvolen PyInstaller (ADR-0003); definitivně potvrdit po úspěšném GH-05 na Windows.

## Poslední ověřený stav / co zkusit dál

- Ověřeno: čtení struktury `.lbrn2` 2.2.00; převod souřadnic pro `MirrorX/MirrorY` True/True i False/True (přepnutí laseru mění jen příznak, ne souřadnice); přesun skupiny bajtovým patchem (2 řádky) odpovídá LightBurnu a výsledek se v LightBurnu otevřel správně.
- Prototypové skripty KAL-00 jsou v `tools/kal00/` (jen diagnostika, nejsou součástí aplikace); čistá implementace vznikne v ADAPT-00.
- CORE-00: testy prošly v pracovním prostředí (Linux, Python 3.12 a 3.13); kontrolní mutace výpočtu (poloviční mezery) byla testy zachycena (114 selhání). Na Windows zatím nespuštěno — postup v `docs/DEVELOPMENT.md`.
- ADAPT-00: `…__grid_001.lbrn2` (umístění podle původní polohy) ověřen vlastníkem v LightBurnu — vše sedí; připomínka: zarovnávat k počátku laseru → spec. v1.10. Vlastníkův ruční vzor `…__grid_001-zarovnani.lbrn2` (mřížka posunuta na desku 700 × 500).
- Desky vlastníka: červený laser (počátek vpravo nahoře) 700 × 500 mm, modrý (vlevo nahoře) 500 × 400 mm.
- `…__grid_002.lbrn2` (deska 700 × 500, okraj 5, roh počátku, plnění od počátku) ověřen vlastníkem v LightBurnu — sedí.
- Python 3.13.6 nainstalován na Windows vlastníka; `.venv` založen; testy jádra a adaptéru prošly na Windows (221 passed, 1 skipped — test jen pro POSIX).
- GUI-00: okno ověřeno automaticky (offscreen) a na snímcích (cs/en, blokace při přesahu desky, příručka). Na Windows: 268 testů prošlo, okno spuštěno vlastníkem. Podle jeho připomínek doplněno: náhled se skutečnými motivy v barvách vrstev, přeskládání kartiček tažením v náhledu.
- Podle připomínek doplněno a vlastníkem ověřeno na Windows: prohození dvou kartiček tažením, vzhled Nastavení → Vzhled (světlý = celá aplikace světlá; tmavý = tmavé ovládání, náhled světlý), plynulý zoom s mezemi.
- EXE-00: `tools\build_exe.bat` → překlady, testy, PyInstaller, samokontrola `GridArranger --self-test` (příručka, překlady vč. tlačítek Qt, ikona, okno, načtení → rozložení → zápis → kontrola na syntetickém projektu), ZIP. Zkušebně sestaveno na Linuxu (Qt 6.12, Python 3.13): samokontrola 5/5, aplikace se spustí. Na Windows sestaveno 2026-10-16 (Windows 11, Python 3.13.6, PySide6 6.12.0): samokontrola 5/5, ZIP `GridArranger-v0.1.0.dev0-win-x64.zip` 28 MB.
- Další bezpečný krok: vlastník spustí `tools\build_exe.bat`, ZIP rozbalí na počítači bez Pythonu (ideálně u laseru), vyzkouší F1, přepnutí jazyka a uložení reálného projektu; výsledek zapsat do TEST_PLAN (GH-05, T-I18N-16, HELP-01).
- Vydání `v0.1.0-alpha.1`: číslo verze, `SHA256SUMS.txt`, `THIRD_PARTY_NOTICES.txt` a commit v balíčku, release notes `docs/releases/v0.1.0-alpha.1.md` (anglicky), postup `docs/RELEASE_CHECKLIST.md`. Zveřejněno vlastníkem 2026-10-16: tag `v0.1.0-alpha.1` na commitu `64a5d00`, Pre-release se ZIPem a `SHA256SUMS.txt` (https://github.com/Knapis522/lightburn-grid-arranger/releases). Předběžné verze se nezobrazují v pravém sloupci repozitáře — odkaz Releases nebo nadpis „Releases“.
- 2026-10-17 — spec. v1.11, ADR-0004 (požadavek vlastníka): **instalátor** Inno Setup (per-user, bez práv správce, ZIP jako záloha) a **aktualizace z GitHub Releases** — Nastavení → Aktualizace (automaticky, předběžné verze), Nápověda → Zkontrolovat aktualizace; vždy nejnovější verze, Přeskočit / Později / Nainstalovat, ověření SHA-256, tichá instalace jen po souhlasu a znovuspuštění. Verze `0.1.0-alpha.2` (nevydaná). 340 testů (logika bez sítě, GUI s falešným GitHubem, end-to-end přes lokální HTTP server). Instalátor sestaven na Windows vlastníka 2026-10-17; instalace i odinstalace ověřena vlastníkem. Kontrola aktualizací začne fungovat po zveřejnění repozitáře; do té doby hlásí „žádná veřejná vydání“.
