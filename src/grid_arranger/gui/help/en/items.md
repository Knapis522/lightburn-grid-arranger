# Selecting and ordering items

After opening a project (the **Open project** toolbar icon, **File → Open project** or Ctrl+O) the list shows all top-level groups:

- **Checked** items are arranged into the grid. The number before the name is their position in the grid.
- **Unchecked** items stay where they are and the application makes sure the grid does not hit them.
- **Grey** items ("cannot be moved") were refused — hover over them to see why. They are never moved.
- ⚠ marks a warning (for example a text that cannot be measured) — the item can be used, but check it in Preview.

Order: **grab an item in the preview with the mouse and drag it onto the place of another item** — a green frame shows where it will land; **the two items swap places**, all others stay where they are and the list is renumbered. Releasing outside the items cancels the drag. Or select an item in the list and use **Up / Down**. A newly checked item is added at the end. **Default order** restores the order from the file. **Select all / Select none** change the selection at once.

**Rotation:** a rotated item shows an arrow and the angle in the list (↻ clockwise, ↺ anticlockwise). Select an item by **clicking it in the preview** (orange frame) or in the list; **Ctrl+click** adds more, **Esc** clears the selection. For the selected items:

- **↺ 90° / ↻ 90°** — turn by 90° (e.g. so that all key rings have the hole at the top);
- **Angle of selected** — enter any angle in degrees (positive = clockwise);
- **No rotation** — the item stays as it is in the project (text direction, material grain);
- **Auto** — removes the manual angle; the application rotates the item again.

A manual angle is marked “(manual)” in the list; the application never changes it and it also applies with Rotation *Do not rotate*. The angle is measured from the position in the original project. Opening another project clears manual angles. See [grid](grid.md).

**Copies (filling the board):** select items and press **Ctrl+C** and **Ctrl+V** — one copy of each is added. For more copies at once use the **Create copies** icon on the toolbar (or **Ctrl+D**, Edit menu) and enter the number, e.g. 5. Copies are added at the end of the order, are marked “(copy of G5)” in the list, take over the manual angle and can be rotated and moved like any other item. Remove a copy with **Delete** or by unchecking it. Copies are written to the saved project as new groups; the original project is not changed.

**Fill the board with copies** (board icon on the toolbar, **Ctrl+Shift+D**, Edit menu): adds as many copies of the selected items as still fit on the board with the layout passing the check. With several items selected, the copies alternate (A, B, A, B…). Works best with the *Automatic* number of columns; with a fixed number of columns only rows are added.

Item number **1** is placed in the grid corner given by *Fill order* (see [grid](grid.md)).

[← Preparing](prepare.md) · [Next: grid →](grid.md)
