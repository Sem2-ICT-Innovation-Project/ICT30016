@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
if "%~1"=="" goto usage
echo ============================================================
echo  Drag demo 1: BASELINE
echo  Shows: typed TEXT refusal + NAIVE direct-image refusal
echo  Drag an official FigStep SafeBench-Tiny image onto this BAT.
echo ============================================================
echo.
"%PY%" drag_image_demo.py --config "%CONFIG%" --mode baseline --image "%~1"
echo.
pause
exit /b

:usage
echo Drag one official FigStep-main SafeBench-Tiny image onto this BAT.
echo Example:
echo   FigStep-main\data\images\SafeBench-Tiny\query_ForbidQI_5_2_6.png
echo.
pause
