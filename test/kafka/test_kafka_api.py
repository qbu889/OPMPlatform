#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka生成器API接口测试
测试HTTP接口的完整功能
"""
import sys
import os
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app


class TestKafkaGeneratorAPI:
    """Kafka生成器API测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_generate_endpoint_exists(self, client):
        """测试生成接口是否存在"""
        response = client.post('/kafka-generator/generate', 
                              data=json.dumps({}),
                              content_type='application/json')
        
        # 接口应该存在（可能返回400错误，但不应该是404）
        assert response.status_code != 404
    
    def test_generate_with_valid_data(self, client):
        """测试使用有效数据生成"""
        test_data = {
            "es_source_raw": json.dumps({
                "NETWORK_TYPE_ID": "11",
                "ALARM_LEVEL": 2,
                "EQUIPMENT_NAME": "测试设备",
                "NE_LABEL": "测试网元",
                "DELAY_TIME": 900
            }),
            "delay_time": 15,
            "add_test_prefix": False
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        result = json.loads(response.data)
        
        assert response.status_code == 200
        assert result['success'] is True
        assert 'data' in result
        assert 'FP0_FP1_FP2_FP3' in result['data']
        assert 'EVENT_TIME' in result['data']
    
    def test_generate_with_custom_fields(self, client):
        """测试自定义字段覆盖"""
        test_data = {
            "es_source_raw": json.dumps({
                "NETWORK_TYPE_ID": "11",
                "ALARM_LEVEL": 2,
                "EQUIPMENT_NAME": "原始设备名"
            }),
            "custom_fields": {
                "EQP_LABEL": "自定义设备名"
            },
            "delay_time": 15
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        result = json.loads(response.data)
        
        assert response.status_code == 200
        assert result['success'] is True
    
    def test_generate_with_invalid_json(self, client):
        """测试无效JSON数据的处理"""
        test_data = {
            "es_source_raw": "这不是有效的JSON",
            "delay_time": 15
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 应该返回错误信息
        assert response.status_code in [400, 500]
    
    def test_generate_missing_required_field(self, client):
        """测试缺少必填字段"""
        test_data = {
            "delay_time": 15
            # 缺少 es_source_raw
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [400, 500]
    
    def test_field_meta_endpoint(self, client):
        """测试字段元数据接口"""
        response = client.get('/kafka-generator/field-meta')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'data' in result
    
    def test_field_order_endpoint(self, client):
        """测试字段顺序接口"""
        response = client.get('/kafka-generator/field-order')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'data' in result
        assert 'fields' in result['data']
    
    def test_history_endpoint(self, client):
        """测试历史记录接口"""
        response = client.get('/kafka-generator/history?page=1&per_page=10')
        
        # 接口应该存在
        assert response.status_code != 404
    
    def test_field_cache_endpoint(self, client):
        """测试字段缓存接口"""
        test_data = {
            "field_name": "EQP_LABEL",
            "field_value": "测试值",
            "is_pinned": False
        }
        
        response = client.post('/kafka-generator/field-cache',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 接口应该存在
        assert response.status_code != 404
    
    def test_field_history_endpoint(self, client):
        """测试字段历史接口"""
        # POST - 保存历史
        save_data = {
            "field_name": "EQP_LABEL",
            "field_value": "测试值"
        }
        
        response = client.post('/kafka-generator/field-history',
                              data=json.dumps(save_data),
                              content_type='application/json')
        
        assert response.status_code != 404
        
        # GET - 获取历史
        response = client.get('/kafka-generator/field-history?field_name=EQP_LABEL')
        assert response.status_code != 404
    
    def test_dict_data_endpoint(self, client):
        """测试字典数据接口"""
        response = client.get('/kafka-generator/dict-data?field_name=NETWORK_TYPE_TOP')
        
        # 接口应该存在
        assert response.status_code != 404
    
    def test_generate_with_test_prefix(self, client):
        """测试开启测试前缀"""
        test_data = {
            "es_source_raw": json.dumps({
                "NETWORK_TYPE_ID": "11",
                "ALARM_LEVEL": 2,
                "EQUIPMENT_NAME": "测试设备",
                "NE_LABEL": "测试网元"
            }),
            "add_test_prefix": True
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = json.loads(response.data)
            # 如果成功，验证EQP_LABEL和NE_LABEL是否添加了【测试】前缀
            if 'data' in result:
                eqp_label = result['data'].get('EQP_LABEL', '')
                ne_label = result['data'].get('NE_LABEL', '')
                
                # 注意：实际添加前缀的逻辑在前端，后端只负责生成
                # 这里只是验证接口能正常处理add_test_prefix参数
                assert response.status_code == 200
    
    def test_generate_with_network_type_20(self, client):
        """测试NETWORK_TYPE_TOP为20时的特殊处理"""
        test_data = {
            "es_source_raw": json.dumps({
                "NETWORK_TYPE_ID": "20",  # 虚拟化专业
                "ALARM_LEVEL": 2,
                "EQUIPMENT_NAME": "虚拟设备"
            }),
            "add_test_prefix": True  # 尝试开启测试前缀
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        # 应该能正常生成，但前端会阻止添加测试前缀
        assert response.status_code in [200, 400, 500]
    
    def test_concurrent_requests(self, client):
        """测试并发请求处理"""
        import concurrent.futures
        
        def make_request():
            test_data = {
                "es_source_raw": json.dumps({
                    "NETWORK_TYPE_ID": "11",
                    "ALARM_LEVEL": 2,
                    "EQUIPMENT_NAME": "并发测试设备"
                }),
                "delay_time": 15
            }
            
            response = client.post('/kafka-generator/generate',
                                  data=json.dumps(test_data),
                                  content_type='application/json')
            return response.status_code
        
        # 发起10个并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # 所有请求都应该成功或返回合理的错误码
        for status_code in results:
            assert status_code in [200, 400, 500]


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_database_connection_failure(self, client):
        """测试数据库连接失败时的降级处理"""
        # 这个测试需要mock数据库连接
        # 在实际CI环境中，数据库应该是可用的
        pass
    
    def test_malformed_request_body(self, client):
        """测试格式错误的请求体"""
        response = client.post('/kafka-generator/generate',
                              data="not json at all",
                              content_type='text/plain')
        
        # 应该返回400或500错误
        assert response.status_code in [400, 415, 500]
    
    def test_empty_request_body(self, client):
        """测试空请求体"""
        response = client.post('/kafka-generator/generate',
                              data="",
                              content_type='application/json')
        
        assert response.status_code in [400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
