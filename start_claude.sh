#!/bin/bash
# 启动 Claude Code 的快捷脚本
# 使用方式: ./start_claude.sh 或 source ./start_claude.sh

export ANTHROPIC_BASE_URL=http://localhost:8081/v1
claude --dangerously-skip-permissions --bare