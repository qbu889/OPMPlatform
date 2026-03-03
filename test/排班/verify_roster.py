#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证排班结果"""
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
print("2026-02-01 至 2026-02-10 排班验证")
print("=" * 80)

# 查询排班数据
sql = """
SELECT date, time_slot, staff_name, is_main, rotation_index
FROM roster 
WHERE date BETWEEN '2026-02-01' AND '2026-02-10'
ORDER BY date, time_slot
"""
cursor.execute(sql)

current_date = None
for row in cursor.fetchall():
    if row['date'] != current_date:
        current_date = row['date']
        # 判断日期类型
        sql_holiday = "SELECT is_working_day FROM holiday_config WHERE holiday_date = %s"
        cursor.execute(sql_holiday, (current_date,))
        result = cursor.fetchone()
        if result:
            date_type = "节假日" if result['is_working_day'] == 0 else "工作日"
        else:
            # 周末是节假日
            weekday = current_date.weekday()
            date_type = "节假日" if weekday >= 5 else "工作日"
        print(f"\n{current_date} ({date_type}):")
        print("-" * 80)
    
    main_flag = "主" if row['is_main'] == 1 else "辅"
    print(f"  {row['time_slot']:15} | {row['staff_name']:5} | 索引:{row['rotation_index']} | {main_flag}")

# 检查轮换配置
print("\n" + "=" * 80)
print("当前轮换配置:")
print("=" * 80)
sql = "SELECT * FROM rotation_config"
cursor.execute(sql)
for row in cursor.fetchall():
    print(f"{row['time_slot_type']}: 顺序={row['rotation_order']}, 索引={row['current_index']}")

cursor.close()
conn.close()
