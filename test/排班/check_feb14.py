#!/usr/bin/env python3
from dotenv import load_dotenv
import os
load_dotenv()

import pymysql

db = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', '3306')),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = db.cursor()

# 检查 2026-02-14 的早班
sql = "SELECT time_slot, staff_name FROM roster WHERE date = '2026-02-14' AND (time_slot = '8:00～9:00' OR time_slot = '8:00～12:00') ORDER BY time_slot"
cursor.execute(sql)
results = cursor.fetchall()
print('2026-02-14 早班时段:')
for r in results:
    print(f'  {r["time_slot"]:20s} - {r["staff_name"]}')

# 检查 2026-02-07（节假日）的早班
sql = "SELECT time_slot, staff_name FROM roster WHERE date = '2026-02-07' AND time_slot = '8:00～12:00' ORDER BY time_slot"
cursor.execute(sql)
results = cursor.fetchall()
print('\n2026-02-07（节假日）早班:')
for r in results:
    print(f'  {r["time_slot"]:20s} - {r["staff_name"]}')
