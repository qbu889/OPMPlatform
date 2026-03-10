#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import sys

# 读取期望的 Excel 文件
excel_file = 'test/fpa/集中故障管理系统 - 监控综合应用 - 关于事件工单自动剔除考核及流程呈现优化的开发需求 -15500_20250318-FPA 预估 2025 版 V3_评审版本.xlsx'

try:
    xls = pd.ExcelFile(excel_file)
    print(f"工作表列表：{xls.sheet_names}")
    print()

    # 检查每个工作表
    for sheet in xls.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        print(f"工作表：{sheet}")
        print(f"行数：{len(df)}, 列数：{len(df.columns)}")
        if len(df) > 0:
            print(f"前 3 行数据:")
            # 打印列名
            print(f"列名：{list(df.columns)}")
            print()
            # 打印前 3 行
            for idx, row in df.head(3).iterrows():
                print(f"行{idx}: {row.tolist()}")
        print("-" * 80)
        print()
except Exception as e:
    print(f"读取文件失败：{e}", file=sys.stderr)
    sys.exit(1)
