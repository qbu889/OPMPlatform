#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证ES到Kafka转换结果
"""

import json

def load_json_file(filepath):
    """加载JSON文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_outputs(actual_file, expected_file):
    """比较实际输出和期望输出"""
    actual = load_json_file(actual_file)
    expected = load_json_file(expected_file)
    
    print("=== ES到Kafka转换结果验证 ===\n")
    
    # 需要忽略的动态字段
    dynamic_fields = [
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
        'ID',
        'TOPIC_PARTITION'
    ]
    
    print(f"实际输出字段数: {len(actual)}")
    print(f"期望输出字段数: {len(expected)}")
    
    # 检查字段一致性
    actual_fields = set(actual.keys())
    expected_fields = set(expected.keys())
    
    missing_in_actual = expected_fields - actual_fields
    extra_in_actual = actual_fields - expected_fields
    
    if missing_in_actual:
        print(f"\n❌ 缺失字段 ({len(missing_in_actual)}个):")
        for field in sorted(missing_in_actual):
            print(f"  - {field}")
    
    if extra_in_actual:
        print(f"\n⚠️  额外字段 ({len(extra_in_actual)}个):")
        for field in sorted(extra_in_actual):
            print(f"  - {field}")
    
    # 检查值的一致性
    common_fields = actual_fields & expected_fields
    mismatches = []
    
    print(f"\n=== 字段值对比 ===")
    for field in sorted(common_fields):
        actual_value = actual[field]
        expected_value = expected[field]
        
        if field in dynamic_fields:
            print(f"⏰ {field}: [动态值] 实际={repr(actual_value)[:30]}...")
            continue
            
        if actual_value != expected_value:
            mismatches.append(field)
            print(f"❌ {field}:")
            print(f"   实际: {repr(actual_value)}")
            print(f"   期望: {repr(expected_value)}")
        else:
            print(f"✅ {field}: 匹配")
    
    print(f"\n=== 验证总结 ===")
    print(f"总字段数: 期望{len(expected_fields)}, 实际{len(actual_fields)}")
    print(f"共同字段: {len(common_fields)}")
    print(f"值不匹配字段: {len(mismatches)}")
    
    if not missing_in_actual and not extra_in_actual and not mismatches:
        print("🎉 所有字段和值都匹配！")
        return True
    else:
        if mismatches:
            print(f"\n值不匹配的字段:")
            for field in mismatches:
                print(f"  - {field}")
        return False

def main():
    actual_file = '/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/输出数据.json'
    expected_file = '/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/原本理想的输出数据.json'
    
    success = compare_outputs(actual_file, expected_file)
    
    if success:
        print("\n✅ 验证通过！输出数据符合预期格式。")
    else:
        print("\n❌ 验证失败！请检查字段映射配置。")

if __name__ == "__main__":
    main()