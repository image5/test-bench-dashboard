@echo off
chcp 65001 >nul
echo ========================================
echo   智能测试台架工厂数字孪生看板
echo   后端启动脚本
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

REM 检查虚拟环境
if not exist "venv" (
    echo [信息] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [信息] 安装依赖...
    pip install -r requirements.txt
)

REM 创建数据目录
if not exist "data" mkdir data

REM 启动服务
echo.
echo [启动] 后端服务运行在 http://localhost:8000
echo [API文档] http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
