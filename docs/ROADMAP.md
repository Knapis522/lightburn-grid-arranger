# Roadmapa

Milníkový harmonogram bez kalendářních termínů (spec. kap. 39). Data se doplní podle skutečného tempa a výsledků KAL-00.

```text
GIT-00 + DOC-00 → PLAN-00
        ↓
KAL-00 (kompatibilita .lbrn2)      CORE-00 (algoritmus, souběžně)
        ↓                                  ↓
ADAPT-00 (čtení, identifikace, zápis, diff)
        ↓
GUI-00 (PySide6 EXE) + HELP-01 (F1, cs/en) + MVP-07 (cs/en)
        ↓
MVP-ACCEPT → [samostatné rozhodnutí] PUBLIC-01 (8 jazyků, PUB-01)
        ↓
V11-ACCEPT → V20-ACCEPT → FUT-01 (jen při veřejném API)
```

| ID | Výstup | Závislost | Stav | Důkaz |
|---|---|---|---|---|
| GIT-00 | Soukromý GitHub repozitář, 2FA, GitHub Desktop | — | **Hotovo** 2026-10-16 | repo `Knapis522/lightburn-grid-arranger` (Private); GH-01 commit `55ab47e`, GH-02 commit `5e94c06` |
| DOC-00 | Kostra dokumentace, specifikace v repozitáři | souběžně s GIT-00 | **Hotovo** 2026-10-16 | commit `55ab47e` |
| PLAN-00 | GitHub Projects board, Issues pro hlavní etapy | GIT-00 | **Rozpracováno** 2026-10-19: formuláře issues, štítky a skript pro úvodní issues hotové; čeká spuštění skriptu vlastníkem; board volitelný | `.github/ISSUE_TEMPLATE/`, `.github/labels.yml`, `tools/github_setup.ps1` |
| KAL-00 | Důkaz bezpečného přesunu skupiny v `.lbrn2` | GIT-00, DOC-00 | **Hotovo** 2026-10-16 (LightBurn 2.2.00-RC-7, Mirror True/True + False/True) | `docs/FORMAT_COMPATIBILITY.md` V-001…V-003, `tools/kal00/` |
| CORE-00 | Deterministický algoritmus mřížky + testy ALG-* | DOC-00 | **Implementováno a otestováno** 2026-10-16 (automaticky; ověření na Windows čeká) | `src/grid_arranger/core`, `tests/unit` (143 testů) |
| ADAPT-00 | Bezpečné čtení, identifikace skupin, zápis, diff | KAL-00 | **Implementováno a otestováno** 2026-10-16 (automaticky); čeká ruční T-MVP-26 | `src/grid_arranger/adapters`, `safety`, `application`; `tests/integration` |
| GUI-00 | PySide6 aplikace: výběr, pořadí, náhled, validace | CORE-00, ADAPT-00 | **Implementováno**, okno ověřeno vlastníkem na Windows 2026-10-16; sestavení EXE (PyInstaller, ADR-0003) ověřeno na PC bez Pythonu — GH-05 splněno 2026-10-17 | `src/grid_arranger/gui`, `tests/gui`, `packaging/`, `tools/build_exe.py` |
| HELP-01 | Offline příručka F1, cs/en | GUI-00 | Rozpracováno: příručka cs/en a F1 hotové; samokontrola sestavení ověřuje přibalení příručky; čeká ruční ověření v EXE na Windows | `src/grid_arranger/gui/help` |
| REL-ALPHA1 | Interní Pre-release `v0.1.0-alpha.1` (soukromý repozitář) | GUI-00, sestavení EXE | **Zveřejněno** 2026-10-16 (tag na `64a5d00`, Pre-release) | `docs/releases/v0.1.0-alpha.1.md`, `docs/RELEASE_CHECKLIST.md` |
| UPD-00 | Instalátor + nabízené aktualizace (spec. v1.11 kap. 32) | REL-ALPHA1 | **Vydáno** v `v0.1.0-alpha.2` 2026-10-17 (instalátor ověřen vlastníkem); aktualizace z aplikace funkční od PUB-00 (2026-10-18) | `updates.py`, `gui/updates_ui.py`, `packaging/GridArranger.iss`, ADR-0004 |
| REL-ALPHA3 | Interní Pre-release `v0.1.0-alpha.3` | ROT-00, SHAPES-00, COPY-00 | **Zveřejněno** 2026-10-17 (tag na `a804585`, Pre-release) | `docs/releases/v0.1.0-alpha.3.md` |
| REL-ALPHA5 | Pre-release `v0.1.0-alpha.5` | AUTO-FILL-PROFILES, TARGET-LASER, ORIGIN-BOTTOM | **Zveřejněno** 2026-10-18 (Pre-release) | `docs/releases/v0.1.0-alpha.5.md` |
| AUTO-FILL-PROFILES | Automatické sloupce (V11-03), vyplnit desku kopiemi, profily rozložení (V11-01) — spec. v1.24 | COPY-00 | **Hotovo, ručně ověřeno** 2026-10-18 | `arrange_job.py` (`AUTO_COLUMNS`), `gui/main_window.py`, `gui/settings.py` |
| TARGET-LASER | Projekt pro jiný laser + katalog laserů (spec. v1.23) | ORIGIN-BOTTOM | **Hotovo, KAL-05 ověřeno vlastníkem** 2026-10-18 | `arrange_job.py` (`TargetLaser`), `write.py` (`header_patches`), `safety/verify.py`, `gui/settings_dialog.py` |
| ORIGIN-BOTTOM | Lasery s počátkem dole (diodové; spec. v1.22) | ADAPT-00 | **Hotovo, KAL-04 ověřeno vlastníkem** 2026-10-18 | `core/grid_layout.py`, `arrange_job.py`, `FORMAT_COMPATIBILITY.md` |
| REL-ALPHA4 | Pre-release `v0.1.0-alpha.4` (první aktualizace z aplikace, T-UPD-07) | PUB-00 | **Zveřejněno** 2026-10-18 (Pre-release); aktualizace z alpha.3 v aplikaci ověřena vlastníkem (T-UPD-07). Obsah: krok zpět/vpřed, lišta, okno Nastavení, panel vlevo/vpravo, Otevřít v LightBurnu, stav po uložení | `docs/releases/v0.1.0-alpha.4.md` |
| PUB-00 | Veřejný repozitář s předběžnými verzemi (spec. v1.17 kap. 33.2) | REL-ALPHA3 | **Splněno** 2026-10-18: repozitář veřejný, aktualizace z aplikace fungují | `LICENSE`, `README.md`, `SECURITY.md`, `THIRD_PARTY_NOTICES.md` |
| ROT-00 | Natočení pro úsporu materiálu (spec. v1.13) | ADAPT-00 | **Implementováno, KAL-01 ověřeno vlastníkem** 2026-10-17; vydáno v `v0.1.0-alpha.3` | `core/rotation.py`, ADR-0005, `FORMAT_COMPATIBILITY.md` |
| SHAPES-00 | Kruh / elipsa / obdélník / mnohoúhelník nakreslené přímo v LightBurnu (spec. v1.14) | testovací soubory C | **Hotovo, ověřeno vlastníkem** 2026-10-17: `Ellipse`, `Rect` (i zaoblený), `Polygon` (libovolné N), vnořené skupiny (klíčenky); přesun shodný s LightBurnem; výstupy otevřeny v LightBurnu; KAL-02 splněno; vydáno v `v0.1.0-alpha.3` | `adapters/lightburn/shapes.py`, `tools/kal02/`, `FORMAT_COMPATIBILITY.md` (vzorky C) |
| COPY-00 | Kopie výrobků pro vyplnění desky (V11-02 předsunuto, spec. v1.16) | ADAPT-00 | **Hotovo, KAL-03 ověřeno vlastníkem** 2026-10-17; vydáno v `v0.1.0-alpha.3` | `write.py` (`copy_block`), `safety/verify.py`, `tests/integration/test_copies.py` |
| OMIT-00 | Vynechání objektů z výstupu (spec. v1.27) | ADAPT-00 | **Hotovo, KAL-07 ověřeno vlastníkem** 2026-10-19 | `write.py` (`omit_shapes`), `safety/verify.py`, `tests/integration/test_omit.py` |
| V20-01-PAGES | Rozdělení zakázky na více desek jako stránky LightBurnu (spec. v1.29–1.30) | OMIT-00, KAL-06 | **Implementováno** 2026-10-19 (automatické testy); **čeká KAL-08** (výstupy v LightBurnu) | `arrange_job.py` (`make_job`, `execute_job`), `pages.py`, `tests/integration/test_boards.py` |
| MVP-ACCEPT | Ověření MVP-01..08, test v LightBurnu | výše | Nezahájeno | — |
| L10N-PUBLIC-01 | Osm jazyků rozhraní a příručky (spec. kap. 36, v1.26) | MVP-07 | **Rozpracováno** 2026-10-18: katalogy a příručka `de/sk/pl/fr/es/it` hotové jako strojový návrh (AI), automatické testy T-I18N-17…20 prochází (542 testů); **čeká jazyková revize rodilými mluvčími** a ruční T-I18N-21 na Windows | `translations/`, `gui/help/<jazyk>/`, `docs/TRANSLATING.md`, `tests/gui/test_i18n.py`, `test_help.py` |
| PUBLIC-01 | Veřejné stabilní v1.0.0 | MVP-ACCEPT + REL-01, PUB-01, L10N-PUBLIC-01, DOC-REL-01 | Neschváleno | — |
| V11-ACCEPT | Profily, množství, automatické sloupce | MVP-ACCEPT | **Implementováno** 2026-10-18: profily (V11-01), počet kusů (V11-02, v1.25), automatické sloupce (V11-03); čeká ruční ověření počtu kusů a MVP-ACCEPT | `tests/integration/test_quantities.py`, `test_auto_columns.py` |
| V20-ACCEPT | Více desek, více projektů | V11-ACCEPT | Plánováno | — |
| FUT-01 | Přímá integrace s LightBurnem | veřejné API | Pouze výhled | — |
