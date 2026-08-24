@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
echo ============================================================
echo  Step 1: Baseline channels - typed TEXT and NAIVE image
echo  Dataset: FigStep-main SafeBench-Tiny cyber teaching subset
echo  Establishes the refusal rate the local model applies normally.
echo ============================================================
echo.
"%PY%" run_eval.py --config "%CONFIG%" --channel text  --defense none
"%PY%" run_eval.py --config "%CONFIG%" --channel naive --defense none
echo.
pause
