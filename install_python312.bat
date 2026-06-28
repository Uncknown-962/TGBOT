@echo off
echo ============================================
echo   Installing Python 3.12 for TelegramBot
echo ============================================
echo.

echo Downloading Python 3.12.4...
curl -o python-3.12.4-amd64.exe https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe

echo.
echo Starting installation...
echo Please check "Add Python 3.12 to PATH" during installation!
echo.
python-3.12.4-amd64.exe /quiet InstallAllUsers=0 PrependPath=1

echo.
echo Waiting for installation to complete...
timeout /t 30

echo.
echo Cleaning up installer...
del python-3.12.4-amd64.exe

echo.
echo ============================================
echo   Installation complete!
echo ============================================
echo.
echo Now run: setup.bat
echo.
pause
