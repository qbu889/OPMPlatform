#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试重用程度默认值修改
"""
from routes.fpa_generator_routes import parse_requirement_document
from pathlib import Path

# 读取测试文件
md_file = Path('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/事件处理类工单流程应用场景.md')
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# 解析文档
function_points = parse_requirement_document(md_content)

print(f"提取到 {len(function_points)} 个功能点\n")

# 统计重用程度分布
high_reuse = []
mid_reuse = []

for point in function_points:
    item = point['level5']
    reuse = point['重用程度']
    category = point['类别']
    
    if reuse == '高':
        high_reuse.append((item, category))
    else:
        mid_reuse.append((item, category))

print(f"重用程度为'高'的功能点：{len(high_reuse)} 个")
print(f"重用程度为'中'的功能点：{len(mid_reuse)} 个\n")

print("=== 重用程度为'中'的功能点 ===")
for item, category in mid_reuse:
    print(f"{category}: {item}")

print("\n=== 前 20 个功能点详情 ===")
for i, point in enumerate(function_points[:20], 1):
    print(f"{i}. {point['level5']}")
    print(f"   类别：{point['类别']}, 重用程度：{point['重用程度']}, UFP: {point['UFP']}, AFP: {point['AFP']}")
