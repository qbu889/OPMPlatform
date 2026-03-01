#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试JSON解析问题
"""

import json
import re

# 提取有问题的部分数据
problematic_data = '''
{
    "SRC_ORG_ALARM_TEXT": """{"alarmSeq":8246971,"alarmTitle":"CELL FAULTY","alarmStatus":1,"alarmType":"QUALITYOFSERVICE","origSeverity":1,"eventTime":"2026-02-06 18: 24: 42","alarmId":"4155657","specificProblemID":"7653","specificProblem":"CELL FAULTY","neUID":"3502NSWXCENB00013FD99","neName":"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS","neType":"ENB","objectUID":"3502NSWXCCEL0000045859400131","objectName":"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131","objectType":"EutranCellTdd","locationInfo":"PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131","addInfo":"DIAGNOSTIC_INFO: 10 unitName=FZFF path=/SMOD_R-1/rfext3_10g/RMOD_R-2 serial_no=10QYX10DA003175 additionalFaultID=3030;SUPPLEMENTARY_INFO:Failure in optical interface;USER_ADDITIONAL_INFO:;DN:PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131;deployment:LTE","rNeUID":"3502NSWXCRRU0001740A4","rNeName":"RMOD_R-2","rNeType":"RRU-LTE"}""",
    "OTHER_FIELD": "normal_value"
}
'''

print("原始数据:")
print(problematic_data)
print("\n" + "="*50)

# 尝试直接解析会失败
try:
    json.loads(problematic_data)
    print("✅ 直接解析成功")
except json.JSONDecodeError as e:
    print(f"❌ 直接解析失败: {e}")

print("\n尝试预处理...")

# 使用现有的预处理函数
def preprocess_json_data(raw_data):
    """预处理JSON数据，修复常见格式问题"""
    print("开始预处理JSON数据...")
    
    # 1. 移除BOM标记
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        print("移除BOM标记")
    
    # 2. 处理三重引号和字符串内引号
    triple_quote_count = raw_data.count('"""')
    if triple_quote_count > 0:
        raw_data = raw_data.replace('"""', '"')
        print(f"处理了 {triple_quote_count} 个三重引号")
    
    # 处理字符串内的引号转义
    def escape_string_quotes(match):
        content = match.group(1)
        # 转义字符串内的双引号
        content = content.replace('"', '\\"')
        # 转义换行符和制表符
        content = content.replace('\n', '\\n')
        content = content.replace('\t', '\\t')
        # 修复无效转义
        content = re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\1', content)
        return f'"{content}"'
    
    raw_data = re.sub(r'"(.*?)"', escape_string_quotes, raw_data, flags=re.DOTALL)
    
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
        count = raw_data.count(entity)
        if count > 0:
            raw_data = raw_data.replace(entity, replacement)
            print(f"处理了 {count} 个 '{entity}' HTML实体")
    
    # 4. 处理控制字符
    control_chars_removed = 0
    cleaned_data = ''
    problematic_positions = []
    
    for i, char in enumerate(raw_data):
        char_code = ord(char)
        # 允许: 制表符(9), 换行符(10), 回车符(13), 空格及以上(32+)
        if char_code == 9 or char_code == 10 or char_code == 13 or char_code >= 32:
            cleaned_data += char
        else:
            control_chars_removed += 1
            if control_chars_removed <= 20:
                problematic_positions.append((i, char_code, repr(char)))
            
    if control_chars_removed > 0:
        print(f"总共移除了 {control_chars_removed} 个控制字符")
        if problematic_positions:
            print("前20个控制字符位置:")
            for pos, code, char_repr in problematic_positions:
                print(f"  位置{pos}: ASCII码{code}, 字符{char_repr}")
        raw_data = cleaned_data
    
    # 5. 处理尾随逗号
    trailing_commas = len(re.findall(r',\s*([\}\]])', raw_data))
    if trailing_commas > 0:
        raw_data = re.sub(r',\s*([\}\]])', r'\1', raw_data)
        print(f"处理了 {trailing_commas} 个尾随逗号")
    
    # 6. 标准化换行符
    raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')
    
    # 7. 移除行尾空格
    lines = raw_data.split('\n')
    raw_data = '\n'.join(line.rstrip() for line in lines)
    
    # 8. 修复JSON键名未加引号的问题
    def fix_json_keys(raw_data):
        import re
        pattern = r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:'
        
        def add_quotes(match):
            prefix = match.group(1)
            key = match.group(2)
            return f'{prefix}"{key}":'
        
        fixed_data = re.sub(pattern, add_quotes, raw_data)
        return fixed_data
    
    raw_data = fix_json_keys(raw_data)
    
    print("预处理完成")
    return raw_data

# 应用预处理
processed_data = preprocess_json_data(problematic_data)

print("\n预处理后的数据:")
print(processed_data)
print("\n" + "="*50)

# 再次尝试解析
try:
    result = json.loads(processed_data)
    print("✅ 预处理后解析成功!")
    print("解析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
except json.JSONDecodeError as e:
    print(f"❌ 预处理后仍然解析失败: {e}")
    # 显示错误附近的上下文
    error_pos_match = re.search(r'line (\d+) column (\d+)', str(e))
    if error_pos_match:
        line_num = int(error_pos_match.group(1))
        col_num = int(error_pos_match.group(2))
        lines = processed_data.split('\n')
        if line_num <= len(lines):
            error_line = lines[line_num - 1]
            context_start = max(0, col_num - 20)
            context_end = min(len(error_line), col_num + 20)
            context = error_line[context_start:context_end]
            print(f"错误位置: 第{line_num}行, 第{col_num}列")
            print(f"错误行内容: {error_line}")
            print(f"错误附近上下文: '{context}'")