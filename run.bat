@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === Hand FX Suite ===
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  py -3.11 -m venv .venv 2>nul
  if errorlevel 1 py -3.12 -m venv .venv 2>nul
  if errorlevel 1 py -3.10 -m venv .venv 2>nul
  if errorlevel 1 python -m venv .venv 2>nul
  if errorlevel 1 (
    echo.
    echo [ERROR] Python not found.
    echo Install Python 3.11 from https://www.python.org/downloads/
    echo IMPORTANT: enable checkbox "Add python.exe to PATH"
    echo.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
echo Installing dependencies...
python -m pip install -U pip >nul
pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] pip install failed
  pause
  exit /b 1
)

echo Downloading models if needed...
python scripts\download_models.py
if errorlevel 1 (
  echo [ERROR] model download failed. Check internet.
  pause
  exit /b 1
)

echo Starting app...
python main.py %*
if errorlevel 1 (
  echo.
  echo If camera failed, try: run.bat --camera 1
)
pause
