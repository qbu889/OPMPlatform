#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试非法转义字符修复"""

import json
import re

# 测试数据（模拟问题数据）
test_data = '{"test": "RRU 上次重启原因\\:POWERON, 光口 1\\:未接收到光信号"}'

print('原始数据:', test_data)
print('原始数据长度:', len(test_data))

# 修复非法转义
def fix_invalid_escapes(text):
    def replace_invalid_escape(match):
        full_match = match.group(0)
        char_after_backslash = match.group(1)
        # 合法的转义字符
        valid_escapes = {'\\': '\\', '"': '"', '/': '/', 'b': '\b', 
                       'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
        if char_after_backslash in valid_escapes:
            return full_match
        # 非法转义：在反斜杠前再加一个反斜杠
        return '\\\\' + char_after_backslash
    
    pattern = r'\\(["\\/bfnrt]|u[0-9a-fA-F]{4}|.)'
    return re.sub(pattern, replace_invalid_escape, text)

fixed_data = fix_invalid_escapes(test_data)
print('修复后:', fixed_data)
print('修复后长度:', len(fixed_data))

try:
    result = json.loads(fixed_data)
    print('✅ JSON 解析成功:', result)
except Exception as e:
    print('❌ JSON 解析失败:', e)

# 测试原始的错误数据
print('\n' + '='*80)
print('测试真实数据片段:')
real_fragment = 'Remark:RRU 上次重启原因\\:POWERON, 光口 1 对应的上联光口\\:未接收到光信号'
print('原始:', real_fragment)

fixed_fragment = fix_invalid_escapes(real_fragment)
print('修复后:', fixed_fragment)
