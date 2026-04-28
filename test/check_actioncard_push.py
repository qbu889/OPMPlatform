#!/usr/bin/env python3
"""检查最新的 ActionCard 推送记录"""
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
cursor.execute('''
    SELECT id, message_content, status, triggered_at 
    FROM dingtalk_push_history 
    ORDER BY triggered_at DESC 
    LIMIT 1
''')

row = cursor.fetchone()
if row:
    print(f"记录 ID: {row['id']}")
    print(f"状态: {row['status']}")
    print(f"时间: {row['triggered_at']}")
    
    if row['message_content']:
        try:
            msg = json.loads(row['message_content'])
            print(f"\n消息内容:")
            print(f"  消息类型: {msg.get('msgtype')}")
            if msg.get('actionCard'):
                print(f"  标题: {msg['actionCard'].get('title')}")
                print(f"  内容: {msg['actionCard'].get('text', '')[:100]}...")
                if msg['actionCard'].get('btns'):
                    print(f"\n  按钮配置:")
                    for btn in msg['actionCard']['btns']:
                        print(f"    - 标题: {btn['title']}")
                        print(f"      URL: {btn['actionURL']}")
            if msg.get('at'):
                print(f"\n  @配置:")
                print(f"    atMobiles: {msg['at'].get('atMobiles')}")
                print(f"    isAtAll: {msg['at'].get('isAtAll')}")
        except Exception as e:
            print(f"消息解析失败: {e}")
else:
    print("未找到 ActionCard 类型的推送记录")

cursor.close()
conn.close()
