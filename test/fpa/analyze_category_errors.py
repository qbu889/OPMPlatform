#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析类别判断错误
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from routes.fpa_generator_routes import parse_requirement_document

# 读取 Markdown 文档并解析
md_file = Path('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/事件处理类工单流程应用场景.md')
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

function_points = parse_requirement_document(md_content)

# 构建实际类别字典
actual = {}
for point in function_points:
    name = point.get('功能点计数项', '').strip()
    category = point.get('类别', '')
    if name and category:
        actual[name] = category

# 读取期望文件
expected = {}
with open('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/期望表格的顺序.txt', 'r', encoding='utf-8') as f:
    for line in f.readlines()[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= 2 and parts[0] != '必填':
            expected[parts[0]] = parts[1]

# 找出不匹配的
mismatches = []
for name in expected:
    if name in actual:
        exp_cat = expected[name]
        act_cat = actual[name]
        if exp_cat != act_cat:
            mismatches.append({
                'name': name,
                'expected': exp_cat,
                'actual': act_cat
            })

print(f'总共有 {len(mismatches)} 个类别不匹配\n')
print('=' * 100)

# 按错误类型分组统计
ei_to_eo = [m for m in mismatches if m['expected'] == 'EI' and m['actual'] == 'EO']
eo_to_ei = [m for m in mismatches if m['expected'] == 'EO' and m['actual'] == 'EI']
eq_errors = [m for m in mismatches if m['expected'] == 'EQ']
other_errors = [m for m in mismatches if m not in ei_to_eo + eo_to_ei + eq_errors]

print(f'\n应该是 EI 但判断成 EO 的 ({len(ei_to_eo)}个):')
for m in ei_to_eo:
    print(f'  - {m["name"]}')

print(f'\n应该是 EO 但判断成 EI 的 ({len(eo_to_ei)}个):')
for m in eo_to_ei:
    print(f'  - {m["name"]}')

print(f'\n应该是 EQ 但判断错的 ({len(eq_errors)}个):')
for m in eq_errors:
    print(f'  - {m["name"]} (期望：{m["expected"]}, 实际：{m["actual"]})')

if other_errors:
    print(f'\n其他错误 ({len(other_errors)}个):')
    for m in other_errors:
        print(f'  - {m["name"]} (期望：{m["expected"]}, 实际：{m["actual"]})')
