# Testovací plán

Úplné definice testů jsou ve specifikaci; zde se eviduje **stav a důkaz**. Stavy: `nezahájeno` / `napsán` / `prochází` / `selhává` / `ruční – ověřeno`.

| Sada | ID | Kap. spec. | Typ | Stav | Důkaz |
|---|---|---|---|---|---|
| Algoritmus | ALG-01 – ALG-10 | 14.1 | automatický (pytest) | prochází | `tests/unit/test_layout.py` |
| MVP jádro: mřížka | T-MVP-01 – 04 | 26.1 | automatický | prochází | `tests/unit/test_layout.py` |
| MVP jádro: výběr, pořadí | T-MVP-05, 06, 08 – 10 | 26.1 | automatický | prochází | `tests/unit/test_ordering.py`, `test_layout.py` |
| MVP jádro: materiál, kolize | T-MVP-11 – 18 | 26.1 | automatický | prochází | `tests/unit/test_collision.py` |
| Integrace `.lbrn2` (syntetické) | LB-01 – 06, 08, 10, 11 | 14.2 | automatický | prochází | `tests/integration/test_lbrn2_read.py`, `test_lbrn2_write.py` |
| Integrace `.lbrn2` (reálné, mimo Git) | V-001 načtení, rozměry, round-trip | 14.2 | automatický, volitelný | prochází | `tests/integration/test_real_projects.py` |
| Integrace v LightBurnu | LB-07, 09, 12, 13 | 14.2 | ruční | nezahájeno | — |
| Invariance MVP | — | 14.3 | automatický | nezahájeno | — |
| MVP: nepodporované skupiny, ukládání | T-MVP-07, T-MVP-19 – T-MVP-25 | 26.1 | automatický | prochází | `tests/integration/` |
| MVP: kontrola v LightBurnu | T-MVP-26 | 26.1 | ruční | ověřeno (CLI, V-001); opakovat s GUI | protokol níže |
| Formát | T-FMT-01 – 05, 07 | 41.5 | automatický | prochází | `tests/integration/` |
| Formát v LightBurnu | T-FMT-06 | 41.5 | ruční | ověřeno pro prototyp (KAL-00) | protokol níže |
| Lokalizace (interní, automatické) | T-I18N-01 – 04, 07 – 15 | 36.6 | automatický | prochází | `tests/gui/test_i18n.py` |
| Lokalizace (interní, ruční) | T-I18N-05, 06, 16 | 36.6 | ruční / EXE | nezahájeno | — |
| GUI | MVP-02 … 06 ovládání | 21, 12 | automatický (offscreen) | prochází | `tests/gui/test_main_window.py` |
| Lokalizace (veřejná) | T-I18N-17 – T-I18N-22 | 36.6 | automatický (17, 18, 19 strojová část, 20) + ruční (19 jazyková revize, 21 na Windows, 22) | automatické prochází; jazyková revize šesti jazyků čeká | `tests/gui/test_i18n.py`, `tests/gui/test_help.py`, samokontrola sestavení (příručka ve všech jazycích) |
| Nápověda (automatické) | T-HELP-01 – 04, 09 | 38.5 | automatický | prochází | `tests/gui/test_help.py` |
| Nápověda (ruční / EXE) | T-HELP-05 – 08, 10 | 38.5 | ruční | nezahájeno | — |
| Sestavení: samokontrola balíčku | GH-05 (část), HELP-01 (přibalení), T-I18N-16 (katalogy) | 34, 38, 36.6 | automatický při `tools/build_exe.py` + pytest | prochází (Windows 11 + Linux) | `tests/gui/test_packaging.py`, `dist/selftest-report.json` |
| Dokumentace | T-DOC-01 – T-DOC-07 | 40.1 | kontrola | nezahájeno | — |
| Řízení | T-PLAN-01 – T-PLAN-06 | 39.6 | kontrola | nezahájeno | — |
| GitHub / distribuce | GH-01, GH-02 | 34 | ruční | prochází | protokol níže |
| Natočení (automatické) | spec. v1.13 kap. 7.6 | 7.6 | automatický | prochází | `tests/unit/test_rotation.py`, `tests/integration/test_rotation_plan.py`, `tests/gui/test_main_window.py` |
| Ruční natočení a výběr v náhledu (automatické) | spec. v1.15 kap. 7.6 | 7.6 | automatický | prochází | `tests/integration/test_rotation_plan.py`, `tests/gui/test_main_window.py` |
| Kopie výrobků (automatické) | V11-02 / spec. v1.16 kap. 22.2 | 22.2 | automatický | prochází | `tests/integration/test_copies.py`, `tests/gui/test_main_window.py` |
| Kopie výrobků v LightBurnu | KAL-03 | 22.2 | ruční | ruční – ověřeno | `…__kal03_kopie.lbrn2` (datová složka) |
| Počátek dole v LightBurnu | KAL-04 | 9.1 | ruční | ruční – ověřeno | testovací zařízení GRBL vlevo dole / vpravo dole |
| Převod na jiný laser v LightBurnu | KAL-05 | 9.1 | ruční | ruční – ověřeno | červený → modrý a zpět, laser s počátkem dole |
| Automatické sloupce, vyplnění desky, profily (ruční) | T-11-01–05, T-11-14–20 (zjednodušeno) | 22.1, 22.3 | automaticky + ručně | ruční – ověřeno | `test_auto_columns.py`, GUI testy |
| Natočení v LightBurnu | KAL-01 | 7.6 | ruční | ruční – ověřeno | `docs/FORMAT_COMPATIBILITY.md`, protokol níže |
| Nativní tvary (automatické) | spec. v1.14 kap. 5 body 8–9 | 5 | automatický | prochází | `tests/unit/test_shapes.py`, `tests/integration/test_native_shapes.py`, `tests/integration/test_real_projects.py` (vzorky C, s `GRID_ARRANGER_REAL_DATA`) |
| Nativní tvary v LightBurnu | vzorky C (výstupy), KAL-02 | 5 | ruční | ruční – ověřeno | `docs/FORMAT_COMPATIBILITY.md` (vzorky C, KAL-02) |
| Aktualizace (automatické) | T-UPD-01 – 06, 08 | 32.4 | automatický | prochází | `tests/unit/test_updates.py`, `tests/gui/test_updates_ui.py` |
| Aktualizace a instalátor (ruční) | T-UPD-07, instalace / odinstalace | 32.4 | ruční (Windows, po zveřejnění) | ruční – ověřeno | alpha.3 → alpha.4 z aplikace (2026-10-18) |
| GitHub / distribuce | GH-05 EXE na PC bez Pythonu | 34 | ruční | ruční – ověřeno | protokol níže (2026-10-17) |
| GitHub / distribuce | GH-03, GH-04, GH-08 – GH-16 | 34 | ruční | nezahájeno | — |
| Verze 1.1 | T-11-01 – T-11-20 | 26.2 | — | plánováno | — |
| Verze 2.0 | T-20-01 – T-20-19 | 26.3 | — | plánováno | — |

