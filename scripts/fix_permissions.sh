#!/bin/bash
# fix_permissions.sh - 修复项目权限的根本解决方案
# 用途: 统一项目文件所有权和权限,避免 Nginx 403 错误

echo "=========================================="
echo "  修复 wordToWord 项目权限"
echo "=========================================="
echo ""

PROJECT_DIR="/project/wordToWord"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ 项目目录不存在: $PROJECT_DIR"
    exit 1
fi

echo "📁 项目目录: $PROJECT_DIR"
echo ""

# 1. 统一所有者为 www:www
echo "1️⃣  统一文件所有者为 www:www..."
chown -R www:www "$PROJECT_DIR"
echo "   ✅ 完成"
echo ""

# 2. 设置目录权限
echo "2️⃣  设置目录权限 (755)..."
find "$PROJECT_DIR" -type d -exec chmod 755 {} \;
echo "   ✅ 完成"
echo ""

# 3. 设置文件权限
echo "3️⃣  设置文件权限 (644)..."
find "$PROJECT_DIR" -type f -exec chmod 644 {} \;
echo "   ✅ 完成"
echo ""

# 4. 特殊处理可执行文件
echo "4️⃣  设置脚本文件可执行权限..."
chmod +x "$PROJECT_DIR"/*.sh 2>/dev/null || true
chmod +x "$PROJECT_DIR"/scripts/*.sh 2>/dev/null || true
echo "   ✅ 完成"
echo ""

# 5. 确保关键目录权限正确
echo "5️⃣  验证关键目录权限..."
chmod 755 "$PROJECT_DIR"
chmod 755 "$PROJECT_DIR/frontend"
chmod 755 "$PROJECT_DIR/frontend/dist" 2>/dev/null || true
echo "   ✅ 完成"
echo ""

# 6. 显示结果
echo "6️⃣  当前权限状态:"
ls -la "$PROJECT_DIR" | head -5
echo ""
ls -la "$PROJECT_DIR/frontend/" | head -5
echo ""

echo "=========================================="
echo "  ✅ 权限修复完成!"
echo "=========================================="
echo ""
echo "提示:"
echo "  - 所有文件所有者: www:www"
echo "  - 目录权限: 755 (rwxr-xr-x)"
echo "  - 文件权限: 644 (rw-r--r--)"
echo "  - Nginx worker (www) 现在可以正常访问所有文件"
echo ""
