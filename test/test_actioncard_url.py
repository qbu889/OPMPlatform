#!/usr/bin/env python3
"""测试 ActionCard 按钮 URL 动态替换"""
import sys
sys.path.append('/Users/linziwang/PycharmProjects/wordToWord')

from routes.dingtalk_push.dingtalk_push_routes import build_dingtalk_message
import json

# 模拟配置数据
config = {
    'data_source_config': json.dumps({
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
    })
}

# 测试 1：有 at_mobiles
print("=" * 60)
print("测试 1：有 at_mobiles 的情况")
print("=" * 60)
message = build_dingtalk_message(
    message_type='actionCard',
    content="### 确认是否打卡\n\n**当前时间**：2026-04-28 11:40:00\n\n---\n\n请确认您是否已完成打卡。",
    at_mobiles=['18659196149'],
    at_all=False,
    config=config
)

print("生成的消息 JSON:")
print(json.dumps(message, ensure_ascii=False, indent=2))
print("\n按钮 URL:")
print(message['actionCard']['btns'][0]['actionURL'])

# 测试 2：多个 at_mobiles（使用第一个）
print("\n" + "=" * 60)
print("测试 2：多个 at_mobiles 的情况（使用第一个）")
print("=" * 60)
message2 = build_dingtalk_message(
    message_type='actionCard',
    content="测试内容",
    at_mobiles=['18659196149', '13800138000'],
    at_all=False,
    config=config
)

print("按钮 URL:")
print(message2['actionCard']['btns'][0]['actionURL'])

# 测试 3：没有 at_mobiles
print("\n" + "=" * 60)
print("测试 3：没有 at_mobiles 的情况")
print("=" * 60)
message3 = build_dingtalk_message(
    message_type='actionCard',
    content="测试内容",
    at_mobiles=[],
    at_all=False,
    config=config
)

print("按钮 URL:")
print(message3['actionCard']['btns'][0]['actionURL'])

print("\n✅ 测试完成！")
