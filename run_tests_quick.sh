#!/bin/bash
# 快速运行测试 - 确保使用正确的虚拟环境

echo "======================================"
echo " 快速运行测试"
echo "======================================"
echo ""

PROJECT_DIR="/Users/linziwang/PycharmProjects/wordToWord"
VENV_DIR="$PROJECT_DIR/.venv"

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 错误：项目目录不存在：$PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || exit 1

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 显示当前 Python 路径
echo "当前 Python: $(which python)"
echo "Python 版本：$(python --version)"
echo ""

# 安装测试依赖
echo "📦 安装测试依赖..."
pip install pytest pytest-cov pytest-flask

# 运行测试
echo ""
echo "🚀 开始运行测试..."
echo ""
python run_tests.py

echo ""
echo "======================================"
echo " 完成!"
echo "======================================"
