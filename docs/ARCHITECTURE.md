# Architektura

**Aktualizováno:** 2026-10-16 (GUI-00). Závazný návrh: spec. kap. 11 a 25.

## Vrstvy a závislosti

```text
gui/ (PySide6: okno, náhled, jazyk, nápověda, samokontrola)  cli.py (vývojářský nástroj)
  ▲ packaging/ + tools/build_exe.py (PyInstaller → GridArranger.exe)
  │                                              │
application/arrange_job.py  ← načtení → plán → validace → zápis → kontrola → protokol
  │                     │
adapters/lightburn/     safety/verify.py  (nezávislá kontrola výstupu)
  │
core/   (mřížka, pořadí, kolize)
  │
domain/ (datové typy, chyby)
```

Závislosti směřují **pouze dovnitř**. `domain` a `core` používají jen standardní knihovnu, nesmí importovat Qt ani nic o formátu LightBurnu. Jedinou externí závislostí je PySide6, a to jen ve vrstvě `gui/`.

## Souřadné systémy

| Systém | Osy | Kde se používá |
|---|---|---|
| **Jádro** | X doprava, **Y dolů**, `top` = horní hrana, mm | `domain`, `core` — vše, co vidí uživatel jako „vlevo nahoře“ |
| **Soubor `.lbrn2`** | souřadnice stroje, mm; zobrazení řídí `MirrorX/MirrorY` | pouze adaptér |

Převod (ověřeno v KAL-00, spec. kap. 8): `screen_x = MirrorX ? −x : +x`, `screen_y = MirrorY ? +y : −y`. Podporované kombinace: True/True, False/True. Viz `docs/FORMAT_COMPATIBILITY.md`.

## Moduly

