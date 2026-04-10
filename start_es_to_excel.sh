#!/bin/bash
# ES 查询结果转 Excel - 启动脚本

echo "=========================================="
echo "  ES 查询结果转 Excel - 启动脚本"
echo "=========================================="
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.13+"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads/es_to_excel
mkdir -p downloads/es_to_excel
echo "✅ 目录创建完成"
echo ""

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask 未安装，正在安装依赖..."
    pip3 install -r requirements.txt
fi

if ! python3 -c "import pandas" 2>/dev/null; then
    echo "⚠️  Pandas 未安装，正在安装..."
    pip3 install pandas openpyxl
fi
echo "✅ 依赖检查完成"
echo ""

# 启动 Flask 应用
echo "🚀 启动 Flask 应用..."
echo "   访问地址: http://localhost:5001/es-to-excel"
echo "   按 Ctrl+C 停止服务"
echo ""
echo "=========================================="

python3 app.py
