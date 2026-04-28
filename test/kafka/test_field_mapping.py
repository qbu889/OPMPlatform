#!/usr/bin/env python3
"""测试 Kafka 字段映射功能"""
import requests
import json

BASE_URL = "http://localhost:5004"

print("=" * 80)
print("Kafka 字段映射功能测试")
print("=" * 80)

# 测试 1: 获取字段映射列表
print("\n1️⃣  测试获取字段映射列表")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/kafka-generator/field-meta/list", params={
        "page": 1,
        "per_page": 10
    })
    result = response.json()
    if result['success']:
        print(f"✅ 获取成功，共 {result['data']['total']} 条记录")
        if result['data']['list']:
            print(f"   第一条记录: {result['data']['list'][0]['kafka_field']} -> {result['data']['list'][0]['es_field']}")
    else:
        print(f"❌ 获取失败: {result['message']}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 2: 新增字段映射
print("\n2️⃣  测试新增字段映射")
print("-" * 80)
try:
    response = requests.post(f"{BASE_URL}/kafka-generator/field-meta", json={
        "kafka_field": "TEST_STANDARD_ALARM_ID",
        "es_field": "ALARM_STANDARD_ID",
        "db_cn": "告警标准化ID",
        "label_cn": "网管告警ID",
        "remark": "测试数据"
    })
    result = response.json()
    if result['success']:
        print(f"✅ 新增成功: {result['data']['kafka_field']}")
    else:
        print(f"⚠️  新增失败（可能已存在）: {result['message']}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 3: 搜索字段映射
print("\n3️⃣  测试搜索字段映射")
print("-" * 80)
try:
    response = requests.get(f"{BASE_URL}/kafka-generator/field-meta/list", params={
        "keyword": "STANDARD_ALARM_ID"
    })
    result = response.json()
    if result['success']:
        print(f"✅ 搜索成功，找到 {result['data']['total']} 条记录")
        for item in result['data']['list'][:3]:
            print(f"   - {item['kafka_field']} -> {item['es_field']}")
    else:
        print(f"❌ 搜索失败: {result['message']}")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 4: 更新字段映射
print("\n4️⃣  测试更新字段映射")
print("-" * 80)
try:
    # 先获取一条记录的 ID
    response = requests.get(f"{BASE_URL}/kafka-generator/field-meta/list", params={
        "keyword": "TEST_STANDARD_ALARM_ID"
    })
    result = response.json()
    if result['success'] and result['data']['list']:
        record_id = result['data']['list'][0]['id']
        
        # 更新备注
        response = requests.put(f"{BASE_URL}/kafka-generator/field-meta/{record_id}", json={
            "es_field": "ALARM_STANDARD_ID",
            "db_cn": "告警标准化ID",
            "label_cn": "网管告警ID",
            "remark": "更新后的测试备注",
            "is_enabled": 1
        })
        update_result = response.json()
        if update_result['success']:
            print(f"✅ 更新成功: ID={record_id}")
        else:
            print(f"❌ 更新失败: {update_result['message']}")
    else:
        print("⚠️  未找到测试记录，跳过更新测试")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 5: 删除字段映射
print("\n5️⃣  测试删除字段映射")
print("-" * 80)
try:
    # 先获取一条记录的 ID
    response = requests.get(f"{BASE_URL}/kafka-generator/field-meta/list", params={
        "keyword": "TEST_STANDARD_ALARM_ID"
    })
    result = response.json()
    if result['success'] and result['data']['list']:
        record_id = result['data']['list'][0]['id']
        
        # 删除
        response = requests.delete(f"{BASE_URL}/kafka-generator/field-meta/{record_id}")
        delete_result = response.json()
        if delete_result['success']:
            print(f"✅ 删除成功: ID={record_id}")
        else:
            print(f"❌ 删除失败: {delete_result['message']}")
    else:
        print("⚠️  未找到测试记录，跳过删除测试")
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 测试 6: 验证动态映射是否生效
print("\n6️⃣  测试生成 Kafka 消息时是否使用数据库映射")
print("-" * 80)
try:
    # 读取测试数据
    with open('test/run/1.txt', 'r', encoding='utf-8') as f:
        es_source_raw = f.read()
    
    response = requests.post(f"{BASE_URL}/kafka-generator/generate", json={
        "es_source_raw": es_source_raw,
        "custom_fields": {},
        "delay_time": 15,
        "add_test_prefix": True
    })
    result = response.json()
    
    if result['success']:
        kafka_message = result['data']['kafka_message']
        standard_alarm_id = kafka_message.get('STANDARD_ALARM_ID', '')
        
        # 检查是否从 ES 数据中正确映射
        print(f"✅ Kafka 消息生成成功")
        print(f"   STANDARD_ALARM_ID: {standard_alarm_id}")
        
        # 如果 ES 数据中有 ALARM_STANDARD_ID，应该被映射到 STANDARD_ALARM_ID
        import json as json_module
        es_data = json_module.loads(es_source_raw)
        expected_value = es_data.get('_source', {}).get('ALARM_STANDARD_ID', '')
        
        if str(expected_value) == str(standard_alarm_id):
            print(f"   ✅ 字段映射正确！ES 中的 ALARM_STANDARD_ID 已映射到 Kafka 的 STANDARD_ALARM_ID")
        else:
            print(f"   ⚠️  字段映射可能不正确")
            print(f"      ES 中的 ALARM_STANDARD_ID: {expected_value}")
            print(f"      Kafka 中的 STANDARD_ALARM_ID: {standard_alarm_id}")
    else:
        print(f"❌ 生成失败: {result['message']}")
except FileNotFoundError:
    print("⚠️  测试文件 test/run/1.txt 不存在，跳过此测试")
except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)
