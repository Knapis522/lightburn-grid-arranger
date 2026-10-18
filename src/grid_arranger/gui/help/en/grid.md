# Grid and placement

**Layout profile** — saved settings under a name (e.g. "Key rings 3 mm"): number of columns (or *Automatic*), gaps, fill order, rotation and placement. Choosing a profile in the **Layout profile** section sets the values; **Save…** saves the current settings as a profile (same name = overwrite), **Delete** removes it. When you change a value, the choice switches to *no profile* — the profile itself is not changed. The board is not part of a profile; it belongs to the laser (Settings → Lasers).

**Columns** — how many items are in one row. The number of rows is calculated. With **Automatic** ticked the application uses as many columns as fit on the board width (the usable area inside the margins); the field then shows the calculated number. Useful together with copies and *Fill the board with copies*.

**Gap X / Y** — distance between the cut outlines of neighbouring items in the selected units (horizontal / vertical). A gap of 0 is allowed, but the application warns about the risk when cutting. Enter decimals as usual in the application language (a dot in English, a comma e.g. in Czech or German).

If items have **different sizes**, a column is as wide as its widest item and a row as tall as its tallest item. The gap is then a **minimum** — it is larger between smaller items.

**Fill order**

- *From the laser origin* (default) — item no. 1 is in the corner at the laser origin; with the origin on the right, rows are filled from right to left; with the origin at the bottom, the first row is at the bottom and the next rows are above it.
- *Reading order* — item no. 1 is always top left, rows from left to right.

**Placement**

- *In the board corner at the laser origin* (default) — the grid corner at the origin lies in the board corner plus margin.
- *In the centre of the board*.
- *Manually* — enter the LightBurn X/Y coordinates (distance from the origin) of the grid corner at the origin.

The **Corner X / Y** fields can be edited only in the *Manually* mode. In the other modes they are greyed out and show the corner the application has just calculated (it changes e.g. with the margins). After switching to *Manually* they keep the current corner, so the grid does not move and you can fine-tune it.
- *At the original position of the items*.

The preview shows the board, the usable area (dashed), the laser origin (●), the moved items with their real artwork and texts in layer colours and with their numbers, and unmoved objects in grey. Items with an error are red. **Show artwork** in the header of the Items section turns the drawing off and leaves only the item rectangles. The mouse wheel (or touchpad) zooms smoothly, dragging empty space pans the view (dragging an item changes the order), the **Fit view** icon on the toolbar (Ctrl+0) or a double-click on empty space shows everything.

## Rotation to save material

The **Rotation** option in the Grid section:

- *Any angle (smallest area)* — default. Each item is rotated so that the rectangle around it is as small as possible (saves space with tilted or irregular shapes such as key rings). Rectangular cards stay straight.
- *In 90° steps* — items are only turned by a quarter turn (landscape / portrait).
- *Do not rotate* — items are only moved.

In all modes the application also checks whether the grid would be smaller with all items in landscape or in portrait and uses the smaller variant — preferably one that fits on the board. If rotating would not make the grid smaller, the items stay as they are; round items are never turned by 90°. Rotation is shown in the preview and in the item list. An item is rotated about its centre together with its texts and artwork; after saving, check the Preview in LightBurn. Exceptions for single items: the **No rotation** button in the Items section.

[← Items](items.md) · [Next: board and check →](board.md)
