import os
import logging
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


def get_mysql_config_from_env() -> Dict[str, Any]:
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PWD", "12345678"),
        "database": os.getenv("MYSQL_DB", "schedule"),
        "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
        "cursorclass": None,  # 由调用方决定是否需要 DictCursor
    }


def get_mysql_conn_dict_cursor():
    """获取 MySQL 连接（DictCursor）。

    失败时返回 None（不会 sys.exit），便于 Web 服务优雅降级。
    """
    try:
        import pymysql
        from pymysql.cursors import DictCursor

        cfg = get_mysql_config_from_env()
        cfg["cursorclass"] = DictCursor
        conn = pymysql.connect(**cfg)
        return conn
    except Exception as e:
        logger.warning(f"MySQL连接不可用，将回退到内置配置: {e}")
        return None

