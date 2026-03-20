#!/usr/bin/env python3
"""测试 fix_json_keys 函数"""

import re

def fix_json_keys_old(data):
    """旧版本 - 会给已有引号的键再加引号"""
    pattern = r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:'
    
    def add_quotes(match):
        prefix = match.group(1)
        key = match.group(2)
        return f'{prefix}"{key}":'
    
    return re.sub(pattern, add_quotes, data)


def fix_json_keys_new(data):
    """新版本 - 只给没有引号的键加引号"""
    # 先保护字符串
    string_placeholders = {}
    counter = [0]
    
    def save_string(match):
        key = f'__STR_{counter[0]}__'
        string_placeholders[key] = match.group(0)
        counter[0] += 1
        return key
    
    data = re.sub(r'"(?:[^"\\]|\\.)*"', save_string, data)
    
    # 处理键名 - 使用负向前瞻检查是否后面有引号
    pattern = r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)(?!")\s*:'
    
    def add_quotes(match):
        prefix = match.group(1)
        key = match.group(2)
        print(f"发现未加引号的键：{key}")
        return f'{prefix}"{key}":'
    
    data = re.sub(pattern, add_quotes, data)
    
    # 恢复字符串
    for i in range(len(string_placeholders) - 1, -1, -1):
        key = f'__STR_{i}__'
        if key in string_placeholders:
            data = data.replace(key, string_placeholders[key])
    
    return data


# 测试数据
test_data = '''
{
    "HOME_BROAD_BAND_LIST" : [ ],
    UNQUOTED_KEY : "value",
    "NE_LOCATION" : "QZ...PORT 5,6, Paras:机框=0"
}
'''

print("=== 原始数据 ===")
print(test_data)

print("\n=== 旧版本处理结果 ===")
result_old = fix_json_keys_old(test_data)
print(result_old)

print("\n=== 新版本处理结果 ===")
result_new = fix_json_keys_new(test_data)
print(result_new)
