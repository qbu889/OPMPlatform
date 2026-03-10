#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/linziwang/PycharmProjects/wordToWord/routes')

from fpa_generator_routes import parse_requirement_document

# 读取真实文档
with open('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/---44500_20250609-_V4.1.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析文档
function_points = parse_requirement_document(content)

print(f"成功解析 {len(function_points)} 个功能点\n")
print("="*80)

for idx, point in enumerate(function_points, 1):
    print(f"\n{idx}. {point.get('level5', '')}")
    print(f"   一级分类：{point.get('level1', '')}")
    print(f"   二级分类：{point.get('level2', '')}")
    print(f"   三级分类：{point.get('level3', '')}")
    print(f"   功能点名称：{point.get('level4', '')}")
    print(f"   功能点计数项：{point.get('level5', '')}")
    print(f"   类别：{point.get('类别', '')}")
    print(f"   UFP: {point.get('UFP', '')}")
    print(f"   重用程度：{point.get('重用程度', '')}")
    print(f"   AFP: {point.get('AFP', '')}")
