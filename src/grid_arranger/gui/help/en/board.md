# Board, margins and collision check

The **board** is the material rectangle in LightBurn coordinates. By default it lies at the laser origin (board corner X 0, Y 0). Its size is pre-filled according to the laser saved in the project; **Save as default for this laser** remembers your values. **Margins** (default 5 mm) are a strip along the board edges where nothing may be placed.

> The board in the application is not the machine work area. Check the real material position and framing on the machine.

Before saving, the application checks that:

- all moved items lie within the usable board area,
- items do not overlap and keep the gap,
- items keep the gap from **unmoved** groups and loose objects as well, if they stay in the output (Settings → Saving); left-out objects are ignored,
- an object whose size cannot be determined **blocks** saving (safety cannot be confirmed).

Errors (✖) block saving and name the items concerned. Warnings (⚠) do not. The application never scales, rotates or moves unselected objects by itself.

The check works with outlines in the project, not with real overscan when engraving, kerf compensation or head movement — that is why **Preview in LightBurn is mandatory**.

## Several boards

When the pieces do not fit on one board, the application splits them into several boards. Choose how in the Board section under **If it does not fit**:

- *Split into boards one after another* (default) — board 1 full, then board 2 …; the fewest boards.
- *Split into boards evenly* — the same number of pieces on every board (e.g. 50 → 17/17/16).
- *Split into boards by item* — each board holds pieces of one item only (the original and its copies).
- *Do not split (error)* — the layout is blocked when it does not fit, as before.

**Fill the last board with copies** adds copies until the last board is full (with *by item*, each item's last board is filled with copies of that item).

Tabs above the preview show the boards, like pages in LightBurn; a tab with an error is marked ✖ and the messages name the board. You can save only when all boards pass the checks. All boards use the same grid settings and the same board; objects kept in place (Settings → Saving) are on board 1 only.

**Saving:** board 1 stays on the arranged page and boards 2 … are added as new pages right after it („Page 1 – board 2“ …). In LightBurn switch pages (**Window → Pages**) and cut one board at a time — Preview and Frame work with the active page only. Alternatively **Settings → Boards → As separate files** saves one file per board (`…__board1.lbrn2` …). The defaults (way of splitting, filling, warning above a number of boards) are in **Settings → Boards**.

[← Grid](grid.md) · [Next: saving →](save.md)
