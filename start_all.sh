#!/bin/bash
# start_all.sh - 统一启动前后端服务
#
# 用法:
#   ./start_all.sh                    # 默认生产模式启动
#   ./start_all.sh prod               # 生产模式 (后端5004 + 前端5173)
#   ./start_all.sh production         # 生产模式 (后端5004 + 前端5173)
#   ./start_all.sh dev                # 开发模式 (后端5001 + 前端5200)
#   ./start_all.sh development        # 开发模式 (后端5001 + 前端5200)
#   ./start_all.sh backend            # 仅启动后端
#   ./start_all.sh frontend           # 仅启动前端

# 设置参数
MODE=${1:-prod}

echo "=========================================="
echo "  诺基亚 OPM 综合业务系统 - 统一启动脚本"
echo "=========================================="
echo ""

# 确定运行模式
if [ "$MODE" = "dev" ] || [ "$MODE" = "development" ]; then
    RUN_MODE="development"
    BACKEND_PORT=5001
    FRONTEND_PORT=5200
    echo "🔧 开发模式"
elif [ "$MODE" = "backend" ]; then
    RUN_MODE="backend_only"
    BACKEND_PORT=5004
    echo "🖥️  仅启动后端"
elif [ "$MODE" = "frontend" ]; then
    RUN_MODE="frontend_only"
    FRONTEND_PORT=5173
    echo "🌐 仅启动前端"
else
    RUN_MODE="production"
    BACKEND_PORT=5004
    FRONTEND_PORT=5173
    echo "🚀 生产模式"
fi
echo ""

# ============================================================================
# 函数定义
# ============================================================================

# 检查并释放端口
check_and_free_port() {
    local port=$1
    lsof -ti:$port > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "⚠️  端口 $port 被占用，正在释放..."
        lsof -ti:$port | xargs kill -9 2>/dev/null
        sleep 1
        echo "✅ 端口 $port 已释放"
    else
        echo "✅ 端口 $port 可用"
    fi
}

# 启动后端服务
start_backend() {
    echo "=========================================="
    echo "  启动后端服务"
    echo "=========================================="
    echo ""
    
    # 进入项目根目录
    cd "$(dirname "$0")"
    
    # 激活虚拟环境
    if [ -d ".venv" ]; then
        echo "✅ 激活 Python 虚拟环境..."
        source .venv/bin/activate
    else
        echo "⚠️  未找到 .venv 虚拟环境，将使用系统 Python"
    fi
    
    # 检查并释放端口
    check_and_free_port $BACKEND_PORT
    
    # 设置环境变量
    export PORT=$BACKEND_PORT
    if [ "$RUN_MODE" = "production" ]; then
        export NODE_ENV=production
        export FLASK_ENV=production
    else
        export NODE_ENV=development
        export FLASK_ENV=development
    fi
    
    echo "🚀 启动 Flask 应用"
    echo "   端口: $BACKEND_PORT"
    echo "   访问地址: http://127.0.0.1:$BACKEND_PORT"
    echo "   按 Ctrl+C 停止服务"
    echo "=========================================="
    echo ""
    
    # 启动应用
    python app.py
}

