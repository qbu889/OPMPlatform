#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 FPA 生成器修复效果"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path('/Users/linziwang/PycharmProjects/wordToWord')
sys.path.insert(0, str(project_root))

from routes.fpa_generator_routes import parse_requirement_document, generate_fpa_excel
import time

# 读取需求文档
md_file = project_root / 'uploads/fpa_input/事件处理类工单流程应用场景_1773114332336.md'
content = md_file.read_text(encoding='utf-8')

print("=" * 80)
print("解析需求文档")
print("=" * 80)

# 解析文档
function_points = parse_requirement_document(content)

print(f"\n提取功能点数量：{len(function_points)}")

print("\n前 15 个功能点类别:")
for i, point in enumerate(function_points[:15], 1):
    print(f"{i}. [{point['类别']}] {point['功能点计数项'][:50]}")

# 统计各类别数量
from collections import Counter
category_count = Counter([p['类别'] for p in function_points])
print("\n类别统计:")
for cat, count in sorted(category_count.items()):
    print(f"  {cat}: {count}个")

# 生成 Excel 文件
print("\n" + "=" * 80)
print("生成 FPA Excel 文件")
print("=" * 80)

timestamp = int(time.time() * 1000)
output_dir = project_root / 'uploads/fpa_output'
output_dir.mkdir(exist_ok=True)
output_file = output_dir / f"事件处理类工单流程应用场景_FPA预估_测试_{timestamp}.xlsx"

generate_fpa_excel(function_points, str(output_file))

print(f"\n✓ Excel 文件生成成功：{output_file.name}")
print(f"\n请打开文件查看结果并对比预期文件")
