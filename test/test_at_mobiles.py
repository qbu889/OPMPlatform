#!/usr/bin/env python3
# test_at_mobiles.py - 测试 @指定人员功能
import json
import requests

# 配置
BASE_URL = "http://localhost:5200"
CONFIG_ID = 1

def test_execute_push():
    """测试立即执行推送"""
    print("=" * 60)
    print("测试钉钉推送 @指定人员功能")
    print("=" * 60)
    
    # 1. 先查看配置
    print("\n1. 查看配置详情...")
    res = requests.get(f"{BASE_URL}/dingtalk-push/configs/{CONFIG_ID}")
    if res.status_code == 200:
        data = res.json()
        if data.get('success'):
            config = data['data']
            print(f"   配置名称: {config.get('name')}")
            print(f"   at_mobiles: {config.get('at_mobiles')}")
            print(f"   at_all: {config.get('at_all')}")
            
            # 解析 at_mobiles
            at_mobiles_raw = config.get('at_mobiles', '[]')
            try:
                at_mobiles = json.loads(at_mobiles_raw) if at_mobiles_raw else []
                print(f"   解析后的 at_mobiles: {at_mobiles} (类型: {type(at_mobiles)})")
            except Exception as e:
                print(f"   解析失败: {e}")
        else:
            print(f"   获取配置失败: {data.get('msg')}")
    else:
        print(f"   请求失败: {res.status_code}")
    
    # 2. 执行推送
    print("\n2. 执行推送任务...")
    res = requests.post(f"{BASE_URL}/dingtalk-push/configs/{CONFIG_ID}/execute")
    if res.status_code == 200:
        data = res.json()
        if data.get('success'):
            print(f"   ✅ 推送任务已提交")
            print(f"   提示: 请查看后端日志确认 at_mobiles 是否正确传递")
        else:
            print(f"   ❌ 推送失败: {data.get('msg')}")
    else:
        print(f"   ❌ 请求失败: {res.status_code}")
        print(f"   响应: {res.text}")

if __name__ == "__main__":
    test_execute_push()
