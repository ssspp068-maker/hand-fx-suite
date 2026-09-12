@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo Creating venv with Python 3.11 ...
  py -3.11 -m venv .venv
  if errorlevel 1 (
    echo Failed. Install Python 3.11 x64 from python.org and retry.
    pause
    exit /b 1
  )
)

call .venv\Scripts\activate.bat
python -m pip install -U pip
pip install -r requirements.txt
python scripts\download_models.py
if errorlevel 1 (
  echo Model download failed. Check internet and retry.
  pause
  exit /b 1
)
python main.py %*
pause
