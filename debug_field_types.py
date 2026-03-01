#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试字段类型问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.kafka_generator_routes import generate_es_to_kafka_mapping
import json

def debug_field_types():
    """调试字段类型问题"""
    print("=== 字段类型调试 ===\n")
    
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
    
    # 需要检查的字段及其预期类型
    fields_to_check = [
        ("ORG_SEVERITY", "字符串", str),
        ("VENDOR_ID", "字符串", str), 
        ("ORG_TYPE", "字符串", str),
        ("PROFESSIONAL_TYPE", "字符串数字", str),
        ("EQP_OBJECT_CLASS", "字符串", str)
    ]
    
    print("字段类型检查结果:")
    print("-" * 50)
    
    for field, expected_desc, expected_type in fields_to_check:
        if field in kafka_message:
            actual_value = kafka_message[field]
            actual_type = type(actual_value)
            type_match = isinstance(actual_value, expected_type)
            
            print(f"字段: {field}")
            print(f"  实际值: {actual_value}")
            print(f"  实际类型: {actual_type.__name__}")
            print(f"  预期类型: {expected_type.__name__} ({expected_desc})")
            print(f"  类型匹配: {'✓' if type_match else '✗'}")
            print()
    
    # 特别检查PROFESSIONAL_TYPE的值
    if "PROFESSIONAL_TYPE" in kafka_message:
        prof_value = kafka_message["PROFESSIONAL_TYPE"]
        print(f"PROFESSIONAL_TYPE 特殊检查:")
        print(f"  当前值: '{prof_value}'")
        print(f"  是否为数字字符串: {prof_value.isdigit() if isinstance(prof_value, str) else 'N/A'}")
        
        # 查看源数据
        main_net_sort = es_data["_source"].get("MAIN_NET_SORT_ONE", "")
        print(f"  源数据 MAIN_NET_SORT_ONE: '{main_net_sort}'")
        print()

if __name__ == "__main__":
    debug_field_types()