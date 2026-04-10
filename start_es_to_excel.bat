@echo off
REM ES 查询结果转 Excel - Windows 启动脚本

echo ==========================================
echo   ES 查询结果转 Excel - 启动脚本
echo ==========================================
echo.

REM 检查 Python 环境
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到 Python，请先安装 Python 3.13+
    pause
    exit /b 1
)

echo ✅ Python 版本:
python --version
echo.

REM 创建必要的目录
echo 📁 创建必要的目录...
if not exist "uploads\es_to_excel" mkdir uploads\es_to_excel
if not exist "downloads\es_to_excel" mkdir downloads\es_to_excel
echo ✅ 目录创建完成
echo.

REM 检查依赖
echo 📦 检查依赖...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Flask 未安装，正在安装依赖...
    pip install -r requirements.txt
)

python -c "import pandas" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Pandas 未安装，正在安装...
    pip install pandas openpyxl
)
echo ✅ 依赖检查完成
echo.

REM 启动 Flask 应用
echo 🚀 启动 Flask 应用...
echo    访问地址: http://localhost:5001/es-to-excel
echo    按 Ctrl+C 停止服务
echo.
echo ==========================================

python app.py

pause
