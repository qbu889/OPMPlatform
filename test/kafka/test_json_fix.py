#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试JSON预处理修复效果
"""

import json
import re

def preprocess_json_for_js(data):
    """模拟前端JavaScript的预处理逻辑"""
    print("开始预处理...")
    
    # 1. 处理三重引号和多行字符串
    triple_quote_matches = re.findall(r'"""([\\s\\S]*?)"""', data)
    if triple_quote_matches:
        print(f"发现 {len(triple_quote_matches)} 个三重引号块")
        def replace_triple_quotes(match):
            content = match.group(1)
            # 转义特殊字符
            escaped_content = (content
                .replace('\\\\', '\\\\\\\\')  # 转义反斜杠
                .replace('"', '\\\\"')       # 转义引号
                .replace('\\n', '\\\\n')     # 转义换行符
                .replace('\\r', '\\\\r')     # 转义回车符
                .replace('\\t', '\\\\t'))    # 转义制表符
            return '"' + escaped_content + '"'
        
        data = re.sub(r'"""([\\s\\S]*?)"""', replace_triple_quotes, data)
    
    # 2. 处理控制字符（排除正常的换行、回车、制表符）
    control_chars = re.findall(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', data)
    if control_chars:
        print(f"发现 {len(control_chars)} 个控制字符")
        data = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F]', '', data)
    
    print("预处理完成")
    return data

# 测试数据
test_json = '''
{
  "test_field": """
这是多行文本
包含换行符
和"引号"
""",
  "normal_field": "正常字段",
  "another_multiline": """
另一段
多行文本
"""
}
'''

print("原始数据:")
print(test_json)
print("\n" + "="*50 + "\n")

try:
    # 尝试直接解析
    result = json.loads(test_json)
    print("✓ 直接解析成功")
except json.JSONDecodeError as e:
    print(f"✗ 直接解析失败: {e}")
    
    # 预处理后尝试解析
    print("\n进行预处理...")
    processed = preprocess_json_for_js(test_json)
    print("\n预处理后数据:")
    print(processed)
    
    try:
        result = json.loads(processed)
        print("\n✓ 预处理后解析成功!")
        print("解析结果:", json.dumps(result, ensure_ascii=False, indent=2))
    except json.JSONDecodeError as e2:
        print(f"\n✗ 预处理后仍然失败: {e2}")