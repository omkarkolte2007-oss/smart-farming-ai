@echo off
echo ============================================
echo  SmartFarm AI — Starting Backend Server
echo ============================================
echo.

cd /d "%~dp0backend"

REM Create venv if it doesn't exist yet
if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies silently
echo [3/3] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ============================================
echo  Open your browser at: http://127.0.0.1:5000
echo  Press Ctrl+C to stop the server.
echo ============================================
echo.

python app.py
