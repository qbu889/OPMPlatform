#!/usr/bin/env python3
"""测试 JSON 预处理修复"""

import json
import sys

sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')

from routes.kafka.kafka_generator_routes import preprocess_json_data

# 读取测试文件
with open('test/kafka/test_payload.json', 'r', encoding='utf-8') as f:
    payload = json.load(f)

es_source_raw = payload['es_source_raw']
print(f'原始数据长度：{len(es_source_raw)}')
print(f'原始数据预览：{es_source_raw[:200]}...\n')

# 预处理
processed = preprocess_json_data(es_source_raw)
print(f'处理后数据长度：{len(processed)}')
print(f'处理后数据预览：{processed[:200]}...\n')

# 尝试解析
try:
    data = json.loads(processed)
    print('✅ JSON 解析成功！')
    if 'NE_LOCATION' in data:
        print(f'NE_LOCATION: {data["NE_LOCATION"]}')
except Exception as e:
    print(f'❌ JSON 解析失败：{e}')
    # 显示错误位置附近的内容
    import re
    error_match = re.search(r'column (\d+)', str(e))
    if error_match:
        col = int(error_match.group(1))
        start = max(0, col - 50)
        end = min(len(processed), col + 50)
        print(f'错误在列 {col} 附近：{processed[start:end]}')
