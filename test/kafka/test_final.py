#!/usr/bin/env python3
"""直接测试原始数据"""

import json

# 从 test_payload.json 读取（这个文件已经是有效的 JSON）
with open('test/kafka/test_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

es_source = payload['es_source_raw']

print("=== 测试简单数据集 ===")
try:
    data = json.loads(es_source)
    print("✅ 简单数据解析成功")
    print(f"NE_LOCATION: {data.get('NE_LOCATION', 'N/A')[:100]}...")
except Exception as e:
    print(f"❌ 失败：{e}")
