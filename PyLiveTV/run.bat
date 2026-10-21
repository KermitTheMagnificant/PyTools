@echo off
cd /d "%~dp0"

set "PY=py"
if exist "..\.venv\Scripts\python.exe" set "PY=..\.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "PY=venv\Scripts\python.exe"

start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8000"

"%PY%" -m uvicorn api:app --reload

pause
