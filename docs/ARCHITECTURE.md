# Architektura

**Aktualizováno:** 2026-10-16 (CORE-00). Závazný návrh: spec. kap. 11 a 25.

## Vrstvy a závislosti

```text
ui/ (PySide6, GUI-00 — zatím neexistuje)
  │
application/ (orchestrace úlohy — zatím neexistuje)
  │
adapters/lightburn/ (čtení, převod souřadnic, zápis .lbrn2 — ADAPT-00, zatím neexistuje)
  │
core/        ← implementováno (CORE-00)
  │
domain/      ← implementováno (CORE-00)
```

Závislosti směřují **pouze dovnitř**. `domain` a `core` používají jen standardní knihovnu, nesmí importovat Qt ani nic o formátu LightBurnu.

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
| `core/grid_layout.py` | `arrange_to_grid(items, request)` — adaptivní mřížka (max. šířka sloupce / výška řádku), `fsum`, pojistka proti porušení mezer | MVP-01, kap. 7 |
| `core/order.py` | `default_order`, `move_up`, `move_down`, `select` (na konec), `deselect`, `validate_permutation` — čisté funkce | MVP-02, MVP-03 |
| `core/collision.py` | `validate_layout(...)` → `ValidationReport` (chyby blokují uložení, varování ne); zametací algoritmus pro dvojice | MVP-04, kap. 21.4 |
| `core/tolerance.py` | `EPSILON = 0.001 mm` | kap. 7.4 |
| `version.py` | `__version__` — jediný zdroj verze | kap. 30.3 |

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
