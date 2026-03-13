#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 FPA 生成的功能点顺序和类别是否与预期一致
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from routes.fpa_generator_routes import parse_requirement_document

# 读取 Markdown 文档
md_file = Path('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/事件处理类工单流程应用场景.md')
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# 解析文档
function_points = parse_requirement_document(md_content)

# 读取预期顺序文件
order_file = Path('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/期望表格的顺序.txt')
expected_data = []
with open(order_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines[1:]:  # 跳过标题行
        parts = line.strip().split('\t')
        if len(parts) >= 2 and parts[0] != '必填':
            expected_data.append({
                '功能点计数项': parts[0].strip(),
                '类别': parts[1].strip(),
                'UFP': parts[2].strip() if len(parts) > 2 else ''
            })

print("=" * 100)
print(f"解析到 {len(function_points)} 个功能点")
print(f"期望有 {len(expected_data)} 个功能点")
print("=" * 100)

# 提取解析到的功能点名称列表
parsed_names = [p.get('功能点计数项', '').strip() for p in function_points]
expected_names = [e['功能点计数项'] for e in expected_data]

# 比对
matched = 0
unmatched_parsed = []
unmatched_expected = []
category_mismatch = []

print("\n详细比对结果:")
print("-" * 100)

for i, name in enumerate(parsed_names, 1):
    if name in expected_names:
        matched += 1
        exp_idx = expected_names.index(name)
        actual_cat = next((p.get('类别', '') for p in function_points if p.get('功能点计数项', '') == name), '')
        exp_cat = next((e['类别'] for e in expected_data if e['功能点计数项'] == name), '')
        
        if actual_cat != exp_cat:
            category_mismatch.append({
                'name': name,
                'actual': actual_cat,
                'expected': exp_cat
            })
            print(f"[{i}/{len(parsed_names)}] ✓ {name}")
            print(f"    类别不匹配！实际：{actual_cat}, 期望：{exp_cat}")
        else:
            print(f"[{i}/{len(parsed_names)}] ✓ {name} - 匹配 (位置：{exp_idx+1}, 类别：{actual_cat})")
    else:
        unmatched_parsed.append(name)
        print(f"[{i}/{len(parsed_names)}] ✗ {name} - 未在期望列表中找到!")

# 检查缺失的功能点
for name in expected_names:
    if name not in parsed_names:
        unmatched_expected.append(name)
        print(f"✗ 期望但缺失：{name}")

# 统计汇总
print("\n" + "=" * 100)
print("统计汇总:")
print("=" * 100)
print(f"成功匹配：{matched}/{len(parsed_names)} ({matched/len(parsed_names)*100:.1f}%)")
print(f"解析但未期望：{len(unmatched_parsed)} 个")
print(f"期望但未解析：{len(unmatched_expected)} 个")
print(f"类别不匹配：{len(category_mismatch)} 个")

if unmatched_parsed:
    print(f"\n解析但未在期望列表中的功能点 ({len(unmatched_parsed)}个):")
    for name in unmatched_parsed:
        print(f"  - {name}")

if unmatched_expected:
    print(f"\n期望但未解析到的功能点 ({len(unmatched_expected)}个):")
    for name in unmatched_expected:
        print(f"  - {name}")

if category_mismatch:
    print(f"\n类别不匹配的功能点 ({len(category_mismatch)}个):")
    for m in category_mismatch:
        print(f"  - {m['name']}: 实际={m['actual']}, 期望={m['expected']}")

# 显示前 20 个功能点的完整信息
print("\n" + "=" * 100)
print("前 20 个功能点详细信息:")
print("=" * 100)
for i, point in enumerate(function_points[:20], 1):
    name = point.get('功能点计数项', '')
    category = point.get('类别', '')
    ufp = point.get('UFP', '')
    reuse = point.get('重用程度', '')
    afp = point.get('AFP', '')
    print(f"{i}. {name}")
    print(f"   类别：{category}, UFP: {ufp}, 重用程度：{reuse}, AFP: {afp}")

print("\n" + "=" * 100)
print("验证完成!")
print("=" * 100)
