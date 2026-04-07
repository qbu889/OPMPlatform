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
echo "🔗 同时启动Cloudflare Tunnel"
echo ""

# 启动Cloudflare Tunnel（后台运行）
echo "📡 启动Cloudflare Tunnel..."
cloudflared tunnel run --token eyJhIjoiYWM0NmFmMGQzZTViYjIyMGM4YWMyZWYxNzdlMjQxNmMiLCJ0IjoiNDRhMGJiZDQtYjhiZC00YzM4LTk2OTQtOTY4NTNmMzExZjMwIiwicyI6Ik9HUm1PRGswTmpVdFpERTVNaTAwTnpFM0xUZ3dOV0V0TmpSaFkySmlaVFExTmpoaiJ9 &
TUNNEL_PID=$!
echo "✅ Cloudflare Tunnel 已启动（PID: $TUNNEL_PID）"
echo ""

# 捕获退出信号，清理 Tunnel 进程
trap "echo ''; echo '⏹️ 正在停止 Cloudflare Tunnel...'; kill $TUNNEL_PID 2>/dev/null; echo '✅ 已停止 Cloudflare Tunnel'" EXIT INT TERM

# 启动 Flask 应用（直接运行 app.py，这样会执行 __main__ 代码块）
python app.py
