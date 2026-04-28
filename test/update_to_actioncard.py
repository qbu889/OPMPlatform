6149#!/usr/bin/env python3
"""修改钉钉推送配置为 text 类型，支持 @指定人员"""
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

# 新的模板内容（text 格式）
# 注意：在文本中使用 @手机号 可以让钉钉识别并 @对应人员
template_content = "确认是否打卡！@{{ phone }}\n\n当前时间：{{ now }}\n\n请确认您是否已完成打卡。"

# text 类型不需要额外的按钮配置
# 但保留 at_mobiles 配置以实现 @功能

# 更新配置
cursor.execute('''
    UPDATE dingtalk_push_config 
    SET message_type = %s,
        template_content = %s,
        data_source_config = NULL
    WHERE id = 1
''', ('text', template_content))

conn.commit()

print("✅ 配置已更新！")
print("消息类型: text")
print("模板内容已更新，支持 @指定人员")
print("\n推送效果：")
print("  - 消息会显示：确认是否打卡！@林子旺")
print("  - atMobiles: [18659196149]")
print("  - 钉钉会高亮显示 @林子旺")

cursor.close()
conn.close()
