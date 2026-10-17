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
| PLAN-00 | GitHub Projects board, Issues pro hlavní etapy | GIT-00 | Nezahájeno | — |
| KAL-00 | Důkaz bezpečného přesunu skupiny v `.lbrn2` | GIT-00, DOC-00 | **Hotovo** 2026-10-16 (LightBurn 2.2.00-RC-7, Mirror True/True + False/True) | `docs/FORMAT_COMPATIBILITY.md` V-001…V-003, `tools/kal00/` |
| CORE-00 | Deterministický algoritmus mřížky + testy ALG-* | DOC-00 | **Implementováno a otestováno** 2026-10-16 (automaticky; ověření na Windows čeká) | `src/grid_arranger/core`, `tests/unit` (143 testů) |
| ADAPT-00 | Bezpečné čtení, identifikace skupin, zápis, diff | KAL-00 | **Implementováno a otestováno** 2026-10-16 (automaticky); čeká ruční T-MVP-26 | `src/grid_arranger/adapters`, `safety`, `application`; `tests/integration` |
| GUI-00 | PySide6 aplikace: výběr, pořadí, náhled, validace | CORE-00, ADAPT-00 | **Implementováno**, okno ověřeno vlastníkem na Windows 2026-10-16; sestavení EXE připraveno (PyInstaller, ADR-0003), čeká GH-05 na PC bez Pythonu | `src/grid_arranger/gui`, `tests/gui`, `packaging/`, `tools/build_exe.py` |
| HELP-01 | Offline příručka F1, cs/en | GUI-00 | Rozpracováno: příručka cs/en a F1 hotové; samokontrola sestavení ověřuje přibalení příručky; čeká ruční ověření v EXE na Windows | `src/grid_arranger/gui/help` |
| REL-ALPHA1 | Interní Pre-release `v0.1.0-alpha.1` (soukromý repozitář) | GUI-00, sestavení EXE | **Zveřejněno** 2026-10-16 (tag na `64a5d00`, Pre-release) | `docs/releases/v0.1.0-alpha.1.md`, `docs/RELEASE_CHECKLIST.md` |
| UPD-00 | Instalátor + nabízené aktualizace (spec. v1.11 kap. 32) | REL-ALPHA1 | **Vydáno** v `v0.1.0-alpha.2` 2026-10-17 (instalátor ověřen vlastníkem); aktualizace z aplikace funkční po PUB-01 | `updates.py`, `gui/updates_ui.py`, `packaging/GridArranger.iss`, ADR-0004 |
| MVP-ACCEPT | Ověření MVP-01..08, test v LightBurnu | výše | Nezahájeno | — |
| PUBLIC-01 | Veřejné v1.0.0 | MVP-ACCEPT + REL-01, PUB-01, L10N-PUBLIC-01, DOC-REL-01 | Neschváleno | — |
| V11-ACCEPT | Profily, množství, automatické sloupce | MVP-ACCEPT | Plánováno | — |
| V20-ACCEPT | Více desek, více projektů | V11-ACCEPT | Plánováno | — |
| FUT-01 | Přímá integrace s LightBurnem | veřejné API | Pouze výhled | — |
