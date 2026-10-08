@echo off
cd /d "%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py -3 dash.py
) else (
    python dash.py
)

if errorlevel 1 (
    echo.
    echo Failed to start PyHub dashboard.
    echo Make sure Python is installed and available on PATH.
    pause
)
