#!/bin/bash
# Claude Code 统一启动脚本
# 支持两种模式：
# 1. 使用 LM Studio Bridge（默认）
# 2. 直接使用本地配置

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "  Claude Code 启动器"
echo "=========================================="
echo ""

# 检查参数
MODE=${1:-"direct"}

case $MODE in
  "bridge"|"lmstudio")
    echo "🚀 模式: LM Studio Bridge"
    echo ""
    
    # 启动代理服务
    cd "$SCRIPT_DIR"
    python3 claude_code.py &
    BRIDGE_PID=$!
    
    echo "✅ LM Studio Bridge 已启动 (PID: $BRIDGE_PID)"
    echo ""
    echo "📋 启动 Claude Code："
    echo ""
    echo "   export ANTHROPIC_BASE_URL=http://localhost:8081/v1"
    echo "   export ANTHROPIC_API_KEY=sk-lm-studio"
    echo "   npx @anthropic-ai/claude-code --dangerously-skip-permissions --bare"
    echo ""
    echo "或一行命令："
    echo "   ANTHROPIC_BASE_URL=http://localhost:8081/v1 ANTHROPIC_API_KEY=sk-lm-studio npx @anthropic-ai/claude-code --dangerously-skip-permissions --bare"
    echo ""
    echo "按 Ctrl+C 停止代理服务"
    
    # 等待中断信号
    trap "kill $BRIDGE_PID 2>/dev/null; exit" INT TERM
    wait $BRIDGE_PID
    ;;
    
  "memory")
    echo "🧠 模式: Claude Code with Local Memory System"
    echo ""

    # 加载项目配置
    cd "$PROJECT_ROOT"
    if [ -f .env.claude ]; then
      echo "✅ 加载配置文件: .env.claude"
      set -a
      source .env.claude
      set +a
    else
      echo "⚠️  未找到 .env.claude 文件"
      echo "   将使用默认配置"
    fi

    echo ""
    echo "📋 当前配置："
    echo "   ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL:-未设置}"
    echo "   ANTHROPIC_MODEL: ${ANTHROPIC_MODEL:-未设置}"
    echo ""

    # 启动记忆系统
    cd "$SCRIPT_DIR"
    python3 claude_code.py --demo
    ;;

  "memory-demo")
    echo "🧠 模式: Claude Code with Local Memory System (Demo)"
    echo ""

    # 加载项目配置
    cd "$PROJECT_ROOT"
    if [ -f .env.claude ]; then
      echo "✅ 加载配置文件: .env.claude"
      set -a
      source .env.claude
      set +a
    else
      echo "⚠️  未找到 .env.claude 文件"
      echo "   将使用默认配置"
    fi

    echo ""
    echo "📋 当前配置："
    echo "   ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL:-未设置}"
    echo "   ANTHROPIC_MODEL: ${ANTHROPIC_MODEL:-未设置}"
    echo ""

    # 启动记忆系统（非交互模式，仅演示）
    cd "$SCRIPT_DIR"
    python3 claude_code.py --demo 2>&1 | head -50
    ;;

  "direct"|*)
    echo "🚀 模式: 直接启动（使用项目配置）"
    echo ""

    # 加载项目配置
    cd "$PROJECT_ROOT"
    if [ -f .env.claude ]; then
      echo "✅ 加载配置文件: .env.claude"
      set -a
      source .env.claude
      set +a
    else
      echo "⚠️  未找到 .env.claude 文件"
      echo "   将使用默认配置"
    fi

    echo ""
    echo "📋 当前配置："
    echo "   ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL:-未设置}"
    echo "   ANTHROPIC_MODEL: ${ANTHROPIC_MODEL:-未设置}"
    echo ""
    echo "🚀 启动 Claude Code..."
    echo ""

    # 启动 Claude Code（带跳过权限和裸模式参数）
    npx @anthropic-ai/claude-code --dangerously-skip-permissions --bare "$@"
    ;;
esac
