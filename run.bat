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
python -c "import sys; v=sys.version_info; print('Python', sys.version.split()[0]); raise SystemExit(0 if v.major==3 and 10<=v.minor<=12 else 1)"
if errorlevel 1 (
  echo [ERROR] Need Python 3.10-3.12. Delete .venv folder and install Python 3.11.
  pause
  exit /b 1
)

echo Installing dependencies...
python -m pip install -U pip >nul
pip install -r requirements.txt
if errorlevel 1 (
  echo [ERROR] pip install failed
  pause
  exit /b 1
)

REM 0.10.30 on Win+Py3.12 crashes: AttributeError function 'free' not found
python -c "import mediapipe as mp; print('mediapipe', mp.__version__); parts=[int(x) for x in mp.__version__.split('.')[:3]]; raise SystemExit(0 if parts>=[0,10,31] else 1)"
if errorlevel 1 (
  echo Upgrading mediapipe to ^>=0.10.31 ...
  pip install -U "mediapipe>=0.10.31,<1.1"
  if errorlevel 1 (
    echo [ERROR] mediapipe upgrade failed
    pause
    exit /b 1
  )
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
  echo If you saw "function 'free' not found":
  echo   1^) close this window
  echo   2^) delete the .venv folder in this project
  echo   3^) run run.bat again
  echo.
  echo If camera failed, try: run.bat --camera 1
)
pause
