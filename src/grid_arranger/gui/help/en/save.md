# Saving and checking in LightBurn

The **Save as new project** icon on the toolbar (or **File → Save as new project**, Ctrl+S) is enabled only when the layout passed the check. A save dialog opens with the proposed name `original__grid_001.lbrn2` (then `_002`, …) in the original's folder — **you can change the folder and the name**. After you confirm, the application:

1. prepares a new file in which only the positions of the selected groups (and their texts) change,
2. independently verifies that nothing else changed (layers, power, texts, other objects),
3. verifies that the original has not changed since it was opened,
4. saves a **new** file under the chosen name.

**Save protocol** (`.json`) — a record of what the output was made from and how: checksums, laser, grid settings, item moves and the check result (no artwork or texts of the items). Useful for tracing or reporting a problem. Settings → **Save protocol**: *Do not save* (default), *Next to the saved project* (`<name>.json`), or *In the application's protocol folder* (open it there with **Open protocol folder**).

Neither existing files nor the original are ever overwritten — if the chosen file (or its protocol next to it) already exists, the application asks for another name. If anything fails, no output is created.

**Then in LightBurn:**

1. Open the output via **File → Open** (not Import — Import does not load the project settings).
2. Check layers, power and speed.
3. Run **Preview** and inspect the paths.
4. Check the position on the machine (**Frame**). Only then cut, under supervision.

[← Board](board.md) · [Troubleshooting →](troubleshooting.md)
