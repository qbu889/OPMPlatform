#!/bin/bash
# Claude Code 完整启动脚本
# 自动启动 LM Studio Bridge + Claude Code

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRIDGE_SCRIPT="$SCRIPT_DIR/utils/claude code/claude_code.py"

echo "=========================================="
echo "  Claude Code 完整启动"
echo "=========================================="
echo ""

# 检查 Bridge 脚本是否存在
if [ ! -f "$BRIDGE_SCRIPT" ]; then
    echo "❌ 错误: 找不到 Bridge 脚本: $BRIDGE_SCRIPT"
    exit 1
fi

# 启动 LM Studio Bridge（后台）
echo "🚀 步骤 1: 启动 LM Studio Bridge..."
cd "$SCRIPT_DIR/utils/claude code"
python3 claude_code.py > /tmp/claude_bridge.log 2>&1 &
BRIDGE_PID=$!
echo "✅ Bridge 已启动 (PID: $BRIDGE_PID, 日志: /tmp/claude_bridge.log)"

# 等待 Bridge 就绪
echo "⏳ 等待 Bridge 服务就绪..."
sleep 2

# 检查 Bridge 是否正常运行
if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ Bridge 服务正常"
else
    echo "⚠️  Bridge 可能未完全就绪，继续启动 Claude Code..."
fi

echo ""
echo "🚀 步骤 2: 启动 Claude Code..."
echo ""

# 加载项目配置
cd "$SCRIPT_DIR"
if [ -f .env.claude ]; then
    set -a
    source .env.claude
    set +a
fi

# 设置 Bridge 环境变量
export ANTHROPIC_BASE_URL=http://localhost:8081/v1
export ANTHROPIC_API_KEY=sk-lm-studio

# 启动 Claude Code（带清理逻辑）
trap "kill $BRIDGE_PID 2>/dev/null; echo ''; echo '✅ Bridge 服务已停止'; exit" INT TERM EXIT

npx @anthropic-ai/claude-code --dangerously-skip-permissions --bare "$@"

# Claude Code 退出后清理 Bridge
kill $BRIDGE_PID 2>/dev/null