## Testovací data

- Automatické testy používají jen syntetické soubory v `tests/fixtures/synthetic/`.
- Reálné projekty pro ruční a kompatibilitní testy leží mimo Git v `..\lightburn-grid-arranger-data\`.
- Každý ruční test v LightBurnu zapsat: datum, verze LightBurnu, verze Windows, soubor (jen název), výsledek, poznámka.

## Protokol ručních testů

| Datum | Test | LightBurn | Soubor | Výsledek | Poznámka |
|---|---|---|---|---|---|
| 2026-10-16 | GH-01 | — | — | prochází | Repo publikováno jako Private; v commitu `55ab47e` jen 9 dokumentačních souborů, žádný `.lbrn2` |
| 2026-10-16 | GH-02 | — | — | prochází | Commit `5e94c06` vytvořen v GitHub Desktop a odeslán; `origin/main` = `5e94c06` |
| 2026-10-16 | KAL-00 / T-FMT-04 | 2.2.00-RC-7 | Kalibrace_C__grid_poc.lbrn2 | prochází | Prototyp posunul skupinu o +50/+30; změněny 2 řádky; originál beze změny |
| 2026-10-16 | KAL-00 / T-FMT-06 | 2.2.00-RC-7 | Kalibrace_C__grid_poc.lbrn2 | ruční – ověřeno | File → Open: poloha, text, vrstvy, Preview v pořádku (vlastník) |
| 2026-10-16 | KAL-00 / LB-06 | 2.2.00-RC-7 | Kalibrace_A/B, Kalibrace_L_A/L_B | ruční – ověřeno | Orientace pro Mirror True/True a False/True |
| 2026-10-16 | T-MVP-26 / LB-13 | 2.2.00-RC-7 | test program …__grid_001.lbrn2 | ruční – ověřeno | 9 kartiček 3 × 3, mezera 5 mm; vlastník: „vše sedí“; požadavek zarovnat k počátku → spec. v1.10 |
| 2026-10-16 | Celá sada (Windows) | — | — | prochází | Windows 11, Python 3.13.6: 221 passed, 1 skipped (POSIX); vč. regresních testů na reálných souborech a zápisu přes `os.rename` |
| 2026-10-16 | T-MVP-26 / LB-13 (v1.10) | 2.2.00-RC-7 | test program …__grid_002.lbrn2 | ruční – ověřeno | Deska 700 × 500, okraj 5, roh počátku vpravo nahoře, plnění od počátku; vlastník: „sedí“ (shoda s ručním vzorem `-zarovnani`) |
| 2026-10-16 | GUI-00 ruční (Windows) | — | reálný projekt | ruční – ověřeno | Vlastník: náhled motivů, prohození tažením, vzhled světlý/tmavý/automaticky, zoom — v pořádku |
| 2026-10-16 | Zkušební sestavení (Linux) | — | syntetický | prochází | `tools/build_exe.py`: 286 testů, PyInstaller 6.22, samokontrola 5/5 v zabalené aplikaci; nejde o důkaz GH-05 (ten vyžaduje Windows) |
| 2026-10-16 | Sestavení EXE (Windows) | — | syntetický | prochází | Windows 11 (26200), Python 3.13.6, PySide6 6.12.0: `tools\build_exe.bat` — testy, PyInstaller, samokontrola 5/5 v `GridArranger.exe` (frozen), ZIP 28 MB. GH-05 ruční test na PC bez Pythonu čeká |
| 2026-10-16 | GH-06 / GH-07 (interní) | — | — | prochází | Tag `v0.1.0-alpha.1` (commit `64a5d00`), GitHub Pre-release se ZIPem `GridArranger-v0.1.0-alpha.1-win-x64.zip` a `SHA256SUMS.txt` v soukromém repozitáři |
| 2026-10-17 | Instalátor (Windows) | — | — | ruční – ověřeno | Windows 11, Inno Setup 6: `dist\v0.1.0-alpha.2\` s instalátorem (22 MB), ZIP, `SHA256SUMS.txt` (součet instalátoru ověřen), `RELEASE_NOTES.md`; samokontrola 6/6 (HTTPS: 43 certifikátů Windows); instalace i odinstalace funguje (vlastník) |
| 2026-10-17 | GH-06 / GH-07 (interní) | — | — | prochází | Tag `v0.1.0-alpha.2` (commit `d8c0cc9`), Pre-release s instalátorem, ZIPem a `SHA256SUMS.txt` |
| 2026-10-17 | GUI ruční (Windows), soupis B | 2.2.00-RC-7 | Kalibrace_A, Kalibrace_A__kal01_rot → `…__kal01_rot__grid_002.lbrn2` | ruční – ověřeno | Vlastník: nástrojová lišta a titulek, uložení s volbou složky/názvu a odmítnutím existujícího souboru, protokol uložení (3 volby), jednotky mm/palce bez posunu, sbalitelné sekce, Roh X/Y, natočení (kartičky rovně, srovnání šikmých, Nenatáčet), výstup s natočením otevřen v LightBurnu — vše v pořádku |
| 2026-10-17 | Vzorky C (automaticky) | 2.2.00-RC-7 | Test_tvary_A, Test_tvary_L_A, Test_tvary_A_posun, Test_klicenky, Kalibrace_A_rot30 | prochází | Všechny výrobky podporované (Ellipse, Rect, Polygon N=6, vnořené skupiny, příznak `S`); náš posun K1 = přesun v LightBurnu (tytéž 2 řádky, rozdíl jen v posledním řádu); klíčenky s natočením −18,5 % plochy mřížky; 411 testů + 6 na reálných datech |
| 2026-10-17 | Vzorky C (výstupy v LightBurnu) | 2.2.00-RC-7 | `C_vystupy\` (Test_tvary_A 4 sl. bez natočení, 2 sl. libovolný úhel; Test_tvary_L_A; Test_klicenky libovolný úhel a po 90°) | ruční – ověřeno | Vlastník: v pořádku |
| 2026-10-17 | KAL-02 | 2.2.00-RC-7 | Test_tvary_A__kal02_tvary, …_prevedeno (Convert to Path) | prochází | 12/12 tvarů odchylka 0,0000 mm po opravě vzorce mnohoúhelníku; zaoblené rohy a všechna N povolena |
| 2026-10-18 | GH-06 / GH-07 | — | — | prochází | Sestavení `tools\build_exe.bat` (J1), tag `v0.1.0-alpha.5`, Pre-release s instalátorem, ZIPem a `SHA256SUMS.txt` (vlastník) |
| 2026-10-18 | Ruční testy alpha.5 (43 kroků) | 2.2.00-RC-7 | reálné projekty, Kalibrace_A__BL/__BR | ruční – ověřeno | 40 OK, 2 připomínky opraveny: B4 Zrušit po Použít (tlačítko se přejmenuje na Zavřít), H7 náhled při odmítnutém převodu (původní polohy na desce projektu, zalomená hlášení). KAL-04 i KAL-05 v pořádku. Sestavení (J1) čeká |
| 2026-10-18 | T-UPD-07 (aktualizace z aplikace) | — | — | ruční – ověřeno | PC u laseru: alpha.3 nabídla alpha.4, stažení, ověření součtu, instalace a nové spuštění v pořádku (vlastník). Připomínka: kontrolovat při každém spuštění → spec. v1.21 |
| 2026-10-18 | GH-06 / GH-07 | — | — | prochází | Tag `v0.1.0-alpha.4`, Pre-release s instalátorem, ZIPem a `SHA256SUMS.txt`; sestavení po opravě testu velikosti okna (nezávislý na velikosti obrazovky) |
| 2026-10-18 | GUI ruční (Windows), alpha.4 | 2.2.00-RC-7 | reálné projekty | ruční – ověřeno | Vlastník: Otevřít v LightBurnu (nahradí projekt, upozorní na neuložené změny), okno si pamatuje velikost a maximalizaci, krok zpět/vpřed, přeuspořádání lišty, titulek „naposledy uloženo jako“ a pokračování s uloženým souborem, okno Nastavení, panel vpravo, výška seznamu hlášení — v pořádku |
| 2026-10-18 | PUB-00, kontrola aktualizací | — | — | ruční – ověřeno | Repozitář veřejný; aplikace alpha.3 na PC u laseru: Zkontrolovat aktualizace → aktuální verze (dříve „vydání nejsou veřejná“). Instalace aktualizace ze starší verze (T-UPD-07) až s příštím vydáním |
| 2026-10-17 | GH-06 / GH-07 (interní) | — | — | prochází | Tag `v0.1.0-alpha.3` (commit `a804585`), Pre-release s instalátorem (21,7 MB), ZIPem a `SHA256SUMS.txt` |
| 2026-10-17 | KAL-03 (kopie) | 2.2.00-RC-7 | Test_klicenky / Test_tvary_A / Test_tvary_L_A `__kal03_kopie` | ruční – ověřeno | Vlastník: kopie v LightBurnu v pořádku |
| 2026-10-17 | GH-05 (PC bez Pythonu) | — | — | ruční – ověřeno | Vlastník: sestavená aplikace funguje na PC u laseru bez instalovaného Pythonu |
| 2026-10-17 | KAL-01 (soupis A) | 2.2.00-RC-7 | Kalibrace_A__kal01_rot, Kalibrace_L_A__kal01_rot, Kalibrace_A__kal01_rot__grid_001 | ruční – ověřeno | Natočené kartičky celé, texty natočené s nimi, Preview v pořádku pro oba lasery; srovnaný výstup aplikace odpovídá původní kalibraci |
