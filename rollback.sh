#!/bin/bash
# rollback.sh - 快速回滚脚本
# 用法: ./rollback.sh [backup_file]
# 如果不指定备份文件，将自动选择最新的备份

echo "=========================================="
echo "  快速回滚到历史版本"
echo "=========================================="
echo ""

# 配置
REMOTE_USER="root"
REMOTE_HOST="8.146.228.47"
REMOTE_PATH="/project/wordToWord"
BACKUP_DIR="/project/backups"

# 检查是否指定了备份文件
if [ -n "$1" ]; then
    BACKUP_FILE="$1"
    echo "📦 使用指定的备份文件: $BACKUP_FILE"
else
    echo "🔍 获取最新的备份文件..."
    # SSH 连接到远程服务器获取最新备份
    LATEST_BACKUP=$(ssh ${REMOTE_USER}@${REMOTE_HOST} "ls -t ${BACKUP_DIR}/wordToWord_backup_*.tar.gz 2>/dev/null | head -1")
    
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ 未找到任何备份文件"
        exit 1
    fi
    
    BACKUP_FILE="$LATEST_BACKUP"
    echo "✅ 找到最新备份: $(basename $BACKUP_FILE)"
fi

# 确认回滚操作
echo ""
echo "⚠️  警告：即将执行回滚操作！"
echo "   当前将回滚到: $(basename $BACKUP_FILE)"
echo ""
read -p "确认执行回滚？(yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ 取消回滚"
    exit 0
fi

echo ""
echo "🔄 开始回滚..."
echo ""

