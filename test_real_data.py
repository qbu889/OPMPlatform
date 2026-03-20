#!/usr/bin/env python3
"""使用真实的大数据集测试修复"""

import json
import re
import sys

sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')

from routes.kafka.kafka_generator_routes import preprocess_json_data

# 读取 curl 文件并提取 es_source_raw
with open('test/kafka/es数据.txt', 'rb') as f:
    content = f.read().decode('utf-8')

# 提取--data-raw 参数
match = re.search(r"--data-raw \\$'(.+?)'", content, re.DOTALL)
if match:
    raw_payload = match.group(1)
    
    # 还原 shell 转义
    raw_payload = raw_payload.replace('\\n', '\n').replace('\\\\', '\\').replace("\\'", "'")
    
    try:
        payload = json.loads(raw_payload)
        es_source_raw = payload['es_source_raw']
        
        print(f"原始数据长度：{len(es_source_raw)}")
        
        # 预处理
        processed = preprocess_json_data(es_source_raw)
        print(f"处理后数据长度：{len(processed)}")
        
        # 尝试解析
        try:
            data = json.loads(processed)
            print("✅ 大数据集解析成功！")
            
            # 检查几个关键字段
            if 'NE_LOCATION' in data:
                ne_loc = data['NE_LOCATION']
                print(f"\nNE_LOCATION 长度：{len(ne_loc)}")
                if 'Paras:' in ne_loc:
                    print("✅ Paras: 字段存在且正确")
                    
            if 'EVENT_REASON' in data:
                print(f"\nEVENT_REASON: {data['EVENT_REASON'][:100]}...")
                
        except json.JSONDecodeError as e:
            print(f"❌ 解析失败：{e}")
            error_pos = e.pos
            if error_pos and len(processed) > error_pos:
                start = max(0, error_pos - 50)
                end = min(len(processed), error_pos + 50)
                print(f"错误位置附近：{repr(processed[start:end])}")
                
    except Exception as e:
        print(f"处理过程出错：{e}")
        import traceback
        traceback.print_exc()
