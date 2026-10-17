@echo off
rem Sestaveni GridArranger.exe - staci spustit dvojklikem nebo z prikazoveho radku.
rem Vystup: dist\GridArranger\GridArranger.exe a dist\GridArranger-v...-win-x64.zip
setlocal
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" (
    echo Chybi .venv - nejdriv proved prvni nastaveni podle docs\DEVELOPMENT.md
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -e .[dev,build]
if errorlevel 1 goto failed
".venv\Scripts\python.exe" tools\build_exe.py %*
if errorlevel 1 goto failed
echo.
echo HOTOVO. Slozka dist se ted otevre - vystupy jsou ve slozce s cislem verze.
start "" "%cd%\dist"
pause
exit /b 0

:failed
echo.
echo SESTAVENI SELHALO - vyse je popis chyby.
pause
exit /b 1
