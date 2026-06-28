@echo off
chcp 65001 > nul
echo ========================================
echo Telegram Bot Setup
echo ========================================
echo.

echo Step 1: Checking Python...
py -3.12 --version > nul 2>&1
if errorlevel 1 (
    echo Error: Python 3.12 is not installed!
    echo.
    echo Please run: install_python312.bat
    echo Or download from: https://www.python.org/downloads/release/python-3124/
    echo.
    pause
    exit /b 1
)

py -3.12 --version
echo Python 3.12 found!
echo.

echo Step 2: Creating virtual environment...
if exist "venv" (
    echo Virtual environment already exists, recreating...
    rmdir /s /q venv
)

py -3.12 -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    echo.
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

echo Step 3: Creating directories...
if not exist "logs" mkdir logs
if not exist "database" mkdir database
echo Directories created!
echo.

echo Step 4: Installing dependencies...
call venv\Scripts\activate.bat && (
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt
) || (
    echo Error: Failed to install dependencies
    echo.
    pause
    exit /b 1
)
echo Dependencies installed successfully!
echo.

echo Step 5: Creating .env file...
if not exist ".env" (
    copy .env.example .env > nul
    echo .env file created from .env.example
    echo.
    echo ========================================
    echo IMPORTANT: Configure your bot now!
    echo ========================================
    echo.
    echo Open .env file and set:
    echo   1. BOT_TOKEN - get from @BotFather
    echo   2. ADMIN_IDS - get from @userinfobot
    echo.
    echo Current values in .env:
    echo   BOT_TOKEN=your_bot_token_here
    echo   ADMIN_IDS=123456789
    echo.
) else (
    echo .env file already exists
    echo.
)

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env file (open with Notepad)
echo   2. Set BOT_TOKEN and ADMIN_IDS
echo   3. Run: run.bat
echo.

pause
