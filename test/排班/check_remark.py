#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证排班备注"""
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

print("=" * 80)
print("检查带备注的排班记录")
print("=" * 80)

# 查询有备注的排班数据
sql = """
SELECT date, time_slot, staff_name, is_main, remark
FROM roster 
WHERE remark IS NOT NULL
ORDER BY date, time_slot
LIMIT 20
"""
cursor.execute(sql)

results = cursor.fetchall()
if results:
    print(f"\n找到 {len(results)} 条带备注的记录:\n")
    for row in results:
        main_flag = "主" if row['is_main'] == 1 else "辅"
        print(f"{row['date']} {row['time_slot']:15} | {row['staff_name']:5} | {main_flag} | {row['remark']}")
else:
    print("\n没有找到带备注的记录")

# 查询请假记录
print("\n" + "=" * 80)
print("最近的请假记录:")
print("=" * 80)
sql = """
SELECT leave_date, staff_name, is_full_day, start_time, end_time
FROM leave_record 
WHERE leave_date >= '2026-02-01'
ORDER BY leave_date
LIMIT 10
"""
cursor.execute(sql)
results = cursor.fetchall()
if results:
    for row in results:
        full_day = "全天" if row['is_full_day'] == 1 else f"{row['start_time']}-{row['end_time']}"
        print(f"{row['leave_date']} {row['staff_name']:5} | {full_day:20}")
else:
    print("\n没有找到请假记录")

cursor.close()
conn.close()
