#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('test/kafka/预计输出.json', 'r', encoding='utf-8') as f:
    expected = json.load(f)

with open('test/kafka/实际输出.json', 'r', encoding='utf-8') as f:
    actual = json.load(f)

print('=== 字段类型对比（期望 vs 实际）===\n')
differences = []

for key in expected.keys():
    if key in actual:
        exp_type = type(expected[key]).__name__
        act_type = type(actual[key]).__name__
        exp_val = expected[key]
        act_val = actual[key]
        
        if exp_type != act_type:
            differences.append(key)
            print(f'✗ {key}:')
            print(f'  期望: {exp_type} = {repr(exp_val)}')
            print(f'  实际: {act_type} = {repr(act_val)}')
            print()

print(f'\n共发现 {len(differences)} 个类型差异')
print('\n需要调整为int的字段:')
for key in differences:
    if type(expected[key]).__name__ == 'int':
        print(f'  - {key}')
