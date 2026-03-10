#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FPA Excel 文件对比工具
对比程序生成的 Excel 和理想 Excel 的差异
"""

import pandas as pd
import sys
from pathlib import Path

# 文件路径
base_path = Path(__file__).parent
ideal_file = base_path / "集中故障管理系统 - 监控综合应用 - 关于监控综合应用系统的网络事件新增复盘流程的开发需求 -44400_20250606-FPA 预估 2025 版 V3_厂家版本.xlsx"
generated_file = base_path / "---03100_20250115-_V4.1_-V2_FPA 预估_1773028480829.xlsx"

print("=" * 80)
print("FPA Excel 文件对比分析")
print("=" * 80)

# 检查文件是否存在
if not ideal_file.exists():
    print(f"\n❌ 理想文件不存在：{ideal_file}")
    sys.exit(1)

if not generated_file.exists():
    print(f"\n❌ 生成文件不存在：{generated_file}")
    sys.exit(1)

print(f"\n✓ 理想文件：{ideal_file.name}")
print(f"✓ 生成文件：{generated_file.name}")

# 读取 Excel 文件
print("\n正在读取文件...")
try:
    df_ideal = pd.read_excel(ideal_file, engine='openpyxl')
    print(f"✓ 理想文件读取成功：{len(df_ideal)} 行，{len(df_ideal.columns)} 列")
except Exception as e:
    print(f"❌ 读取理想文件失败：{e}")
    sys.exit(1)

try:
    df_generated = pd.read_excel(generated_file, engine='openpyxl')
    print(f"✓ 生成文件读取成功：{len(df_generated)} 行，{len(df_generated.columns)} 列")
except Exception as e:
    print(f"❌ 读取生成文件失败：{e}")
    sys.exit(1)

# 对比列名
print("\n" + "=" * 80)
print("列名对比")
print("=" * 80)

ideal_cols = list(df_ideal.columns)
generated_cols = list(df_generated.columns)

print(f"\n理想文件列名 ({len(ideal_cols)}):")
for i, col in enumerate(ideal_cols, 1):
    print(f"  {i}. {col}")

print(f"\n生成文件列名 ({len(generated_cols)}):")
for i, col in enumerate(generated_cols, 1):
    print(f"  {i}. {col}")

# 找出差异
missing_cols = set(ideal_cols) - set(generated_cols)
extra_cols = set(generated_cols) - set(ideal_cols)

if missing_cols:
    print(f"\n⚠️ 生成文件缺少的列：{missing_cols}")
if extra_cols:
    print(f"\n⚠️ 生成文件多出的列：{extra_cols}")

if not missing_cols and not extra_cols:
    print("\n✅ 列名完全一致")

# 对比数据行数
print("\n" + "=" * 80)
print("数据行数对比")
print("=" * 80)
print(f"理想文件：{len(df_ideal)} 行")
print(f"生成文件：{len(df_generated)} 行")
print(f"差异：{len(df_ideal) - len(df_generated)} 行")

# 对比关键列的内容
print("\n" + "=" * 80)
print("关键列内容抽样对比")
print("=" * 80)

key_columns = ['功能点计数项', '功能描述', '内部逻辑文件数', '外部逻辑文件数']

for col in key_columns:
    if col in df_ideal.columns and col in df_generated.columns:
        print(f"\n【{col}】")
        print(f"  理想文件前 5 行:")
        for i, val in enumerate(df_ideal[col].head(5), 1):
            print(f"    {i}. {val}")
        
        print(f"  生成文件前 5 行:")
        for i, val in enumerate(df_generated[col].head(5), 1):
            print(f"    {i}. {val}")

# 统计信息对比
print("\n" + "=" * 80)
print("统计信息对比")
print("=" * 80)

if '内部逻辑文件数' in df_ideal.columns and '内部逻辑文件数' in df_generated.columns:
    print(f"\n内部逻辑文件数:")
    print(f"  理想文件 - 总计：{df_ideal['内部逻辑文件数'].sum()}, 平均：{df_ideal['内部逻辑文件数'].mean():.2f}")
    print(f"  生成文件 - 总计：{df_generated['内部逻辑文件数'].sum()}, 平均：{df_generated['内部逻辑文件数'].mean():.2f}")

if '外部逻辑文件数' in df_ideal.columns and '外部逻辑文件数' in df_generated.columns:
    print(f"\n外部逻辑文件数:")
    print(f"  理想文件 - 总计：{df_ideal['外部逻辑文件数'].sum()}, 平均：{df_ideal['外部逻辑文件数'].mean():.2f}")
    print(f"  生成文件 - 总计：{df_generated['外部逻辑文件数'].sum()}, 平均：{df_generated['外部逻辑文件数'].mean():.2f}")

# 保存对比报告
print("\n" + "=" * 80)
print("生成对比报告")
print("=" * 80)

report_path = Path("/Users/linziwang/PycharmProjects/wordToWord/test/fpa/fpa_comparison_report.md")

with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# FPA Excel 文件对比分析报告\n\n")
    f.write(f"**对比时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**理想文件**: {ideal_file.name}\n\n")
    f.write(f"**生成文件**: {generated_file.name}\n\n")
    
    f.write("## 一、基本统计\n\n")
    f.write(f"- 理想文件行数：{len(df_ideal)}\n")
    f.write(f"- 生成文件行数：{len(df_generated)}\n")
    f.write(f"- 行数差异：{len(df_ideal) - len(df_generated)}\n\n")
    
    f.write("## 二、列名对比\n\n")
    f.write(f"- 理想文件列数：{len(ideal_cols)}\n")
    f.write(f"- 生成文件列数：{len(generated_cols)}\n\n")
    
    if missing_cols:
        f.write(f"### 缺少的列\n{', '.join(missing_cols)}\n\n")
    if extra_cols:
        f.write(f"### 多出的列\n{', '.join(extra_cols)}\n\n")
    
    f.write("## 三、数据统计\n\n")
    if '内部逻辑文件数' in df_ideal.columns:
        f.write(f"- 内部逻辑文件数总计 (理想): {df_ideal['内部逻辑文件数'].sum()}\n")
        f.write(f"- 内部逻辑文件数总计 (生成): {df_generated['内部逻辑文件数'].sum()}\n\n")
    
    f.write("## 四、主要差异\n\n")
    f.write("### 1. 功能点计数项提取差异\n\n")
    f.write("理想文件示例:\n")
    for i, val in enumerate(df_ideal['功能点计数项'].head(3), 1):
        f.write(f"{i}. {val}\n")
    f.write("\n生成文件示例:\n")
    for i, val in enumerate(df_generated['功能点计数项'].head(3), 1):
        f.write(f"{i}. {val}\n")

print(f"\n✅ 对比报告已保存：{report_path}")
print(f"\n请查看报告了解详细差异")
