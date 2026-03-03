#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复轮换配置"""
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

cursor = conn.cursor()

print("=" * 60)
print("修复轮换配置")
print("=" * 60)

# 1. 删除所有日常 8-9 的配置 (包括有空格的)
print("\n1. 删除旧的日常 8-9 配置...")
sql_delete_daily = "DELETE FROM rotation_config WHERE time_slot_type LIKE '%日常%8-9%'"
cursor.execute(sql_delete_daily)
print(f"   已删除 {cursor.rowcount} 条记录")

# 2. 删除节假日配置
print("\n2. 删除旧的节假日配置...")
sql_delete_holiday = "DELETE FROM rotation_config WHERE time_slot_type = '节假日'"
cursor.execute(sql_delete_holiday)
print(f"   已删除 {cursor.rowcount} 条记录")

conn.commit()

# 3. 插入新的正确配置
print("\n3. 插入新的轮换配置...")

# 正确的顺序应该是：林子旺，陈伟强，曾婷婷，吴绍烨，郑晨昊 (核心)
daily_order = ["林子旺", "陈伟强", "曾婷婷", "吴绍烨", "郑晨昊"]
holiday_order = ["林子旺", "陈伟强", "曾婷婷", "吴绍烨", "郑晨昊"]

# 插入日常 8-9 配置
sql_insert_daily = """
INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) 
VALUES (%s, %s, %s)
"""
cursor.execute(sql_insert_daily, ("日常 8-9", ",".join(daily_order), 0))
print(f"   已插入日常 8-9 配置，顺序：{daily_order}, 初始索引：0")

# 插入节假日配置
sql_insert_holiday = """
INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) 
VALUES (%s, %s, %s)
"""
cursor.execute(sql_insert_holiday, ("节假日", ",".join(holiday_order), 0))
print(f"   已插入节假日配置，顺序：{holiday_order}, 初始索引：0")

conn.commit()

# 4. 验证结果
print("\n4. 验证配置...")
sql_check = "SELECT time_slot_type, rotation_order, current_index FROM rotation_config"
cursor.execute(sql_check)

print("\n当前轮换配置:")
for row in cursor.fetchall():
    print(f"  - {row[0]}: 顺序={row[1]}, 索引={row[2]}")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("配置修复完成！请重新生成排班数据")
print("=" * 60)
