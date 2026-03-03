#!/usr/bin/env python3
from dotenv import load_dotenv
import os, pymysql

load_dotenv()

db = pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', '3306')),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    charset='utf8mb4'
)

cursor = db.cursor()

print('=' * 60)
print('验证排班逻辑：避免连续排班')
print('=' * 60)

# 检查 2026-02-14 的晚班
print('\n2026-02-14（日常）晚班 (18:00～21:00):')
sql = "SELECT staff_name FROM roster WHERE date = '2026-02-14' AND time_slot = '18:00～21:00'"
cursor.execute(sql)
result = cursor.fetchone()
if result:
    print(f'  {result[0]}')
    feb14_evening = result[0]
else:
    print('  无记录')
    feb14_evening = None

# 检查 2026-02-15 的早班
print('\n2026-02-15（节假日）早班 (8:00～12:00):')
sql = "SELECT staff_name FROM roster WHERE date = '2026-02-15' AND time_slot = '8:00～12:00'"
cursor.execute(sql)
result = cursor.fetchone()
if result:
    print(f'  {result[0]}')
    feb15_morning = result[0]
else:
    print('  无记录')
    feb15_morning = None

# 检查是否重复
print('\n' + '=' * 60)
if feb14_evening and feb15_morning:
    if feb14_evening == feb15_morning:
        print(f'❌ 错误：{feb14_evening} 连续排班！')
        print(f'   2026-02-14 晚班 → 2026-02-15 早班')
    else:
        print(f'✓ 正确：避免了连续排班')
        print(f'   2026-02-14 晚班：{feb14_evening}')
        print(f'   2026-02-15 早班：{feb15_morning}')
else:
    print('数据不完整')

print('=' * 60)
