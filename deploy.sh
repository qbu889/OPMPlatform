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
    
    echo "6️⃣ 启动前端预览服务..."
    cd frontend
    nohup npx vite preview --port 5173 --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   前端 PID: $FRONTEND_PID"
    
    cd ..
    
    echo "7️⃣ 等待服务完全启动..."
    sleep 3
    
    echo ""
    echo "8️⃣ 检查服务状态..."
    ps -ef | grep -E "python app.py|vite preview" | grep -v grep
    
    echo ""
    echo "9️⃣ 查看后端日志（最后20行）..."
    tail -20 logs/backend.log
    
    echo ""
    echo "🔟 查看前端日志（最后20行）..."
    tail -20 logs/frontend.log
    
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
echo "  ssh root@8.146.228.47 'tail -f /project/wordToWord/logs/frontend.log'"
echo "=========================================="
