#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确调试键名问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.kafka_generator_routes import fix_json_keys
import json
import re

def debug_key_names(data, sample_name):
    """调试键名问题"""
    print(f"\n=== 调试 {sample_name} 的键名问题 ===")
    
    # 查找所有未加引号的键名模式
    pattern = r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:'
    matches = re.finditer(pattern, data)
    
    print("发现的未加引号键名:")
    key_positions = []
    for match in matches:
        prefix = match.group(1)
        key = match.group(2)
        position = match.start()
        line_num = data[:position].count('\n') + 1
        key_positions.append((key, position, line_num))
        print(f"  行{line_num}: {key}")
    
    print(f"\n总共发现 {len(key_positions)} 个未加引号的键名")
    
    # 应用修复
    print("\n--- 应用键名修复 ---")
    fixed_data = fix_json_keys(data)
    
    # 验证修复效果
    print("\n--- 验证修复效果 ---")
    try:
        result = json.loads(fixed_data)
        print("✅ 键名修复成功! JSON解析通过")
        print(f"解析后的字段数: {len(result)}")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ 仍有问题: {e}")
        return False

# 测试简化数据
simple_test = '''{
    name: "测试",
    age: 25,
    info: {
        city: "北京",
        active: true
    }
}'''

print("=== 测试键名修复函数 ===")
debug_key_names(simple_test, "简化测试")

# 从测试数据中提取问题片段
from test_json_processing import test_data2

# 提取问题区域的数据片段
lines = test_data2.split('\n')
problem_area = '\n'.join(lines[50:60])  # 取错误位置附近的几行

print("\n" + "="*50)
print("=== 测试实际问题数据 ===")
debug_key_names(problem_area, "实际问题区域")