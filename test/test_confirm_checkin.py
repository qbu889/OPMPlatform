#!/usr/bin/env python3
"""测试打卡确认接口"""
import requests

# 模拟用户点击 ActionCard 按钮后的请求
url = "http://localhost:5200/dingtalk-push/confirm-checkin"
params = {
    "phone": "18659196149",
    "time": "2026-04-28 15:00:00"
}

print("=" * 60)
print("测试打卡确认接口")
print("=" * 60)
print(f"请求 URL: {url}")
print(f"请求参数: {params}")
print()

try:
    response = requests.get(url, params=params)
    result = response.json()
    
    print("✅ 接口调用成功！")
    print(f"HTTP 状态码: {response.status_code}")
    print(f"\n响应内容:")
    print(f"  成功状态: {result.get('success')}")
    print(f"  消息: {result.get('message')}")
    print(f"  数据:")
    print(f"    - 手机号: {result.get('data', {}).get('phone')}")
    print(f"    - 打卡时间: {result.get('data', {}).get('checkin_time')}")
    print(f"    - 状态: {result.get('data', {}).get('status')}")
    
except Exception as e:
    print(f"❌ 接口调用失败: {e}")
