@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
set "CONFIG=config_figstep_tiny.yaml"
echo ============================================================
echo  Step 4: Compare refusal rates / ASR across channels x defenses
echo  Dataset: FigStep-main SafeBench-Tiny cyber teaching subset
echo ============================================================
echo.
"%PY%" vlm_compare_results.py --config "%CONFIG%"
echo.
echo Full summary saved to: code\outputs_vlm_figstep_tiny\comparison_summary.txt
echo.
pause
