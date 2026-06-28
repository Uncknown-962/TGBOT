@echo off
chcp 65001 > nul
cls
echo ========================================
echo Starting Telegram Bot...
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please run setup.bat first
    echo.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Starting bot...
echo ========================================
echo Bot is running. Press Ctrl+C to stop.
echo ========================================
echo.

python main.py

echo.
echo ========================================
echo Bot stopped
echo ========================================
pause
