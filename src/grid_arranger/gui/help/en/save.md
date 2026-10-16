# Saving and checking in LightBurn

**Save as new project** is enabled only when the layout passed the check. After you confirm, the application:

1. prepares a new file in which only the positions of the selected groups (and their texts) change,
2. independently verifies that nothing else changed (layers, power, texts, other objects),
3. verifies that the original has not changed since it was opened,
4. saves a **new** file next to the original: `original__grid_001.lbrn2` (then `_002`, …) and a `.json` protocol.

Existing files are never overwritten. If anything fails, no output is created.

**Then in LightBurn:**

1. Open the output via **File → Open** (not Import — Import does not load the project settings).
2. Check layers, power and speed.
3. Run **Preview** and inspect the paths.
4. Check the position on the machine (**Frame**). Only then cut, under supervision.

[← Board](board.md) · [Troubleshooting →](troubleshooting.md)
