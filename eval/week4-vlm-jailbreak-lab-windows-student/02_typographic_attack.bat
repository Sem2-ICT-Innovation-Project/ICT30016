@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
echo ============================================================
echo  Step 2: Typographic attack - FigStep and FigStep-Pro channels
echo  Dataset: FigStep-main SafeBench-Tiny cyber teaching subset
echo  Same requests, delivered so OCR cannot recover one clean
echo  harmful sentence. Watch the refusal rate fall.
echo ============================================================
echo.
"%PY%" run_eval.py --config "%CONFIG%" --channel figstep     --defense none
"%PY%" run_eval.py --config "%CONFIG%" --channel figstep_pro --defense none
echo.
pause
