#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试修复 JSON 数据中的转义问题"""

import json
import re

# 读取文件
with open('/Users/linziwang/PycharmProjects/wordToWord/test/kafka/es数据.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 JSON 部分
match = re.search(r'"es_source_raw":"(.+?)","custom_fields"', content, re.DOTALL)
if not match:
    print("未找到 es_source_raw")
    exit(1)

json_str = match.group(1)

print("=" * 80)
print("原始 JSON 长度:", len(json_str))
print("=" * 80)

# 查找 ProbableCauseTxt 附近的内容
pos = json_str.find('ProbableCauseTxt')
if pos > 0:
    print("\nProbableCauseTxt 附近内容:")
    print(repr(json_str[pos-20:pos+300]))
    print()

# 尝试直接解析
try:
    data = json.loads(json_str)
    print("✅ 直接解析成功!")
except Exception as e:
    print(f"❌ 直接解析失败：{e}")
    print(f"错误类型：{type(e).__name__}")

print("\n" + "=" * 80)
print("开始修复...")
print("=" * 80)

# 修复策略：处理字符串值内部的非法转义
def fix_json_escapes(text):
    """修复 JSON 字符串中的转义问题"""
    
    print("\n【fix_json_escapes】开始处理...")
    
    # 【关键】第一步：处理多个连续反斜杠后跟 Unicode 的情况
    # 将 \\\\uXXXX（四个反斜杠）转换为 \\uXXXX（两个反斜杠 + Unicode）
    count_before = len(re.findall(r'\\\\+', text))
    text = re.sub(r'\\{4,}(?=u[0-9a-fA-F]{4})', r'\\', text)
    count_after = len(re.findall(r'\\\\+', text))
    print(f"四重反斜杠 + Unicode: {count_before} -> {count_after}")
    
    # 第二步：保护所有合法的 \uXXXX
    def protect_unicode(match):
        return f'__UNICODE_{match.group(0)[1:]}__'
    
    text = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, text)
    
    # 第三步：现在所有的 \\ 都应该是字面意思的反斜杠，需要转义
    # 将单个反斜杠替换为双反斜杠
    text = text.replace('\\', '\\\\')
    
    # 第四步：恢复 Unicode
    def restore_unicode(match):
        return match.group(0).replace('__UNICODE_', '\\').replace('__', '')
    
    text = re.sub(r'__UNICODE_[0-9a-fA-F]{4}__', restore_unicode, text)
    
    print("【fix_json_escapes】完成")
    return text

# 应用修复
fixed_json = fix_json_escapes(json_str)

print("\n修复后 JSON 长度:", len(fixed_json))

# 再次尝试解析
try:
    data = json.loads(fixed_json)
    print("✅ 修复后解析成功!")
    
    # 检查 SRC_ORG_ALARM_TEXT 字段
    if 'SRC_ORG_ALARM_TEXT' in data:
        alarm_text = data['SRC_ORG_ALARM_TEXT']
        print(f"\nSRC_ORG_ALARM_TEXT 长度：{len(alarm_text)}")
        
        # 查找包含反斜杠的行
        lines = alarm_text.split('\n')
        for i, line in enumerate(lines):
            if '\\' in line and ('中兴' in line or 'ProbableCauseTxt' in line):
                print(f"第{i+1}行：{repr(line)}")
                
except Exception as e:
    print(f"❌ 修复后仍然失败：{e}")
    error_match = re.search(r'line (\d+) column (\d+)', str(e))
    if error_match:
        line_num = int(error_match.group(1))
        col_num = int(error_match.group(2))
        lines = fixed_json.split('\n')
        if line_num <= len(lines):
            error_line = lines[line_num - 1]
            context_start = max(0, col_num - 50)
            context_end = min(len(error_line), col_num + 50)
            context = error_line[context_start:context_end]
            print(f"\n错误位置：第{line_num}行第{col_num}列")
            print(f"附近内容：{repr(context)}")
