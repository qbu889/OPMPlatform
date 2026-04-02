#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试：直接验证 前端展示Kafka 消息.txt 中的 JSON
"""

import json
import re

# 读取文件
with open('test/kafka/前端展示Kafka 消息.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 方法 1: 从 curl 命令中提取 --data-raw 的内容
print("="*80)
print("方法 1: 从 curl 命令提取")
print("="*80)

match = re.search(r"--data-raw \$'(.+?)'$", content, re.MULTILINE | re.DOTALL)
if match:
    raw_data = match.group(1)
    print(f"✅ 提取成功，原始长度：{len(raw_data)}")
    
    # 尝试解析整个请求 JSON
    try:
        request_json = json.loads(raw_data)
        print("✅ 请求 JSON 直接解析成功！")
        
        # 提取 es_source_raw
        es_source = request_json.get('es_source_raw', '')
        print(f"✅ es_source_raw 长度：{len(es_source)}")
        
        # 尝试解析 es_source
        try:
            es_json = json.loads(es_source)
            print(f"✅ es_source 解析成功！字段数：{len(es_json.keys())}")
            print("\n✅ 所有 JSON 格式都正确！")
            
        except json.JSONDecodeError as e:
            print(f"❌ es_source 解析失败：{e}")
            print(f"\n错误位置附近的内容:")
            start = max(0, e.pos - 100)
            end = min(len(es_source), e.pos + 100)
            print(f"...{repr(es_source[start:end])}...")
            
    except json.JSONDecodeError as e:
        print(f"❌ 请求 JSON 解析失败：{e}")
        print(f"\n错误位置附近的内容:")
        start = max(0, e.pos - 50)
        end = min(len(raw_data), e.pos + 50)
        print(f"...{repr(raw_data[start:end])}...")
else:
    print("❌ 无法从 curl 命令中提取数据")

print("\n" + "="*80)
print("方法 2: 查看文件中的实际内容")
print("="*80)

# 显示文件前几行看看格式
lines = content.split('\n')
for i, line in enumerate(lines[:20], 1):
    print(f"{i}: {line[:100]}")
