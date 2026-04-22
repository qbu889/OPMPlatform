#!/bin/bash
# start_all_dev.sh - 一键启动开发环境（后端 + 前端）
#
# 用法:
#   ./start_all_dev.sh          # 启动开发环境
#   ./start_all_dev.sh --help   # 显示帮助信息

# 显示帮助信息
show_help() {
    echo "=========================================="
    echo "  诺基亚 OPM 综合业务系统 - 开发环境启动"
    echo "=========================================="
    echo ""
    echo "用法:"
    echo "  ./start_all_dev.sh          # 启动开发环境（后端5002 + 前端5200）"
    echo "  ./start_all_dev.sh --help   # 显示此帮助信息"
    echo ""
    echo "服务说明:"
    echo "  - 后端服务: http://localhost:5002"
    echo "  - 前端服务: http://localhost:5200"
    echo "  - Cloudflare Tunnel: 自动启动"
    echo "  - IOPaint AI 服务: 自动启动（端口 8080）"
    echo ""
    echo "停止服务:"
    echo "  按 Ctrl+C 停止所有服务"
    echo "=========================================="
    exit 0
}

# 检查帮助参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
fi

echo "=========================================="
echo "  启动诺基亚 OPM 综合业务系统（开发环境）"
echo "=========================================="
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 获取本机局域网 IP 地址
get_local_ip() {
    # macOS 使用 ifconfig 获取 en0（通常是 WiFi）或 en1 的 IP
    if command -v ifconfig &> /dev/null; then
        local ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
        if [ -n "$ip" ]; then
            echo "$ip"
            return
        fi
    fi
    
    # Linux 使用 ip 命令
    if command -v ip &> /dev/null; then
        local ip=$(ip route get 1 | awk '{print $7; exit}')
        if [ -n "$ip" ]; then
            echo "$ip"
            return
        fi
    fi
    
    echo "localhost"
}

LOCAL_IP=$(get_local_ip)

echo " 本机局域网 IP: $LOCAL_IP"
echo ""

# ============================================================================
# 1. 启动后端服务
# ============================================================================
echo "📌 步骤 1/2: 启动后端服务..."
echo ""

# 激活虚拟环境
if [ -d ".venv" ]; then
    echo "✅ 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "⚠️  未找到 .venv 虚拟环境，将使用系统 Python"
fi

# 检查端口是否被占用
BACKEND_PORT=${PORT:-5002}
echo "🔍 检查后端端口 $BACKEND_PORT..."
lsof -ti:$BACKEND_PORT > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️  端口 $BACKEND_PORT 被占用，正在释放..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

echo "🚀 启动 Flask 后端应用（端口：$BACKEND_PORT）..."
echo ""

# 在后台启动后端服务
PORT=$BACKEND_PORT python app.py &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端是否成功启动
if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功（PID: $BACKEND_PID）"
    echo "   本机访问: http://localhost:$BACKEND_PORT"
    echo "   局域网访问: http://$LOCAL_IP:$BACKEND_PORT"
else
    echo "❌ 后端服务启动失败！"
    echo "   请检查日志或手动运行: PORT=$BACKEND_PORT python app.py"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# ============================================================================
# 2. 启动前端服务
# ============================================================================
echo "📌 步骤 2/2: 启动前端服务..."
echo ""

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到 npm"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ npm 版本: $(npm --version)"
echo ""

# 进入前端目录
cd frontend || {
    echo "❌ 错误: 找不到 frontend 目录"
    kill $BACKEND_PID 2>/dev/null
    exit 1
}

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    npm install
    echo ""
fi

# 设置环境变量
export NODE_ENV=development
export BACKEND_PORT=$BACKEND_PORT

# 检查前端端口是否被占用
FRONTEND_PORT=5200
echo "🔍 检查前端端口 $FRONTEND_PORT..."
lsof -ti:$FRONTEND_PORT > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️  端口 $FRONTEND_PORT 被占用，正在释放..."
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

echo "🚀 启动前端开发服务器（端口：$FRONTEND_PORT）..."
echo ""

# 在前台启动前端服务（这样 Ctrl+C 可以同时停止前后端）
echo "=========================================="
echo "  ✅ 所有服务已启动成功！"
echo "=========================================="
echo ""
echo "  🌐 前端服务:"
echo "     - 本机访问: http://localhost:$FRONTEND_PORT"
echo "     - 局域网访问: http://$LOCAL_IP:$FRONTEND_PORT"
echo ""
echo "  🔧 后端服务:"
echo "     - 本机访问: http://localhost:$BACKEND_PORT"
echo "     - 局域网访问: http://$LOCAL_IP:$BACKEND_PORT"
echo ""
echo "  📡 Cloudflare Tunnel: 已自动启动"
echo "  🤖 IOPaint AI 服务: 已自动启动（端口 8080）"
echo ""
echo "  按 Ctrl+C 停止所有服务"
echo "=========================================="
echo ""

# 启动前端（前台运行，便于 Ctrl+C 统一停止，--host 0.0.0.0 支持局域网访问）
npm run dev -- --host 0.0.0.0

# 如果前端退出，清理后端进程
echo ""
echo "🛑 前端服务已停止，正在清理后端服务..."
kill $BACKEND_PID 2>/dev/null
wait $BACKEND_PID 2>/dev/null
echo "✅ 所有服务已停止"
