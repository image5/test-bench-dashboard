@echo off
chcp 65001 >nul
echo ========================================
echo   智能测试台架工厂数字孪生看板
echo   一键启动脚本
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo [1/4] 初始化后端...
cd backend
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
pip show fastapi >nul 2>&1
if errorlevel 1 (
    pip install -r requirements.txt
)
if not exist "data" mkdir data
python init_db.py

echo.
echo [2/4] 启动后端服务...
start "后端服务" cmd /k "venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo [3/4] 初始化前端...
cd ..\frontend
if not exist "node_modules" (
    npm install
)

echo.
echo [4/4] 启动前端服务...
start "前端服务" cmd /k "npm run dev"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo   前端: http://localhost:3000
echo   后端: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo   按任意键打开浏览器...
pause >nul
start http://localhost:3000
