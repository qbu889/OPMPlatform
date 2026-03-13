#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Excel 公式转换为 Python 代码的测试示例

原始 Excel 公式：
=IF('3. 调整因子'!C2='3. 调整因子'!B36,'3. 调整因子'!D36,
  IF('3. 调整因子'!C2='3. 调整因子'!B37,'3. 调整因子'!D37,
    IF('3. 调整因子'!C2='3. 调整因子'!B38,'3. 调整因子'!D38,
      IF('3. 调整因子'!C2='3. 调整因子'!B39,'3. 调整因子'!D39,0))))
"""

def excel_if_formula_c2_b36_d39(selected_value, config_data):
    """将 Excel 公式转化为程序逻辑"""
    for config in config_data:
        if selected_value == config['option_name']:
            return float(config['score_value'])
    return 0.0


def excel_formula_lookup(selected_value, b_cells, d_cells):
    """通用的 Excel 公式查找函数"""
    if len(b_cells) != len(d_cells):
        raise ValueError("B 列和 D 列的长度必须相同")
    
    for i in range(len(b_cells)):
        if selected_value == b_cells[i]:
            return float(d_cells[i])
    
    return 0.0


# =============================================
# 测试示例
# =============================================

if __name__ == '__main__':
    print("=" * 80)
    print("Excel 公式转换为 Python 代码测试")
    print("=" * 80)
    
    # 方法 1：使用字典配置
    print("\n【方法 1】使用字典配置")
    print("-" * 80)
    
    config_data = [
        {'option_name': '估算早期', 'score_value': 1.39},
        {'option_name': '估算中期', 'score_value': 1.21},
        {'option_name': '估算晚期', 'score_value': 1.10},
        {'option_name': '项目完成', 'score_value': 1.00},
    ]
    
    # 测试不同的选择
    test_cases = ['估算早期', '估算中期', '估算晚期', '项目完成', '未知选项']
    
    for selected in test_cases:
        score = excel_if_formula_c2_b36_d39(selected, config_data)
        print(f"C2='{selected}' → 分值：{score:.2f}")
    
    # 方法 2：使用列表
    print("\n【方法 2】使用列表参数")
    print("-" * 80)
    
    b_cells = ['估算早期', '估算中期', '估算晚期', '项目完成']
    d_cells = [1.39, 1.21, 1.10, 1.00]
    
    for selected in test_cases:
        score = excel_formula_lookup(selected, b_cells, d_cells)
        print(f"C2='{selected}' → 分值：{score:.2f}")
    
    # 方法 3：从数据库动态加载
    print("\n【方法 3】从数据库加载配置（模拟）")
    print("-" * 80)
    
    # 模拟从数据库查询的数据
    db_config_data = [
        {'option_name': '估算早期', 'score_value': '1.39'},
        {'option_name': '估算中期', 'score_value': '1.21'},
        {'option_name': '估算晚期', 'score_value': '1.10'},
        {'option_name': '项目完成', 'score_value': '1.00'},
    ]
    
    print("从数据库加载配置:")
    for item in db_config_data:
        print(f"  B 列：{item['option_name']:10s} | D 列：{item['score_value']}")
    
    # 用户选择的值（相当于 Excel 的 C2 单元格）
    user_choice = '估算中期'
    result = excel_if_formula_c2_b36_d39(user_choice, db_config_data)
    
    print(f"\n用户选择：{user_choice}")
    print(f"计算结果：{result:.2f}")
    print(f"Excel 公式逻辑：C2='{user_choice}' 匹配 B37='{db_config_data[1]['option_name']}' → D37={result}")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试完成！")
    print("=" * 80)
