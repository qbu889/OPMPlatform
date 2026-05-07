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

# 获取 Git 变更的文件列表（更可靠的检测方式）
echo "   📋 检查 Git 状态..."
LAST_COMMIT=$(git log -1 --oneline 2>/dev/null)
echo "   最新提交: $LAST_COMMIT"

# 方法1: 获取最近3次提交变更的文件（避免遗漏相关文件）
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD~3..HEAD 2>/dev/null)

# 方法2: 如果方法1失败，尝试其他方式
if [ -z "$CHANGED_FILES" ]; then
    echo "   ⚠️  git diff-tree 未检测到变更，尝试其他方式..."
    CHANGED_FILES=$(git diff --name-only HEAD~3 HEAD 2>/dev/null)
fi

# 方法3: 如果还是为空，检查是否有未提交的修改
if [ -z "$CHANGED_FILES" ]; then
    echo "   ⚠️  未检测到已提交的变更，检查未提交文件..."
    CHANGED_FILES=$(git ls-files --modified 2>/dev/null)
fi

# 方法4: 如果仍然为空，使用默认核心文件
if [ -z "$CHANGED_FILES" ]; then
    echo "   ⚠️  未检测到任何变更，将上传核心文件..."
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
    echo "   📋 准备上传的文件列表:"
    for file in "${BACKEND_FILES[@]}"; do
        if [ -f "$file" ]; then
            DEST_DIR="$TEMP_DIR/$(dirname $file)"
            mkdir -p "$DEST_DIR"
            cp "$file" "$DEST_DIR/"
            echo "      + $file"
        else
            echo "      ⚠️ $file (文件不存在，跳过)"
        fi
    done
    
    # 打包
    cd "$TEMP_DIR"
    echo "   📦 压缩包内容预览:"
    tar -tzf <(tar -czf - .) | head -20
    tar -czf "$BACKEND_TAR" .
    BACKEND_TAR_SIZE=$(du -h "$BACKEND_TAR" | cut -f1)
    echo "   📦 压缩包大小: $BACKEND_TAR_SIZE"
    
    # 上传压缩包
    echo "   🚀 上传压缩包..."
    scp $SSH_OPTS "$BACKEND_TAR" ${REMOTE_USER}@${REMOTE_HOST}:/tmp/backend_update.tar.gz
    
    # 远程解压
    echo "   📂 远程解压..."
    ssh $SSH_OPTS ${REMOTE_USER}@${REMOTE_HOST} << REMOTE_EOF
        cd ${REMOTE_PATH}
        echo "   📋 当前工作目录: \$(pwd)"
        echo "   📋 检查压缩包:"
        ls -lh /tmp/backend_update.tar.gz 2>/dev/null || echo "   ⚠️ 压缩包不存在!"
        
        echo "   📦 开始解压..."
        tar -xzf /tmp/backend_update.tar.gz
        TAR_EXIT=\$?
        
        if [ \$TAR_EXIT -eq 0 ]; then
            EXTRACTED_COUNT=\$(tar -tzf /tmp/backend_update.tar.gz | wc -l)
            rm -f /tmp/backend_update.tar.gz
            echo "   ✅ 解压成功！共 \$EXTRACTED_COUNT 个文件/目录"
            
            echo "   📋 验证关键文件是否已更新:"
            VERIFIED=0
            FAILED=0
            for file in $(echo "${BACKEND_FILES[@]}" | tr ' ' '\n' | head -10); do
                if [ -f "$file" ]; then
                    FILE_TIME=\$(stat -c '%y' "$file" 2>/dev/null || stat -f '%Sm' "$file" 2>/dev/null)
                    echo "      ✓ $file (更新时间: \$FILE_TIME)"
                    VERIFIED=\$((VERIFIED + 1))
                else
                    echo "      ✗ $file (缺失!)"
                    FAILED=\$((FAILED + 1))
                fi
            done
            echo "   📊 验证结果: \$VERIFIED 个成功, \$FAILED 个失败"
        else
            echo "   ❌ 解压失败！退出码: \$TAR_EXIT"
            echo "   📋 尝试查看压缩包内容:"
            tar -tzf /tmp/backend_update.tar.gz 2>&1 | head -20
        fi
REMOTE_EOF
    
    # 清理临时文件
    rm -rf "$TEMP_DIR"
    
    echo "✅ 后端文件上传完成（使用打包方式）"
