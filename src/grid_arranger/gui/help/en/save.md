# Saving and checking in LightBurn

The **Save as new project** icon on the toolbar (or **File → Save as new project**, Ctrl+S) is enabled only when the layout passed the check. A save dialog opens with the proposed name `original__grid_001.lbrn2` (then `_002`, …) in the original's folder — **you can change the folder and the name**. After you confirm, the application:

1. prepares a new file in which only the positions of the selected groups (and their texts) change, left-out objects are removed,
2. independently verifies that nothing else changed (layers, power, texts, other objects),
3. verifies that the original has not changed since it was opened,
4. saves a **new** file under the chosen name.

**Save protocol** (`.json`) — a record of what the output was made from and how: checksums, laser, grid settings, item moves and the check result (no artwork or texts of the items). Useful for tracing or reporting a problem. **Settings → Saving → Save protocol**: *Do not save* (default), *Next to the saved project* (`<name>.json`), or *In the application's protocol folder* (open it there with **Open protocol folder**).

**After saving you keep working on the original.** The saved file is a separate new copy; the original project stays open in the application, so you can try another layout and save another variant (`_002`, …). The window title and the Project section show *last saved as …*. To continue with the saved file instead (like "Save as"), tick **Continue working on the saved file here** in the save message — it opens instead of the original, its copies and rotations are now fixed and undo starts again. The next save then continues the original's numbering (`_002`, not `__grid_001__grid_001`).

Neither existing files nor the original are ever overwritten — if the chosen file (or its protocol next to it) already exists, the application asks for another name. If anything fails, no output is created.

**Then in LightBurn:**

1. Open the output: in the save message with **Open in LightBurn** (or the toolbar icon, **File → Open saved project in LightBurn**, Ctrl+L). The application opens the file like a double-click in Explorer: a running LightBurn replaces its open project — if it has unsaved changes, LightBurn asks to save them; otherwise LightBurn starts. To open it manually use **File → Open** (not Import — Import does not load the project settings).
2. Check layers, power and speed.
3. Run **Preview** and inspect the paths.
4. Check the position on the machine (**Frame**). Only then cut, under supervision.

[← Board](board.md) · [Troubleshooting →](troubleshooting.md)
