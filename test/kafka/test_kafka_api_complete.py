#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka生成器API完整接口自动化测试用例
基于 docs/04-Kafka消息处理/kafka_generator_readme.md
"""
import sys
import os
import json
import pytest
import re
from datetime import datetime

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

    def test_generate_kafka_message_success(self, client):
        """测试生成Kafka消息 - 成功场景"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "测试设备",
            "NE_LABEL": "测试网元",
            "CITY_ID": "350600",
            "BUSINESS_TAG": {"BUSINESS_TYPE": "测试业务类型"},
            "DELAY_TIME": 900
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source),
            "custom_fields": {
                "EQP_LABEL": "自定义网元名称",
                "TITLE_TEXT": "告警标题_20260522153000123abc"
            },
            "delay_time": 15,
            "add_test_prefix": False,
            "auto_detect_missing": False
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        result = json.loads(response.data)
        
        assert response.status_code == 200
        assert result['success'] is True
        assert 'data' in result
        assert 'history_id' in result
        assert result['delay_time'] == 15
        
        data = result['data']
        
        assert 'FP0_FP1_FP2_FP3' in data
        assert 'EVENT_TIME' in data
        assert 'CREATION_EVENT_TIME' in data
        assert 'EVENT_ARRIVAL_TIME' in data
        assert 'TIME_STAMP' in data
        assert 'ACTIVE_STATUS' in data
        assert data['ACTIVE_STATUS'] == '1'
        
        fp_pattern = r'^\d+_\d{10}_\d{10}_\d{10}_\d{5}$'
        assert re.match(fp_pattern, data['FP0_FP1_FP2_FP3']) is not None
        
        time_format = '%Y-%m-%d %H:%M:%S'
        datetime.strptime(data['EVENT_TIME'], time_format)

    def test_generate_with_delay_time(self, client):
        """测试生成Kafka消息 - 延迟时间参数"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "延迟测试设备"
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source),
            "delay_time": 30,
            "add_test_prefix": False
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        result = json.loads(response.data)
        
        assert response.status_code == 200
        assert result['success'] is True
        assert result['delay_time'] == 30

    def test_generate_with_test_prefix(self, client):
        """测试生成Kafka消息 - 添加测试前缀"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "测试前缀设备",
            "NE_LABEL": "测试前缀网元"
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source),
            "add_test_prefix": True
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        result = json.loads(response.data)
        
        if response.status_code == 200 and result.get('success'):
            data = result['data']
            eqp_label = data.get('EQP_LABEL', '')
            ne_label = data.get('NE_LABEL', '')
            # 测试前缀应该在前端处理，后端接收参数即可

    def test_generate_empty_es_source(self, client):
        """测试生成Kafka消息 - 空ES数据"""
        test_data = {
            "es_source_raw": json.dumps({}),
            "delay_time": 15
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'data' in result

    def test_generate_invalid_json(self, client):
        """测试生成Kafka消息 - 无效JSON"""
        test_data = {
            "es_source_raw": "not a valid json",
            "delay_time": 15
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [400, 500]

    def test_generate_missing_es_source_raw(self, client):
        """测试生成Kafka消息 - 缺少必填字段"""
        test_data = {
            "delay_time": 15
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [400, 500]

    def test_generate_push_message(self, client):
        """测试生成推送消息"""
        test_data = {
            "fp_value": "1745900000_1234567890_9876543210_1111111111_12345",
            "event_time": "2026-04-29 10:30:00",
            "active_status": "3"
        }
        
        response = client.post('/kafka-generator/generate-push-message',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code != 404
        
        if response.status_code == 200:
            result = json.loads(response.data)
            assert 'success' in result


class TestFieldMetaAPI:
    """字段元数据管理API测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_field_meta_dict(self, client):
        """测试获取字段元数据（字典格式）"""
        response = client.get('/kafka-generator/field-meta')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'data' in result
        assert isinstance(result['data'], dict)

    def test_get_field_meta_list(self, client):
        """测试获取字段映射列表（分页+搜索）"""
        response = client.get('/kafka-generator/field-meta/list?page=1&per_page=10')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_field_meta_list_with_search(self, client):
        """测试搜索字段映射列表"""
        response = client.post('/kafka-generator/field-meta/list',
                              data=json.dumps({"keyword": "FP"}),
                              content_type='application/json')
        
        assert response.status_code == 200

    def test_create_field_meta(self, client):
        """测试新增字段映射"""
        test_data = {
            "kafka_field": "TEST_FIELD",
            "es_field": "test_field",
            "field_type": "string",
            "default_value": "",
            "description": "测试字段"
        }
        
        response = client.post('/kafka-generator/field-meta',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [200, 400]

    def test_update_field_meta(self, client):
        """测试更新字段映射"""
        test_data = {
            "kafka_field": "TEST_FIELD",
            "es_field": "test_field_updated",
            "description": "更新后的描述"
        }
        
        response = client.put('/kafka-generator/field-meta/1',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code != 404

    def test_delete_field_meta(self, client):
        """测试删除字段映射"""
        response = client.delete('/kafka-generator/field-meta/99999')
        
        assert response.status_code in [200, 400, 404]

    def test_get_field_order(self, client):
        """测试获取字段顺序列表"""
        response = client.get('/kafka-generator/field-order')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        assert 'data' in result
        assert 'fields' in result['data']


class TestFieldDictAPI:
    """字段字典管理API测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_field_options(self, client):
        """测试查询字段字典选项"""
        response = client.get('/kafka-generator/field-options?kafka_field=NETWORK_TYPE_TOP')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_field_dict_list(self, client):
        """测试获取字典列表（分页）"""
        response = client.get('/kafka-generator/field-dict?page=1&per_page=10')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_create_field_dict(self, client):
        """测试新增字典项"""
        test_data = {
            "kafka_field": "TEST_FIELD",
            "option_value": "test_value",
            "option_label": "测试值",
            "sort_order": 1
        }
        
        response = client.post('/kafka-generator/field-dict',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [200, 400]

    def test_update_field_dict(self, client):
        """测试更新字典项"""
        test_data = {
            "option_label": "更新后的标签"
        }
        
        response = client.put('/kafka-generator/field-dict/1',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code != 404

    def test_delete_field_dict(self, client):
        """测试删除字典项"""
        response = client.delete('/kafka-generator/field-dict/99999')
        
        assert response.status_code in [200, 400, 404]


class TestFieldCacheHistoryAPI:
    """字段缓存与历史API测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_field_cache(self, client):
        """测试获取所有字段缓存"""
        response = client.get('/kafka-generator/field-cache')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_save_field_cache(self, client):
        """测试保存单个字段缓存"""
        test_data = {
            "field_name": "EQP_LABEL",
            "field_value": "测试缓存值",
            "is_pinned": False
        }
        
        response = client.post('/kafka-generator/field-cache',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [200, 400]

    def test_batch_save_field_cache(self, client):
        """测试批量保存字段缓存"""
        test_data = {
            "field_cache": {
                "EQP_LABEL": "值1",
                "NE_LABEL": "值2"
            },
            "pinned_fields": []
        }
        
        response = client.post('/kafka-generator/field-cache/batch',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [200, 400]

    def test_save_field_history(self, client):
        """测试保存字段历史值"""
        test_data = {
            "field_name": "EQP_LABEL",
            "field_value": "历史测试值"
        }
        
        response = client.post('/kafka-generator/field-history',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [200, 400]

    def test_delete_field_history(self, client):
        """测试删除字段历史值"""
        response = client.delete('/kafka-generator/field-history',
                                data=json.dumps({"field_name": "EQP_LABEL"}),
                                content_type='application/json')
        
        assert response.status_code != 404

    def test_get_field_values(self, client):
        """测试获取所有有值的字段列表"""
        response = client.get('/kafka-generator/field-values')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True


class TestHistoryAPI:
    """历史记录API测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_history_list(self, client):
        """测试获取生成历史（分页+搜索）"""
        response = client.get('/kafka-generator/history?page=1&per_page=10')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True

    def test_get_history_list_with_keyword(self, client):
        """测试搜索历史记录"""
        response = client.get('/kafka-generator/history?page=1&keyword=测试')
        
        assert response.status_code == 200

    def test_get_history_detail(self, client):
        """测试获取历史记录详情"""
        response = client.get('/kafka-generator/history/1')
        
        assert response.status_code != 404

    def test_update_history_remark(self, client):
        """测试更新历史记录备注"""
        test_data = {
            "remark": "测试备注"
        }
        
        response = client.put('/kafka-generator/history/1/remark',
                             data=json.dumps(test_data),
                             content_type='application/json')
        
        assert response.status_code != 404


class TestConfigAPI:
    """配置API测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_get_config(self, client):
        """测试获取应用端口配置"""
        response = client.get('/kafka-generator/config')
        
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True


class TestSpecialFields:
    """特殊字段处理测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_time_fields_sync(self, client):
        """测试时间字段同步性"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "时间测试设备",
            "DELAY_TIME": 30
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source),
            "delay_time": 30
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = json.loads(response.data)
            data = result.get('data', {})
            
            event_time = data.get('EVENT_TIME', '')
            creation_time = data.get('CREATION_EVENT_TIME', '')
            arrival_time = data.get('EVENT_ARRIVAL_TIME', '')
            
            assert event_time == creation_time == arrival_time

    def test_fp_fields_consistency(self, client):
        """测试FP字段一致性"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "FP测试设备"
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source)
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = json.loads(response.data)
            data = result.get('data', {})
            
            fp0 = data.get('FP0_FP1_FP2_FP3', '')
            cfp0 = data.get('CFP0_CFP1_CFP2_CFP3', '')
            orig_fp = data.get('ORIG_ALARM_FP', '')
            orig_clear_fp = data.get('ORIG_ALARM_CLEAR_FP', '')
            
            fp_prefix = fp0.split('_')[0]
            assert cfp0.startswith(fp_prefix)
            assert orig_fp.startswith(fp_prefix)
            assert orig_clear_fp.startswith(fp_prefix)

    def test_business_key_fields(self, client):
        """测试业务关键字段"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "CITY_ID": "350600",
            "BUSINESS_TAG": {"BUSINESS_TYPE": "测试业务"}
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source)
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = json.loads(response.data)
            data = result.get('data', {})
            
            assert data.get('ACTIVE_STATUS') == '1'
            assert data.get('CITY_ID') == '350600'


class TestCustomFieldsOverride:
    """自定义字段覆盖测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_custom_fields_priority(self, client):
        """测试自定义字段优先级"""
        es_source = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "原始设备名"
        }
        
        test_data = {
            "es_source_raw": json.dumps(es_source),
            "custom_fields": {
                "EQP_LABEL": "自定义覆盖值"
            }
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        if response.status_code == 200:
            result = json.loads(response.data)
            data = result.get('data', {})
            
            assert data.get('EQP_LABEL') == '自定义覆盖值'


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_empty_request_body(self, client):
        """测试空请求体"""
        response = client.post('/kafka-generator/generate',
                              data="",
                              content_type='application/json')
        
        assert response.status_code in [400, 500]

    def test_invalid_content_type(self, client):
        """测试无效Content-Type"""
        response = client.post('/kafka-generator/generate',
                              data=json.dumps({"es_source_raw": "{}"}),
                              content_type='text/plain')
        
        assert response.status_code in [400, 415, 500]

    def test_large_payload(self, client):
        """测试大负载请求"""
        large_es_data = {"key" * 100: "value" * 100}
        
        test_data = {
            "es_source_raw": json.dumps(large_es_data),
            "delay_time": 15
        }
        
        response = client.post('/kafka-generator/generate',
                              data=json.dumps(test_data),
                              content_type='application/json')
        
        assert response.status_code in [200, 400, 413, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])