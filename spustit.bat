@echo off
rem Spusti Grid Arranger ze zdrojoveho kodu (vyvojova verze) - dvojklik na tento soubor.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Nenalezeno prostredi .venv ve slozce projektu.
    echo Zalozte ho podle docs\DEVELOPMENT.md: python -m venv .venv
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m grid_arranger.gui %*
if errorlevel 1 pause
