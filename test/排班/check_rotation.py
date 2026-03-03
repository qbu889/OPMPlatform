#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查轮换配置"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# 连接数据库
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "12345678"),
    database=os.getenv("DB_NAME", "schedule"),
    charset="utf8mb4"
)

cursor = conn.cursor(pymysql.cursors.DictCursor)

# 查询轮换配置
print("=" * 60)
print("轮换配置表:")
print("=" * 60)
sql = "SELECT * FROM rotation_config"
cursor.execute(sql)
for row in cursor.fetchall():
    print(f"类型：{row['time_slot_type']}")
    print(f"  顺序：{row['rotation_order']}")
    print(f"  当前索引：{row['current_index']}")
    print()

# 查询节假日配置
print("=" * 60)
print("2026-02 月节假日配置:")
print("=" * 60)
sql = """
SELECT holiday_date, is_working_day, remark 
FROM holiday_config 
WHERE holiday_date BETWEEN '2026-02-01' AND '2026-02-28'
ORDER BY holiday_date
"""
cursor.execute(sql)
for row in cursor.fetchall():
    date_type = "工作日" if row['is_working_day'] == 1 else "节假日"
    print(f"{row['holiday_date']} ({date_type}): {row['remark'] or '无备注'}")

cursor.close()
conn.close()
