#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 - 直接从 curl 命令中提取 JSON 并解析

关键理解:
1. curl $'...' 中的反斜杠会被 shell 解释
2. \\\\n (4 个反斜杠) -> \\n (shell 解释后，表示字面的反斜杠+n)  
3. \\n (JSON 中) -> 表示字面的反斜杠 + n,不是换行符
"""

import json
import re

# 读取 curl 命令
with open('/Users/linziwang/PycharmProjects/wordToWord/test/kafka/es数据.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 es_source_raw 的值 - 注意要匹配到最后一个引号
match = re.search(r'"es_source_raw":"(.+?)","custom_fields":\{\}\}', content, re.DOTALL)
if not match:
    print("❌ 未找到 es_source_raw")
    exit(1)

raw_json = match.group(1)

print("=" * 80)
print(f"原始 JSON 长度：{len(raw_json)}")
print(f"前 100 字符：{repr(raw_json[:100])}")
print("=" * 80)

# 第一步：处理 shell 转义 - 将 \\\\ 转换为 \\
def shell_unescape(text):
    """模拟 bash 对$'...'的转义解释"""
    # 保护 Unicode
    unicode_map = {}
    def save_unicode(m):
        key = f'__U{len(unicode_map)}__'
        unicode_map[key] = m.group(0)
        return key
    text = re.sub(r'\\u[0-9a-fA-F]{4}', save_unicode, text)
    
    # Shell 转义：\\\\X -> \\X
    text = text.replace('\\\\n', '\\n')
    text = text.replace('\\\\r', '\\r') 
    text = text.replace('\\\\t', '\\t')
    text = text.replace('\\\\\\\\', '\\\\')
    text = text.replace('\\\\"', '\\"')
    
    # 恢复 Unicode
    for key, val in unicode_map.items():
        text = text.replace(key, val)
    
    return text

processed = shell_unescape(raw_json)

print(f"\nShell 处理后长度：{len(processed)}")
print(f"前 100 字符：{repr(processed[:100])}")

# 第二步：尝试直接解析
try:
    data = json.loads(processed)
    print("\n✅ 解析成功!")
    
    # 验证关键字段
    if 'SRC_ORG_ALARM_TEXT' in data:
        text = data['SRC_ORG_ALARM_TEXT']
        print(f"\nSRC_ORG_ALARM_TEXT 长度：{len(text)}")
        lines = text.split('\n')
        for i, line in enumerate(lines[:10]):
            if '\\' in line:
                print(f"行{i+1}: {repr(line)}")
                
except Exception as e:
    print(f"\n❌ 解析失败：{e}")
    
    # 定位错误
    error_match = re.search(r'line (\d+) column (\d+)', str(e))
    if error_match:
        line_num = int(error_match.group(1))
        col_num = int(error_match.group(2))
        lines = processed.split('\n')
        if line_num <= len(lines):
            error_line = lines[line_num - 1]
            start = max(0, col_num - 30)
            end = min(len(error_line), col_num + 30)
            print(f"\n错误位置：第{line_num}行第{col_num}列")
            print(f"附近内容：{repr(error_line[start:end])}")
            
            # 检查是否有非法控制字符
            if start < len(error_line):
                char_at_error = error_line[col_num-1] if col_num > 0 else ''
                print(f"错误位置的字符：{repr(char_at_error)} (ASCII: {ord(char_at_error) if char_at_error else 'N/A'})")
