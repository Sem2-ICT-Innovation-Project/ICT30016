@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PY=%SCRIPT_DIR%..\python-portable\python.exe"
if not exist "%PY%" set "PY=python"
cd /d "%SCRIPT_DIR%code"
echo ============================================================
echo  Student setup: install dependencies, then download the VLM
echo  model into this lab folder's hf_cache.
echo.
echo  Needs internet. The model download is several GB.
echo ============================================================
echo.
"%PY%" -m pip install --upgrade pip
"%PY%" -m pip install -r requirements.txt
"%PY%" download_model.py --config config_figstep_tiny.yaml
echo.
echo Done. Run 00_smoke_test.bat next.
echo.
pause
