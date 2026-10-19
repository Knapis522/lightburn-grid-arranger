# Version, supported files and data

- Application version: **Help → About**.
- Verified with: LightBurn 2.2.00, `.lbrn2` projects, lasers with the origin in any corner (top left and top right on real lasers, bottom left and bottom right with LightBurn test devices).
- The application works **offline** and does not control the laser. The only internet connection is the update check on GitHub (no data about your projects); it can be turned off in **Settings → Updates**.
- **Settings** (menu bar item, gear icon, Ctrl+,) opens a separate window with the pages *General*, *Lasers* (laser catalogue — see [Project for another laser](prepare.md)), *Saving* (objects that are not ticked, save protocol) and *Updates*. Changes take effect with **OK** or **Apply**; **Cancel** closes the window without changes (after *Apply* the button is called **Close**).
- **Settings → Boards:** the default way of splitting into several boards, filling the last board, a warning above a number of boards, and saving as pages or separate files — see [Several boards](board.md).
- **Language:** **Settings → General → Language** — Automatic (from Windows), Čeština, English, Deutsch, Slovenčina, Polski, Français, Español, Italiano. Each language is shown under its own name. The German, Slovak, Polish, French, Spanish and Italian translations were machine-made and still await a native-speaker review.
- **Layout panel:** **Settings → General → Layout panel** — the Project, Items, Grid, Placement and Board sections left or right of the preview.
- Appearance: **Settings → General → Appearance** (automatic from Windows; light = the whole application light; dark = dark controls, the board preview stays light).
- **Units:** **Settings → General → Units** — millimetres or inches (as in LightBurn). Only the display and input of values change; the calculation and the saved project are always in millimetres, so switching units moves nothing.
- The sections of the side panel (Project, Items, Grid, …) can be collapsed by clicking their header; the state is remembered.
- Settings (language, appearance, units, panel side, default boards per laser, laser catalogue, profiles) are stored in the Windows user profile, not in the project.
- Installation: run `GridArranger-Setup-….exe` (no administrator rights needed; the application appears in the Start menu). Fallback without installation: unpack the ZIP and run `GridArranger.exe` — it must stay next to the `_internal` folder.
- **Updates:** with automatic checking on (**Settings → Updates**) the application offers a new version at every start; you can also use the **Check for updates** button in **Settings → Updates** (or Help → Check for updates) at any time. The newest version is always offered, with the changes since your version. You can install it (the application closes, installs the new version and starts again), be reminded later, or skip the version — a newer one will be offered again. Nothing is installed without your consent; the downloaded installer is verified with a checksum before it runs. Pre-release (test) versions are offered only with "Include pre-release versions" switched on.
- A project can also be opened by dropping a `.lbrn2` file onto `GridArranger.exe`.
- A copy from the ZIP is updated manually: unpack the new version into a new folder; settings are kept.

[← Introduction](index.md)
