#!/usr/bin/env bash
# 删除远程服务器上的指定备份文件
set -euo pipefail
source "$(dirname "$0")/.env.deploy"

if [ $# -eq 0 ]; then
    echo "用法: $0 <备份文件名>" >&2
    echo "示例: $0 wordToWord_backup_20260507_154600.tar.gz" >&2
    exit 1
fi
FILENAME="$1"

ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "rm -f ${BACKUP_DIR}/${FILENAME}"
if [ $? -eq 0 ]; then
    echo "✅ 删除成功: ${FILENAME}"
else
    echo "❌ 删除失败: ${FILENAME}"
fi
