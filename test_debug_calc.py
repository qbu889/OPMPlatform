#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试调整因子计算器 API
"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_calculate_debug():
    """测试计算调整因子接口 - 调试版本"""
    print("=" * 60)
    print("调试测试：计算调整因子")
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
        print("\n发送请求...")
        print(f"URL: {BASE_URL}/adjustment-calc/api/calculate")
        print(f"数据：{json.dumps(test_data, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/adjustment-calc/api/calculate",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"\n响应状态码：{response.status_code}")
        print(f"响应头：{response.headers}")
        print(f"\n响应内容：")
        
        if response.status_code == 200:
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
            else:
                print(f"✗ API 返回失败：{result.get('message', '')}")
                print(f"完整响应：{json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"✗ HTTP 错误：{response.status_code}")
            print(f"响应内容：{response.text}")
            
    except Exception as e:
        print(f"✗ 请求异常：{e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_calculate_debug()
