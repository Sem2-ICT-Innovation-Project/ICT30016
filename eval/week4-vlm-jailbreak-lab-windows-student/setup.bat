@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
echo ============================================================
echo  Setup: install CPU dependencies into python-portable
echo  (torch, transformers, accelerate, pillow, pyyaml, safetensors)
echo  Run this ONCE. Needs internet for the pip download only;
echo  the model weights are already in ..\hf_cache.
echo ============================================================
echo.
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
echo.
echo Done. If there were no errors, run 00_smoke_test.bat next.
echo.
pause
