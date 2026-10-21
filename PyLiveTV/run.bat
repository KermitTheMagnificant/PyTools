@echo off
call ..\.venv\Scripts\activate.bat
cd /d "%~dp0"

if exist venv\Scripts\activate.bat call venv\Scripts\activate.bat

start "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:8000"

python -m uvicorn api:app --reload

pause
