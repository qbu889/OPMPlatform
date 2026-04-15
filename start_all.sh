#!/bin/bash
# 完整启动脚本 - 同时启动后端和前端

echo "=========================================="
echo "  OPM 系统 - 完整启动脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否安装了 tmux 或 screen
if command -v tmux &> /dev/null; then
    SESSION_MANAGER="tmux"
elif command -v screen &> /dev/null; then
    SESSION_MANAGER="screen"
else
    echo "⚠️  未找到 tmux 或 screen，将使用后台模式启动"
    SESSION_MANAGER="background"
fi

echo "📋 使用会话管理器: $SESSION_MANAGER"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads/es_to_excel
mkdir -p downloads/es_to_excel
mkdir -p logs
echo "✅ 目录创建完成"
echo ""

# 启动后端
echo -e "${BLUE}🚀 启动后端服务...${NC}"
if [ "$SESSION_MANAGER" = "tmux" ]; then
    tmux new-session -d -s opm-backend "python3 app.py"
    echo "✅ 后端已在 tmux 会话 'opm-backend' 中启动"
    echo "   查看日志: tmux attach -t opm-backend"
elif [ "$SESSION_MANAGER" = "screen" ]; then
    screen -dmS opm-backend python3 app.py
    echo "✅ 后端已在 screen 会话 'opm-backend' 中启动"
    echo "   查看日志: screen -r opm-backend"
else
    nohup python3 app.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ 后端已在后台启动 (PID: $BACKEND_PID)"
    echo "   查看日志: tail -f logs/backend.log"
    echo "   停止服务: kill $BACKEND_PID"
fi
echo ""

# 等待后端启动
echo "⏳ 等待后端启动..."
sleep 3
echo ""

# 启动前端
echo -e "${BLUE}🚀 启动前端服务...${NC}"
cd frontend || {
    echo "❌ 错误: 找不到 frontend 目录"
    exit 1
}

if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
    echo ""
fi

if [ "$SESSION_MANAGER" = "tmux" ]; then
    tmux new-window -t opm-backend -n opm-frontend "npm run dev"
    echo "✅ 前端已在 tmux 会话 'opm-backend' 的 'opm-frontend' 窗口中启动"
    echo "   切换到前端: tmux attach -t opm-backend"
    echo "   切换窗口: Ctrl+B, 然后按 1"
elif [ "$SESSION_MANAGER" = "screen" ]; then
    screen -S opm-backend -X screen -t opm-frontend npm run dev
    echo "✅ 前端已在 screen 会话 'opm-backend' 中启动"
    echo "   查看日志: screen -r opm-backend"
else
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端已在后台启动 (PID: $FRONTEND_PID)"
    echo "   查看日志: tail -f logs/frontend.log"
    echo "   停止服务: kill $FRONTEND_PID"
fi

cd ..
echo ""

echo -e "${GREEN}=========================================="
echo "  ✅ 所有服务已启动！"
echo "==========================================${NC}"
echo ""
echo "📍 访问地址:"
echo "   后端 API: http://localhost:5001"
echo "   前端页面: http://localhost:5173"
echo ""
echo "📋 管理命令:"
if [ "$SESSION_MANAGER" = "tmux" ]; then
    echo "   查看所有会话: tmux list-sessions"
    echo "   连接到会话: tmux attach -t opm-backend"
    echo "   停止所有服务: tmux kill-session -t opm-backend"
elif [ "$SESSION_MANAGER" = "screen" ]; then
    echo "   查看所有会话: screen -ls"
    echo "   连接到会话: screen -r opm-backend"
    echo "   停止所有服务: screen -S opm-backend -X quit"
else
    echo "   查看后端日志: tail -f logs/backend.log"
    echo "   查看前端日志: tail -f logs/frontend.log"
    if [ ! -z "$BACKEND_PID" ]; then
        echo "   停止后端: kill $BACKEND_PID"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "   停止前端: kill $FRONTEND_PID"
    fi
fi
echo ""
echo "=========================================="
