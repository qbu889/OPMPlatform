#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用维表导入脚本

用途：
- 从 csv/Excel 导出的维表（如 business_layer.csv、circuit_level.csv 等）
- 自动在 MySQL 中创建同名表（或指定表名），并导入所有数据

注意：
- 默认所有列类型使用 VARCHAR(255)
- CSV 第一行作为表头，列名会按原样作为字段名（用反引号包裹）
"""

import argparse
import csv
import os
import sys
from typing import List, Tuple

# 确保可以导入 utils.mysql_helper
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.mysql_helper import get_mysql_conn_dict_cursor


def detect_encoding(path: str) -> str:
    for enc in ("utf-8-sig", "utf-8", "gbk"):
        try:
            with open(path, "r", encoding=enc) as f:
                f.read(2048)
            return enc
        except Exception:
            continue
    return "utf-8"


def load_csv(path: str) -> Tuple[List[str], List[List[str]]]:
    enc = detect_encoding(path)
    with open(path, "r", encoding=enc, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise RuntimeError(f"CSV 为空: {path}")
    headers = rows[0]
    # 去掉首列可能存在的 BOM
    if headers:
        headers[0] = headers[0].lstrip("\ufeff")
    data_rows = rows[1:]
    return headers, data_rows


def create_table(conn, table: str, headers: List[str]) -> None:
    # 使用 CSV 头作为字段名，字段类型统一为 VARCHAR(255)
    # 特殊情况：如果列名为 'TXT' 或 '备注',使用 TEXT 类型以支持更长的内容
    cols_sql = []
    for h in headers:
        col = h.strip()
        if not col:
            continue
        col_escaped = col.replace("`", "``")
        # 对于 TXT 和备注列，使用 TEXT 类型
        if col.upper() == "TXT" or col == "备注":
            cols_sql.append(f"`{col_escaped}` TEXT NULL")
        else:
            cols_sql.append(f"`{col_escaped}` VARCHAR(255) NULL")
    if not cols_sql:
        raise RuntimeError("CSV 表头为空，无法创建表")

    table_escaped = table.replace("`", "``")
    create_sql = f"""
    DROP TABLE IF EXISTS `{table_escaped}`;
    CREATE TABLE `{table_escaped}` (
      {", ".join(cols_sql)}
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """

    with conn.cursor() as cur:
        for stmt in create_sql.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                cur.execute(stmt)
    conn.commit()


def insert_rows(conn, table: str, headers: List[str], rows: List[List[str]]) -> int:
    table_escaped = table.replace("`", "``")
    # 过滤掉空表头列
    valid_indices = [i for i, h in enumerate(headers) if h.strip()]
    cols = [headers[i].strip().replace("`", "``") for i in valid_indices]
    cols_fragment = ", ".join(f"`{c}`" for c in cols)
    placeholders = ", ".join(["%s"] * len(cols))
    sql = f"INSERT INTO `{table_escaped}` ({cols_fragment}) VALUES ({placeholders})"

    values = []
    for row in rows:
        if not any(cell.strip() for cell in row):
            continue
        vals = []
        for idx in valid_indices:
            vals.append(row[idx] if idx < len(row) else None)
        values.append(tuple(vals))

    inserted = 0
    if values:
        with conn.cursor() as cur:
            cur.executemany(sql, values)
        conn.commit()
        inserted = len(values)
    return inserted


def main():
    parser = argparse.ArgumentParser(description="导入 Kafka 相关维表 CSV 到 MySQL")
    parser.add_argument("--csv", help="CSV 文件路径，例如 sql/business_layer.csv（批量导入时不需要此参数）")
    parser.add_argument(
        "--table",
        help="目标表名（默认：使用文件名去掉扩展名，如 business_layer）",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="批量导入模式：自动导入 sql/目录下所有 CSV 文件"
    )
    args = parser.parse_args()

    conn = get_mysql_conn_dict_cursor()
    if not conn:
        raise SystemExit("无法连接 MySQL，请检查 MYSQL_HOST / MYSQL_USER / MYSQL_PWD / MYSQL_DB 等环境变量")

    try:
        # 批量导入模式
        if args.batch:
            sql_dir = os.path.join(PROJECT_ROOT, "sql")
            if not os.path.exists(sql_dir):
                raise SystemExit(f"sql 目录不存在：{sql_dir}")
            
            csv_files = [
                os.path.join(sql_dir, f) for f in os.listdir(sql_dir)
                if f.endswith('.csv') and not f.startswith('.')
            ]
            
            if not csv_files:
                print(f"在 {sql_dir} 目录下未找到 CSV 文件")
                return
            
            print(f"找到 {len(csv_files)} 个 CSV 文件，开始批量导入...")
            print("=" * 60)
            
            success_count = 0
            failed_files = []
            
            for csv_path in sorted(csv_files):
                table_name = os.path.splitext(os.path.basename(csv_path))[0]
                try:
                    print(f"\n正在处理：{os.path.basename(csv_path)} -> {table_name}")
                    headers, rows = load_csv(csv_path)
                    print(f"  ✓ 读取 CSV 成功，列数={len(headers)},行数={len(rows)}")
                    
                    create_table(conn, table_name, headers)
                    print(f"  ✓ 已创建/重建表 `{table_name}`")
                    
                    inserted = insert_rows(conn, table_name, headers, rows)
                    print(f"  ✓ 成功导入 {inserted} 行数据到 `{table_name}`")
                    success_count += 1
                except Exception as e:
                    print(f"  ✗ 处理失败：{e}")
                    failed_files.append((csv_path, str(e)))
            
            print("\n" + "=" * 60)
            print(f"批量导入完成！成功：{success_count}/{len(csv_files)}")
            if failed_files:
                print(f"\n失败的文件 ({len(failed_files)}):")
                for fp, err in failed_files:
                    print(f"  - {os.path.basename(fp)}: {err}")
            return
        
        # 单文件导入模式
        if not args.csv:
            parser.error("非批量模式下，--csv 参数是必需的")
        
        csv_path = os.path.abspath(args.csv)
        if not os.path.exists(csv_path):
            raise SystemExit(f"CSV 文件不存在：{csv_path}")

        table = args.table or os.path.splitext(os.path.basename(csv_path))[0]

        headers, rows = load_csv(csv_path)
        print(f"读取 CSV 成功，列数={len(headers)}，行数={len(rows)}")

        create_table(conn, table, headers)
        print(f"已创建/重建表 `{table}`")

        inserted = insert_rows(conn, table, headers, rows)
        print(f"成功导入 {inserted} 行数据到 `{table}`")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
#     import_dimension_table.py --batch

