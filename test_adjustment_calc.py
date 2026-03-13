#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试调整因子计算器 API
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_calculator_data():
    """测试获取计算器数据接口"""
    print("=" * 60)
    print("测试 1: 获取计算器数据")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/adjustment-calc/api/calculator-data")
        response.raise_for_status()
        
        data = response.json()
        if data['success']:
            print("✓ 成功获取计算器数据")
            
            calculator_data = data['data']
            print(f"\n数据分类统计:")
            for key, value in calculator_data.items():
                print(f"  - {key}: {len(value)} 条")
            
            # 显示部分示例数据
            if calculator_data['application_types']:
                print(f"\n应用类型示例:")
                for item in calculator_data['application_types'][:2]:
                    print(f"  - {item['factor_name']} | {item['option_name']} | {item['score_value']}")
            
            return True
        else:
            print(f"✗ API 返回失败：{data.get('message', '')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求失败：{e}")
        return False


def test_calculate():
    """测试计算调整因子接口"""
    print("\n" + "=" * 60)
    print("测试 2: 计算调整因子")
    print("=" * 60)
    
    test_data = {
        'scale_timing': '估算中期',
        'application_type': '业务处理',
        'distributed_processing': '没有明示对分布式处理的需求事项',
        'performance': '没有明示对性能的特别需求事项或活动，因此提供基本性能',
        'reliability': '没有明示对可靠性的特别需求事项或活动，因此提供基本的可靠性',
        'multi_site': '在相同用途的硬件或软件环境下运行',
        'language': 'JAVA、C++、C#及其他同级别语言/平台',
        'team_background': '为本行业（政府）开发过类似的软件',
        'reuse_level': '低',
        'change_type': '新增'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/adjustment-calc/api/calculate",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        result = response.json()
        if result['success']:
            print("✓ 计算成功")
            
            calc_data = result['data']
            print(f"\n计算结果:")
            print(f"  规模变更调整因子：{calc_data['scale_factor']}")
            print(f"  应用类型调整因子：{calc_data['application_factor']}")
            print(f"  质量特性调整因子：{calc_data['quality_factor']}")
            print(f"  开发语言调整因子：{calc_data['language_factor']}")
            print(f"  开发团队背景调整因子：{calc_data['team_factor']}")
            print(f"  重用程度调整因子：{calc_data['reuse_factor']}")
            print(f"  修改类型调整因子：{calc_data['change_factor']}")
            print(f"\n总调整因子：{calc_data['total_factor']:.4f}")
            
            # 显示详细计算过程
            print(f"\n详细计算过程:")
            details = calc_data['details']
            for key, detail in details.items():
                if isinstance(detail, dict):
                    if 'sub_items' in detail:
                        print(f"  {detail['name']}:")
                        for sub in detail['sub_items']:
                            print(f"    - {sub['name']}: {sub['value']}")
                        print(f"    小计：{detail['total']}")
                    elif 'value' in detail:
                        print(f"  {detail['name']}: {detail['option']} = {detail['value']}")
            
            return True
        else:
            print(f"✗ 计算失败：{result.get('message', '')}")
            return False
            
    except Exception as e:
        print(f"✗ 请求失败：{e}")
        return False


def main():
    """主测试函数"""
    print("\n🚀 开始测试调整因子计算器 API")
    print("=" * 60)
    
    # 测试 1: 获取数据
    test1_passed = test_calculator_data()
    
    # 测试 2: 计算功能
    test2_passed = test_calculate()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"测试 1 (获取数据): {'✓ 通过' if test1_passed else '✗ 失败'}")
    print(f"测试 2 (计算功能): {'✓ 通过' if test2_passed else '✗ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败，请检查日志")


if __name__ == '__main__':
    main()
