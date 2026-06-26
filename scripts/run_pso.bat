@echo off
setlocal
cd /d "%~dp0\.."
if not exist .env (
  echo ERROR: Copy .env.example to .env and configure PLAXIS first.
  exit /b 1
)
set PYTHONPATH=%CD%\src;%PYTHONPATH%
python scripts\run_pso_legacy.py
endlocal
