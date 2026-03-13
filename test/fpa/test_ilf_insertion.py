#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 ILF 表的提取和插入
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

print("=" * 100)
print(f"总共生成 {len(function_points)} 个功能点")
print("=" * 100)

# 找出所有 ILF 表
ilf_points = [p for p in function_points if p.get('类别') == 'ILF']
print(f"\nILF 表数量：{len(ilf_points)}")
print("\nILF 表列表:")
for i, point in enumerate(ilf_points, 1):
    name = point.get('功能点计数项', '')
    print(f"{i}. {name}")

# 检查期望的 3 个表是否存在
expected_missing = [
    '工单管控时段规则基本信息配置表',
    '工单管剔除规则条件表',
    '规则状态变更历史记录表'
]

print("\n" + "=" * 100)
print("检查期望的 3 个表:")
print("=" * 100)
for table in expected_missing:
    found = any(p.get('功能点计数项', '') == table for p in function_points)
    status = "✓ 存在" if found else "✗ 缺失"
    print(f"{status}: {table}")

# 显示前 30 个功能点的顺序
print("\n" + "=" * 100)
print("前 30 个功能点顺序:")
print("=" * 100)
for i, point in enumerate(function_points[:30], 1):
    name = point.get('功能点计数项', '')
    category = point.get('类别', '')
    print(f"{i}. {name} ({category})")
