#!/bin/bash
# deploy_with_backup.sh - 带备份的快速部署脚本
# 用法: ./deploy_with_backup.sh

echo "=========================================="
echo "  快速部署到远程服务器（含备份）"
echo "=========================================="
echo ""

# 配置
REMOTE_USER="root"
REMOTE_HOST="8.146.228.47"
REMOTE_PATH="/project/wordToWord"
BACKUP_DIR="/project/backups"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# SSH选项：抑制警告信息
SSH_OPTS="-o LogLevel=ERROR -o StrictHostKeyChecking=no"

# 检查是否有文件需要提交
if git status --porcelain | grep -q .; then
    echo "📝 检测到未提交的更改，正在提交..."
    git add -A
    git commit -m "Auto deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "✅ 提交完成"
    echo ""
fi

# 推送到远程仓库
echo "📤 推送到 Git 仓库..."
git push origin q/dev
if [ $? -ne 0 ]; then
    echo "❌ Git 推送失败"
    exit 1
fi
echo "✅ Git 推送成功"
echo ""

# 高效部署策略：
# - 后端文件：打包成tar.gz一次性上传
# - 前端文件：直接上传整个dist目录
# - 使用rsync进行增量同步（如果可用）

echo "🔍 检测变更文件..."

# 获取 Git 变更的文件列表
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git ls-files --modified)

if [ -z "$CHANGED_FILES" ]; then
    echo "⚠️  未检测到变更文件，将上传核心文件..."
    # 默认上传核心文件
    CHANGED_FILES="app.py config.py requirements.txt routes/kafka/kafka_generator_routes.py"
fi

echo "📦 检测到以下变更文件："
echo "$CHANGED_FILES" | head -20 | while read file; do
    echo "   - $file"
done
TOTAL_FILES=$(echo "$CHANGED_FILES" | wc -l | tr -d ' ')
if [ "$TOTAL_FILES" -gt 20 ]; then
    echo "   ... 还有 $((TOTAL_FILES - 20)) 个文件"
fi
echo "   总计: $TOTAL_FILES 个文件"
echo ""

# 分类文件
BACKEND_FILES=()
FRONTEND_SOURCE_FILES=()
NEED_FRONTEND_BUILD=false

