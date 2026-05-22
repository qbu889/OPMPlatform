#!/usr/bin/env python3
"""测试Kafka生成器自定义字段修复"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

def test_custom_fields_fix():
    """测试自定义字段是否直接使用用户输入"""
    app = create_app('testing')
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # 测试数据
        es_source = {
            "EQUIPMENT_NAME": "原始设备名",
            "ALARM_LEVEL": "WARNING",
            "CITY_ID": 1,
            "ALARM_NAME": "测试告警",
            "BUSINESS_TAG": {
                "BUSINESS_TYPE": "传输网"
            }
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source),
            "custom_fields": {
                "EQP_LABEL": "自定义覆盖值"
            }
        }
        
        print("发送测试请求...")
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = json.loads(response.data)
            data = result.get('data', {})
            
            eqp_label = data.get('EQP_LABEL', '')
            print(f"EQP_LABEL 值: {eqp_label}")
            print(f"期望值: 自定义覆盖值")
            print(f"是否匹配: {eqp_label == '自定义覆盖值'}")
            
            if eqp_label == '自定义覆盖值':
                print("\n✅ 修复成功！自定义字段直接使用用户输入")
                return True
            else:
                print("\n❌ 修复失败！自定义字段仍然被合并")
                return False
        else:
            print(f"请求失败: {response.data}")
            return False

if __name__ == "__main__":
    print("="*60)
    print("测试 Kafka 生成器自定义字段修复")
    print("="*60)
    success = test_custom_fields_fix()
    sys.exit(0 if success else 1)
