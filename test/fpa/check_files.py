#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比生成的 Excel 和预期的 Excel"""
import pandas as pd
from pathlib import Path
import sys
import os

# 使用绝对路径
base_path = Path('/Users/linziwang/PycharmProjects/wordToWord')

# 查找所有 xlsx 文件
fpa_dir = base_path / "test/fpa"
xlsx_files = list(fpa_dir.glob("*.xlsx"))
print("=" * 80)
print("找到的 Excel 文件:")
for f in xlsx_files:
    print(f"  - {f.name}")
    print(f"    完整路径：{f.absolute()}")
    print(f"    存在：{f.exists()}")

# 找到预期的文件 (FPA预估2025 版 V3.xlsx)
expected_file = fpa_dir / "FPA预估2025版V3.xlsx"
generated_file = base_path/ "uploads/fpa_output/事件处理类工单流程应用场景_FPA预估_1773112620094.xlsx"

print("\n" + "=" * 80)
print("目标文件:")
print(f"  预期文件：{expected_file.name}")
print(f"  生成文件：{generated_file.name}")

# 检查文件是否存在
if not expected_file.exists():
    print(f"\n❌ 预期文件不存在：{expected_file}")
    sys.exit(1)

if not generated_file.exists():
    print(f"\n❌ 生成文件不存在：{generated_file}")
    sys.exit(1)

print("\n✓ 两个文件都存在")

# 读取预期文件
print("\n" + "=" * 80)
print("分析预期文件")
print("=" * 80)

try:
    xls_expected = pd.ExcelFile(str(expected_file))
    print(f"\n工作表列表：{xls_expected.sheet_names}")
    
    for sheet_name in xls_expected.sheet_names:
        df = pd.read_excel(str(expected_file), sheet_name=sheet_name)
        print(f"\n【{sheet_name}】")
        print(f"  行数：{len(df)}, 列数：{len(df.columns)}")
        if len(df) > 0:
            print(f"  列名：{list(df.columns)}")
            # 打印第 10 行数据 (索引为 9，因为从标题后开始)
            if len(df) >= 10:
                print(f"  第 10 行数据:")
                row10 = df.iloc[9]
                for col_name, val in row10.items():
                    print(f"    {col_name}: {val}")
except Exception as e:
    print(f"❌ 读取预期文件失败：{e}")
    import traceback
    traceback.print_exc()

# 读取生成文件
print("\n" + "=" * 80)
print("分析生成文件")
print("=" * 80)

try:
    xls_generated = pd.ExcelFile(str(generated_file))
    print(f"\n工作表列表：{xls_generated.sheet_names}")
    
    for sheet_name in xls_generated.sheet_names:
        df = pd.read_excel(str(generated_file), sheet_name=sheet_name)
        print(f"\n【{sheet_name}】")
        print(f"  行数：{len(df)}, 列数：{len(df.columns)}")
        if len(df) > 0:
            print(f"  列名：{list(df.columns)}")
            # 打印第 10 行数据
            if len(df) >= 10:
                print(f"  第 10 行数据:")
                row10 = df.iloc[9]
                for col_name, val in row10.items():
                    print(f"    {col_name}: {val}")
except Exception as e:
    print(f"❌ 读取生成文件失败：{e}")
    import traceback
    traceback.print_exc()
