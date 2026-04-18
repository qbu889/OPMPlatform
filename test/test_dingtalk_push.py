#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试钉钉排班消息推送功能
"""
import requests
import json

# API 地址
API_URL = "http://localhost:5200/schedule-config/api/send-dingtalk-message"

# 测试配置
TEST_CONFIG = {
    "start_date": "2026-04-17",
    "end_date": "2026-04-19",
    "time_slots": [
        "8:00～9:00",
        "9:00～12:00",
        "13:30～18:00",
        "18:00～21:00"
    ],
    # ⚠️ 请在这里填写您的钉钉 Webhook 地址
    "dingtalk_webhook": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN"
}


def test_dingtalk_push():
    """测试钉钉消息推送"""
    print("=" * 60)
    print("钉钉排班消息推送测试")
    print("=" * 60)
    
    # 检查 Webhook 是否配置
    if "YOUR_ACCESS_TOKEN" in TEST_CONFIG["dingtalk_webhook"]:
        print("\n⚠️  警告：请先在脚本中配置钉钉 Webhook 地址！")
        print("\n获取 Webhook 的方法：")
        print("1. 打开钉钉群 -> 群设置 -> 智能群助手")
        print("2. 添加机器人 -> 自定义机器人")
        print("3. 复制 Webhook 地址并替换脚本中的 YOUR_ACCESS_TOKEN")
        return
    
    print(f"\n📅 测试日期范围：{TEST_CONFIG['start_date']} 至 {TEST_CONFIG['end_date']}")
    print(f"⏰ 推送时段：{', '.join(TEST_CONFIG['time_slots']) if TEST_CONFIG['time_slots'] else '全部时段'}")
    print(f"🔗 Webhook：{TEST_CONFIG['dingtalk_webhook'][:50]}...")
    
    try:
        # 发送请求
        print("\n🚀 正在发送请求...")
        response = requests.post(
            API_URL,
            headers={"Content-Type": "application/json"},
            data=json.dumps(TEST_CONFIG),
            timeout=10
        )
        
        result = response.json()
        
        print("\n" + "=" * 60)
        if result.get("success"):
            print("✅ 推送成功！")
            print(f"📊 推送数据：")
            print(f"   - 日期总数：{result.get('data', {}).get('total_dates', 'N/A')}")
            print(f"   - 时段数量：{result.get('data', {}).get('time_slots', 'N/A')}")
        else:
            print("❌ 推送失败！")
            print(f"📝 错误信息：{result.get('msg', '未知错误')}")
        
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 连接失败：无法连接到后端服务")
        print("💡 请确保后端服务已启动在 http://localhost:5200")
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时：后端服务响应超时")
    except Exception as e:
        print(f"\n❌ 发生错误：{str(e)}")


def preview_message_content():
    """预览消息内容（不实际发送）"""
    print("=" * 60)
    print("消息内容预览（未发送）")
    print("=" * 60)
    
    print("\n📅 **排班信息推送**\n")
    print("📆 **2026-04-17 (周五)**")
    print("  ⏰ 8:00～9:00: 郑晨昊")
    print("  ⏰ 9:00～12:00: 郑晨昊、林子旺、曾婷婷")
    print("  ⏰ 13:30～18:00: 林子旺、曾婷婷、郑晨昊")
    print("  ⏰ 18:00～21:00: 郑晨昊")
    print("\n📆 **2026-04-18 (周六)**")
    print("  ⏰ 8:00～12:00: 曾婷婷")
    print("  ⏰ 13:30～17:30: 曾婷婷")
    print("  ⏰ 17:30～21:30: 曾婷婷")
    print("\n📆 **2026-04-19 (周日)**")
    print("  ⏰ 8:00～12:00: 郑晨昊")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        # 预览模式：只显示消息格式，不实际发送
        preview_message_content()
    else:
        # 正常模式：实际发送消息
        test_dingtalk_push()
        
        print("\n💡 提示：")
        print("   - 运行 'python test_dingtalk_push.py preview' 可预览消息格式")
        print("   - 运行 'python test_dingtalk_push.py' 将实际发送消息到钉钉")
