# Grid and placement

**Columns** — how many items are in one row. The number of rows is calculated.

**Gap X / Y** — distance between the cut outlines of neighbouring items in the selected units (horizontal / vertical). A gap of 0 is allowed, but the application warns about the risk when cutting. Enter decimals with a dot (English) or a comma (Czech) depending on the application language.

If items have **different sizes**, a column is as wide as its widest item and a row as tall as its tallest item. The gap is then a **minimum** — it is larger between smaller items.

**Fill order**

- *From the laser origin* (default) — item no. 1 is in the corner at the laser origin; with the origin at the top right, rows are filled from right to left.
- *Reading order* — item no. 1 is always top left, rows from left to right.

**Placement**

- *In the board corner at the laser origin* (default) — the grid corner at the origin lies in the board corner plus margin.
- *In the centre of the board*.
- *Manually* — enter the LightBurn X/Y coordinates (distance from the origin) of the grid corner at the origin.
- *At the original position of the items*.

The preview shows the board, the usable area (dashed), the laser origin (●), the moved items with their real artwork and texts in layer colours and with their numbers, and unmoved objects in grey. Items with an error are red. **Show artwork** turns the drawing off and leaves only the item rectangles. The mouse wheel (or touchpad) zooms smoothly, dragging empty space pans the view (dragging an item changes the order), **Fit view** or a double-click on empty space shows everything.

[← Items](items.md) · [Next: board and check →](board.md)
