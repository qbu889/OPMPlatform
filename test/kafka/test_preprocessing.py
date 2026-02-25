#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Kafka生成器的数据预处理功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.kafka_generator_routes import generate_es_to_kafka_mapping
import json

def test_data_preprocessing():
    """测试数据预处理功能"""
    
    # 模拟包含三重引号的ES数据
    problematic_data = '''
{
  "EVENT_ID": 311980616,
  "EVENT_NAME": "单条集客A本地专线故障事件-设备脱网",
  "SRC_ORG_ALARM_TEXT": """
【发生时间】2026-02-09 14:03:50;
【告警对象】MSP;
【告警内容】设备脱网(影响1条电路);
""",
  "ALARM_NAME": "设备脱网(影响1条电路)",
  "VENDOR_NAME": "瑞斯康达",
  "CITY_NAME": "漳州市",
  "EQUIPMENT_NAME": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
  "NETWORK_TYPE_ID": "11",
  "OBJECT_CLASS_ID": 87002,
  "MAINTAIN_TEAM": "漳州漳浦集客铁通维护组"
}
'''
    
    print("测试数据预处理功能...")
    print("=" * 50)
    
    # 预处理数据
    processed_data = problematic_data.replace('"""', '"')
    print("原始数据长度:", len(problematic_data))
    print("处理后数据长度:", len(processed_data))
    
    try:
        # 解析处理后的数据
        es_data = json.loads(processed_data)
        print("✓ JSON解析成功")
        
        # 生成Kafka消息
        kafka_message = generate_es_to_kafka_mapping(es_data)
        print("✓ Kafka消息生成成功")
        
        print("\n生成的关键字段:")
        print(f"ID: {kafka_message.get('ID', 'N/A')}")
        print(f"NETWORK_TYPE_TOP: {kafka_message.get('NETWORK_TYPE_TOP', 'N/A')}")
        print(f"CITY_NAME: {kafka_message.get('CITY_NAME', 'N/A')}")
        print(f"EVENT_TIME: {kafka_message.get('EVENT_TIME', 'N/A')}")
        print(f"VENDOR_NAME: {kafka_message.get('VENDOR_NAME', 'N/A')}")
        print(f"TITLE_TEXT: {kafka_message.get('TITLE_TEXT', 'N/A')}")
        
        print("\n" + "=" * 50)
        print("测试成功完成!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON解析失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 处理失败: {e}")
        return False

def test_special_characters():
    """测试特殊字符处理"""
    print("\n测试特殊字符处理...")
    print("=" * 30)
    
    test_cases = [
        ('包含"""三重引号"""的数据', '包含"三重引号"的数据'),
        ('包含&lt;HTML&gt;实体', '包含<HTML>实体'),
        ('正常数据', '正常数据')
    ]
    
    for original, expected in test_cases:
        processed = original.replace('"""', '"').replace('&lt;', '<').replace('&gt;', '>')
        status = "✓" if processed == expected else "✗"
        print(f"{status} '{original}' → '{processed}'")

if __name__ == "__main__":
    success1 = test_data_preprocessing()
    test_special_characters()
    
    if success1:
        print("\n🎉 所有测试通过!")
    else:
        print("\n❌ 部分测试失败!")