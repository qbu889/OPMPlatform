#!/bin/bash
# 启动 LM Studio Bridge 并配置 Claude Code 使用代理

echo "🚀 正在启动 LM Studio Bridge..."

# 启动代理服务（后台运行）
python3 claude_code.py &
BRIDGE_PID=$!

echo "✅ LM Studio Bridge 已启动 (PID: $BRIDGE_PID)"
echo ""
echo "📋 现在可以启动 Claude Code："
echo ""
echo "   方式 1 - 临时设置环境变量："
echo "   export ANTHROPIC_BASE_URL=http://localhost:8081/v1"
echo "   export ANTHROPIC_API_KEY=sk-lm-studio"
echo "   claude"
echo ""
echo "   方式 2 - 在一行中执行："
echo "   ANTHROPIC_BASE_URL=http://localhost:8081/v1 ANTHROPIC_API_KEY=sk-lm-studio claude"
echo ""
echo "按 Ctrl+C 停止代理服务"

# 等待中断信号
trap "kill $BRIDGE_PID 2>/dev/null; exit" INT TERM
wait $BRIDGE_PID
