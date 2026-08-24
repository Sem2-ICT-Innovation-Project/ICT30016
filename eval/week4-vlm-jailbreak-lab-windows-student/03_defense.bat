@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
echo ============================================================
echo  Step 3: Defenses on the FigStep channel
echo  Dataset: FigStep-main SafeBench-Tiny cyber teaching subset
echo  system = safety system prompt; ocr = transcribe-then-filter
echo  How much refusal is restored?
echo ============================================================
echo.
"%PY%" run_eval.py --config "%CONFIG%" --channel figstep --defense system
"%PY%" run_eval.py --config "%CONFIG%" --channel figstep --defense ocr
echo.
pause
