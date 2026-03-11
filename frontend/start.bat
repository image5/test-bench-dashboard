@echo off
chcp 65001 >nul
echo ========================================
echo   智能测试台架工厂数字孪生看板
echo   前端启动脚本
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

REM 检查依赖
if not exist "node_modules" (
    echo [信息] 安装依赖...
    npm install
)

REM 启动开发服务器
echo.
echo [启动] 前端服务运行在 http://localhost:3000
echo.
npm run dev
