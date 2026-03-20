#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简单测试 - 直接模拟后端接收的数据"""

import json
import re

# 从文件读取完整的 curl 命令
with open('/Users/linziwang/PycharmProjects/wordToWord/test/kafka/es数据.txt', 'r', encoding='utf-8') as f:
    curl_content = f.read()

# 提取 es_source_raw 的值
match = re.search(r'"es_source_raw":"(.+?)","custom_fields":\{\}\}', curl_content, re.DOTALL)
if not match:
    print("未找到匹配")
    exit(1)

raw_json = match.group(1)

print("=" * 80)
print(f"原始 es_source_raw 长度：{len(raw_json)}")
print("=" * 80)

# 现在模拟后端的 preprocess_json_data 函数处理
def preprocess_json_data(raw_data):
    """预处理 JSON 数据"""
    print("\n开始预处理...")
    
    # 1. 移除 BOM
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        print("移除 BOM")
    
    # 2. 处理三重引号
    triple_count = raw_data.count('"""')
    if triple_count > 0:
        print(f"检测到 {triple_count} 个三重引号")
        raw_data = raw_data.replace('"""', '__TEMP_TRIPLE_QUOTE__')
        
        def escape_nested_quotes(match):
            content = match.group(1)
            content = content.replace('"', '\\"')
            content = content.replace('\n', '\\n')
            content = content.replace('\r', '\\r')
            content = content.replace('\t', '\\t')
            return f'"{content}"'
        
        raw_data = re.sub(r'__TEMP_TRIPLE_QUOTE__(.*?)__TEMP_TRIPLE_QUOTE__', 
                         escape_nested_quotes, raw_data, flags=re.DOTALL)
        print("处理完三重引号")
    
    # 3. 修复非法转义 - 简化版本
    def fix_invalid_escapes(text):
        print("【fix_invalid_escapes】开始")
        
        # 保护合法转义
        placeholders = {}
        valid_escapes = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']
        
        for i, escape_seq in enumerate(valid_escapes):
            placeholder = f'__VALID_ESCAPE_{i}__'
            placeholders[placeholder] = escape_seq
            text = text.replace(escape_seq, placeholder)
        
        # 保护 Unicode
        def protect_unicode(match):
            return f'__UNICODE_{match.group(0)[1:]}__'
        
        text = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, text)
        
        # 【关键】处理多个反斜杠 + Unicode -> 只保留两个反斜杠
        text = re.sub(r'\\{2,}(?=u[0-9a-fA-F]{4})', r'\\', text)
        
        # 恢复合法转义
        for placeholder, escape_seq in placeholders.items():
            text = text.replace(placeholder, escape_seq)
        
        # 恢复 Unicode
        text = re.sub(r'__UNICODE_([0-9a-fA-F]{4})__', r'\\u\1', text)
        
        print("【fix_invalid_escapes】完成")
        return text
    
    raw_data = fix_invalid_escapes(raw_data)
    
    # 4. 处理字符串中的双重转义
    def process_json_strings(text):
        pattern = r'"((?:[^"\\]|\\.)*)"'
        
        def replace_string_content(match):
            content = match.group(1)
            # 修复双重转义
            content = content.replace('\\\\"', '\\"')  
            content = content.replace('\\\\n', '\\n')  
            content = content.replace('\\\\r', '\\r')  
            content = content.replace('\\\\t', '\\t')  
            content = content.replace('\\\\\\\\', '\\\\')  
            return f'"{content}"'
        
        return re.sub(pattern, replace_string_content, text)
    
    raw_data = process_json_strings(raw_data)
    print("处理完双重转义")
    
    return raw_data

# 应用预处理
processed = preprocess_json_data(raw_json)
print(f"\n处理后长度：{len(processed)}")

# 尝试解析
try:
    data = json.loads(processed)
    print("✅ 解析成功!")
    
    # 检查关键字段
    if 'SRC_ORG_ALARM_TEXT' in data:
        text = data['SRC_ORG_ALARM_TEXT']
        print(f"\nSRC_ORG_ALARM_TEXT 长度：{len(text)}")
        lines = text.split('\n')
        for i, line in enumerate(lines[:20]):  # 只看前 20 行
            if '\\' in line:
                print(f"行{i+1}: {repr(line)}")
                
except Exception as e:
    print(f"❌ 解析失败：{e}")
    error_match = re.search(r'line (\d+) column (\d+)', str(e))
    if error_match:
        line_num = int(error_match.group(1))
        col_num = int(error_match.group(2))
        lines = processed.split('\n')
        if line_num <= len(lines):
            error_line = lines[line_num - 1]
            context_start = max(0, col_num - 50)
            context_end = min(len(error_line), col_num + 50)
            print(f"\n错误位置：第{line_num}行第{col_num}列")
            print(f"附近内容：{repr(error_line[context_start:context_end])}")
