#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试一致性修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.kafka_generator_routes import generate_es_to_kafka_mapping
import json
from datetime import datetime, timedelta

def test_consistency_fix():
    """测试一致性修复效果"""
    print("=== 一致性修复测试 ===\n")
    
    # 模拟ES数据
    es_data = {
        "_source": {
            "FULL_REGION_NAME": "福建省/福州市/永泰县",
            "PROVINCE_NAME": "福建省",
            "CITY_NAME": "福州市",
            "COUNTY_NAME": "永泰县",
            "ROOT_NETWORK_TYPE_ID": "5",
            "ALARM_LEVEL": 1,
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
            "EVENT_PROBABLE_CAUSE_TXT": "0",
            "NMS_ALARM_ID": "255603421",
            "NE_TAG": {
                "MACHINE_ROOM_INFO": "福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房",
                "ROOM_ID": "DEVICEROOM-NMS-10517"
            },
            "TYPE_KEYCODE": "关联到资源,",
            "NE_LOCATION": "无线设备：福州永泰龙峰村龙峰园法院邮电局宿舍二楼201机房-NLS-BBU01...",
            "EVENT_EXPLANATION": "电池处于放电状态",
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
            "EFFECT_NE_NUM": 0,
            "SATOTAL": 2,
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
    
    # 生成Kafka消息
    kafka_message = generate_es_to_kafka_mapping(es_data)
    
    print("生成的Kafka消息关键字段:")
    
    # 检查FP字段一致性
    fp_fields = ["FP0_FP1_FP2_FP3", "CFP0_CFP1_CFP2_CFP3", "ORIG_ALARM_FP", "ORIG_ALARM_CLEAR_FP"]
    fp_values = []
    
    print("\nFP字段一致性检查:")
    for field in fp_fields:
        if field in kafka_message:
            value = kafka_message[field]
            fp_values.append(value)
            print(f"  {field}: {value}")
    
    # 验证FP字段是否一致
    all_same = len(set(fp_values)) == 1 if fp_values else False
    print(f"\nFP字段一致性: {'✓ 一致' if all_same else '✗ 不一致'}")
    
    # 检查时间字段
    time_fields = ["EVENT_TIME", "CREATION_EVENT_TIME", "EVENT_ARRIVAL_TIME"]
    print("\n时间字段检查:")
    current_time_minus_15 = (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    
    for field in time_fields:
        if field in kafka_message:
            value = kafka_message[field]
            is_correct = value == current_time_minus_15
            print(f"  {field}: {value} {'✓' if is_correct else '✗'}")
    
    # 检查关键字段类型
    print("\n关键字段类型检查:")
    type_checks = [
        ("ORG_SEVERITY", int, 1),
        ("EQP_OBJECT_CLASS", int, 30014),
        ("VENDOR_ID", int, 771),
        ("NETWORK_TYPE", str, "500"),
        ("ORG_TYPE", int, 1),
        ("STANDARD_FLAG", int, 2),
        ("EFFECT_NE", int, 0),
        ("EFFECT_SERVICE", int, 2)
    ]
    
    for field, expected_type, expected_value in type_checks:
        if field in kafka_message:
            actual_value = kafka_message[field]
            type_correct = isinstance(actual_value, expected_type)
            value_correct = actual_value == expected_value
            status = "✓" if type_correct and value_correct else "✗"
            print(f"  {field}: {actual_value} (类型:{type(actual_value).__name__}) {status}")
    
    print("\n=== 测试完成 ===")
    
    if all_same:
        print("🎉 FP字段一致性修复成功！")
    else:
        print("❌ FP字段一致性仍有问题")
        
    return kafka_message

if __name__ == "__main__":
    result = test_consistency_fix()