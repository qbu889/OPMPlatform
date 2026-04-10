#!/bin/bash
# 前端开发服务器启动脚本

echo "=========================================="
echo "  前端开发服务器 - 启动脚本"
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

# 启动开发服务器
echo "🚀 启动前端开发服务器..."
echo "   访问地址: http://localhost:5173"
echo "   按 Ctrl+C 停止服务"
echo ""
echo "=========================================="

npm run dev
