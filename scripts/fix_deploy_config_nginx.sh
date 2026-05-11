#!/bin/bash
# 修复部署配置页面的 Nginx 代理问题

echo "========================================="
echo "修复 /deploy-config API 路由"
echo "========================================="

# SSH 到服务器
ssh root@8.146.228.47 << 'ENDSSH'

echo "1. 检查当前 Nginx 配置..."
cat /www/server/panel/vhost/nginx/sql-formatter-5173.conf | grep -A 5 "deploy-config" || echo "未找到 deploy-config 配置"

echo ""
echo "2. 备份当前配置..."
cp /www/server/panel/vhost/nginx/sql-formatter-5173.conf /www/server/panel/vhost/nginx/sql-formatter-5173.conf.backup.$(date +%Y%m%d_%H%M%S)

echo ""
echo "3. 添加 deploy-config location 配置..."

# 检查是否已有配置
if grep -q "location /deploy-config" /www/server/panel/vhost/nginx/sql-formatter-5173.conf; then
    echo "配置已存在，跳过添加"
else
    # 在最后一个 location 块之前插入新的 location
    sed -i '/location \/ {/i\
    # Deploy Config API\
    location /deploy-config {\
        proxy_pass http://127.0.0.1:5004;\
        proxy_set_header Host $host;\
        proxy_set_header X-Real-IP $remote_addr;\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\
        proxy_set_header X-Forwarded-Proto $scheme;\
        proxy_http_version 1.1;\
        proxy_set_header Upgrade $http_upgrade;\
        proxy_set_header Connection "upgrade";\
        proxy_read_timeout 86400s;\
        proxy_send_timeout 86400s;\
    }\
' /www/server/panel/vhost/nginx/sql-formatter-5173.conf
    echo "✅ 已添加 /deploy-config location 配置"
fi

echo ""
echo "4. 测试 Nginx 配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置测试通过"
    echo ""
    echo "5. 重载 Nginx..."
    nginx -s reload
    echo "✅ Nginx 已重载"
else
    echo "❌ Nginx 配置测试失败，恢复备份..."
    cp /www/server/panel/vhost/nginx/sql-formatter-5173.conf.backup.* /www/server/panel/vhost/nginx/sql-formatter-5173.conf
    exit 1
fi

echo ""
echo "6. 验证后端服务状态..."
ps aux | grep "python app.py" | grep -v grep
lsof -i:5004 | head -3

echo ""
echo "7. 测试 API 接口..."
curl -s http://localhost:5004/deploy-config/status | head -c 200
echo ""

echo ""
echo "========================================="
echo "修复完成！"
echo "请在浏览器中刷新页面测试"
echo "========================================="

ENDSSH
