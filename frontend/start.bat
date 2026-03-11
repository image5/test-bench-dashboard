@echo off
echo ========================================
echo   Test Bench Dashboard
echo   Frontend Start Script
echo ========================================
echo.

cd /d "%~dp0"

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

REM Check dependencies
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    npm install
)

REM Start development server
echo.
echo [START] Frontend server running at http://localhost:3000
echo.
npm run dev
