# Grid Arranger for LightBurn (pracovní název)

Offline desktopová aplikace pro Windows, která **přesune již existující, navzájem odlišné skupiny** v projektu LightBurn `.lbrn2` do přesné mřížky s nastavitelnými mezerami — bez kopírování a bez změny obsahu skupin. Výsledkem je vždy **nový soubor**; originál se nikdy nepřepisuje.

> **Stav projektu:** ve vývoji, nepoužitelné pro výrobu. Hotové a automaticky otestované je výpočetní jádro (mřížka, pořadí, kontrola kolizí) a čtení/zápis `.lbrn2` s nezávislou kontrolou výstupu a okno aplikace v češtině a angličtině s nápovědou F1 (samostatné `GridArranger.exe` se sestavuje skriptem `tools\build_exe.bat`, viz `docs/DEVELOPMENT.md`; ověření na počítači bez Pythonu zatím čeká). Aktuální ověřený stav je v [docs/STATUS.md](docs/STATUS.md).

> **Neoficiální nástroj.** Není produktem společnosti LightBurn Software a není jí podporován. Formát `.lbrn2` není veřejné stabilní rozhraní; podpora platí jen pro výslovně otestované verze (viz `docs/FORMAT_COMPATIBILITY.md`, vznikne v etapě KAL-00).

## Plánovaný rozsah první verze (MVP)

- Načtení jednoho projektu `.lbrn2` (jiné formáty včetně `.lbrn` nejsou podporovány).
- Seznam nalezených nejvyšších skupin, ruční výběr a ruční pořadí (Nahoru/Dolů).
- Mřížka: počet sloupců, mezera X/Y v mm, počátek.
- Kontrola materiálu, okrajů a kolizí (i s objekty, které se nepřesouvají).
- Bezpečné uložení nového projektu `puvodni__grid_001.lbrn2` s validací a protokolem.
- Grafické rozhraní PySide6, čeština a angličtina, offline nápověda (F1).

Úplné požadavky: [docs/specification.md](docs/specification.md).

## Co nástroj nedělá

- Neupravuje otevřený projekt v LightBurnu a nepřebírá jeho výběr.
- Neovládá laser, negeneruje strojové soubory.
- Nepracuje s `.lbrn`, SVG, DXF ani PDF.

## Bezpečnost použití

Výstup vždy otevři v LightBurnu přes **File → Open** (ne Import), zkontroluj vrstvy, **Preview** a polohu na stroji. Kontrola v aplikaci nenahrazuje kontrolu obsluhy stroje.

## Dokumentace

| Soubor | Obsah |
|---|---|
| [docs/specification.md](docs/specification.md) | Závazná technická specifikace |
| [docs/STATUS.md](docs/STATUS.md) | Aktuální stav, další krok — **číst jako první při navázání práce** |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Etapy, závislosti a brány |
| [docs/TEST_PLAN.md](docs/TEST_PLAN.md) | Testovací plán a evidence výsledků |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Moduly, souřadné systémy, kódy chyb |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Vývojové prostředí, testy a sestavení `GridArranger.exe` |
| [docs/FORMAT_COMPATIBILITY.md](docs/FORMAT_COMPATIBILITY.md) | Ověřené verze LightBurnu a zjištění o formátu |
| [docs/TRANSLATING.md](docs/TRANSLATING.md) | Překlady a terminologie |
| [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md) | Postup vydání na GitHub |
| [docs/releases/](docs/releases/) | Popisy jednotlivých vydání (anglicky) |
| [CHANGELOG.md](CHANGELOG.md) | Přehled změn |
| [docs/DECISIONS/](docs/DECISIONS/) | Záznamy technických rozhodnutí (ADR) |

## Testovací data

Reálné projekty `.lbrn2` **nepatří do tohoto repozitáře**. Ukládají se do sousední složky mimo Git (`..\lightburn-grid-arranger-data\`). V repozitáři smějí být jen uměle vytvořené vzorky v `tests/fixtures/synthetic/`.
