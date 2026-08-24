@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
echo ============================================================
echo  Step 0: Smoke test - load Qwen2-VL-2B + one FigStep-main case
echo  Uses ..\FigStep-main\data\question\SafeBench-Tiny.csv.
echo  Confirms the weights in ..\hf_cache load and official images work.
echo  (First model load on CPU takes a minute; be patient.)
echo ============================================================
echo.
"%PY%" demo_one.py --config "%CONFIG%" --id ForbidQI_5_2 --channels text,naive,figstep
echo.
echo If you saw model output above (no [error]/import error), you are ready.
echo If imports failed, run setup.bat first.
echo.
pause
