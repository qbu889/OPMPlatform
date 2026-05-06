#!/bin/bash
# deploy.sh - 快速部署脚本
# 用法: ./deploy.sh

echo "=========================================="
echo "  快速部署到远程服务器"
echo "=========================================="
echo ""

# 配置
REMOTE_USER="root"
REMOTE_HOST="8.146.228.47"
REMOTE_PATH="/project/wordToWord"

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

# SCP 上传关键文件到远程服务器
echo "📦 上传文件到远程服务器..."

# 上传后端核心文件
scp routes/kafka/kafka_generator_routes.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/routes/kafka/
scp app.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/
scp config.py ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/
scp requirements.txt ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

# 上传前端文件（如果有修改）
if [ -d "frontend/dist" ]; then
    echo "📦 上传前端构建文件..."
    scp -r frontend/dist/* ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/frontend/dist/
fi

echo "✅ 文件上传完成"
echo ""

# SSH 执行远程重启
echo "🔄 重启远程服务..."
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
    cd /project/wordToWord
    
    echo "1️⃣ 停止现有进程..."
    pkill -f "python app.py" || true
    pkill -f "vite" || true
    pkill -f "npm run" || true
    sleep 2
    
    echo "2️⃣ 清理进程..."
    ps -ef | grep -E "python|vite|node" | grep wordToWord | grep -v grep || echo "   所有进程已停止"
    
    echo "3️⃣ 激活虚拟环境..."
    source .venv/bin/activate
    
    echo "4️⃣ 启动后端服务..."
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   后端 PID: $BACKEND_PID"
    
    echo "5️⃣ 等待后端启动..."
    sleep 3
    
    echo "6️⃣ 验证前端构建产物..."
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
    
    echo ""
    echo "7️⃣ 检查并更新 Nginx 配置..."
    NGINX_CONF="/www/server/panel/vhost/nginx/sql-formatter-5173.conf"
    if [ -f "$NGINX_CONF" ]; then
        # 检查是否包含关键的 API 代理规则
        if ! grep -q "schedule-config/api" "$NGINX_CONF" || \
           ! grep -q "fpa-generator" "$NGINX_CONF" || \
           ! grep -q "chatbot/upload_progress" "$NGINX_CONF"; then
            echo "   ⚠️  Nginx 配置不完整，正在更新..."
            
            cat > /tmp/nginx_5173_update.conf << 'NGINX'
server {
    listen 5173;
    server_name 8.146.228.47 localhost opmvue.nokiafz.asia;
    
    root /project/wordToWord/frontend/dist;
    index index.html;
    
    access_log /project/wordToWord/logs/nginx_5173_access.log;
    error_log /project/wordToWord/logs/nginx_5173_error.log;
    
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires 0;
        try_files $uri =404;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location = /login { proxy_pass http://127.0.0.1:5004; }
    location = /register { proxy_pass http://127.0.0.1:5004; }
    location = /forgot-password { proxy_pass http://127.0.0.1:5004; }
    
    location = /dingtalk-push/configs { proxy_pass http://127.0.0.1:5004; }
    location = /dingtalk-push/test-webhook { proxy_pass http://127.0.0.1:5004; }
    location = /dingtalk-push/history { proxy_pass http://127.0.0.1:5004; }
    location = /dingtalk-push/statistics { proxy_pass http://127.0.0.1:5004; }
    location = /dingtalk-push/preview { proxy_pass http://127.0.0.1:5004; }
    location = /dingtalk-push/confirm-checkin { proxy_pass http://127.0.0.1:5004; }
    location = /dingtalk-push/view-checkin { proxy_pass http://127.0.0.1:5004; }
    
    location = /kafka-generator/field-meta { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/field-meta/list { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/field-cache { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/field-order { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/field-options { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/generate { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/history { proxy_pass http://127.0.0.1:5004; }
    location = /kafka-generator/field-history { proxy_pass http://127.0.0.1:5004; }
    
    location /schedule-config/api/ {
        proxy_pass http://127.0.0.1:5004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location = /fpa-generator/upload { proxy_pass http://127.0.0.1:5004; }
    location /fpa-generator/download/ { proxy_pass http://127.0.0.1:5004; }
    location /fpa-generator/api/ { proxy_pass http://127.0.0.1:5004; }
    
    location /fpa-rules { proxy_pass http://127.0.0.1:5004; }
    
    location /adjustment { proxy_pass http://127.0.0.1:5004; }
    location /adjustment-calc { proxy_pass http://127.0.0.1:5004; }
    
    location /chatbot/upload_progress/ { proxy_pass http://127.0.0.1:5004; }
    location = /chatbot/chat { proxy_pass http://127.0.0.1:5004; }
    location = /chatbot/upload_document/preview { proxy_pass http://127.0.0.1:5004; }
    location = /chatbot/upload_document/confirm { proxy_pass http://127.0.0.1:5004; }
    location /chatbot/knowledge { proxy_pass http://127.0.0.1:5004; }
    location /chatbot/session { proxy_pass http://127.0.0.1:5004; }
    location = /chatbot/feedback { proxy_pass http://127.0.0.1:5004; }
    
    location /excel2word { proxy_pass http://127.0.0.1:5004; }
    
    location /word-to-excel/api { proxy_pass http://127.0.0.1:5004; }
    
    location = /markdown-upload/upload { proxy_pass http://127.0.0.1:5004; }
    location = /markdown-upload/convert { proxy_pass http://127.0.0.1:5004; }
    location = /markdown-upload/download { proxy_pass http://127.0.0.1:5004; }
    
    location /spreadsheet { proxy_pass http://127.0.0.1:5004; }
    
    location /swagger { proxy_pass http://127.0.0.1:5004; }
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location ~ /\. {
        deny all;
    }
}
NGINX
            
            cp /tmp/nginx_5173_update.conf "$NGINX_CONF"
            nginx -t && nginx -s reload
            echo "   ✅ Nginx 配置已更新并重新加载"
        else
            echo "   ✅ Nginx 配置正常"
        fi
    else
        echo "   ⚠️  未找到 Nginx 配置文件: $NGINX_CONF"
    fi
    
    echo ""
    echo "8️⃣ 检查服务状态..."
    ps -ef | grep "python app.py" | grep -v grep
    
    echo ""
    echo "9️⃣ 查看后端日志（最后20行）..."
    tail -20 logs/backend.log
    
    echo ""
    echo "✅ 部署完成！"
    echo "   后端: http://8.146.228.47:5004"
    echo "   前端: http://8.146.228.47:5173"
EOF

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  后端: http://8.146.228.47:5004"
echo "  前端: http://8.146.228.47:5173"
echo ""
echo "查看日志:"
echo "  ssh root@8.146.228.47 'tail -f /project/wordToWord/logs/backend.log'"
echo "=========================================="
