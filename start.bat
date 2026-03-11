@echo off
echo ========================================
echo   Test Bench Dashboard
echo   Quick Start Script
echo ========================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo [1/4] Initializing backend...
cd backend
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)
if not exist "data" mkdir data
python init_db.py

echo.
echo [2/4] Starting backend server...
start "Backend Server" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [3/4] Initializing frontend...
cd ..\frontend
if not exist "node_modules" (
    echo Installing npm dependencies...
    npm install
)

echo.
echo [4/4] Starting frontend server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo   Startup Complete!
echo ========================================
echo.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Press any key to open browser...
pause >nul
start http://localhost:3000
