# Preparing the project in LightBurn

1. **Group each item separately** (Ctrl+G). One group = one item.
2. Each group needs a **closed cut outline** that contains everything else (texts, artwork). The outline may have rounded corners or another shape — the item size is the rectangle around the outline. The outline can be a curve or a shape drawn directly in LightBurn (circle, ellipse, rectangle, polygon); a group may contain further groups (e.g. a keyring: circle with a hole + text).
3. Save the project (**Save As**) as `.lbrn2`. The application reads only the saved file — it cannot see unsaved changes in LightBurn.
4. Save the project for the laser you will cut on. The application detects the laser and its origin (top left / top right) from the project. **After switching the laser in LightBurn, save the project again** and reopen it.

Supported: LightBurn 2.2, `.lbrn2` projects, lasers with the origin at the top (left or right). Legacy `.lbrn` files are refused — save the project in LightBurn as `.lbrn2`.

[← Introduction](index.md) · [Next: items →](items.md)
