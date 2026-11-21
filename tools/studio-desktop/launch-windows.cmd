@echo off
setlocal
cd /d "%~dp0\..\.."
set "TAVIX_REPO_ROOT=%CD%"
python tools\studio-desktop\build_windows.py
if errorlevel 1 (
  echo TaviX Studio build failed; no application started.
  pause
  exit /b 1
)
python tools\studio-desktop\run_windows.py
if errorlevel 1 (
  echo TaviX Studio closed with a failure. Inspect the console output.
  pause
  exit /b 1
)
endlocal
