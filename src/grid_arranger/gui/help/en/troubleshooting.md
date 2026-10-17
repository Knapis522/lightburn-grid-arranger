# Troubleshooting

**"This application supports only .lbrn2 projects"** — save the project in LightBurn as `.lbrn2`.

**"Unsupported LightBurn version"** — the project was saved by a LightBurn version the application has not been verified with. The output might not be safe, so it is refused.

**"This laser origin has not been verified yet"** — lasers with the origin at the top (left or right) are supported.

**Item "cannot be moved"** — hover over it. Most often: the group has no closed cut outline, something extends beyond the outline, it is locked, or it contains an object type the application cannot move safely yet (for example a bitmap).

**"Text geometry does not match its position"** — open the project in LightBurn and save it again.

**Saving is blocked** — read the errors (✖) under the preview: board overrun, collision, gap too small or an object that cannot be measured. Change the columns, gaps, board or selection.

**"The original file has changed"** — the project was saved again in the meantime. Open it again in the application.

**Windows says "Windows protected your PC"** — the application is not digitally signed yet. If the ZIP comes from the application's maintainer, click **More info → Run anyway**. Do not disable your antivirus.

**The application does not start or reports a missing file** — most likely the `_internal` folder is missing next to `GridArranger.exe` (for example only the EXE was copied). Unpack the whole ZIP again. To check the installation, run `GridArranger.exe --self-test report.json` from a command prompt; the result is written to `report.json`.

**Reporting a problem** — turn on Settings → Save protocol, save again and send the `.json` protocol (it contains checksums and parameters, not the item contents) and the steps. Send customer projects only with permission.

[← Introduction](index.md)
