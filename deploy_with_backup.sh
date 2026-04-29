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

# 动态检测变更文件并上传
echo "🔍 检测变更文件..."

# 获取 Git 变更的文件列表
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git ls-files --modified)

if [ -z "$CHANGED_FILES" ]; then
    echo "⚠️  未检测到变更文件，将上传核心文件..."
    # 默认上传核心文件
    CHANGED_FILES="app.py config.py requirements.txt routes/kafka/kafka_generator_routes.py"
fi

echo "📦 检测到以下变更文件："
echo "$CHANGED_FILES" | while read file; do
    echo "   - $file"
done
echo ""

# 分类上传文件
BACKEND_FILES=()
FRONTEND_FILES=()

while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi
    
    # 判断是前端还是后端文件
    if [[ "$file" == frontend/* ]]; then
        FRONTEND_FILES+=("$file")
    else
        BACKEND_FILES+=("$file")
    fi
done <<< "$CHANGED_FILES"

# 上传后端文件
if [ ${#BACKEND_FILES[@]} -gt 0 ]; then
    echo "📤 上传后端文件 (${#BACKEND_FILES[@]} 个)..."
    for file in "${BACKEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            # 确保远程目录存在
            REMOTE_DIR="${REMOTE_PATH}/$(dirname $file)"
            ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}" 2>/dev/null
            
            echo "   📄 $file"
            scp "$file" ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"$file"
        fi
    done
    echo "✅ 后端文件上传完成"
else
    echo "ℹ️  无后端文件变更"
fi

echo ""

# 上传前端文件
if [ ${#FRONTEND_FILES[@]} -gt 0 ]; then
    echo "📤 上传前端文件 (${#FRONTEND_FILES[@]} 个)..."
    
    # 如果有前端源码变更，需要重新构建
    NEED_REBUILD=false
    for file in "${FRONTEND_FILES[@]}"; do
        if [[ "$file" != frontend/dist/* ]] && [[ "$file" != frontend/node_modules/* ]]; then
            NEED_REBUILD=true
            break
        fi
    done
    
    if [ "$NEED_REBUILD" = true ]; then
        echo "🔨 检测到前端源码变更，正在重新构建..."
        cd frontend
        npm run build
        if [ $? -eq 0 ]; then
            echo "✅ 前端构建成功"
            # 上传整个 dist 目录
            scp -r dist/* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/frontend/dist/
        else
            echo "❌ 前端构建失败"
            exit 1
        fi
        cd ..
    else
        # 只上传 dist 文件的变更
        for file in "${FRONTEND_FILES[@]}"; do
            if [ -f "$file" ]; then
                echo "   📄 $file"
                scp "$file" ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"$file"
            fi
        done
    fi
    echo "✅ 前端文件上传完成"
else
    echo "ℹ️  无前端文件变更"
fi

echo "✅ 文件上传完成"
echo ""

# SSH 执行远程备份和重启
echo "🔄 远程备份并重启服务..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << EOF
    cd /project/wordToWord
    
    echo "=========================================="
    echo "  步骤 1: 备份现有项目"
    echo "=========================================="
    
    # 创建备份目录
    mkdir -p ${BACKUP_DIR}
    
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
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    BACKEND_PID=\$!
    echo "   后端 PID: \$BACKEND_PID"
    
    sleep 3
    
    # 启动前端
    echo "🚀 启动前端预览服务..."
    cd frontend
    nohup npx vite preview --port 5173 --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=\$!
    echo "   前端 PID: \$FRONTEND_PID"
    
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
    tail -15 logs/backend.log
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
    echo "   tail -f ${REMOTE_PATH}/logs/backend.log"
    echo "   tail -f ${REMOTE_PATH}/logs/frontend.log"
    echo "=========================================="
EOF

echo ""
echo "=========================================="
echo "  ✅ 本地部署脚本执行完成！"
echo "=========================================="
echo ""
echo "提示："
echo "  1. 如果看到密码提示，请输入: nokia@123"
echo "  2. 等待远程服务器完成备份和重启（约10-15秒）"
echo "  3. 查看上方输出的日志确认服务是否正常"
echo "=========================================="
