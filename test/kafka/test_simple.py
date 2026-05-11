#!/usr/bin/env python3
"""
简单集成测试 - 需要本地服务器运行
在CI环境中会被跳过（标记为slow）
"""
import pytest
import requests
import json

@pytest.mark.slow
@pytest.mark.integration
def test_kafka_generator_api():
    """测试Kafka生成器API（需要本地服务器）"""
    # 测试数据包含路径分隔符
    test_data = {
        "es_source_raw": '{"test":"\\n 中兴\\中\\兴\\n"}',
        "custom_fields": {}
    }

    print("发送测试数据...")
    print(f"原始数据：{repr(test_data['es_source_raw'])}")
    print()

    try:
        response = requests.post('http://127.0.0.1:5001/kafka-generator/generate', json=test_data, timeout=5)
        
        print(f"状态码：{response.status_code}")
        if response.status_code == 200:
            print("✅ 成功!")
        else:
            print(f"响应：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except requests.exceptions.ConnectionError:
        pytest.skip("本地服务器未运行，跳过集成测试")

if __name__ == "__main__":
    test_kafka_generator_api()
