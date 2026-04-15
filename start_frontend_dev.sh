#!/bin/bash
# 前端服务器启动脚本
#
# 用法:
#   ./start_frontend_prod.sh          # 开发模式 (默认, 端口 5200)
#   ./start_frontend_prod.sh dev      # 开发模式 (端口 5200)
#   ./start_frontend_prod.sh prod     # 生产模式 (端口 5173)
#   ./start_frontend_prod.sh production  # 生产模式 (端口 5173)

# 检查参数
MODE=${1:-dev}

echo "=========================================="
if [ "$MODE" = "prod" ] || [ "$MODE" = "production" ]; then
    echo "  前端生产服务器 - 启动脚本"
else
    echo "  前端开发服务器 - 启动脚本"
fi
echo "=========================================="
echo ""

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo ""

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到 npm"
    exit 1
fi

echo "✅ npm 版本: $(npm --version)"
echo ""

# 进入前端目录
cd frontend || {
    echo "❌ 错误: 找不到 frontend 目录"
    exit 1
}

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，正在安装依赖..."
    npm install
    echo ""
fi

# 启动服务器
if [ "$MODE" = "prod" ] || [ "$MODE" = "production" ]; then
    # 生产模式：先构建，再预览
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
    echo "🚀 启动生产预览服务器..."
    echo "   前端端口: 5173"
    echo "   后端端口: 5004"
    echo "   访问地址: http://localhost:5173"
    echo "   按 Ctrl+C 停止服务"
    echo ""
    echo "=========================================="
    
    npm run preview
else
    # 开发模式
    export NODE_ENV=development
    
    echo "🚀 启动前端开发服务器..."
    echo "   前端端口: 5200"
    echo "   后端端口: 5001"
    echo "   访问地址: http://localhost:5200"
    echo "   按 Ctrl+C 停止服务"
    echo ""
    echo "=========================================="
    
    npm run dev
fi
