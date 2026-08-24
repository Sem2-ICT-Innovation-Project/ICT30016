@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
echo ============================================================
echo  Live demo: one request through text vs FigStep, side by side
echo  Dataset: FigStep-main SafeBench-Tiny cyber teaching subset
echo  Usage:  05_demo_one.bat  [case_id]   (default ForbidQI_5_2)
echo ============================================================
echo.
set "CASE=%~1"
if "%CASE%"=="" set "CASE=ForbidQI_5_2"
"%PY%" demo_one.py --config "%CONFIG%" --id "%CASE%" --channels text,figstep
echo.
pause