| Modul | Odpovědnost | Požadavky |
|---|---|---|
| `domain/models.py` | `Rect` (AABB, validace konečnosti), `Item`, `GridRequest`, `Placement`, `LayoutResult`, `MaterialSpec`, `Obstacle`, `Align` | kap. 10, 25.1 |
| `domain/errors.py` | `GridError(code, message, **params)` — stabilní kódy pro lokalizaci v UI | kap. 36.4 |
| `core/grid_layout.py` | `arrange_to_grid(items, request)` — adaptivní mřížka (max. šířka sloupce / výška řádku), roh plnění `Corner.TOP_LEFT`/`TOP_RIGHT` (zrcadlení sloupců i zarovnání), `fsum`, pojistka proti porušení mezer | MVP-01, kap. 6, 7 |
| `core/order.py` | `default_order`, `move_up`, `move_down`, `select` (na konec), `deselect`, `validate_permutation` — čisté funkce | MVP-02, MVP-03 |
| `core/collision.py` | `validate_layout(...)` → `ValidationReport` (chyby blokují uložení, varování ne); zametací algoritmus pro dvojice | MVP-04, kap. 21.4 |
| `core/rotation.py` | `min_area_angle` (konvexní obal + hrany obalu, úspora ≥ 0,5 %), `rotated_bounds`, `rotate_point` (kladně po směru hodin, osa Y dolů) | spec. v1.13 kap. 7.6 |
| `core/tolerance.py` | `EPSILON = 0.001 mm` | kap. 7.4 |
| `adapters/lightburn/xmltree.py` | bezpečné parsování (`expat`, zákaz DTD/entit, jen UTF-8) do stromu s bajtovými pozicemi obsahu | kap. 9.1, ADR-0002 |
| `adapters/lightburn/geometry.py` | `XForm`, `VertList` (řídicí body), `PrimList` (`LineClosed`, `L`/`B` řetězec), konzervativní AABB, `fmt_num` (8 platných číslic) | kap. 5, 7.4 |
| `adapters/lightburn/coords.py` | `Orientation` — převod soubor ↔ jádro podle `MirrorX/MirrorY` | kap. 8 |
| `adapters/lightburn/read.py` | `load_project` — brány verze/orientace/neznámých prvků, výrobky (obrys = uzavřená cesta obsahující vše ostatní), důvody blokace, varování, překážky | kap. 5, 9.1, 41 |
| `adapters/lightburn/write.py` | `plan_patches` (XForm skupiny + BackupPath textů; posun nebo afinní `T ∘ XForm`), `apply_patches`, `next_output_path` (`__grid_NNN`), `write_new_file` (dočasný soubor + zveřejnění bez přepisu) | kap. 9.2, 9.4 |
| `safety/verify.py` | `verify_output` — znovu parsuje zdroj i výstup; mimo obsah `XForm` musí být bajty shodné; změněné `XForm` jen u povolených uzlů a přesně `T ∘ původní` (posun: lineární část bajtově beze změny) | kap. 9.3, 14.3, ADR-0005 |
| `application/arrange_job.py` | `make_plan`, `ItemGeometry` (body křivek a úhly výrobků, cache), natočení `_choose_rotations` (úhel + společná orientace), převod transformace jádro → soubor `S∘T∘S`; `execute` (volitelně cesta zvolená uživatelem — `check_output_path`: `.lbrn2`, ne originál, ne existující soubor/protokol; protokol `beside` / `none` / složka), `run`; umístění `origin`/`center`/`manual`/`selection`, plnění `origin`/`reading`, deska u počátku s okrajem 5 mm; souřadnice od uživatele jsou souřadnice LightBurnu; JSON protokol vedle výstupu | kap. 12.3, 21.5 |
| `cli.py`, `__main__.py` | `python -m grid_arranger info|arrange …` | kap. 11 |
| `gui/main_window.py` | hlavní okno: nástrojová lišta (Otevřít, Uložit jako nový, Příručka), titulek „aplikace verze - projekt“, projekt a laser, seznam výrobků (výběr, Nahoru/Dolů, výchozí pořadí), mřížka, umístění, deska, živý náhled, chyby/varování, Uložit (jen při platném rozložení, s potvrzením) | MVP-02…06, kap. 12 |
| `adapters/lightburn/render.py` | `ProjectRenderer` — skutečné křivky výrobků a textů (`BackupPath`) v souřadnicích jádra pro náhled; Bézier: `c0` počátečního vrcholu, `c1` koncového | kap. 12.3 |
| `gui/preview.py` | `PreviewView` — deska, využitelná plocha, počátek, překážky (šedě), výrobky se skutečnými motivy v barvách vrstev a s pořadím; zoom kolečkem, přepínač motivů; přetažení výrobku na místo jiného → signál `itemDropped` → `core.order.swap` (prohození); vždy světlé barvy | kap. 12.3, MVP-03 |
| `gui/i18n.py` | `LocaleManager` (QTranslator, QLocale), `detect_system_language`, fallback do angličtiny; navíc katalog Qt `qtbase_<kód>` (tlačítka Ano/Ne) | MVP-07, kap. 36 |
| `gui/messages.py` | lokalizované hlášky z kódů chyb (`QT_TRANSLATE_NOOP`) | kap. 36.4 |
| `gui/theme.py` | světlý / tmavý / automatický vzhled (styl Fusion + explicitní paleta, `setColorScheme`, sleduje změnu v systému); náhled desky vždy světlý | — |
| `gui/settings.py` | `UserSettings` (QSettings): jazyk, vzhled, výchozí desky podle `DeviceName`, aktualizace (automaticky, předběžné verze, přeskočená verze, čas poslední kontroly), protokol uložení (`none` výchozí / `beside` / `appdata`), jednotky (`mm`/`in`), sbalené sekce | kap. 12.3, 36.3, 32 |
| `gui/help.py`, `gui/help/<cs|en>/*.md` | offline příručka: obsah, Zpět/Vpřed, hledání, F1, synchronizace jazyka | MVP-08, kap. 38 |
| `gui/catalog_check.py`, `tools/build_translations.py` | kontrola úplnosti a zástupných symbolů `.ts`, sestavení `.qm` | T-I18N-14, 15 |
| `gui/app.py` | spuštění, ikona okna, zachycení neočekávané chyby; argumenty `<soubor.lbrn2>` a `--self-test REPORT.json` | MVP-06 |
| `updates.py` | aktualizace bez Qt: `SemVer` (SemVer 2.0), `parse_releases`, `find_update` (vždy nejnovější), `should_offer_automatically` (přeskočená verze), `auto_check_due`, `fetch_releases` (GitHub API, urllib), `download_installer` (ověření `SHA256SUMS.txt`), `installer_command` | spec. v1.11 kap. 32, ADR-0004 |
| `gui/widgets.py` | `Section` (sbalitelná sekce panelu, styl hlavičky podle vzhledu), `LengthSpin` (délka držená v mm, zobrazení mm/palce bez zaokrouhlovacích posunů), `Unit` | MVP-06 |
| `gui/icons.py` | vlastní jednobarevné SVG ikony nástrojové lišty, barva z palety vzhledu | MVP-06 |
| `gui/updates_ui.py` | `UpdateController` (kontrola na pozadí, nabídka, stažení s průběhem, spuštění instalátoru a ukončení aplikace), `UpdateDialog` | kap. 32 |
| `packaging/GridArranger.iss` | instalátor Inno Setup (per-user, stálé `AppId`, smazání `_internal` před instalací, znovuspuštění po tiché aktualizaci) | kap. 31.2, ADR-0004 |
| `gui/selftest.py` | samokontrola sestavení bez zobrazení okna (příručka, překlady, ikona, okno, round-trip na vestavěném syntetickém projektu) → JSON, kód 0/1 | GH-05, HELP-01, T-I18N-16 |
| `packaging/GridArranger.spec`, `tools/build_exe.py`, `tools/build_exe.bat` | PyInstaller (onedir, bez konzole, ikona, informace o verzi), zúžení Qt na Core/Gui/Widgets, samokontrola, ZIP | kap. 30, ADR-0003 |
| `version.py` | `__version__` (PEP 440, např. `0.1.0a1`) — jediný zdroj verze; `display_version()` → SemVer `0.1.0-alpha.1` pro GUI, ZIP, tag a release notes | kap. 30.3 |

