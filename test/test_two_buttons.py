#!/usr/bin/env python3
"""测试两个打卡按钮"""
import requests
import json

print("=" * 60)
print("测试打卡功能")
print("=" * 60)

# 测试 1: 打卡确认按钮
print("\n1️⃣  测试打卡确认按钮")
print("-" * 60)
try:
    response = requests.get(
        "http://localhost:5004/dingtalk-push/confirm-checkin",
        params={"phone": "18659196149", "time": "2026-04-28 17:00:00"}
    )
    result = response.json()
    print(f"✅ 打卡确认接口调用成功")
    print(f"   响应: {result['message']}")
except Exception as e:
    print(f"❌ 打卡确认接口调用失败: {e}")

# 测试 2: 查看打卡信息按钮
print("\n2️⃣  测试查看打卡信息按钮")
print("-" * 60)
try:
    response = requests.get(
        "http://localhost:5004/dingtalk-push/view-checkin",
        params={"phone": "18659196149"}
    )
    result = response.json()
    print(f"✅ 查看打卡信息接口调用成功")
    print(f"   手机号: {result['data']['phone']}")
    print(f"   总打卡次数: {result['data']['total_checkins']}")
except Exception as e:
    print(f"❌ 查看打卡信息接口调用失败: {e}")

# 测试 3: 检查推送配置
print("\n3️⃣  检查推送配置中的按钮")
print("-" * 60)
try:
    import pymysql
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='12345678',
        database='dingtalk_push',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT data_source_config FROM dingtalk_push_config WHERE id = 1')
    row = cursor.fetchone()
    
    if row and row[0]:
        config = json.loads(row[0])
        if 'actionCard' in config and 'btns' in config['actionCard']:
            print(f"✅ 配置中有 {len(config['actionCard']['btns'])} 个按钮:")
            for i, btn in enumerate(config['actionCard']['btns'], 1):
                print(f"   {i}. {btn['title']}")
                print(f"      URL: {btn['actionURL']}")
        else:
            print("❌ 未找到按钮配置")
    else:
        print("❌ 未找到配置")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ 检查配置失败: {e}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
