#!/bin/bash
# start_all_prod.sh - 一键启动生产环境（后端 + 前端）
#
# 用法:
#   ./start_all_prod.sh          # 启动生产环境
#   ./start_all_prod.sh --help   # 显示帮助信息

# 显示帮助信息
show_help() {
    echo "=========================================="
    echo "  诺基亚 OPM 综合业务系统 - 生产环境启动"
    echo "=========================================="
    echo ""
    echo "用法:"
    echo "  ./start_all_prod.sh          # 启动生产环境（后端5004 + 前端5173）"
    echo "  ./start_all_prod.sh --help   # 显示此帮助信息"
    echo ""
    echo "服务说明:"
    echo "  - 后端服务: http://localhost:5004"
    echo "  - 前端服务: http://localhost:5173"
    echo "  - Cloudflare Tunnel: 自动启动"
    echo ""
    echo "停止服务:"
    echo "  按 Ctrl+C 停止所有服务"
    echo "=========================================="
    exit 0
}

# 检查帮助参数
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    show_help
fi

echo "=========================================="
echo "  启动诺基亚 OPM 综合业务系统（生产环境）"
echo "=========================================="
echo ""

# 进入项目目录
cd "$(dirname "$0")"

# 获取本机局域网 IP 地址
get_local_ip() {
    # macOS 使用 ifconfig 获取 en0（通常是 WiFi）或 en1 的 IP
    if command -v ifconfig &> /dev/null; then
        local ip=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)
        if [ -n "$ip" ]; then
            echo "$ip"
            return
        fi
    fi
    
    # Linux 使用 ip 命令
    if command -v ip &> /dev/null; then
        local ip=$(ip route get 1 | awk '{print $7; exit}')
        if [ -n "$ip" ]; then
            echo "$ip"
            return
        fi
    fi
    
    echo "localhost"
}

LOCAL_IP=$(get_local_ip)

echo " 本机局域网 IP: $LOCAL_IP"
echo ""

# ============================================================================
# 1. 启动后端服务
# ============================================================================
echo "📌 步骤 1/2: 启动后端服务..."
echo ""

# 激活虚拟环境
if [ -d ".venv" ]; then
    echo "✅ 激活虚拟环境..."
    source .venv/bin/activate
else
    echo "⚠️  未找到 .venv 虚拟环境，将使用系统 Python"
fi

# 检查端口是否被占用
BACKEND_PORT=${PORT:-5004}
echo "🔍 检查后端端口 $BACKEND_PORT..."
lsof -ti:$BACKEND_PORT > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "⚠️  端口 $BACKEND_PORT 被占用，正在释放..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

echo "🚀 启动 Flask 后端应用（端口：$BACKEND_PORT）..."
echo ""

# 在后台启动后端服务（绑定 0.0.0.0 以支持局域网访问）
PORT=$BACKEND_PORT python app.py --host 0.0.0.0 &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 检查后端是否成功启动
if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
    echo "✅ 后端服务启动成功（PID: $BACKEND_PID）"
    echo "   本机访问: http://localhost:$BACKEND_PORT"
    echo "   局域网访问: http://$LOCAL_IP:$BACKEND_PORT"
else
    echo "❌ 后端服务启动失败！"
    echo "   请检查日志或手动运行: PORT=$BACKEND_PORT python app.py"
    exit 1
fi

echo ""
echo "=========================================="
echo ""

# ============================================================================
# 2. 验证前端构建产物
# ============================================================================
echo "📌 步骤 2/2: 验证前端构建产物..."
echo ""

# 检查前端构建产物是否存在
if [ ! -d "frontend/dist" ] || [ ! -f "frontend/dist/index.html" ]; then
    echo "⚠️  前端未构建，正在构建..."
    cd frontend || {
        echo "❌ 错误: 找不到 frontend 目录"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    }
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo "📦 首次运行，正在安装依赖..."
        npm install
        echo ""
    fi
    
    # 设置环境变量
    export NODE_ENV=production
    export BACKEND_PORT=$BACKEND_PORT
    
    # 构建生产版本
    echo "🔨 正在构建前端生产版本..."
    npm run build
    
    if [ $? -ne 0 ]; then
        echo "❌ 前端构建失败"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    echo "✅ 前端构建完成"
    cd ..
else
    echo "✅ 前端构建产物已存在"
fi

echo ""
echo "=========================================="
echo "  ✅ 所有服务已启动成功！"
echo "=========================================="
echo ""
echo "  🌐 前端服务 (由 Nginx 提供):"
echo "     - 本机访问: http://localhost:5173"
echo "     - 局域网访问: http://$LOCAL_IP:5173"
echo ""
echo "  🔧 后端服务:"
echo "     - 本机访问: http://localhost:$BACKEND_PORT"
echo "     - 局域网访问: http://$LOCAL_IP:$BACKEND_PORT"
echo ""

# 检查并修复 Nginx 配置
echo "  🔍 检查 Nginx 配置..."
NGINX_CONF="/www/server/panel/vhost/nginx/sql-formatter-5173.conf"
if [ -f "$NGINX_CONF" ]; then
    # 检查是否包含关键的 API 代理规则
    if ! grep -q "schedule-config/api" "$NGINX_CONF" || \
       ! grep -q "fpa-generator" "$NGINX_CONF" || \
       ! grep -q "chatbot/upload_progress" "$NGINX_CONF"; then
        echo "  ⚠️  Nginx 配置不完整，正在更新..."
        
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
        echo "  ✅ Nginx 配置已更新并重新加载"
    else
        echo "  ✅ Nginx 配置正常"
    fi
else
    echo "  ⚠️  未找到 Nginx 配置文件: $NGINX_CONF"
fi

echo ""
echo "  ⚠️  注意: 前端由 Nginx 提供静态文件服务"
echo "  📝 如需重启 Nginx: sudo nginx -s reload"
echo ""
echo "  按 Ctrl+C 停止后端服务"
echo "=========================================="
echo ""

# 等待后端进程
wait $BACKEND_PID
