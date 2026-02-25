#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版JSON预处理测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import re

def simple_preprocess(raw_data):
    """简化的预处理函数"""
    print("=== 简化预处理开始 ===")
    
    # 1. 移除BOM
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        print("移除BOM标记")
    
    # 2. 处理三重引号
    if '"""' in raw_data:
        raw_data = raw_data.replace('"""', '"')
        print("处理三重引号")
    
    # 3. 处理HTML实体
    html_entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, replacement in html_entities.items():
        if entity in raw_data:
            raw_data = raw_data.replace(entity, replacement)
            print(f"处理HTML实体: {entity}")
    
    # 4. 简单的控制字符清理（保留换行符）
    cleaned = ''
    control_count = 0
    for char in raw_data:
        char_code = ord(char)
        if char_code == 9 or char_code == 10 or char_code == 13 or char_code >= 32:
            cleaned += char
        else:
            control_count += 1
    
    if control_count > 0:
        print(f"移除 {control_count} 个控制字符")
        raw_data = cleaned
    
    # 5. 标准化换行符
    raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')
    
    print("预处理完成")
    return raw_data

def debug_json_parsing(data):
    """调试JSON解析问题"""
    print("\n=== JSON解析调试 ===")
    try:
        parsed = json.loads(data)
        print("✅ JSON解析成功!")
        print(f"包含 {len(parsed)} 个字段")
        return True, parsed
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        
        # 提取错误位置
        line_num = e.lineno
        col_num = e.colno
        print(f"错误位置: 第{line_num}行，第{col_num}列")
        
        # 显示附近的内容
        lines = data.split('\n')
        if line_num <= len(lines):
            error_line = lines[line_num - 1]
            start = max(0, col_num - 30)
            end = min(len(error_line), col_num + 30)
            context = error_line[start:end]
            print(f"错误行: {repr(error_line)}")
            print(f"上下文: {repr(context)}")
            
            # 显示ASCII码
            if col_num <= len(error_line):
                char = error_line[col_num - 1]
                print(f"问题字符: '{char}' (ASCII: {ord(char)})")
        
        return False, None

# 测试数据片段
test_fragment = '''{
          "HOME_BROAD_BAND_LIST" : [ ],
          "FULL_REGION_ID" : "35000/350600/350623",
          "EVENT_LEVEL" : 4,'''

if __name__ == "__main__":
    print("测试数据片段长度:", len(test_fragment))
    
    # 测试简化预处理
    processed = simple_preprocess(test_fragment)
    print("处理后长度:", len(processed))
    
    # 测试JSON解析
    success, result = debug_json_parsing(processed)
    
    if not success:
        print("\n=== 原始数据对比 ===")
        success_orig, _ = debug_json_parsing(test_fragment)
        if success_orig:
            print("原始数据可以解析，问题是预处理引入的")