#!/bin/bash
# Git CI/CD 快速启动脚本
# 用于初始化测试环境并运行自动化测试

set -e  # 遇到错误立即退出

echo "=========================================="
echo " Git CI/CD 快速启动脚本"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo -e "${YELLOW}检查 Python 版本...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本：$python_version"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python3 -m venv .venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source .venv/bin/activate

# 升级 pip
echo -e "${YELLOW}升级 pip...${NC}"
pip install --upgrade pip

# 安装依赖
echo -e "${YELLOW}安装项目依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo -e "${GREEN}✓ requirements.txt 安装完成${NC}"
fi

if [ -f "requirements-linux.txt" ]; then
    pip install -r requirements-linux.txt
    echo -e "${GREEN}✓ requirements-linux.txt 安装完成${NC}"
fi

# 安装测试工具
echo -e "${YELLOW}安装测试工具...${NC}"
pip install pytest pytest-cov pytest-flask
echo -e "${GREEN}✓ 测试工具安装完成${NC}"

# 创建测试配置文件
echo -e "${YELLOW}创建测试配置文件...${NC}"
cat > .env << EOF
# Test Environment Configuration
FLASK_ENV=testing
SECRET_KEY=test-secret-key-for-ci

# MySQL Database Configuration (如果需要)
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=12345678
MYSQL_CHARSET=utf8mb4

# Ollama Configuration (可选)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b

# Logging Configuration
LOG_LEVEL=ERROR
LOG_TO_CONSOLE=true
LOG_TO_FILE=false
EOF
echo -e "${GREEN}✓ .env 文件创建完成${NC}"

# 显示配置信息
echo ""
echo "=========================================="
echo " 环境配置完成！"
echo "=========================================="
echo ""
echo -e "${YELLOW}运行测试的方法:${NC}"
echo ""
echo "1. 使用运行脚本（推荐）:"
echo -e "   ${GREEN}python run_tests.py${NC}"
echo ""
echo "2. 直接使用 pytest:"
echo -e "   ${GREEN}pytest test/ -v --cov=. --cov-report=html${NC}"
echo ""
echo "3. 运行特定测试:"
echo -e "   ${GREEN}pytest test/kafka/ -v${NC}"
echo ""
echo "4. 查看覆盖率报告:"
echo -e "   ${GREEN}open htmlcov/index.html${NC} (Mac)"
echo -e "   ${GREEN}start htmlcov\\index.html${NC} (Windows)"
echo ""
echo "=========================================="
echo ""

# 询问是否立即运行测试
read -p "是否现在运行测试？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}开始运行测试...${NC}"
    python run_tests.py
fi

echo ""
echo -e "${GREEN}✓  setup 完成！${NC}"
echo ""
