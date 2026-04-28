#!/usr/bin/env python3
"""测试完整的打卡确认流程"""
import requests
import json

print("=" * 70)
print("测试完整的打卡确认流程")
print("=" * 70)

# 1. 测试后端直接调用
print("\n1️⃣  测试后端直接调用 (localhost:5004)")
print("-" * 70)
try:
    response = requests.get(
        "http://localhost:5004/dingtalk-push/confirm-checkin",
        params={"phone": "18659196149", "time": "2026-04-28 15:00:00"}
    )
    result = response.json()
    print(f"✅ 后端接口调用成功！")
    print(f"   HTTP 状态码: {response.status_code}")
    print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
except Exception as e:
    print(f"❌ 后端接口调用失败: {e}")

# 2. 测试通过 Vite 代理调用
print("\n2️  测试通过 Vite 代理调用 (localhost:5200)")
print("-" * 70)
try:
    response = requests.get(
        "http://localhost:5200/dingtalk-push/confirm-checkin",
        params={"phone": "18659196149", "time": "2026-04-28 15:00:00"},
        headers={"Accept": "application/json"}
    )
    print(f"   HTTP 状态码: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Vite 代理调用成功！")
        print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"❌ Vite 代理调用失败")
        print(f"   响应内容: {response.text[:200]}")
except Exception as e:
    print(f"❌ Vite 代理调用异常: {e}")

# 3. 检查推送历史
print("\n3️⃣  检查最近的推送历史")
print("-" * 70)
try:
    response = requests.get("http://localhost:5004/dingtalk-push/history?page=1&size=1")
    result = response.json()
    if result.get('success'):
        history = result['data']['list'][0]
        print(f"✅ 推送历史查询成功！")
        print(f"   记录 ID: {history['id']}")
        print(f"   消息类型: {history['message_type']}")
        print(f"   状态: {history['status']}")
        print(f"   时间: {history['triggered_at']}")
        
        # 显示消息快照中的按钮配置
        if history.get('message_snapshot'):
            try:
                snapshot = json.loads(history['message_snapshot']) if isinstance(history['message_snapshot'], str) else history['message_snapshot']
                if snapshot.get('actionCard', {}).get('btns'):
                    print(f"\n   按钮配置:")
                    for btn in snapshot['actionCard']['btns']:
                        print(f"   - 标题: {btn['title']}")
                        print(f"     URL: {btn['actionURL']}")
                else:
                    print(f"\n   消息类型: {history.get('message_type', 'N/A')}")
            except Exception as e:
                print(f"\n   消息快照解析失败: {e}")
    else:
        print(f"❌ 推送历史查询失败: {result.get('msg')}")
except Exception as e:
    print(f"❌ 推送历史查询异常: {e}")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
