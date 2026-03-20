#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 SRC_ORG_ALARM_TEXT 字段中的非法反斜杠
"""

import subprocess
import re
import json

with open('test/kafka/kafka生成请求CURL.txt', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r"--data-raw \$'(.+?)'$", content, re.DOTALL)
if match:
    raw = match.group(1)
    cmd = ['bash', '-c', f'echo -n ${repr(raw)}']
    result = subprocess.run(cmd, capture_output=True)
    post_data = result.stdout.decode('utf-8')
    request_json = json.loads(post_data)
    es_source = request_json['es_source_raw']
    
    # 查找 SRC_ORG_ALARM_TEXT 字段
    pattern = r'"SRC_ORG_ALARM_TEXT"\s*:\s*"""(.*?)"""'
    match = re.search(pattern, es_source, re.DOTALL)
    if match:
        field_value = match.group(1)
        print('SRC_ORG_ALARM_TEXT 字段值（三重引号内）:')
        print('='*80)
        
        # 查找所有反斜杠及其上下文
        print('\n发现的反斜杠:')
        for i, m in enumerate(re.finditer(r'.{30}\\.{30}', field_value)):
            print(f'{i+1}. {repr(m.group())}')
            
        print('\n' + '='*80)
        print(f'\n字段总长度：{len(field_value)}')
        
        # 特别检查错误位置附近
        error_pos = 4172
        # 找到字段在原始 JSON 中的位置
        field_start = es_source.find('"""', es_source.find('"SRC_ORG_ALARM_TEXT"'))
        if field_start > 0:
            actual_error_in_field = error_pos - field_start
            print(f'\n错误在字段中的位置：{actual_error_in_field}')
            print(f'错误附近内容:')
            start = max(0, actual_error_in_field - 50)
            end = min(len(field_value), actual_error_in_field + 50)
            print(repr(field_value[start:end]))
