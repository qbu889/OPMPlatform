#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试ES数据格式处理
"""

import json
from routes.kafka_generator_routes import generate_es_to_kafka_mapping, get_nested_value

# 模拟ES查询结果格式的数据
es_query_result = {
    "took": 5,
    "timed_out": False,
    "_shards": {
        "total": 5,
        "successful": 5,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 1.0,
        "hits": [
            {
                "_index": "test_index",
                "_type": "_doc",
                "_id": "1",
                "_score": 1.0,
                "_source": {
                    "EVENT_ID": 311176565,
                    "EVENT_NAME": "小区退服事件-CELL FAULTY",
                    "EVENT_TIME": "2026-02-06 18:24:42",
                    "CITY_NAME": "福州市",
                    "EQUIPMENT_NAME": "福州鼓楼-鼓楼卫前街小站-NLH-64",
                    "VENDOR_NAME": "诺基亚",
                    "ALARM_NAME": "CELL FAULTY",
                    "ALARM_LEVEL": 2,
                    "NETWORK_TYPE_ID": "1",
                    "OBJECT_CLASS_ID": 8105,
                    "MAINTAIN_TEAM": "漳州龙文主城网格超讯基站维护组1",
                    "PROVINCE_NAME": "福建省",
                    "EVENT_LOCATION": "测试位置",
                    "MAIN_NET_SORT_ONE": "无线网",
                    "NETWORK_SUB_TYPE_ID": "1001",
                    "ORG_TYPE": 14101,
                    "VENDOR_EVENT_TYPE": "1001",
                    "ALARM_STANDARD_NAME": "小区退服",
                    "ALARM_STANDARD_ID": "STD001",
                    "ALARM_STANDARD_FLAG": 1,
                    "VENDOR_SEVERITY": "2",
                    "EVENT_PROBABLE_CAUSE_TXT": "硬件故障",
                    "NMS_ALARM_ID": "ALM001",
                    "EVENT_EXPLANATION": "小区服务中断",
                    "EVENT_EXPLANATION_ADDITION": "需要现场处理",
                    "SITE_TYPE": "宏站",
                    "EVENT_CAT": "设备故障",
                    "NMS_NAME": "网管系统",
                    "CITY_ID": "350100",
                    "REMOTE_EQUIPMENT_NAME": "",
                    "BUSINESS_TAG": {
                        "GCSS_CLIENT": "",
                        "GCSS_CLIENT_NAME": "",
                        "GCSS_CLIENT_NUM": "",
                        "GCSS_CLIENT_LEVEL": "",
                        "GCSS_SERVICE": "",
                        "GCSS_SERVICE_NUM": "",
                        "GCSS_SERVICE_LEVEL": "",
                        "GCSS_SERVICE_TYPE": "",
                        "BUSINESS_SYSTEM": "无线网络",
                        "CIRCUIT_NO": "",
                        "PRODUCT_TYPE": "无线通信",
                        "CIRCUIT_LEVEL": "",
                        "BUSINESS_TYPE": "",
                        "IRMS_GRID_NAME": "",
                        "ADMIN_GRID_ID": "",
                        "HOME_CLIENT_NUM": "",
                        "GCSS_CLIENT_GRADE": "",
                        "EFFECT_CIRCUIT_NUM": ""
                    },
                    "NE_TAG": {
                        "MACHINE_ROOM_INFO": "福州鼓楼机房",
                        "ROOM_ID": "ROOM001"
                    },
                    "EQUIPMENT_IP": "192.168.1.1",
                    "LOGIC_ALARM_TYPE": "1001",
                    "LOGIC_SUB_ALARM_TYPE": "001",
                    "EFFECT_NE_NUM": "5",
                    "SATOTAL": "10",
                    "ALARM_SOURCE": "网管告警",
                    "SRC_ORG_ALARM_TEXT": "小区服务中断告警",
                    "FAULT_DIAGNOSIS": "初步诊断为硬件故障",
                    "EXTRA_ID2": "EXT001",
                    "EXTRA_STRING1": "扩展信息1",
                    "PORT_NUM": "P001",
                    "NE_ADMIN_STATUS": "1",
                    "TMSC_CAT": "1",
                    "INTERFERENCE_FLAG": "0",
                    "PROJ_INTERFERENCE_TYPE": "无干扰",
                    "INDUSTRY_CUST_TYPE": "1",
                    "FAULT_LOCATION": "机房A区",
                    "ALARM_UNIQUE_ID": "UNIQ001",
                    "EVENT_SOURCE": 1,
                    "TYPE_KEYCODE": "故障处理"
                }
            }
        ]
    }
}

def test_es_format_processing():
    """测试ES格式数据处理"""
    print("=== 测试ES格式数据处理 ===\n")
    
    # 测试原始ES查询结果
    print("1. 测试完整的ES查询结果格式:")
    try:
        # 提取_source数据
        source_data = es_query_result["hits"]["hits"][0]["_source"]
        print("✓ 成功提取_source数据")
        
        # 测试字段映射
        kafka_message = generate_es_to_kafka_mapping(source_data)
        print("✓ 成功生成Kafka消息")
        
        # 检查关键字段
        expected_fields = ["ID", "NETWORK_TYPE_TOP", "ORG_SEVERITY", "CITY_NAME", "EQP_LABEL", "VENDOR_NAME"]
        for field in expected_fields:
            if field in kafka_message:
                print(f"  ✓ 字段 {field}: {kafka_message[field]}")
            else:
                print(f"  ✗ 缺少字段 {field}")
                
        # 测试ORG_TEXT生成
        org_text = kafka_message.get("ORG_TEXT", "")
        if org_text:
            print(f"✓ ORG_TEXT生成成功，长度: {len(org_text)}")
            print(f"  前50个字符: {org_text[:50]}...")
        else:
            print("✗ ORG_TEXT生成失败")
            
    except Exception as e:
        print(f"✗ 处理失败: {e}")
    
    print("\n2. 测试直接_source数据格式:")
    try:
        source_data = es_query_result["hits"]["hits"][0]["_source"]
        kafka_message = generate_es_to_kafka_mapping(source_data)
        print("✓ 直接_source数据处理成功")
        
        # 验证一些关键映射
        mappings_to_check = {
            "NETWORK_TYPE_TOP": "NETWORK_TYPE_ID",
            "ORG_SEVERITY": "ALARM_LEVEL", 
            "CITY_NAME": "CITY_NAME",
            "EQP_LABEL": "EQUIPMENT_NAME",
            "VENDOR_NAME": "VENDOR_NAME"
        }
        
        for kafka_field, es_field in mappings_to_check.items():
            if kafka_field in kafka_message and es_field in source_data:
                print(f"  ✓ {kafka_field} <- {es_field}: {kafka_message[kafka_field]}")
                
    except Exception as e:
        print(f"✗ 直接处理失败: {e}")

def test_get_nested_value():
    """测试嵌套值获取函数"""
    print("\n=== 测试嵌套值获取 ===")
    
    # 测试数据
    test_data = {
        "_source": {
            "BUSINESS_TAG": {
                "GCSS_CLIENT": "client123",
                "GCSS_CLIENT_NAME": "测试客户"
            },
            "NE_TAG": {
                "MACHINE_ROOM_INFO": "测试机房"
            },
            "simple_field": "简单值"
        }
    }
    
    # 测试_cases
    test_cases = [
        ("BUSINESS_TAG.GCSS_CLIENT", "client123"),
        ("NE_TAG.MACHINE_ROOM_INFO", "测试机房"), 
        ("simple_field", "简单值"),
        ("nonexistent.field", None)
    ]
    
    for path, expected in test_cases:
        result = get_nested_value(test_data, path)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {path}: {result} (期望: {expected})")

if __name__ == "__main__":
    test_es_format_processing()
    test_get_nested_value()