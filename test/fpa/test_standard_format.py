#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试标准 FPA 格式生成
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from routes.fpa_generator_routes import parse_requirement_document, generate_fpa_excel
import pandas as pd

# 读取需求文档
md_path = Path("/Users/linziwang/PycharmProjects/wordToWord/tmp/集中故障管理系统 - 集团事件工单省部接口数据上报保障 - 需求规格说明书_V4.1-5. 功能需求 (3).md")

if md_path.exists():
    print("="*80)
    print("测试标准 FPA 格式生成")
    print("="*80)
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # 解析文档
    function_points = parse_requirement_document(md_content)
    print(f"\n✓ 成功解析 {len(function_points)} 个功能点\n")
    
    # 显示前 5 个功能点的新字段
    print("前 5 个功能点详细信息:")
    print("-"*80)
    for i, point in enumerate(function_points[:5], 1):
        print(f"\n{i}. {point.get('功能点计数项', '')}")
        print(f"   类别：{point.get('类别', '')}")
        print(f"   UFP: {point.get('UFP', '')}")
        print(f"   重用程度：{point.get('重用程度', '')}")
        print(f"   修改类型：{point.get('修改类型', '')}")
        print(f"   AFP: {point.get('AFP', '')}")
    
    # 生成 Excel
    output_path = Path("tmp/test_standard_fpa.xlsx")
    generate_fpa_excel(function_points, str(output_path))
    print(f"\n✓ Excel 生成成功：{output_path}")
    print(f"  文件包含 {len(function_points)} 个功能点")
    
    # 读取生成的 Excel 验证
    print("\n" + "="*80)
    print("Excel 内容抽样检查")
    print("="*80)
    
    df = pd.read_excel(output_path, sheet_name='1.规模估算表', skiprows=9, nrows=5)
    print("\n规模估算表前 5 行:")
    print(df.columns.tolist())
    print(df.head(5).to_string())
    
    # 检查评估结果表
    df_result = pd.read_excel(output_path, sheet_name='3.评估结果表')
    print(f"\n评估结果表行数：{len(df_result)}")
    print("\n评估结果表内容:")
    print(df_result.head(12).to_string())
    
    print("\n" + "="*80)
    print("✅ 测试完成!")
    print("="*80)
    print(f"\n生成的 Excel 文件：{output_path.absolute()}")
    print("请用 Excel 打开查看详细格式")
    
else:
    print(f"❌ 文档不存在：{md_path}")
