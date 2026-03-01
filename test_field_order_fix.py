#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试字段顺序修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.kafka_generator_routes import STANDARD_FIELD_ORDER, generate_es_to_kafka_mapping
import json
from collections import OrderedDict

def test_field_order():
    """测试字段顺序是否正确"""
    # 模拟ES数据
    es_data = {
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
    
    # 提取实际字段顺序
    actual_fields = list(kafka_message.keys())
    expected_fields = STANDARD_FIELD_ORDER
    
    print("=== 字段顺序测试结果 ===\n")
    print(f"期望字段数量: {len(expected_fields)}")
    print(f"实际字段数量: {len(actual_fields)}")
    print(f"匹配字段数量: {len(set(expected_fields) & set(actual_fields))}\n")
    
    # 检查前20个字段的顺序
    print("=== 前20个字段顺序对比 ===")
    print(f"{'位置':<4} {'期望字段':<30} {'实际字段':<30} {'状态'}")
    print("-" * 80)
    
    for i in range(min(20, len(expected_fields), len(actual_fields))):
        expected_field = expected_fields[i]
        actual_field = actual_fields[i]
        status = "✓" if expected_field == actual_field else "✗"
        print(f"{i:<4} {expected_field:<30} {actual_field:<30} {status}")
    
    # 检查所有字段是否按顺序排列
    print("\n=== 完整顺序验证 ===")
    all_correct = True
    for i, expected_field in enumerate(expected_fields):
        if i < len(actual_fields):
            actual_field = actual_fields[i]
            if expected_field != actual_field:
                print(f"位置 {i}: 期望 '{expected_field}' 但得到 '{actual_field}'")
                all_correct = False
        else:
            print(f"位置 {i}: 缺少字段 '{expected_field}'")
            all_correct = False
    
    if all_correct:
        print("✅ 所有字段顺序完全正确！")
    else:
        print("❌ 存在字段顺序问题")
    
    # 输出JSON格式的结果供对比
    print("\n=== 生成的Kafka消息（前10个字段）===")
    ordered_message = OrderedDict()
    for field in expected_fields:
        if field in kafka_message:
            ordered_message[field] = kafka_message[field]
    
    sample_data = dict(list(ordered_message.items())[:10])
    print(json.dumps(sample_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test_field_order()