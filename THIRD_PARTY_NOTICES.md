# Third-party components

Grid Arranger's own source code is licensed under the MIT License (see [LICENSE](LICENSE)).

## Bundled in the Windows builds (installer and ZIP)

| Component | Licence | Notes |
|---|---|---|
| Python | Python Software Foundation License v2 | https://docs.python.org/3/license.html |
| Qt 6 (Core, Gui, Widgets, Svg, OpenGL and plugins) | LGPL-3.0 | Shipped as separate, unmodified dynamic libraries in `_internal\PySide6`; can be replaced by the user. Source: https://code.qt.io/ |
| PySide6 / Shiboken6 (Qt for Python) | LGPL-3.0 | Source: https://download.qt.io/official_releases/QtForPython/ |
| PyInstaller bootloader | GPL-2.0 with the bootloader exception | https://pyinstaller.org/en/stable/license.html |
| OpenSSL | Apache License 2.0 | https://www.openssl.org/source/license.html |
| libffi | MIT | https://github.com/libffi/libffi/blob/master/LICENSE |
| Microsoft Visual C++ runtime | Microsoft redistributable | |

Every build contains `THIRD_PARTY_NOTICES.txt` with the exact versions used.

## Development and build tools (not distributed)

pytest (MIT), Inno Setup (Inno Setup License), Pillow (HPND, only for `tools/make_icon.py`).

## Trademarks

"LightBurn" is a trademark of LightBurn Software, LLC. Grid Arranger is an unofficial tool, is not affiliated with, endorsed or supported by LightBurn Software, and does not use the LightBurn logo. The application icon and toolbar icons were drawn for this project.
