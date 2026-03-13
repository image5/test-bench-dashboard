@echo off
echo ========================================
echo   前端清理和重新构建
echo ========================================
echo.

cd /d "%~dp0frontend"

echo [步骤1/4] 清理缓存...
if exist ".next" rmdir /s /q ".next"
if exist "out" rmdir /s /q "out"
if exist "node_modules\.cache" rmdir /s /q "node_modules\.cache"

echo [步骤2/4] 重新安装依赖...
call npm install

echo [步骤3/4] 清理构建...
call npm run build

echo [步骤4/4] 构建完成！
echo.
echo ========================================
echo   构建成功！
echo ========================================
echo.
echo 输出目录: %~dp0frontend\out
echo.
pause
