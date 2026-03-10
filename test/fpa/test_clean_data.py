#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/linziwang/PycharmProjects/wordToWord/routes')

from fpa_generator_routes import parse_requirement_document, generate_fpa_excel
import pandas as pd
import os

# 读取真实文档
with open('/Users/linziwang/PycharmProjects/wordToWord/test/fpa/---44500_20250609-_V4.1.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 解析文档
function_points = parse_requirement_document(content)
print(f"成功解析 {len(function_points)} 个功能点")

# 生成 Excel
output_path = '/Users/linziwang/PycharmProjects/wordToWord/tmp/test_clean_fpa.xlsx'
generate_fpa_excel(function_points, output_path)

print(f"\n✓ Excel 生成成功：{output_path}")
print(f"✓ 文件大小：{os.path.getsize(output_path)} bytes")

# 验证数据
print("\n验证 Excel 数据 (前 3 行):")
df = pd.read_excel(output_path, sheet_name='1.规模估算表', header=None)
for idx in range(10, 13):
    row = df.iloc[idx].tolist()
    print(f"行{idx+1}:")
    print(f"  B 列 (一级分类): {row[1]}")
    print(f"  C 列 (二级分类): {row[2]}")
    print(f"  D 列 (三级分类): {row[3]}")
    print(f"  E 列 (功能点名称): {row[4]}")
    print(f"  F 列 (功能点计数项): {row[5]}")
