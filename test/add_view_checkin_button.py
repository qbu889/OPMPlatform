#!/usr/bin/env python3
"""添加查看打卡信息按钮"""
import pymysql
import json

conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='12345678',
    database='dingtalk_push',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 更新配置，添加两个按钮
action_card_config = {
    "type": "static",
    "config": {},
    "actionCard": {
        "btns": [
            {
                "title": "✅ 已确认打卡",
                "actionURL": "http://localhost:5200/dingtalk-push/confirm-checkin?phone={{ phone }}&time={{ timestamp }}"
            },
            {
                "title": "📋 查看打卡信息",
                "actionURL": "http://localhost:5200/dingtalk-push/view-checkin?phone={{ phone }}"
            }
        ]
    }
}

# 更新配置
cursor.execute('''
    UPDATE dingtalk_push_config 
    SET data_source_config = %s
    WHERE id = 1
''', (json.dumps(action_card_config)))

conn.commit()

print("✅ 按钮配置已更新！")
print("\n现在有两个按钮:")
print("1. ✅ 已确认打卡 - 确认打卡")
print("2. 📋 查看打卡信息 - 查看打卡记录")

cursor.close()
conn.close()
