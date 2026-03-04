#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import os
import sys
from typing import Dict, Any, List, Optional

# 确保可以从项目根目录导入 utils 包
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.mysql_helper import get_mysql_conn_dict_cursor


def normalize_kafka_field(push_field: str) -> str:
    # CSV里是 network_type_top 这种；前端用的是 NETWORK_TYPE_TOP
    return (push_field or "").strip().upper()


def read_csv_rows(csv_path: str) -> List[Dict[str, Any]]:
    encodings = ["utf-8-sig", "utf-8", "gbk"]
    last_err: Optional[Exception] = None
    for enc in encodings:
        try:
            with open(csv_path, "r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"读取CSV失败（已尝试 {encodings} ）: {last_err}")


def upsert_rows(rows: List[Dict[str, Any]]) -> int:
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        raise RuntimeError("无法连接MySQL，请先设置 MYSQL_HOST/MYSQL_USER/MYSQL_PWD/MYSQL_DB 等环境变量")

    sql = """
    INSERT INTO kafka_field_meta (kafka_field, es_field, db_cn, label_cn, is_enabled)
    VALUES (%s, %s, %s, %s, 1)
    ON DUPLICATE KEY UPDATE
      es_field = VALUES(es_field),
      db_cn = VALUES(db_cn),
      label_cn = VALUES(label_cn),
      is_enabled = 1
    """

    inserted = 0
    try:
        with conn.cursor() as cur:
            for r in rows:
                kafka_field = normalize_kafka_field(r.get("推送告警消息字段", ""))
                if not kafka_field:
                    continue

                es_field = (r.get("对应ES字段", "") or "").strip() or None
                db_cn = (r.get("匹配数据库", "") or "").strip() or None
                label_cn = (r.get("字段中文解释", "") or "").strip() or None

                cur.execute(sql, (kafka_field, es_field, db_cn, label_cn))
                inserted += 1
        conn.commit()
        return inserted
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="导入 Kafka 字段元数据到 MySQL(kafka_field_meta)")
    parser.add_argument("--csv", help="CSV 文件路径 (例如：sql/事件关联 - 分级调度接口协议.csv)")
    parser.add_argument("--batch", action="store_true", help="批量导入模式：自动查找 sql 目录下的事件关联文件")
    args = parser.parse_args()

    # 如果没有提供 CSV 参数，尝试自动查找
    if not args.csv:
        sql_dir = os.path.join(PROJECT_ROOT, "sql")
        if os.path.exists(sql_dir):
            # 查找包含"事件关联"或"分级调度"的 CSV 文件
            target_files = [
                f for f in os.listdir(sql_dir)
                if f.endswith('.csv') and ('事件关联' in f or '分级调度' in f)
            ]
            if target_files:
                args.csv = os.path.join(sql_dir, target_files[0])
                print(f"自动检测到文件：{args.csv}")
            else:
                print("错误：未指定 CSV 文件，且未在 sql 目录中找到事件关联相关文件")
                print("\n使用方法:")
                print("  python scripts/import_kafka_field_meta.py --csv \"sql/事件关联 - 分级调度接口协议.csv\"")
                parser.print_help()
                sys.exit(1)
        else:
            print("错误：未指定 CSV 文件，且 sql 目录不存在")
            print("\n使用方法:")
            print("  python scripts/import_kafka_field_meta.py --csv \"sql/事件关联 - 分级调度接口协议.csv\"")
            parser.print_help()
            sys.exit(1)

    csv_path = os.path.abspath(args.csv)
    if not os.path.exists(csv_path):
        raise SystemExit(f"CSV 文件不存在：{csv_path}")

    rows = read_csv_rows(csv_path)
    count = upsert_rows(rows)
    print(f"导入完成：{count} 条 (包含 upsert)")


if __name__ == "__main__":
    '''
    命令行运行：python3 scripts/import_kafka_field_meta.py --csv "sql/事件关联-分级调度接口协议.csv"
    import_kafka_field_meta --csv
    '''
    main()

