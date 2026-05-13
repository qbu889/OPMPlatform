#!/bin/bash
# check_duplicate_processes.sh - 检查是否有重复的Python进程
# 用于排查钉钉消息重复发送问题

echo "=========================================="
echo "  检查 wordToWord Python 进程"
echo "=========================================="
echo ""

# 查找所有 python app.py 进程
PROCESSES=$(ps aux | grep 'python app.py' | grep -v grep)
COUNT=$(echo "$PROCESSES" | grep -c 'python app.py' 2>/dev/null || echo 0)

if [ "$COUNT" -eq 0 ]; then
    echo "❌ 没有找到运行中的 Python 进程"
    exit 1
elif [ "$COUNT" -eq 1 ]; then
    echo "✅ 找到 1 个 Python 进程（正常）"
    echo ""
    echo "进程信息："
    echo "$PROCESSES"
else
    echo "⚠️  警告：找到 $COUNT 个 Python 进程（可能存在重复）"
    echo ""
    echo "进程列表："
    echo "$PROCESSES"
    echo ""
    echo "监听端口的进程："
    netstat -tlnp 2>/dev/null | grep python || ss -tlnp | grep python
    echo ""
    echo "💡 建议操作："
    echo "   1. 确认哪个进程是主进程（监听5004端口）"
    echo "   2. 清理其他僵尸进程: kill -9 <PID>"
    echo "   3. 或使用部署脚本重新部署: ./deploy.sh"
fi

echo ""
echo "=========================================="
