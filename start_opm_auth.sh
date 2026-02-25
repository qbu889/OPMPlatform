#!/bin/bash
# start_opm_auth.sh
# OPM系统带认证功能启动脚本

echo "=== 启动OPM系统（带认证功能）==="

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python版本: $PYTHON_VERSION"

# 检查必要的依赖
echo "检查依赖包..."
python3 -c "import flask" 2>/dev/null && echo "✓ Flask已安装" || echo "✗ Flask未安装"
python3 -c "import sqlite3" 2>/dev/null && echo "✓ SQLite3已安装" || echo "✗ SQLite3未安装"

# 创建必要目录
mkdir -p templates/auth
mkdir -p models

echo "初始化数据库..."
# 运行测试脚本初始化数据库和测试用户
python3 auth_manual_test.py

echo "启动应用服务器..."
echo "访问地址: http://localhost:5001"
echo "默认管理员账户: admin / Admin123"
echo "按 Ctrl+C 停止服务"

# 启动应用
python3 app.py