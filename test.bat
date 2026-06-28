@echo off
chcp 65001 > nul
cls

echo ========================================
echo Bot System Check
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo X Virtual environment not found
    echo   Please run setup.bat first
    echo.
    pause
    exit /b 1
)
echo [OK] Virtual environment found
echo.

REM Check if .env exists
if not exist ".env" (
    echo X .env file not found
    echo   Please run setup.bat first
    echo.
    pause
    exit /b 1
)
echo [OK] .env file exists
echo.

REM Activate venv and run check
call venv\Scripts\activate.bat

echo Running system check...
echo.
python check_system.py

echo.
pause
