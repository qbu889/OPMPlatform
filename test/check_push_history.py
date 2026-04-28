#!/usr/bin/env python3
import pymysql
import json

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='12345678',
    database='dingtalk_push',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# 查询最近的推送历史
cursor.execute('''
    SELECT id, config_id, status, message_content, triggered_at 
    FROM dingtalk_push_history 
    ORDER BY triggered_at DESC 
    LIMIT 3
''')

rows = cursor.fetchall()

print('最近3条推送历史记录:')
print('=' * 80)

for row in rows:
    print(f"记录ID: {row['id']}")
    print(f"配置ID: {row['config_id']}")
    print(f"状态: {row['status']}")
    print(f"时间: {row['triggered_at']}")
    
    # 解析 message_content
    if row['message_content']:
        try:
            msg = json.loads(row['message_content'])
            print(f"消息类型: {msg.get('msgtype')}")
            print(f"@对象: {msg.get('at', {})}")
        except:
            print(f"消息内容: {str(row['message_content'])[:200]}...")
    
    print('-' * 80)

cursor.close()
conn.close()
