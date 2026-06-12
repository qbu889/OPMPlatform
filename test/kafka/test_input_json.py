#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用输入json.json测试Kafka消息生成器
"""
import sys
import os
import json

sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')



def test_with_input_json():
    """使用输入json.json文件进行测试"""
    # 读取输入JSON文件
    input_file = '/Users/linziwang/PycharmProjects/wordToWord/test/kafka/输入json.json'
    
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return False
    
    print(f"📖 读取输入文件: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        kafka_message = json.load(f)
    
    print(f"✅ 成功读取JSON数据")
    print(f"   数据包含 {len(kafka_message)} 个字段")
    
    # 打印原始数据的关键字段
    print("\n=== 原始数据关键字段 ===")
    key_fields = ['ID', 'NETWORK_TYPE_TOP', 'ORG_SEVERITY', 'REGION_NAME', 'CITY_NAME', 'EQP_LABEL', 'EVENT_TIME', 'TITLE_TEXT']
    for field in key_fields:
        value = kafka_message.get(field, 'N/A')
        print(f"  {field}: {value}")
    
    # 测试：将Kafka消息作为ES数据重新生成
    print("\n=== 测试：将Kafka消息作为ES数据重新生成 ===")
    print("正在调用 generate_es_to_kafka_mapping...")
    
    try:
        # 将Kafka消息作为ES的_source数据传入
        generated = generate_es_to_kafka_mapping(kafka_message)
        
        print(f"✅ 成功生成Kafka消息")
        print(f"   生成的消息包含 {len(generated)} 个字段")
        
        # 验证生成结果
        print("\n=== 生成结果关键字段验证 ===")
        for field in key_fields:
            original = kafka_message.get(field, 'N/A')
            generated_val = generated.get(field, 'N/A')
            
            # 注意：ID是动态生成的，所以不会完全匹配
            if field == 'ID':
                status = "🔄" if generated_val != 'N/A' else "❌"
            else:
                status = "✅" if str(original) == str(generated_val) else "⚠️"
            
            print(f"  {status} {field}:")
            print(f"     原始: {original}")
            print(f"     生成: {generated_val}")
        
        # 检查ORG_TEXT字段（特殊处理）
        original_org_text = kafka_message.get('ORG_TEXT', '')
        generated_org_text = generated.get('ORG_TEXT', '')
        
        print(f"\n  📝 ORG_TEXT 字段:")
        print(f"     原始长度: {len(original_org_text)}")
        print(f"     生成长度: {len(generated_org_text)}")
        print(f"     前100字符匹配: {original_org_text[:100] == generated_org_text[:100]}")
        
        # 保存生成结果到临时文件
        output_file = '/Users/linziwang/PycharmProjects/wordToWord/test/kafka/生成输出.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(generated, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 生成结果已保存到: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("使用输入json.json测试Kafka消息生成器")
    print("=" * 60)
    
    success = test_with_input_json()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成！")
    else:
        print("❌ 测试失败！")
    print("=" * 60)