else
    echo "ℹ️  无后端文件变更"
fi

echo ""

# 上传前端文件（高效方式：直接上传dist目录）
# 策略：始终检查并上传前端dist，确保线上与本地一致
echo " 处理前端文件..."

# 检查前端dist是否存在
if [ ! -d "frontend/dist" ] || [ ! -f "frontend/dist/index.html" ]; then
    echo "⚠️  前端未构建，正在构建..."
    cd /Users/linziwang/PycharmProjects/wordToWord/frontend
    npm run build
    BUILD_RESULT=$?
    cd /Users/linziwang/PycharmProjects/wordToWord
    
    if [ $BUILD_RESULT -ne 0 ]; then
        echo "❌ 前端构建失败"
        exit 1
    fi
    echo "✅ 前端构建成功"
else
    echo "✅ 前端构建产物已存在"
fi

# 总是上传前端dist目录（确保线上与本地一致）
echo "🚀 上传前端构建产物..."

# 使用scp强制全量上传（因为远程服务器没有rsync）
echo "   📡 使用scp上传整个dist目录..."
# 先删除远程旧文件，再上传新文件（确保一致性）
ssh $SSH_OPTS ${REMOTE_USER}@${REMOTE_HOST} "rm -rf ${REMOTE_PATH}/frontend/dist/*"
scp -r $SSH_OPTS /Users/linziwang/PycharmProjects/wordToWord/frontend/dist/* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/frontend/dist/

if [ $? -eq 0 ]; then
    echo "✅ 前端文件上传成功"
    # 验证上传结果
    REMOTE_FILE_COUNT=$(ssh $SSH_OPTS ${REMOTE_USER}@${REMOTE_HOST} "find ${REMOTE_PATH}/frontend/dist -type f | wc -l")
    LOCAL_FILE_COUNT=$(find /Users/linziwang/PycharmProjects/wordToWord/frontend/dist -type f | wc -l)
    echo "   📊 本地文件数: $LOCAL_FILE_COUNT, 远程文件数: $REMOTE_FILE_COUNT"
else
    echo "❌ 前端文件上传失败！"
    exit 1
fi

echo "✅ 前端文件上传完成"

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
    echo "   正在清理旧进程..."
    pkill -f "python app.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm run" 2>/dev/null || true
    
    # 等待端口释放
    sleep 3
    
    # 如果端口仍被占用，强制清理
    if lsof -ti:5004 > /dev/null 2>&1; then
        echo "   端口 5004 仍被占用，强制清理..."
        lsof -ti:5004 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
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
    export PORT=5002
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   后端 PID: $BACKEND_PID"
    
    sleep 3
    
    # 验证前端构建产物
    echo "🚀 验证前端构建产物..."
    if [ ! -f "frontend/dist/index.html" ]; then
        echo "   ⚠️  前端未构建，请在本地执行: cd frontend && npm run build"
    else
        echo "   ✅ 前端构建产物已存在（由 Nginx 提供）"
        
        # 修复 Nginx 访问权限
        echo "   🔧 修复 Nginx 访问权限..."
        chown -R root:root /project/wordToWord
        chmod 755 /project/wordToWord/
        chmod 755 /project/wordToWord/frontend/
        chmod -R 755 frontend/dist/
        chown -R www:www frontend/dist/
    fi
    
    # 确保 Nginx 配置正确（支持公网 IP + 完整的 API 代理）
    echo "   🔧 检查并更新 Nginx 配置..."
    cat > /tmp/nginx_5173.conf << 'NGINX'
server {
    listen 5173;
    server_name 8.146.228.47 localhost opmvue.nokiafz.asia;
    
    root /project/wordToWord/frontend/dist;
    index index.html;
    
    access_log /project/wordToWord/logs/nginx_5173_access.log;
    error_log /project/wordToWord/logs/nginx_5173_error.log;
    
    # 静态资源缓存控制
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires off;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        try_files $uri =404;
    }
    
    # 通用 API 代理（捕获所有 /api/ 开头的请求）
    location /api/ {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 认证 API
    location = /login { proxy_pass http://127.0.0.1:5002; }
    location = /register { proxy_pass http://127.0.0.1:5002; }
    location = /forgot-password { proxy_pass http://127.0.0.1:5002; }
    
    # DingTalk Push API
    location = /dingtalk-push/configs { proxy_pass http://127.0.0.1:5002; }
    location = /dingtalk-push/test-webhook { proxy_pass http://127.0.0.1:5002; }
    location = /dingtalk-push/history { proxy_pass http://127.0.0.1:5002; }
    location = /dingtalk-push/statistics { proxy_pass http://127.0.0.1:5002; }
    location = /dingtalk-push/preview { proxy_pass http://127.0.0.1:5002; }
    location = /dingtalk-push/confirm-checkin { proxy_pass http://127.0.0.1:5002; }
    location = /dingtalk-push/view-checkin { proxy_pass http://127.0.0.1:5002; }
    
    # Kafka Generator API
    location = /kafka-generator/field-meta { proxy_pass http://127.0.0.1:5002; }
    location = /kafka-generator/field-meta/list { proxy_pass http://127.0.0.1:5002; }
    location = /kafka-generator/field-cache { proxy_pass http://127.0.0.1:5002; }
    location = /kafka-generator/field-order { proxy_pass http://127.0.0.1:5002; }
    location = /kafka-generator/field-options { proxy_pass http://127.0.0.1:5002; }
    location = /kafka-generator/generate { proxy_pass http://127.0.0.1:5002; }
    location /kafka-generator/history { proxy_pass http://127.0.0.1:5002; }
    location = /kafka-generator/field-history { proxy_pass http://127.0.0.1:5002; }
    
    # Schedule Config API
    location /schedule-config/api/ {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # FPA Generator API
    location = /fpa-generator/upload { proxy_pass http://127.0.0.1:5002; }
    location /fpa-generator/download/ { proxy_pass http://127.0.0.1:5002; }
    location /fpa-generator/api/ { proxy_pass http://127.0.0.1:5002; }
    
    # FPA Rules API
    location /fpa-rules { proxy_pass http://127.0.0.1:5002; }
    
    # Adjustment API
    location /adjustment { proxy_pass http://127.0.0.1:5002; }
    location /adjustment-calc { proxy_pass http://127.0.0.1:5002; }
    
    # Chatbot API
    location /chatbot/upload_progress/ { proxy_pass http://127.0.0.1:5002; }
    location = /chatbot/chat { proxy_pass http://127.0.0.1:5002; }
    location = /chatbot/upload_document/preview { proxy_pass http://127.0.0.1:5002; }
    location = /chatbot/upload_document/confirm { proxy_pass http://127.0.0.1:5002; }
    location /chatbot/knowledge { proxy_pass http://127.0.0.1:5002; }
    location /chatbot/session { proxy_pass http://127.0.0.1:5002; }
    location = /chatbot/feedback { proxy_pass http://127.0.0.1:5002; }
    
    # Excel2Word API
    location /excel2word { proxy_pass http://127.0.0.1:5002; }
    
    # Word to Excel API
    location /word-to-excel/api { proxy_pass http://127.0.0.1:5002; }
    
    # Markdown Upload API
    location = /markdown-upload/upload { proxy_pass http://127.0.0.1:5002; }
    location = /markdown-upload/convert { proxy_pass http://127.0.0.1:5002; }
    location = /markdown-upload/download { proxy_pass http://127.0.0.1:5002; }
    
    # Spreadsheet API
    location /spreadsheet { proxy_pass http://127.0.0.1:5002; }
    
    # Swagger API
    location /swagger { proxy_pass http://127.0.0.1:5002; }
    
    # SPA 路由 - 所有非文件请求返回 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
NGINX
    
    cp /tmp/nginx_5173.conf /www/server/panel/vhost/nginx/sql-formatter-5173.conf
    nginx -t && nginx -s reload
    echo "   ✅ Nginx 配置已更新"
    
    echo ""
    echo "=========================================="
    echo "  步骤 4: 验证服务状态"
    echo "=========================================="
    
    echo ""
    echo "📊 运行中的进程："
    ps -ef | grep "python app.py" | grep -v grep
    
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
    echo "=========================================="
    echo "  ✅ 部署完成！"
    echo "=========================================="
    echo ""
    echo "📍 访问地址:"
    echo "   后端: http://8.146.228.47:5002"
    echo "   前端: http://8.146.228.47:5173 或 http://localhost:5173"
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
