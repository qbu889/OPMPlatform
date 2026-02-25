#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON键名修复工具
专门修复缺少双引号包围的属性名问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import re

def fix_unquoted_keys(json_str):
    """修复未加引号的JSON键名"""
    print("开始修复未加引号的键名...")
    
    # 匹配未加引号的键名模式：键名后跟冒号
    # 支持字母、数字、下划线、中文等字符作为键名
    pattern = r'([{,]\s*)([a-zA-Z_\u4e00-\u9fff][a-zA-Z0-9_\u4e00-\u9fff]*)\s*:'
    
    def add_quotes(match):
        prefix = match.group(1)  # 前导字符（{ 或 ,）
        key = match.group(2)     # 键名
        return f'{prefix}"{key}":'
    
    # 应用修复
    fixed_json = re.sub(pattern, add_quotes, json_str)
    
    # 统计修复数量
    original_matches = len(re.findall(pattern, json_str))
    fixed_matches = len(re.findall(pattern, fixed_json))
    
    print(f"修复了 {original_matches} 个未加引号的键名")
    
    return fixed_json

def comprehensive_json_fix(raw_data):
    """综合JSON修复函数"""
    print("=== 综合JSON修复开始 ===")
    print(f"原始数据长度: {len(raw_data)}")
    
    # 1. 基础预处理
    # 移除BOM
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        print("移除BOM标记")
    
    # 处理三重引号
    triple_count = raw_data.count('"""')
    if triple_count > 0:
        raw_data = raw_data.replace('"""', '"')
        print(f"处理了 {triple_count} 个三重引号")
    
    # 处理字符串内的引号转义
    def escape_inner_quotes(match):
        content = match.group(1)
        # 转义字符串内的双引号
        content = content.replace('"', '\\"')
        # 转义换行符和制表符
        content = content.replace('\n', '\\n')
        content = content.replace('\t', '\\t')
        # 修复无效转义
        content = re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\1', content)
        return f'"{content}"'
    
    raw_data = re.sub(r'"(.*?)"', escape_inner_quotes, raw_data, flags=re.DOTALL)
    
    # 处理HTML实体
    html_entities = {
        '&lt;': '<', '&gt;': '>', '&amp;': '&', 
        '&quot;': '"', '&#39;': "'", '&nbsp;': ' '
    }
    
    for entity, replacement in html_entities.items():
        count = raw_data.count(entity)
        if count > 0:
            raw_data = raw_data.replace(entity, replacement)
            print(f"处理了 {count} 个 '{entity}'")
    
    # 2. 修复未加引号的键名
    raw_data = fix_unquoted_keys(raw_data)
    
    # 3. 处理字符串内的特殊字符（跳过，已在前面处理）
    
    # 4. 清理控制字符
    cleaned = ''
    control_removed = 0
    for char in raw_data:
        char_code = ord(char)
        if char_code == 9 or char_code == 10 or char_code == 13 or char_code >= 32:
            cleaned += char
        else:
            control_removed += 1
    
    if control_removed > 0:
        print(f"移除了 {control_removed} 个控制字符")
        raw_data = cleaned
    
    # 5. 标准化格式
    raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')
    lines = raw_data.split('\n')
    raw_data = '\n'.join(line.rstrip() for line in lines)
    
    # 6. 结构完整性检查
    # 确保只有一个顶层对象
    brace_count = 0
    last_complete_pos = -1
    
    for i, char in enumerate(raw_data):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                last_complete_pos = i
                break
    
    if last_complete_pos != -1 and last_complete_pos < len(raw_data) - 1:
        extra = raw_data[last_complete_pos + 1:].strip()
        if extra:
            print(f"截取多余内容: {repr(extra[:30])}")
            raw_data = raw_data[:last_complete_pos + 1]
    
    print(f"修复后数据长度: {len(raw_data)}")
    print("=== 综合修复完成 ===")
    
    return raw_data

# 测试函数
def test_fix_on_samples():
    """测试修复函数"""
    from test_json_processing import test_samples
    
    print("开始测试综合修复功能")
    print(f"测试样本数量: {len(test_samples)}")
    
    results = []
    
    for name, original_data in test_samples:
        print(f"\n{'='*50}")
        print(f"测试: {name}")
        print(f"{'='*50}")
        
        try:
            # 应用综合修复
            fixed_data = comprehensive_json_fix(original_data)
            
            # 尝试解析
            parsed = json.loads(fixed_data)
            print("✅ 修复成功，JSON解析通过!")
            print(f"解析字段数: {len(parsed)}")
            results.append((name, True, len(original_data), len(fixed_data)))
            
        except Exception as e:
            print(f"❌ 修复失败: {e}")
            # 显示详细错误信息
            error_msg = str(e)
            if "column" in error_msg:
                import re
                match = re.search(r"line (\d+) column (\d+)", error_msg)
                if match:
                    line_num = int(match.group(1))
                    col_num = int(match.group(2))
                    lines = fixed_data.split('\n')
                    if line_num <= len(lines):
                        error_line = lines[line_num - 1]
                        print(f"错误位置: 第{line_num}行，第{col_num}列")
                        print(f"错误行内容: {repr(error_line)}")
            results.append((name, False, len(original_data), len(fixed_data) if 'fixed_data' in locals() else 0))
    
    # 输出汇总
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    
    success_count = sum(1 for _, success, _, _ in results if success)
    print(f"总样本数: {len(results)}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {len(results) - success_count}")
    print(f"成功率: {success_count/len(results)*100:.1f}%")
    
    print("\n详细结果:")
    for name, success, orig_len, fixed_len in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {name}: {status} (原始:{orig_len}, 修复后:{fixed_len})")

if __name__ == "__main__":
    test_fix_on_samples()