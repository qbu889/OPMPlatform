#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openpyxl
import os

# 查找文件
target_dir = 'test/fpa/'
files = [f for f in os.listdir(target_dir) if f.endswith('.xlsx') and '评审版本' in f]

excel_file = target_dir + files[0]
print(f"读取文件：{excel_file}")
print()

# 读取 Excel
wb = openpyxl.load_workbook(excel_file)

# 重点查看"2. 规模估算"表
ws = wb['2. 规模估算']
print("工作表：2. 规模估算")
print()

# 获取所有数据
rows = list(ws.iter_rows(values_only=True))

# 打印第 10 行附近的数据（第 9-15 行）
print("第 9-15 行数据:")
for i in range(8, min(15, len(rows))):
    row = rows[i]
    clean_row = [str(cell) if cell is not None else '' for cell in row]
    print(f"行{i+1}: {clean_row}")
print()

# 查看类别列（第 7 列，索引 6）的唯一值
print("统计类别分布:")
categories = {}
for row in rows[9:]:  # 从第 10 行开始（跳过表头）
    if len(row) > 6:
        category = row[6]
        if category:
            categories[category] = categories.get(category, 0) + 1

for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count} 条")
print()

# 查看不同类别的功能点计数项特征
print("各类别示例:")
samples = {}
for row in rows[9:]:
    if len(row) > 6:
        category = row[6]
        item = row[5] if len(row) > 5 else ''
        if category and category not in samples:
            samples[category] = item

for cat, item in sorted(samples.items()):
    print(f"  {cat}: {item}")
