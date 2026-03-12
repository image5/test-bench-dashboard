@echo off
echo ========================================
echo   Test Bench Dashboard
echo   Production Deployment
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo [STEP 1/3] Starting Backend Server...
echo ========================================
start "Backend Server" cmd /k "cd /d %~dp0backend && start.bat"
timeout /t 5 /nobreak >nul

echo.
echo [STEP 2/3] Installing serve for frontend...
echo ========================================
npm list -g serve >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing serve globally...
    npm install -g serve
)

echo.
echo [STEP 3/3] Starting Frontend Server...
echo ========================================
echo [INFO] Frontend will run at: http://192.168.1.100:3000
echo [INFO] Backend API at: http://192.168.1.100:8000
echo [INFO] API Docs at: http://192.168.1.100:8000/docs
echo.
echo [IMPORTANT] Press Ctrl+C to stop the servers
echo ========================================
echo.

cd /d %~dp0frontend
serve -s out -l 3000

pause