while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi
    
    # 判断是前端还是后端文件
    if [[ "$file" == frontend/* ]]; then
        # 如果是前端源码（非dist），需要重新构建
        if [[ "$file" != frontend/dist/* ]] && [[ "$file" != frontend/node_modules/* ]]; then
            FRONTEND_SOURCE_FILES+=("$file")
            NEED_FRONTEND_BUILD=true
        fi
    else
        BACKEND_FILES+=("$file")
    fi
done <<< "$CHANGED_FILES"

# 上传后端文件（高效方式：打包后一次性上传）
if [ ${#BACKEND_FILES[@]} -gt 0 ]; then
    echo "📤 上传后端文件 (${#BACKEND_FILES[@]} 个)..."
    
    # 创建临时目录存放要上传的文件
    TEMP_DIR=$(mktemp -d)
    BACKEND_TAR="$TEMP_DIR/backend_update.tar.gz"
    
    echo "   📦 正在打包后端文件..."
    cd /Users/linziwang/PycharmProjects/wordToWord
    
    # 复制文件到临时目录，保持目录结构
    for file in "${BACKEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            DEST_DIR="$TEMP_DIR/$(dirname $file)"
            mkdir -p "$DEST_DIR"
            cp "$file" "$DEST_DIR/"
        fi
    done
    
    # 打包
    cd "$TEMP_DIR"
    tar -czf "$BACKEND_TAR" --remove-files $(find . -type f | sed 's|^\./||')
    
    # 上传压缩包
    echo "   🚀 上传压缩包..."
    scp $SSH_OPTS "$BACKEND_TAR" ${REMOTE_USER}@${REMOTE_HOST}:/tmp/backend_update.tar.gz
    
    # 远程解压
    echo "   📂 远程解压..."
    ssh $SSH_OPTS ${REMOTE_USER}@${REMOTE_HOST} << REMOTE_EOF
        cd ${REMOTE_PATH}
        tar -xzf /tmp/backend_update.tar.gz
        rm -f /tmp/backend_update.tar.gz
        echo "   ✅ 已解压 \$(tar -tzf /tmp/backend_update.tar.gz 2>/dev/null | wc -l || echo '${#BACKEND_FILES[@]}') 个文件"
REMOTE_EOF
    
    # 清理临时文件
    rm -rf "$TEMP_DIR"
    
    echo "✅ 后端文件上传完成（使用打包方式）"
else
    echo "ℹ️  无后端文件变更"
fi

echo ""

# 上传前端文件（高效方式：直接上传dist目录）
if [ "$NEED_FRONTEND_BUILD" = true ] || [ ${#FRONTEND_SOURCE_FILES[@]} -gt 0 ]; then
    echo "📤 处理前端文件..."
    
    # 重新构建前端
    echo "🔨 正在重新构建前端..."
    cd frontend
    npm run build
    if [ $? -eq 0 ]; then
        echo "✅ 前端构建成功"
        
        # 使用rsync或直接scp上传整个dist目录
        echo "🚀 上传前端构建产物..."
        
        # 检查是否可用rsync（更高效，支持增量传输）
        if command -v rsync &> /dev/null; then
            echo "   📡 使用rsync进行增量同步..."
            rsync -avz --delete -e "ssh $SSH_OPTS" dist/ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/frontend/dist/
        else
            echo "   📡 使用scp上传整个dist目录..."
            scp -r $SSH_OPTS dist/* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/frontend/dist/
        fi
        
        echo "✅ 前端文件上传完成"
    else
        echo "❌ 前端构建失败"
        exit 1
    fi
    cd ..
elif [ -d "frontend/dist" ]; then
    # 如果前端dist已存在且无需重新构建，可以选择性上传
    echo "ℹ️  前端无需重新构建，如需更新请手动执行: cd frontend && npm run build"
else
    echo "ℹ️  无前端文件变更"
fi

echo "✅ 文件上传完成"
echo ""

# SSH 执行远程备份和重启
echo "🔄 远程备份并重启服务..."
ssh $SSH_OPTS ${REMOTE_USER}@${REMOTE_HOST} << EOF
    cd /project/wordToWord
    
    echo "=========================================="
    echo "  步骤 1: 备份现有项目"
    echo "=========================================="
    
    # 创建备份目录
    mkdir -p ${BACKUP_DIR}
    
    # 检查今天是否已经有备份
    TODAY=$(date '+%Y%m%d')
    EXISTING_BACKUP=$(ls ${BACKUP_DIR}/wordToWord_backup_${TODAY}_*.tar.gz 2>/dev/null | head -1)
    
    if [ -n "$EXISTING_BACKUP" ]; then
        BACKUP_SIZE=$(du -h "$EXISTING_BACKUP" | cut -f1)
        echo "⚠️  检测到今天已有备份："
        echo "   $(basename $EXISTING_BACKUP) (大小: $BACKUP_SIZE)"
        echo "ℹ️  跳过备份，直接重启服务..."
    else
        # 压缩备份当前项目
        echo "📦 正在备份项目到 ${BACKUP_DIR}/wordToWord_backup_${TIMESTAMP}.tar.gz ..."
        cd /project
        tar -czf ${BACKUP_DIR}/wordToWord_backup_${TIMESTAMP}.tar.gz \
            --exclude='node_modules' \
            --exclude='.venv' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='logs/*.log' \
            wordToWord/
        
        if [ \$? -eq 0 ]; then
            BACKUP_SIZE=\$(du -h ${BACKUP_DIR}/wordToWord_backup_${TIMESTAMP}.tar.gz | cut -f1)
            echo "✅ 备份完成！大小: \$BACKUP_SIZE"
        else
            echo "⚠️  备份失败，继续部署..."
        fi
    fi
    
    # 保留最近5个备份，删除旧的
    echo "🧹 清理旧备份（保留最近5个）..."
    cd ${BACKUP_DIR}
    ls -t wordToWord_backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null
    REMAINING=\$(ls wordToWord_backup_*.tar.gz 2>/dev/null | wc -l)
    echo "   当前备份数量: \$REMAINING"
    
    echo ""
    echo "=========================================="
    echo "  步骤 2: 停止现有服务"
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
    echo "  步骤 3: 启动新服务"
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
    echo "  步骤 4: 验证服务状态"
    echo "=========================================="
    
    echo ""
    echo "📊 运行中的进程："
    ps -ef | grep -E "python app.py|vite preview" | grep -v grep
    
    echo ""
    echo "📋 后端日志（最后15行）："
    echo "---"
    # 动态获取当天的日志文件
    TODAY_LOG=$(ls -t logs/app_*.log 2>/dev/null | head -1)
    if [ -n "$TODAY_LOG" ] && [ -f "$TODAY_LOG" ]; then
        tail -15 "$TODAY_LOG"
    else
        # 如果没有按天分割的日志，尝试 backend.log
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
    echo "  ✅ 部署完成！"
    echo "=========================================="
    echo ""
    echo "📍 访问地址:"
    echo "   后端: http://8.146.228.47:5004"
    echo "   前端: http://8.146.228.47:5173"
    echo ""
    echo "💾 备份位置:"
    echo "   ${BACKUP_DIR}/wordToWord_backup_${TIMESTAMP}.tar.gz"
    echo ""
    echo "📝 查看日志命令:"
    echo "   # 查看当天日志（自动识别）"
    echo "   ssh root@8.146.228.47 'cd /project/wordToWord && ls -t logs/app_*.log 2>/dev/null | head -1 | xargs tail -f'"
    echo "   # 或直接查看 backend.log"
    echo "   ssh root@8.146.228.47 'tail -f /project/wordToWord/logs/backend.log'"
    echo "=========================================="
EOF

echo ""
echo "=========================================="
echo "  ✅ 本地部署脚本执行完成！"
echo "=========================================="
echo ""
echo "提示："
echo "  1. ✅ 已配置 SSH 免密登录，无需输入密码"
echo "  2. 等待远程服务器完成备份和重启（约10-15秒）"
echo "  3. 查看上方输出的日志确认服务是否正常"
echo "=========================================="
