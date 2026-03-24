@echo off
chcp 65001 >nul
echo ========================================
echo   Test Bench Dashboard - 一键启动
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请安装 Node.js 18+
    pause
    exit /b 1
)

echo [1/2] 启动后端服务...
cd backend

REM 创建虚拟环境
if not exist "venv" (
    echo [信息] 创建 Python 虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [信息] 安装后端依赖...
    pip install -r requirements.txt
)

REM 创建数据目录
if not exist "data" mkdir data

REM 启动后端
start "Backend Server" cmd /k "venv\Scripts\activate && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo [后端] http://localhost:8000
echo [API文档] http://localhost:8000/docs
echo.

timeout /t 5 /nobreak >nul

echo [2/2] 启动前端服务...
cd ..\frontend

REM 安装依赖
if not exist "node_modules" (
    echo [信息] 安装前端依赖...
    call npm install
)

REM 启动前端
start "Frontend Server" cmd /k "npm run dev"

echo [前端] http://localhost:3000
echo.

echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8000
echo API文档:  http://localhost:8000/docs
echo.
echo 按任意键打开浏览器...
pause >nul

start http://localhost:3000
