#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FPA预估表生成器测试脚本
用于测试从需求文档中提取功能点并生成 Excel 表格
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量以便导入
os.environ['FLASK_APP'] = 'app'

from routes.fpa_generator_routes import parse_requirement_document, generate_fpa_excel


def test_parse_requirement():
    """测试需求文档解析功能"""
    
    # 示例需求文档内容
    test_md_content = """
## 监控管理应用

### 故障监控应用

#### 集团事件对接

##### 网络事件业务影响

###### 家宽业务 OLT 脱管场景业务采集（注：对应FPA功能点计数项）

**功能描述：**进行家宽业务 OLT 脱管场景业务采集

**系统界面：**无

**输入：**系统自动实时触发

**输出：**查询出满足条件的事件数据

**处理过程：**系统自动实时触发，进行家宽业务 OLT 脱管场景业务采集。

**本事务功能预计涉及到 1 个内部逻辑文件，0 个外部逻辑文件**

本期新增/变更的内部逻辑文件：家宽业务影响指标清单表

本期涉及原有但没修改的内部逻辑文件：网络事件表

本期新增/变更的外部逻辑文件：无

本期涉及原有但没修改的外部逻辑文件：无

###### 家宽业务 PON 口故障场景业务影响分析判定

**功能描述：**进行家宽业务 PON 口故障场景业务影响分析判定

**系统界面：**无

**输入：**系统自动实时触发

**输出：**输出满足条件的家宽业务 PON 口故障场景业务影响分析结果

**处理过程：**系统自动实时触发，根据家宽阈值配置表，进行判定。

**本事务功能预计涉及到 2 个内部逻辑文件，0 个外部逻辑文件**

本期新增/变更的内部逻辑文件：家宽业务影响指标清单表

本期涉及原有但没修改的内部逻辑文件：家宽业务影响阈值配置表

本期新增/变更的外部逻辑文件：无

本期涉及原有但没修改的外部逻辑文件：无
"""
    
    print("=" * 60)
    print("测试需求文档解析功能")
    print("=" * 60)
    
    function_points = parse_requirement_document(test_md_content)
    
    print(f"\n✓ 成功解析 {len(function_points)} 个功能点\n")
    
    for i, point in enumerate(function_points, 1):
        print(f"{i}. {point['level5']}")
        print(f"   一级分类：{point['level1']}")
        print(f"   二级分类：{point['level2']}")
        print(f"   三级分类：{point['level3']}")
        print(f"   功能点名称：{point['level4']}")
        print(f"   功能描述：{point['功能描述']}")
        print(f"   内部逻辑文件数：{point['内部逻辑文件数']}")
        print(f"   外部逻辑文件数：{point['外部逻辑文件数']}")
        print()
    
    return function_points


def test_excel_generation(function_points):
    """测试 Excel 生成功能"""
    
    print("=" * 60)
    print("测试 Excel 生成功能")
    print("=" * 60)
    
    output_dir = project_root / "tmp" / "fpa_test"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = output_dir / "test_fpa_output.xlsx"
    
    try:
        generate_fpa_excel(function_points, str(output_path))
        print(f"\n✓ Excel 文件生成成功：{output_path}")
        print(f"✓ 文件大小：{os.path.getsize(output_path)} bytes")
        return True
    except Exception as e:
        print(f"\n✗ Excel 生成失败：{e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_document():
    """测试真实的需求文档"""
    
    print("=" * 60)
    print("测试真实需求文档解析")
    print("=" * 60)
    
    # 尝试读取用户提供的需求文档
    doc_path = project_root.parent / "Downloads" / "---03100_20250115-_V4.1_-V2.md"
    
    if not os.path.exists(doc_path):
        print(f"⚠ 文档不存在：{doc_path}")
        print("跳过真实文档测试")
        return None
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✓ 成功读取文档：{doc_path}")
        print(f"✓ 文档大小：{len(content)} 字符")
        
        function_points = parse_requirement_document(content)
        print(f"\n✓ 从真实文档中解析出 {len(function_points)} 个功能点")
        
        # 生成 Excel
        output_dir = project_root / "tmp"
        output_path = output_dir / "集中故障管理系统 - 监控综合应用 - 关于集团事件业务影响分析开发需求-FPA预估.xlsx"
        
        generate_fpa_excel(function_points, str(output_path))
        print(f"✓ Excel 文件已生成：{output_path}")
        
        return function_points
        
    except Exception as e:
        print(f"✗ 处理真实文档失败：{e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FPA预估表生成器测试开始")
    print("=" * 60 + "\n")
    
    # 测试 1: 解析示例文档
    function_points = test_parse_requirement()
    
    # 测试 2: 生成 Excel
    if function_points:
        test_excel_generation(function_points)
    
    # 测试 3: 真实文档测试
    test_real_document()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
