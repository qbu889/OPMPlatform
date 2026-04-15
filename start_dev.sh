#!/bin/bash
# start_prod.sh - 快速启动 Flask 应用

echo "======================================"
echo "启动诺基亚 OPM 综合业务系统"
echo "======================================"
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d ".venv" ]; then
    echo "✅ 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "⚠️  未找到 .venv 虚拟环境，将使用系统 Python"
fi

# 检查端口是否被占用
PORT=${PORT:-5001}
echo "🔍 检查端口 $PORT..."
lsof -ti:$PORT > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️  端口 $PORT 被占用，正在释放..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# 启动应用
echo "🚀 启动 Flask 应用，端口：$PORT"
echo "🌐 访问地址：http://127.0.0.1:$PORT"
echo ""
echo "按 Ctrl+C 停止应用"
echo "======================================"
echo ""

python -m flask run --port=$PORT
