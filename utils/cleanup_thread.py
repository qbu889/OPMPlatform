# utils/cleanup_thread.py
from typing import Tuple  # 关键：导入大写的 Tuple（3.9 以下专用）

import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from threading import Thread
from flask import current_app
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 清理配置（默认值，可以通过线程参数覆盖）
RETENTION_HOURS = 1          # 默认保留 1 小时
INTERVAL_SECONDS = 1800      # 默认清理间隔 30 分钟
TIMESTAMP_PATTERN = re.compile(r".+_(\d{13})\..+")

class CleanupThread(Thread):
    def __init__(self, app, cleanup_interval=1800, retention_hours=1):
        super().__init__()
        self.app = app
        self.cleanup_interval = cleanup_interval
        self.retention_hours = retention_hours

    def run(self):
        # 将 Flask 应用实例和配置传递给清理循环
        run_cleanup_loop(self.app, self.cleanup_interval, self.retention_hours)




def is_timestamp_file(path: Path) -> bool:
    """判断文件是否是带时间戳的临时文件"""
    return TIMESTAMP_PATTERN.match(path.name) is not None


# 在 utils/cleanup_thread.py 中修改类型注解
def cleanup_dir(directory: str, cutoff: str) -> Tuple[int, int]:  # 小写tuple → 大写Tuple
    """清理指定目录下过期的文件"""
    # 转换为Path对象
    directory_path = Path(directory)
    if isinstance(cutoff, datetime):
        cutoff_datetime = cutoff
    else:
        cutoff_datetime = datetime.fromisoformat(cutoff)

    deleted_count = 0
    freed_bytes = 0
    if not directory_path.exists():
        return deleted_count, freed_bytes

    for file_path in directory_path.iterdir():
        if not file_path.is_file() or not is_timestamp_file(file_path):
            continue
        try:
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
            if last_modified < cutoff_datetime:
                size = file_path.stat().st_size
                file_path.unlink()
                deleted_count += 1
                freed_bytes += size
        except Exception as e:
            print(f"清理文件失败 {file_path}: {e}")
    return deleted_count, freed_bytes

# 需要修改 utils/cleanup_thread.py 中的函数定义
def run_cleanup_loop(app, cleanup_interval: int = INTERVAL_SECONDS, retention_hours: int = RETENTION_HOURS):
    """后台清理循环

    :param app: Flask 应用实例
    :param cleanup_interval: 清理间隔秒数
    :param retention_hours: 文件保留小时数
    """
    print(f"[CLEANUP_THREAD] Started | Retention: {retention_hours}h | Interval: {cleanup_interval}s")
    while True:
        now = datetime.now()
        cutoff = now - timedelta(hours=retention_hours)

        # 使用应用上下文访问配置
        with app.app_context():
            upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
            excel_input_dir = upload_dir / "excel_input"
            word_output_dir = upload_dir / "word_output"

            in_del, _ = cleanup_dir(excel_input_dir, cutoff)
            out_del, _ = cleanup_dir(word_output_dir, cutoff)

            if in_del + out_del > 0:
                logger.info(f"[CLEANUP_DONE] Excel: {in_del} files | Word: {out_del} files")
        time.sleep(cleanup_interval)
