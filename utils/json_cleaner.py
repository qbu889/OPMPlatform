#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON数据清理工具
专门处理ES数据中的各种格式问题
"""

import json
import re
from datetime import datetime

def clean_json_data(raw_data):
    """
    清理JSON数据中的各种问题
    """
    print("开始清理JSON数据...")
    
    # 1. 移除BOM标记
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        print("✓ 移除了BOM标记")
    
    # 2. 处理三重引号
    triple_quote_count = raw_data.count('"""')
    if triple_quote_count > 0:
        raw_data = raw_data.replace('"""', '"')
        print(f"✓ 处理了 {triple_quote_count} 个三重引号")
    
    # 3. 处理HTML实体
    html_entities = {
        '&quot;': '"',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&nbsp;': ' ',
        '&#39;': "'"
    }
    
    for entity, replacement in html_entities.items():
        count = raw_data.count(entity)
        if count > 0:
            raw_data = raw_data.replace(entity, replacement)
            print(f"✓ 处理了 {count} 个 '{entity}' HTML实体")
    
    # 4. 处理控制字符（这是主要问题）
    control_chars_found = []
    # 找到所有控制字符的位置
    for i, char in enumerate(raw_data):
        if ord(char) < 32 and char not in ['\n', '\r', '\t']:
            control_chars_found.append((i, ord(char), repr(char)))
    
    if control_chars_found:
        print(f"发现 {len(control_chars_found)} 个控制字符:")
        for pos, code, rep in control_chars_found[:10]:  # 只显示前10个
            print(f"  位置 {pos}: ASCII {code} {rep}")
        
        # 移除所有控制字符
        cleaned_data = ''.join(char for char in raw_data if ord(char) >= 32 or char in '\n\r\t')
        print(f"✓ 移除了所有控制字符")
        raw_data = cleaned_data
    
    # 5. 处理多余的转义字符
    escape_patterns = [
        (r'\\"', '"'),  # 双重转义引号
        (r'\\\\', '\\'),  # 双重反斜杠
    ]
    
    for pattern, replacement in escape_patterns:
        count = len(re.findall(pattern, raw_data))
        if count > 0:
            raw_data = re.sub(pattern, replacement, raw_data)
            print(f"✓ 处理了 {count} 个 '{pattern}' 转义模式")
    
    # 6. 标准化换行符
    raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')
    
    # 7. 移除行尾空格
    lines = raw_data.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    raw_data = '\n'.join(cleaned_lines)
    
    print("✓ 完成了所有清理步骤")
    return raw_data

def validate_json(json_string):
    """
    验证JSON格式并返回详细错误信息
    """
    try:
        parsed = json.loads(json_string)
        print("✓ JSON格式验证通过")
        return True, parsed, None
    except json.JSONDecodeError as e:
        error_info = {
            'message': str(e),
            'position': e.pos,
            'lineno': e.lineno,
            'colno': e.colno
        }
        
        # 显示错误位置附近的文本
        start_pos = max(0, e.pos - 50)
        end_pos = min(len(json_string), e.pos + 50)
        context = json_string[start_pos:end_pos]
        
        print(f"✗ JSON解析错误:")
        print(f"  错误信息: {e}")
        print(f"  位置: 第{e.lineno}行第{e.colno}列 (总位置:{e.pos})")
        print(f"  上下文: ...{repr(context)}...")
        
        return False, None, error_info

def analyze_problem_area(json_string, lineno, colno):
    """
    分析问题区域的详细信息
    """
    lines = json_string.split('\n')
    if lineno <= len(lines):
        problem_line = lines[lineno - 1]
        print(f"\n问题行分析 (第{lineno}行):")
        print(f"内容: {repr(problem_line)}")
        print(f"长度: {len(problem_line)} 字符")
        
        # 显示指定列附近的内容
        start_col = max(0, colno - 10)
        end_col = min(len(problem_line), colno + 10)
        context = problem_line[start_col:end_col]
        
        print(f"问题位置附近: ...{repr(context)}...")
        print(f"问题字符: {repr(problem_line[colno-1:colno])}")

def main():
    """
    主函数 - 可以直接运行此脚本来测试数据清理
    """
    print("=== JSON数据清理工具 ===\n")
    
    # 这里可以放入您的测试数据
    test_data = '''{
    "took": 5,
    "timed_out": false,
    "_shards": {
        "total": 5,
        "successful": 5,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 1.0,
        "hits": [
            {
                "_index": "test_index",
                "_type": "_doc",
                "_id": "1",
                "_score": 1.0,
                "_source": {
                    "name": "测试数据",
                    "description": "包含特殊字符的数据"""
                }
            }
        ]
    }
}'''
    
    print("原始数据长度:", len(test_data))
    print("原始数据预览:", repr(test_data[:100]))
    
    # 清理数据
    cleaned_data = clean_json_data(test_data)
    
    # 验证清理后的数据
    is_valid, parsed_data, error_info = validate_json(cleaned_data)
    
    if is_valid:
        print("\n✓ 数据清理成功！")
        print("清理后数据长度:", len(cleaned_data))
        # 可以在这里保存清理后的数据
        # with open('cleaned_data.json', 'w', encoding='utf-8') as f:
        #     json.dump(parsed_data, f, ensure_ascii=False, indent=2)
    else:
        print("\n✗ 清理后仍然存在问题:")
        print("错误详情:", error_info)

if __name__ == "__main__":
    main()