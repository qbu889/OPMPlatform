#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化版的JSON修复方案
"""

import json
import re

def simple_preprocess(data):
    """简化版预处理函数"""
    print("=== 简化预处理 ===")
    processed = data
    
    # 1. 处理三重引号
    triple_count = len(re.findall(r'"""', processed))
    if triple_count > 0:
        print(f"发现 {triple_count} 个三重引号")
        processed = processed.replace('"""', '"')
        print("三重引号已替换为双引号")
    
    # 2. 移除控制字符
    before_len = len(processed)
    processed = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', processed)
    if len(processed) != before_len:
        print(f"移除了 {before_len - len(processed)} 个控制字符")
    
    return processed

# 测试数据
test_data = '''{
  "test_field": """
这是多行文本
包含换行符
和"引号"
""",
  "normal_field": "正常字段"
}'''

print("原始数据:")
print(test_data)
print()

try:
    result = json.loads(test_data)
    print("✓ 直接解析成功")
except json.JSONDecodeError as e:
    print(f"✗ 直接解析失败: {e}")
    
    print("\\n应用简化预处理...")
    processed = simple_preprocess(test_data)
    print("\\n处理后数据:")
    print(processed)
    
    try:
        result = json.loads(processed)
        print("\\n✓ 预处理后解析成功!")
        print("解析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except json.JSONDecodeError as e2:
        print(f"\\n✗ 预处理后仍然失败: {e2}")