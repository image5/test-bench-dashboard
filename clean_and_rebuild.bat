@echo off
echo ========================================
echo   完整清理和重新构建
echo ========================================
echo.

cd /d "%~dp0"

echo [步骤1/5] 清理前端缓存...
cd frontend
if exist ".next" rmdir /s /q ".next"
if exist "out" rmdir /s /q "out"
if exist "node_modules\.cache" rmdir /s /q "node_modules\.cache"
cd ..

echo [步骤2/5] 清理后端缓存...
cd backend
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "app\__pycache__" rmdir /s /q "app\__pycache__"
cd ..

echo [步骤3/5] 重新安装前端依赖...
cd frontend
call npm install
cd ..

echo [步骤4/5] 构建前端...
cd frontend
call npm run build
cd ..

echo [步骤5/5] 验证构建...
if exist "frontend\out\index.html" (
    echo.
    echo ========================================
    echo   构建成功！
    echo ========================================
    echo.
    echo 输出目录: %~dp0frontend\out
    echo.
) else (
    echo.
    echo ========================================
    echo   构建失败！
    echo ========================================
    echo.
    echo 请检查错误信息
    echo.
)

pause
