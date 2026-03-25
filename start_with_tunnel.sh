#!/bin/bash
# 启动脚本：同时启动 Flask 应用和 Cloudflare Tunnel

echo "================================================================================"
echo "  启动诺基亚 OPM 系统 + Cloudflare Tunnel"
echo "================================================================================"

# 检查 cloudflared 是否安装
if ! command -v cloudflared &> /dev/null; then
    echo "❌ 未找到 cloudflared 命令"
    echo "   请先安装：brew install cloudflared"
    exit 1
fi

echo "✅ cloudflared 已安装"
echo ""

# 激活虚拟环境
if [ -d ".venv" ]; then
    echo "📦 激活虚拟环境：.venv"
    source .venv/bin/activate
else
    echo "⚠️  未找到虚拟环境 .venv，使用系统 Python"
fi

# 设置环境变量
export FLASK_APP=app.py
export FLASK_ENV=development
export PORT=5001

echo "🚀 启动 Flask 应用（端口：$PORT）"
echo "🔗 同时启动 Cloudflare Tunnel"
echo ""

# 启动 Flask 应用（直接运行 app.py，这样会执行 __main__ 代码块）
python app.py
