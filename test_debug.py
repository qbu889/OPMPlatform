#!/usr/bin/env python3
"""调试 JSON 预处理"""

import json
import sys

sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')

from routes.kafka.kafka_generator_routes import preprocess_json_data

# 读取测试文件
with open('test/kafka/test_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

es_source_raw = payload['es_source_raw']
print('=== 原始数据 ===')
print(repr(es_source_raw))
print()

# 预处理
processed = preprocess_json_data(es_source_raw)
print('=== 处理后数据 ===')
print(repr(processed))
print()

# 逐行检查
lines = processed.split('\n')
for i, line in enumerate(lines, 1):
    print(f'行{i}: {repr(line)}')
