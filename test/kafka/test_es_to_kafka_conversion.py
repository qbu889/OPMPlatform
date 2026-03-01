#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ES到Kafka消息转换功能
"""

import sys
import os
import json
from datetime import datetime, timedelta
import uuid

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from routes.kafka_generator_routes import generate_es_to_kafka_mapping, preprocess_json_data

def load_test_data():
    """加载测试数据"""
    input_file = '/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/输入数据.json'
    expected_file = '/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/原本理想的输出数据.json'
    
    # 读取输入数据
    with open(input_file, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # 读取期望输出数据
    with open(expected_file, 'r', encoding='utf-8') as f:
        expected_data = json.load(f)
    
    return input_data, expected_data

def compare_results(actual, expected):
    """比较实际结果和期望结果"""
    differences = {}
    
    # 需要忽略的时间相关字段
    time_fields = [
        'CFP0_CFP1_CFP2_CFP3',
        'ORIG_ALARM_FP', 
        'ORIG_ALARM_CLEAR_FP',
        'FP0_FP1_FP2_FP3',
        'EVENT_TIME',
        'CREATION_EVENT_TIME',
        'EVENT_ARRIVAL_TIME',
        'TIME_STAMP',
        'SRC_ID',
        'SRC_ORG_ID',
        'ID'
    ]
    
    all_fields = set(actual.keys()) | set(expected.keys())
    
    for field in sorted(all_fields):
        actual_value = actual.get(field, "MISSING")
        expected_value = expected.get(field, "MISSING")
        
        # 对于时间字段，我们只检查是否存在，不比较具体值
        if field in time_fields:
            if actual_value == "MISSING" or expected_value == "MISSING":
                differences[field] = {
                    'actual': actual_value,
                    'expected': expected_value,
                    'status': 'MISSING'
                }
            continue
            
        # 对于其他字段，进行严格比较
        if actual_value != expected_value:
            differences[field] = {
                'actual': actual_value,
                'expected': expected_value,
                'status': 'DIFFERENT'
            }
    
    return differences

def main():
    print("=== ES到Kafka消息转换测试 ===\n")
    
    # 加载测试数据
    input_data, expected_data = load_test_data()
    print(f"输入数据字段数: {len(input_data)}")
    print(f"期望输出字段数: {len(expected_data)}")
    
    # 生成Kafka消息
    print("\n生成Kafka消息...")
    actual_result = generate_es_to_kafka_mapping(input_data)
    print(f"实际生成字段数: {len(actual_result)}")
    
    # 保存实际输出
    output_file = '/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/输出数据.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(actual_result, f, ensure_ascii=False, indent=2)
    print(f"实际输出已保存到: {output_file}")
    
    # 比较结果
    print("\n=== 结果对比 ===")
    differences = compare_results(actual_result, expected_data)
    
    if not differences:
        print("✅ 所有字段匹配！")
        return
    
    print(f"发现 {len(differences)} 个差异:")
    print("-" * 50)
    
    for field, diff in differences.items():
        print(f"\n字段: {field}")
        print(f"  状态: {diff['status']}")
        print(f"  实际值: {repr(diff['actual'])}")
        print(f"  期望值: {repr(diff['expected'])}")
    
    # 统计差异类型
    missing_count = sum(1 for d in differences.values() if d['status'] == 'MISSING')
    different_count = sum(1 for d in differences.values() if d['status'] == 'DIFFERENT')
    
    print(f"\n=== 统计 ===")
    print(f"缺失字段: {missing_count}")
    print(f"值不同的字段: {different_count}")
    print(f"总差异字段: {len(differences)}")

if __name__ == "__main__":
    main()