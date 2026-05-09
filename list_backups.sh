#!/usr/bin/env bash
# 列出远程服务器上的备份文件列表
set -euo pipefail
source "$(dirname "$0")/.env.deploy"

ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "ls -1t ${BACKUP_DIR}/wordToWord_backup_*.tar.gz | head" > /tmp/backup_list.txt
cat /tmp/backup_list.txt
