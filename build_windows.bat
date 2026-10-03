@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python Launcher "py" was not found. Install Python 3.12 for Windows first.
    exit /b 1
)

py -3.12 --version >nul 2>nul
if errorlevel 1 (
    echo Python 3.12 was not found. Install it from python.org and retry.
    exit /b 1
)

if not exist ".venv-build\Scripts\python.exe" (
    py -3.12 -m venv .venv-build
    if errorlevel 1 exit /b 1
)

".venv-build\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

".venv-build\Scripts\python.exe" -m pip install -r requirements-windows-build.txt
if errorlevel 1 exit /b 1

".venv-build\Scripts\python.exe" -m PyInstaller --clean --noconfirm FightingGame.spec
if errorlevel 1 exit /b 1

echo.
echo Build complete: dist\FightingGame\FightingGame.exe
echo Keep the entire dist\FightingGame folder together when sharing the game.
endlocal