# 启动前端服务
start_frontend() {
    echo "=========================================="
    echo "  启动前端服务"
    echo "=========================================="
    echo ""
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ 错误: 未找到 Node.js，请先安装 Node.js"
        exit 1
    fi
    
    echo "✅ Node.js 版本: $(node --version)"
    echo "✅ npm 版本: $(npm --version)"
    echo ""
    
    # 进入前端目录
    cd "$(dirname "$0")/frontend" || {
        echo "❌ 错误: 找不到 frontend 目录"
        exit 1
    }
    
    # 检查依赖
    if [ ! -d "node_modules" ]; then
        echo "📦 首次运行，正在安装依赖..."
        npm install
        echo ""
    fi
    
    # 检查并释放端口
    check_and_free_port $FRONTEND_PORT
    
    if [ "$RUN_MODE" = "production" ]; then
        # 生产模式：先构建再预览
        export NODE_ENV=production
        
        echo "🔨 正在构建生产版本..."
        npm run build
        
        if [ $? -ne 0 ]; then
            echo "❌ 构建失败"
            exit 1
        fi
        
        echo ""
        echo "✅ 构建完成"
        echo ""
        echo "🚀 启动生产预览服务器"
        echo "   端口: $FRONTEND_PORT"
        echo "   后端端口: $BACKEND_PORT"
        echo "   访问地址: http://localhost:$FRONTEND_PORT"
        echo "   按 Ctrl+C 停止服务"
        echo "=========================================="
        echo ""
        
        npm run preview
    else
        # 开发模式
        export NODE_ENV=development
        
        echo "🚀 启动前端开发服务器"
        echo "   端口: $FRONTEND_PORT"
        echo "   后端端口: $BACKEND_PORT"
        echo "   访问地址: http://localhost:$FRONTEND_PORT"
        echo "   按 Ctrl+C 停止服务"
        echo "=========================================="
        echo ""
        
        npm run dev
    fi
}

# 同时启动前后端（后台运行）
start_both_background() {
    echo "=========================================="
    echo "  同时启动前后端服务（后台运行）"
    echo "=========================================="
    echo ""
    
    # 获取脚本所在目录的绝对路径
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    
    # 创建日志目录
    mkdir -p "$SCRIPT_DIR/logs"
    
    # 启动后端（后台）
    echo "🚀 启动后端服务（后台）..."
    cd "$SCRIPT_DIR"
    
    # 激活虚拟环境并启动后端
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    export PORT=$BACKEND_PORT
    if [ "$RUN_MODE" = "production" ]; then
        export NODE_ENV=production
        export FLASK_ENV=production
    else
        export NODE_ENV=development
        export FLASK_ENV=development
    fi
    
    nohup python app.py > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    echo "   日志: $SCRIPT_DIR/logs/backend.log"
    echo ""
    
    # 等待后端启动
    echo "⏳ 等待后端服务就绪..."
    sleep 3
    
    # 启动前端（后台）
    echo "🚀 启动前端服务（后台）..."
    cd "$SCRIPT_DIR/frontend"
    
    export NODE_ENV=$([ "$RUN_MODE" = "production" ] && echo "production" || echo "development")
    
    if [ "$RUN_MODE" = "production" ]; then
        # 生产模式需要先构建
        npm run build > "$SCRIPT_DIR/logs/frontend_build.log" 2>&1
        if [ $? -ne 0 ]; then
            echo "❌ 前端构建失败"
            kill $BACKEND_PID
            exit 1
        fi
        nohup npm run preview > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    else
        nohup npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
    fi
    
    FRONTEND_PID=$!
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    echo "   日志: $SCRIPT_DIR/logs/frontend.log"
    echo ""
    
    # 保存 PID 文件
    echo "$BACKEND_PID" > "$SCRIPT_DIR/.backend.pid"
    echo "$FRONTEND_PID" > "$SCRIPT_DIR/.frontend.pid"
    
    echo "=========================================="
    echo "  服务启动完成"
    echo "=========================================="
    echo ""
    echo "📊 服务信息:"
    echo "   后端: http://127.0.0.1:$BACKEND_PORT (PID: $BACKEND_PID)"
    echo "   前端: http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
    echo ""
    echo "📝 日志文件:"
    echo "   后端: $SCRIPT_DIR/logs/backend.log"
    echo "   前端: $SCRIPT_DIR/logs/frontend.log"
    echo ""
    echo "🛑 停止服务:"
    echo "   ./start_all.sh stop"
    echo ""
    echo "💡 提示: 查看实时日志可使用:"
    echo "   tail -f $SCRIPT_DIR/logs/backend.log"
    echo "   tail -f $SCRIPT_DIR/logs/frontend.log"
    echo "=========================================="
}

