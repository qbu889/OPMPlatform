#!/bin/bash
# 在线表格系统快速启动脚本

echo "🚀 启动在线表格系统..."
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    exit 1
fi

# 检查虚拟环境
if [ -d ".venv1" ]; then
    echo "✅ 激活虚拟环境..."
    source .venv1/bin/activate
fi

# 检查依赖
echo "📦 检查依赖..."
pip3 install -q flask flask-sqlalchemy python-dotenv markdown

# 启动应用
echo ""
echo "🌐 正在启动服务器..."
echo "📍 访问地址：http://localhost:5001/spreadsheet/"
echo ""
echo "💡 提示：按 Ctrl+C 停止服务器"
echo ""

python3 app.py
