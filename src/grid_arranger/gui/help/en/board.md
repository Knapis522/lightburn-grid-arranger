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

[← Grid](grid.md) · [Next: saving →](save.md)
