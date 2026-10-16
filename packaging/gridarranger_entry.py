"""Vstupní bod pro PyInstaller (GridArranger.exe). Veškerá logika je v balíčku ``grid_arranger``."""

import sys

from grid_arranger.gui.app import main

if __name__ == "__main__":
    sys.exit(main())
