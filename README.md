# Grid Arranger for LightBurn

Windows desktop application that arranges the items (groups) of a **LightBurn `.lbrn2` project** into an exact grid with the gaps you choose — and saves the result as a **new project**. The original file is never changed.

> **Status: early pre-release (alpha).** Tested with LightBurn 2.2.00 on two lasers. Always check the output in LightBurn before cutting (see *Safety* below).
>
> **Unofficial tool.** Grid Arranger is not a product of LightBurn Software and is not supported by them. The `.lbrn2` format is not a public, stable interface; only the versions listed in [docs/FORMAT_COMPATIBILITY.md](docs/FORMAT_COMPATIBILITY.md) are supported.

*Česky:* aplikace pro Windows, která rozmístí výrobky (skupiny) z projektu LightBurn `.lbrn2` do přesné mřížky s nastavitelnými mezerami a uloží nový projekt; originál se nikdy nemění. Aplikace i vestavěná příručka (F1) jsou v češtině a angličtině; vývojová dokumentace v `docs/` je česky.

## Features

- Open a `.lbrn2` project; every top-level group with a closed cut outline is an item (cards, key rings, signs…). Outlines can be curves or shapes drawn in LightBurn (circle, ellipse, rectangle incl. rounded corners, polygon), also in nested groups.
- Choose the items and their order (list, or drag & drop in the preview).
- Grid: number of columns, gap X/Y, fill order from the laser origin; board size, margins, placement at the origin corner, centred or at a manual position.
- **Rotation to save material:** automatic (any angle or 90° steps), manual angle per item, or none.
- **Copies** to fill the board (Ctrl+C / Ctrl+V or *Create copies…*), or **Fill the board** with as many copies as fit.
- **Automatic number of columns** (as many as fit the board width) and named **layout profiles**.
- **Prepare a project for another laser** from a laser catalogue (e.g. origin top right → top left): the items are mirrored so that they look the same on the target laser (new in v0.1.0-alpha.5).
- Collision and board checks, including objects that are not moved.
- Safe saving: a new file only, independent verification of the output before it is written, optional save protocol.
- Millimetres or inches, light/dark appearance, eight languages (Czech, English, German, Slovak, Polish, French, Spanish, Italian — the last six machine-translated, awaiting native review), offline user guide (F1), optional update check.

## What it does not do

It does not edit the project open in LightBurn, does not control the laser, does not generate machine code and does not read `.lbrn`, SVG, DXF or PDF. It is a grid arranger, not a free-form nesting tool.

## Install

1. Download `GridArranger-Setup-v…-win-x64.exe` from [Releases](https://github.com/Knapis522/lightburn-grid-arranger/releases) (Windows 10/11 x64; no Python, no administrator rights needed). A portable ZIP is available as well.
2. Optional: compare the file with `SHA256SUMS.txt` (PowerShell: `Get-FileHash <file>`).
3. The installer is not digitally signed yet; Windows SmartScreen may show a warning (*More info → Run anyway*).

Newer versions are offered by the application itself (*Settings → Updates*); nothing is installed without your confirmation.

## Supported projects

- LightBurn 2.2.x projects saved as `.lbrn2`.
- Lasers with the origin in any corner: **top left, top right, bottom left, bottom right** (bottom origins are typical for diode lasers; new in v0.1.0-alpha.5).
- Projects with several pages, unknown object types (e.g. bitmaps inside items) or unverified constructions are refused or the affected items are blocked — the application never guesses.

## Safety

Always open the output in LightBurn with **File → Open** (not Import) and check the layers, the position on the machine and the **Preview** before cutting. The checks in the application do not replace the operator's check.

## Privacy

The application works offline. The only network request is the optional update check against the public GitHub API — no project data are sent. See [SECURITY.md](SECURITY.md).

## Building from source

Python 3.12+ on Windows: see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) (Czech). In short:

```
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev,build]
python -m pytest
python -m grid_arranger.gui          # run the application
tools\build_exe.bat                  # installer + ZIP in dist\v<version>\
```

## Documentation

| File | Content |
|---|---|
| [CHANGELOG.md](CHANGELOG.md) | Changes per version (Czech); release notes in English in [docs/releases/](docs/releases/) |
| [docs/FORMAT_COMPATIBILITY.md](docs/FORMAT_COMPATIBILITY.md) | Verified LightBurn versions and findings about the format |
| [docs/specification.md](docs/specification.md) | Technical specification (Czech) |
| [docs/STATUS.md](docs/STATUS.md), [docs/ROADMAP.md](docs/ROADMAP.md) | Current state and plan |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | Code structure, development and build |
| [docs/TRANSLATING.md](docs/TRANSLATING.md) | Translations |

Customer projects are never stored in this repository; tests use synthetic projects only.

## Licence

Source code: [MIT License](LICENSE). Bundled third-party components (Qt/PySide6 under LGPL-3.0, Python, …): [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

"LightBurn" is a trademark of LightBurn Software, LLC, used here only to describe compatibility.
