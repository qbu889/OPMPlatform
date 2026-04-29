#!/bin/bash
# 远程服务器重启服务脚本

echo "正在连接到远程服务器..."

ssh root@8.146.228.47 << 'EOF'
    echo "=== 进入项目目录 ==="
    cd /project/wordToWord
    
    echo "=== 停止现有进程 ==="
    pkill -f "python app.py" || echo "后端进程未运行"
    pkill -f "vite" || echo "前端进程未运行"
    sleep 2
    
    echo "=== 检查进程是否已停止 ==="
    ps -ef | grep -E "python|vite" | grep wordToWord || echo "所有进程已停止"
    
    echo "=== 重新启动服务 ==="
    ./start_all_prod.sh
    
    echo "=== 等待5秒后检查服务状态 ==="
    sleep 5
    
    echo "=== 检查服务状态 ==="
    ps -ef | grep -E "python|vite" | grep wordToWord
    
    echo "=== 查看后端日志（最后20行）==="
    tail -20 logs/backend.log
    
    echo "=== 查看前端日志（最后20行）==="
    tail -20 logs/frontend.log
    
    echo "=== 服务重启完成 ==="
EOF

echo "远程命令执行完毕"
