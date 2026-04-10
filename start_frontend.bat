@echo off
REM 前端开发服务器 - Windows 启动脚本

echo ==========================================
echo   前端开发服务器 - 启动脚本
echo ==========================================
echo.

REM 检查 Node.js 环境
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo ✅ Node.js 版本:
node --version
echo.

REM 检查 npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 npm
    pause
    exit /b 1
)

echo ✅ npm 版本:
npm --version
echo.

REM 进入前端目录
cd frontend
if errorlevel 1 (
    echo ❌ 错误: 找不到 frontend 目录
    pause
    exit /b 1
)

REM 检查 node_modules
if not exist "node_modules" (
    echo 📦 首次运行，正在安装依赖...
    call npm install
    echo.
)

REM 启动开发服务器
echo 🚀 启动前端开发服务器...
echo    访问地址: http://localhost:5173
echo    按 Ctrl+C 停止服务
echo.
echo ==========================================

npm run dev

pause