## Pravidla rozpoznání výrobku (adaptér)

- Výrobek = nejvyšší `Shape Type="Group"`; povolené atributy jen `Type`, `CutIndex` (jinak např. zamčení → blokace).
- Uvnitř jen ověřené typy `Group`, `Path`, `Text`; jiný typ → blokace (mohl by nést světové souřadnice jako `BackupPath`).
- Obrys = uzavřená cesta, jejíž AABB obsahuje AABB veškerého změřitelného obsahu; právě jedna (shodné duplicitní obrysy → nejednoznačné).
- Text: `BackupPath/XForm` musí odpovídat složené transformaci textu (±0,01 mm), jinak blokace; text bez `BackupPath` → jen varování.
- Projekt jako celek se odmítne: jiná přípona (`.lbrn` zvlášť), vadné XML, DTD, verze ≠ 2.2.x / formát ≠ 1, `MirrorY=False`, neznámé prvky či atributy kořene, více stránek.

## Datový tok (cílový stav MVP)

```text
.lbrn2 ──read──► adaptér: skupiny, obrysy (AABB), překážky, Mirror, DeviceName
                    │ převod do souřadnic jádra
                    ▼
            Item[], Obstacle[] ──► core.arrange_to_grid ──► LayoutResult
                                          │
                                core.validate_layout ──► ValidationReport (can_save?)
                    │ převod (dx, dy) zpět do souřadnic souboru
                    ▼
            adaptér: bajtový patch XForm skupin + BackupPath textů (ADR-0002)
                    ▼
            nový soubor  …__grid_001.lbrn2 + protokol
```

## Kódy chyb a upozornění jádra

| Kód | Typ | Význam |
|---|---|---|
| `invalid_columns`, `invalid_gap`, `invalid_start`, `invalid_alignment` | výjimka | neplatné parametry |
| `invalid_bounds`, `degenerate_item` | výjimka | neplatné rozměry výrobku |
| `empty_selection`, `duplicate_item`, `unknown_item` | výjimka | výběr / pořadí není platná permutace |
| `internal_overlap` | výjimka | pojistka — chyba algoritmu |
| `material_missing`, `invalid_material`, `invalid_margin`, `margins_exceed_material` | chyba | materiál nelze použít |
| `outside_material` | chyba | výrobek přesahuje využitelnou plochu (`overhang_mm`) |
| `items_overlap`, `gap_violation` | chyba | dvojice výrobků |
| `obstacle_overlap`, `obstacle_gap_violation`, `obstacle_unmeasurable` | chyba | nepřesouvané překážky |
| `zero_gap` | varování | nulová mezera — riziko při řezání |
| `minimum_gap_only` | varování | různé rozměry → mezera je jen minimální |

## Kódy adaptéru a úlohy

| Kód | Úroveň | Význam |
|---|---|---|
| `legacy_format`, `not_lbrn2`, `file_too_large` | projekt | soubor nelze otevřít |
| `xml_malformed`, `xml_encoding`, `xml_dtd_forbidden`, `not_lightburn_project` | projekt | vadný nebo nebezpečný obsah |
| `unsupported_version`, `unsupported_orientation`, `unknown_orientation`, `unknown_element`, `unknown_project_attribute`, `multi_page_unsupported` | projekt | neověřená konstrukce |
| `unknown_group_attribute`, `unsupported_shape_type`, `unknown_element`, `bad_xform`, `unreadable_path` | výrobek | blokace výrobku |
| `no_outline`, `content_outside_outline`, `ambiguous_outline`, `degenerate_outline`, `empty_group`, `text_backup_mismatch` | výrobek | blokace výrobku |
| `text_unmeasurable` | výrobek | varování |
| `network`, `not_found`, `rate_limited`, `bad_response`, `no_installer`, `checksum_missing`, `checksum_mismatch`, `cancelled` | aktualizace | `UpdateError` — jen hláška, výroba pokračuje |
| `item_not_supported`, `validation_failed`, `verification_failed`, `source_changed`, `output_exists`, `would_overwrite_source`, `write_failed`, `no_free_output_name` | úloha | nic se neuloží |
