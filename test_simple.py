#!/usr/bin/env python3
import requests
import json

# 测试数据包含路径分隔符
test_data = {
    "es_source_raw": '{"test":"\\n 中兴\\中\\兴\\n"}',
    "custom_fields": {}
}

print("发送测试数据...")
print(f"原始数据：{repr(test_data['es_source_raw'])}")
print()

response = requests.post('http://127.0.0.1:5001/kafka-generator/generate', json=test_data)

print(f"状态码：{response.status_code}")
if response.status_code == 200:
    print("✅ 成功!")
else:
    print(f"响应：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