# 停止所有服务
stop_services() {
    echo "=========================================="
    echo "  停止所有服务"
    echo "=========================================="
    echo ""
    
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    
    # 停止后端
    if [ -f "$SCRIPT_DIR/.backend.pid" ]; then
        BACKEND_PID=$(cat "$SCRIPT_DIR/.backend.pid")
        if ps -p $BACKEND_PID > /dev/null; then
            echo "🛑 停止后端服务 (PID: $BACKEND_PID)..."
            kill $BACKEND_PID
            sleep 1
            echo "✅ 后端服务已停止"
        else
            echo "⚠️  后端服务未运行"
        fi
        rm -f "$SCRIPT_DIR/.backend.pid"
    else
        echo "⚠️  未找到后端 PID 文件，尝试通过端口查找..."
        lsof -ti:5004 | xargs kill -9 2>/dev/null
        lsof -ti:5001 | xargs kill -9 2>/dev/null
        echo "✅ 已清理后端进程"
    fi
    
    # 停止前端
    if [ -f "$SCRIPT_DIR/.frontend.pid" ]; then
        FRONTEND_PID=$(cat "$SCRIPT_DIR/.frontend.pid")
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "🛑 停止前端服务 (PID: $FRONTEND_PID)..."
            kill $FRONTEND_PID
            sleep 1
            echo "✅ 前端服务已停止"
        else
            echo "⚠️  前端服务未运行"
        fi
        rm -f "$SCRIPT_DIR/.frontend.pid"
    else
        echo "⚠️  未找到前端 PID 文件，尝试通过端口查找..."
        lsof -ti:5173 | xargs kill -9 2>/dev/null
        lsof -ti:5200 | xargs kill -9 2>/dev/null
        echo "✅ 已清理前端进程"
    fi
    
    echo ""
    echo "✅ 所有服务已停止"
    echo "=========================================="
}

# 显示服务状态
show_status() {
    echo "=========================================="
    echo "  服务状态"
    echo "=========================================="
    echo ""
    
    # 检查后端
    BACKEND_RUNNING=false
    if lsof -ti:5004 > /dev/null 2>&1; then
        echo "✅ 后端服务运行中 (端口 5004)"
        BACKEND_RUNNING=true
    elif lsof -ti:5001 > /dev/null 2>&1; then
        echo "✅ 后端服务运行中 (端口 5001)"
        BACKEND_RUNNING=true
    else
        echo "❌ 后端服务未运行"
    fi
    
    # 检查前端
    FRONTEND_RUNNING=false
    if lsof -ti:5173 > /dev/null 2>&1; then
        echo "✅ 前端服务运行中 (端口 5173)"
        FRONTEND_RUNNING=true
    elif lsof -ti:5200 > /dev/null 2>&1; then
        echo "✅ 前端服务运行中 (端口 5200)"
        FRONTEND_RUNNING=true
    else
        echo "❌ 前端服务未运行"
    fi
    
    echo ""
    
    if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ]; then
        echo "💡 访问地址:"
        echo "   前端: http://localhost:5173 或 http://localhost:5200"
        echo "   后端: http://127.0.0.1:5004 或 http://127.0.0.1:5001"
    fi
    
    echo "=========================================="
}

# ============================================================================
# 主逻辑
# ============================================================================

case "$MODE" in
    prod|production)
        start_both_background
        ;;
    dev|development)
        start_both_background
        ;;
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    stop)
        stop_services
        ;;
    status)
        show_status
        ;;
    *)
        echo "❌ 未知模式: $MODE"
        echo ""
        echo "用法:"
        echo "  ./start_all.sh                    # 生产模式后台启动"
        echo "  ./start_all.sh prod               # 生产模式后台启动"
        echo "  ./start_all.sh dev                # 开发模式后台启动"
        echo "  ./start_all.sh backend            # 仅启动后端（前台）"
        echo "  ./start_all.sh frontend           # 仅启动前端（前台）"
        echo "  ./start_all.sh stop               # 停止所有服务"
        echo "  ./start_all.sh status             # 查看服务状态"
        exit 1
        ;;
esac
