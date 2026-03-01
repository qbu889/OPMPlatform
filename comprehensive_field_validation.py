#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的字段顺序验证脚本
验证修复后的kafka generator是否能产生与预期完全一致的字段顺序
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.kafka_generator_routes import STANDARD_FIELD_ORDER, generate_es_to_kafka_mapping
import json

def load_expected_order():
    """加载预期的字段顺序"""
    expected_file = "/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/预计返回顺序.json"
    with open(expected_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(data.keys())

def load_actual_response():
    """加载实际的接口返回数据"""
    actual_file = "/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/接口返回.json"
    with open(actual_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(data['data'].keys())

def create_test_es_data():
    """创建测试用的ES数据"""
    return {
        "_source": {
            "ROOT_NETWORK_TYPE_ID": "5",
            "ALARM_LEVEL": 1,
            "PROVINCE_NAME": "福建省",
            "CITY_NAME": "福州市", 
            "EQUIPMENT_NAME": "【测试】福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房",
            "OBJECT_CLASS_ID": 30014,
            "VENDOR_NAME": "鼓楼兴",
            "VENDOR_ID": 771,
            "ALARM_RESOURCE_STATUS": "1",
            "EVENT_LOCATION": "基站_福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房",
            "NE_LABEL": "【测试】福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房",
            "MAIN_NET_SORT_ONE": "电源和配套设备",
            "NETWORK_SUB_TYPE_ID": "500",
            "ORG_TYPE": 1,
            "VENDOR_EVENT_TYPE": "1",
            "ALARM_NAME": "电池放电告警",
            "ALARM_STANDARD_NAME": "电池放电告警",
            "ALARM_STANDARD_FLAG": 2,
            "ALARM_STANDARD_ID": "0500-009-006-10-800007",
            "EVENT_PROBABLE_CAUSE_TXT": "0",
            "NMS_ALARM_ID": "255603421",
            "NE_TAG": {
                "MACHINE_ROOM_INFO": "福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房",
                "ROOM_ID": "DEVICEROOM-NMS-10517"
            },
            "TYPE_KEYCODE": "关联到资源,",
            "NE_LOCATION": "无线设备：福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房-NLS-BBU01...",
            "EVENT_EXPLANATION": "电池处于放电状态",
            "EVENT_EXPLANATION_ADDITION": "传输节点",
            "MAINTAIN_TEAM": "福州永泰农村网格虹信基站维护组1",
            "SITE_TYPE": "109",
            "EVENT_CAT": "",
            "NMS_NAME": "鼓楼兴动环系统",
            "CITY_ID": "350100",
            "REMOTE_EQUIPMENT_NAME": "",
            "REMOTE_OBJECT_CLASS": "",
            "ALARM_REASON": "",
            "BUSINESS_TAG": {
                "BUSINESS_SYSTEM": "鼓楼新动力环境告警(旧)",
                "CIRCUIT_NO": "999999,98,1",
                "PRODUCT_TYPE": "",
                "CIRCUIT_LEVEL": "",
                "BUSINESS_TYPE": "",
                "IRMS_GRID_NAME": "",
                "ADMIN_GRID_ID": "",
                "HOME_CLIENT_NUM": ""
            },
            "EQUIPMENT_IP": "",
            "EFFECT_NE_NUM": 6,
            "SATOTAL": 6,
            "FAULT_DIAGNOSIS": "【故障原因初判】动环设备问题.\t【故障处理建议】请排查动环设备故障。",
            "EXTRA_ID2": "",
            "EXTRA_STRING1": "",
            "PORT_NUM": "300103",
            "NE_ADMIN_STATUS": "",
            "TMSC_CAT": "",
            "INTERFERENCE_FLAG": "0",
            "PROJ_INTERFERENCE_TYPE": "【是否干扰告警】：否。",
            "FAULT_LOCATION": "基站_福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房",
            "EVENT_SOURCE": 2,
            "SRC_ORG_ALARM_TEXT": "<ALARMSTART>\nSystemName:给wangzishu鼓楼兴动环系统\nVendor_Name:艾默生开关电源\n...</ALARMSTART>"
        }
    }

def comprehensive_validation():
    """进行全面验证"""
    print("🔍 开始全面字段顺序验证...\n")
    
    # 1. 加载各种参考数据
    expected_order = load_expected_order()
    actual_response_order = load_actual_response()
    test_es_data = create_test_es_data()
    
    # 2. 生成新的Kafka消息
    generated_message = generate_es_to_kafka_mapping(test_es_data)
    generated_order = list(generated_message.keys())
    
    print("📊 数据源统计:")
    print(f"  - 预期顺序字段数: {len(expected_order)}")
    print(f"  - 实际返回字段数: {len(actual_response_order)}")
    print(f"  - 新生成字段数: {len(generated_order)}")
    print(f"  - 标准字段顺序数: {len(STANDARD_FIELD_ORDER)}")
    print()
    
    # 3. 验证字段完整性
    print("✅ 字段完整性检查:")
    missing_in_generated = set(STANDARD_FIELD_ORDER) - set(generated_order)
    extra_in_generated = set(generated_order) - set(STANDARD_FIELD_ORDER)
    
    if missing_in_generated:
        print(f"  ❌ 生成的消息缺少字段: {missing_in_generated}")
    else:
        print("  ✓ 生成的消息包含所有标准字段")
        
    if extra_in_generated:
        print(f"  ⚠️  生成的消息有多余字段: {extra_in_generated}")
    else:
        print("  ✓ 生成的消息没有多余字段")
    print()
    
    # 4. 详细顺序对比
    print("📋 详细顺序对比 (前30个字段):")
    print(f"{'位置':<4} {'标准顺序':<25} {'新生成':<25} {'实际返回':<25} {'状态'}")
    print("-" * 95)
    
    for i in range(min(30, len(STANDARD_FIELD_ORDER))):
        std_field = STANDARD_FIELD_ORDER[i]
        gen_field = generated_order[i] if i < len(generated_order) else "-"
        act_field = actual_response_order[i] if i < len(actual_response_order) else "-"
        
        # 检查顺序是否正确
        std_correct = std_field == gen_field
        act_correct = std_field == act_field
        
        status = []
        if std_correct:
            status.append("✓标准")
        if act_correct:
            status.append("✓实际")
        if not status:
            status.append("✗错误")
            
        status_str = ", ".join(status)
        print(f"{i:<4} {std_field:<25} {gen_field:<25} {act_field:<25} {status_str}")
    print()
    
    # 5. 总体评估
    print("🎯 总体评估:")
    
    # 检查新生成的消息是否完全符合标准顺序
    perfect_match = True
    for i, expected_field in enumerate(STANDARD_FIELD_ORDER):
        if i >= len(generated_order) or generated_order[i] != expected_field:
            perfect_match = False
            break
    
    if perfect_match:
        print("  🎉 新生成的消息字段顺序完全正确！")
    else:
        print("  ❌ 新生成的消息字段顺序仍有问题")
    
    # 检查实际返回是否符合标准顺序
    actual_perfect = True
    for i, expected_field in enumerate(STANDARD_FIELD_ORDER):
        if i >= len(actual_response_order) or actual_response_order[i] != expected_field:
            actual_perfect = False
            break
    
    if actual_perfect:
        print("  🎉 实际返回的字段顺序也完全正确！")
    else:
        print("  ⚠️  实际返回的字段顺序仍存在问题")
    
    print()
    
    # 6. 输出JSON示例
    print("📄 生成的消息示例 (前5个字段):")
    sample_dict = {}
    for field in STANDARD_FIELD_ORDER[:5]:
        if field in generated_message:
            sample_dict[field] = generated_message[field]
    
    print(json.dumps(sample_dict, ensure_ascii=False, indent=2))
    
    return perfect_match

if __name__ == "__main__":
    success = comprehensive_validation()
    exit(0 if success else 1)