#!/bin/bash
# Claude Code Skills 安装脚本

echo "=========================================="
echo "  安装 Claude Code Skills"
echo "=========================================="
echo ""

# Change to the correct directory
cd /Users/linziwang/PycharmProjects/OPMPlatform

SKILLS=(
  "superpowers"
  "gsd"
  "find-skills"
  "web-design-guidelines"
  "frontend-design"
  "agent-browser"
)

for skill in "${SKILLS[@]}"; do
  echo "📦 安装 skill: $skill"
  npx @anthropic-ai/claude-code --dangerously-skip-permissions --bare -p "/skills install $skill"
  echo ""
done

echo "✅ 所有 skills 安装完成！"