# SSH 执行远程回滚
ssh ${REMOTE_USER}@${REMOTE_HOST} << EOF
    cd /project
    
    echo "=========================================="
    echo "  步骤 1: 停止现有服务"
    echo "=========================================="
    
    cd ${REMOTE_PATH}
    pkill -f "python app.py" || true
    pkill -f "vite" || true
    pkill -f "npm run" || true
    sleep 2
    
    echo "✅ 进程已停止"
    ps -ef | grep -E "python|vite|node" | grep wordToWord | grep -v grep || echo "   确认：所有进程已清理"
    
    echo ""
    echo "=========================================="
    echo "  步骤 2: 备份当前版本（以防需要再次回滚）"
    echo "=========================================="
    
    ROLLBACK_TIMESTAMP=\$(date '+%Y%m%d_%H%M%S')
    CURRENT_BACKUP="${BACKUP_DIR}/wordToWord_before_rollback_\${ROLLBACK_TIMESTAMP}.tar.gz"
    
    echo "📦 正在备份当前版本到 \${CURRENT_BACKUP} ..."
    tar -czf "\${CURRENT_BACKUP}" \
        --exclude='node_modules' \
        --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='logs/*.log' \
        wordToWord/
    
    if [ \$? -eq 0 ]; then
        BACKUP_SIZE=\$(du -h "\${CURRENT_BACKUP}" | cut -f1)
        echo "✅ 当前版本备份完成！大小: \$BACKUP_SIZE"
    else
        echo "⚠️  备份失败，继续回滚..."
    fi
    
    echo ""
    echo "=========================================="
    echo "  步骤 3: 恢复备份版本"
    echo "=========================================="
    
    # 清空当前项目目录（保留必要的配置文件）
    echo "🗑️  清空当前项目目录..."
    cd ${REMOTE_PATH}
    
    # 保留重要的配置和数据文件
    mkdir -p /tmp/wordToWord_preserve
    cp -r logs /tmp/wordToWord_preserve/ 2>/dev/null || true
    cp .env /tmp/wordToWord_preserve/ 2>/dev/null || true
    cp users.db /tmp/wordToWord_preserve/ 2>/dev/null || true
    cp knowledge_base.db /tmp/wordToWord_preserve/ 2>/dev/null || true
    
    # 删除旧代码
    rm -rf routes utils models config static templates frontend/dist uploads downloads tmp
    rm -f app.py config.py requirements.txt *.py *.json *.db 2>/dev/null || true
    
    echo "✅ 清理完成"
    
    # 解压备份
    echo "📂 正在解压备份文件: $(basename $BACKUP_FILE) ..."
    tar -xzf "${BACKUP_FILE}" -C /project/
    
    if [ \$? -eq 0 ]; then
        echo "✅ 备份恢复成功"
    else
        echo "❌ 备份恢复失败！"
        echo "⚠️  尝试从回滚前备份恢复..."
        tar -xzf "\${CURRENT_BACKUP}" -C /project/
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    echo "  步骤 4: 恢复配置和数据文件"
    echo "=========================================="
    
    cd ${REMOTE_PATH}
    
    # 恢复日志目录
    if [ -d "/tmp/wordToWord_preserve/logs" ]; then
        cp -r /tmp/wordToWord_preserve/logs/* logs/ 2>/dev/null || true
        echo "✅ 日志文件已恢复"
    fi
    
    # 恢复环境变量
    if [ -f "/tmp/wordToWord_preserve/.env" ]; then
        cp /tmp/wordToWord_preserve/.env .env
        echo "✅ .env 文件已恢复"
    fi
    
    # 恢复数据库文件
    if [ -f "/tmp/wordToWord_preserve/users.db" ]; then
        cp /tmp/wordToWord_preserve/users.db .
        echo "✅ users.db 已恢复"
    fi
    
    if [ -f "/tmp/wordToWord_preserve/knowledge_base.db" ]; then
        cp /tmp/wordToWord_preserve/knowledge_base.db .
        echo "✅ knowledge_base.db 已恢复"
    fi
    
    # 清理临时文件
    rm -rf /tmp/wordToWord_preserve
    
    echo ""
    echo "=========================================="
    echo "  步骤 5: 启动服务"
    echo "=========================================="
    
    # 激活虚拟环境
    source .venv/bin/activate
    
    # 启动后端
    echo "🚀 启动后端服务..."
    export PORT=5004
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   后端 PID: $BACKEND_PID"
    
    sleep 3
    
    # 启动前端
    echo "🚀 启动前端预览服务..."
    cd frontend
    export BACKEND_PORT=5004
    nohup npm run preview > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   前端 PID: $FRONTEND_PID"
    
    cd ..
    
    sleep 3
    
    echo ""
    echo "=========================================="
    echo "  步骤 6: 验证服务状态"
    echo "=========================================="
    
    echo ""
    echo "📊 运行中的进程："
    ps -ef | grep -E "python app.py|vite preview" | grep -v grep
    
    echo ""
    echo "📋 后端日志（最后15行）："
    echo "---"
    TODAY_LOG=$(ls -t logs/app_*.log 2>/dev/null | head -1)
    if [ -n "$TODAY_LOG" ] && [ -f "$TODAY_LOG" ]; then
        tail -15 "$TODAY_LOG"
    else
        if [ -f "logs/backend.log" ]; then
            tail -15 logs/backend.log
        else
            echo "   ⚠️  未找到日志文件"
        fi
    fi
    echo "---"
    
    echo ""
    echo "📋 前端日志（最后15行）："
    echo "---"
    tail -15 logs/frontend.log
    echo "---"
    
    echo ""
    echo "=========================================="
    echo "  ✅ 回滚完成！"
    echo "=========================================="
    echo ""
    echo "📍 访问地址:"
    echo "   后端: http://8.146.228.47:5004"
    echo "   前端: http://8.146.228.47:5173"
    echo ""
    echo "💾 备份信息:"
    echo "   回滚目标版本: $(basename $BACKUP_FILE)"
    echo "   回滚前备份: \${CURRENT_BACKUP}"
    echo ""
    echo "📝 查看日志命令:"
    echo "   ssh root@8.146.228.47 'cd /project/wordToWord && ls -t logs/app_*.log 2>/dev/null | head -1 | xargs tail -f'"
    echo "=========================================="
EOF

echo ""
echo "=========================================="
echo "  ✅ 本地回滚脚本执行完成！"
echo "=========================================="
echo ""
echo "提示："
echo "  1. 等待远程服务器完成回滚和重启（约10-15秒）"
echo "  2. 查看上方输出的日志确认服务是否正常"
echo "  3. 如需再次回滚，可使用回滚前的备份文件"
echo "=========================================="
