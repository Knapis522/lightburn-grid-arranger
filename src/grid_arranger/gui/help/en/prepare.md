# Preparing the project in LightBurn

1. **Group each item separately** (Ctrl+G). One group = one item.
2. Each group needs a **closed cut outline** that contains everything else (texts, artwork). The outline may have rounded corners or another shape — the item size is the rectangle around the outline. The outline can be a curve or a shape drawn directly in LightBurn (circle, ellipse, rectangle, polygon); a group may contain further groups (e.g. a keyring: circle with a hole + text).
3. Save the project (**Save As**) as `.lbrn2`. The application reads only the saved file — it cannot see unsaved changes in LightBurn.
4. Save the project for the laser you will cut on. The application detects the laser and its origin (top left, top right, bottom left or bottom right — e.g. diode lasers) from the project. **After switching the laser in LightBurn, save the project again** and reopen it.

Supported: LightBurn 2.2, `.lbrn2` projects, lasers with the origin in any corner. Legacy `.lbrn` files are refused — save the project in LightBurn as `.lbrn2`.

## Project for another laser

A project saved for one laser can be prepared for another one, e.g. from a laser with the origin at the top right for a laser with the origin at the top left — without switching the device and flipping the design in LightBurn. In the **Project** section choose **Prepare for:** a laser from the catalogue. The application offers its board, fills the grid from its origin, and the saved file (`…__Laser_name__grid_001.lbrn2`) is ready for it: the file names the target laser and the items are mirrored so that they look the same on it (texts readable).

- Laser catalogue: **Settings → Lasers** (or *Manage lasers…* in the list). Lasers from opened projects are added automatically; add others (e.g. a diode laser) manually — **the name must match the device in LightBurn**; choose the origin corner and the board.
- With a different origin, **all items** must be selected and the project must not contain other objects (they would stay mirrored on the other laser). This only concerns objects kept in the output — unchecked and left-out objects are not in the output (the default), so they do not stand in the way.
- **Layer settings (power, speed) are not converted** — they stay as in the original project. Open the output in LightBurn with the target laser and check the layers.

[← Introduction](index.md) · [Next: items →](items.md)
