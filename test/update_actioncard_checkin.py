#!/usr/bin/env python3
"""更新配置为 ActionCard 类型，添加打卡确认按钮"""
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

# ActionCard 消息内容
template_content = """### 确认是否打卡！ @{{ phone }}

**当前时间**：{{ now }}

---

请确认您是否已完成打卡。"""

# ActionCard 按钮配置
# 按钮点击后调用打卡确认接口
action_card_config = {
    "type": "static",
    "config": {},
    "actionCard": {
        "btns": [
            {
                "title": "✅ 已确认打卡",
                "actionURL": "http://localhost:5200/dingtalk-push/confirm-checkin?phone={{ phone }}&time={{ timestamp }}"
            }
        ]
    }
}

# 更新配置
cursor.execute('''
    UPDATE dingtalk_push_config 
    SET message_type = %s,
        template_content = %s,
        data_source_config = %s
    WHERE id = 1
''', ('actionCard', template_content, json.dumps(action_card_config)))

conn.commit()

print("✅ 配置已更新！")
print("消息类型: actionCard")
print("模板内容: 确认是否打卡（支持 @手机号）")
print("按钮配置: 已确认打卡")
print("\n推送效果：")
print("  - 消息会显示打卡确认内容并 @指定人员")
print("  - 底部有【已确认打卡】按钮")
print("  - 点击按钮会调用打卡确认接口")

cursor.close()
conn.close()
