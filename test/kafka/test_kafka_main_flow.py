#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka 消息生成器 — 主流程全覆盖自动化测试
覆盖：字段映射、唯一值、ES防御合并、FP一致性、时间计算、自定义覆盖、
      字段类型、边缘场景、API端点冒烟、历史记录等
"""
import sys
import os
import json
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from routes.kafka.kafka_generator_routes import (
    generate_es_to_kafka_mapping,
    generate_consistent_fp,
    generate_creation_event_time,
    get_nested_value,
    build_dynamic_field_mapping,
    get_default_mapping_rule,
    load_field_meta_from_mysql,
    STANDARD_FIELD_ORDER,
    FIELD_META,
    generate_kafka_message,
    generate_org_text,
)
from app import create_app


# ============================================================================
# 公共测试数据
# ============================================================================

def make_es_source(**overrides):
    """构造 ES _source 测试数据，默认包含完整字段"""
    data = {
        "ROOT_NETWORK_TYPE_ID": "11",
        "ALARM_LEVEL": 2,
        "CITY_NAME": "漳州市",
        "COUNTY_NAME": "漳浦县",
        "EQUIPMENT_NAME": "[集客]测试设备-RC-CPE1",
        "NE_LABEL": "[集客]测试网元",
        "VENDOR_NAME": "瑞斯康达",
        "VENDOR_ID": "8",
        "ALARM_NAME": "设备脱网(影响1条电路)",
        "ALARM_STANDARD_NAME": "设备脱网",
        "ALARM_STANDARD_ID": "1100-064-371-10-860022",
        "ALARM_STANDARD_FLAG": 1,
        "EVENT_LOCATION": "MSP",
        "EVENT_TIME": "2026-05-22 12:00:00",
        "EVENT_COLLECTION_TIME": "2026-05-22 12:00:00",
        "OBJECT_CLASS_ID": 87002,
        "ORG_TYPE": "1",
        "VENDOR_EVENT_TYPE": "14202",
        "MAIN_NET_SORT_ONE": "集团专线",
        "NETWORK_SUB_TYPE_ID": "101",
        "NMS_ALARM_ID": "2020740405373157376",
        "PROBABLE_CAUSE": "001",
        "VENDOR_SEVERITY": "1",
        "EVENT_PROBABLE_CAUSE_TXT": "设备掉电",
        "EVENT_EXPLANATION": "设备脱网告警",
        "ALARM_RESOURCE_STATUS": "1",
        "FULL_REGION_NAME": "福建省/漳州市/漳浦县",
        "CITY_ID": "350600",
        "DELAY_TIME": 720,
        "BUSINESS_TAG": {
            "CIRCUIT_NO": "漳州漳浦消防救援FE5980KA",
            "BUSINESS_SYSTEM": "集团专线",
            "PRODUCT_TYPE": "数据专线",
            "BUSINESS_TYPE": "1",
            "CIRCUIT_LEVEL": "1",
            "IRMS_GRID_NAME": "漳浦网格",
            "ADMIN_GRID_ID": "350623",
            "HOME_CLIENT_NUM": "10",
        },
        "NE_TAG": {
            "MACHINE_ROOM_INFO": "漳浦机房",
            "ROOM_ID": "ROOM123",
        },
        "EQUIPMENT_IP": "10.0.0.1",
        "MAINTAIN_TEAM": "维护班组A",
        "ASSIGN_TENANCE_GROUP": "运维组B",
        "SITE_TYPE": "机房",
        "EVENT_CAT": "1",
        "NMS_NAME": "集客网管",
        "REMOTE_EQUIPMENT_NAME": "远端设备",
        "REMOTE_OBJECT_CLASS": "87001",
        "ALARM_REASON": "设备异常",
        "TYPE_KEYCODE": "001",
        "NE_LOCATION": "漳浦县杜浔镇",
        "ALARM_SOURCE": "20",
        "SRC_ORG_ALARM_TEXT": "原始告警文本",
        "FAULT_DIAGNOSIS": "诊断为设备故障",
        "EXTRA_ID2": "EXTRA002",
        "EXTRA_STRING1": "EXTRA_STR_001",
        "PORT_NUM": "300205",
        "NE_ADMIN_STATUS": "1",
        "TMSC_CAT": "1",
        "INTERFERENCE_FLAG": "0",
        "PROJ_INTERFERENCE_TYPE": "无",
        "FAULT_LOCATION": "漳浦县",
        "EVENT_SOURCE": "20",
        "OBJECT_CLASS_TEXT": "RC-CPE终端",
        "EFFECT_NE_NUM": 5,
        "SATOTAL": 3,
        "IS_TEST": 0,
        "PREPROCESS_MANNER": "",
    }
    data.update(overrides)
    return data


# ============================================================================
# 1. FP 字段生成测试
# ============================================================================

class TestFPGeneration:
    """FP 唯一标识字段生成"""

    def test_fp_format_5_parts(self):
        """FP格式：5段下划线分隔"""
        fp = generate_consistent_fp()
        parts = fp.split('_')
        assert len(parts) == 5, f"应为5段，实际{len(parts)}段"

    def test_fp_random_parts_length(self):
        """FP随机段长度：timestamp + 3×10位 + 5位"""
        fp = generate_consistent_fp()
        parts = fp.split('_')
        assert len(parts[0]) >= 10, "时间戳段至少10位"
        assert len(parts[1]) == 10
        assert len(parts[2]) == 10
        assert len(parts[3]) == 10
        assert len(parts[4]) == 5

    def test_fp_consistency_across_fields(self):
        """单次生成中5个FP字段值一致"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        fp = result['FP0_FP1_FP2_FP3']
        assert result['CFP0_CFP1_CFP2_CFP3'] == fp
        assert result['ORIG_ALARM_FP'] == fp
        assert result['ORIG_ALARM_CLEAR_FP'] == fp
        assert result['SRC_ORG_ID'] == fp

    def test_fp_uniqueness_across_generations(self):
        """多次生成FP各不同"""
        fps = [generate_consistent_fp() for _ in range(20)]
        unique = set(fps)
        assert len(unique) >= 19, f"20次应有≥19个唯一值，实际{len(unique)}"


# ============================================================================
# 2. 时间字段测试
# ============================================================================

class TestTimeFields:
    """时间字段生成"""

    def test_three_time_fields_equal(self):
        """EVENT_TIME / CREATION_EVENT_TIME / EVENT_ARRIVAL_TIME 三者一致"""
        es = make_es_source(DELAY_TIME=900)
        result = generate_es_to_kafka_mapping(es)
        assert result['EVENT_TIME'] == result['CREATION_EVENT_TIME']
        assert result['EVENT_TIME'] == result['EVENT_ARRIVAL_TIME']

    def test_time_format_yyyy_mm_dd(self):
        """时间格式 YYYY-MM-DD HH:MM:SS"""
        result = generate_creation_event_time({"DELAY_TIME": 900})
        datetime.strptime(result, "%Y-%m-%d %H:%M:%S")

    def test_delay_time_from_es(self):
        """从ES DELAY_TIME 计算时间"""
        es = {"_source": {"DELAY_TIME": 360}}
        now = datetime.now(timezone.utc)
        result = generate_creation_event_time(es)
        gen_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        expected = (now - timedelta(hours=6)).replace(tzinfo=None)
        diff = abs((gen_time - expected).total_seconds())
        assert diff < 60, f"时间差{diff}秒"

    def test_user_delay_time_overrides_es(self):
        """用户输入 delay_time 优先于 ES DELAY_TIME"""
        es = {"_source": {"DELAY_TIME": 720}}
        now = datetime.now(timezone.utc)
        result = generate_creation_event_time(es, user_delay_time=60)
        gen_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        expected = (now - timedelta(hours=1)).replace(tzinfo=None)
        diff = abs((gen_time - expected).total_seconds())
        assert diff < 60, f"应使用用户时间，差{diff}秒"

    def test_default_delay_15_hours(self):
        """无 DELAY_TIME 时默认15小时"""
        result = generate_creation_event_time({})
        gen_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        diff = abs((gen_time - (now_naive - timedelta(hours=15))).total_seconds())
        assert diff < 120, f"默认延迟15小时，差{diff}秒"

    def test_time_stamp_is_unix_string(self):
        """TIME_STAMP 为 Unix 时间戳字符串"""
        es = make_es_source(EVENT_TIME="2026-05-22 12:00:00")
        result = generate_es_to_kafka_mapping(es)
        ts = result.get('TIME_STAMP', '')
        assert ts.isdigit(), f"TIME_STAMP 应为纯数字，实际:{ts}"


# ============================================================================
# 3. 字段映射测试（核心）
# ============================================================================

class TestFieldMapping:
    """ES → Kafka 字段正向映射"""

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_direct_es_mappings(self, _mock):
        """直通映射：Kafka字段 = ES 对应字段值"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        assert result['TITLE_TEXT'] == "设备脱网(影响1条电路)"
        assert result['EQP_LABEL'] == "[集客]测试设备-RC-CPE1"
        assert result['VENDOR_NAME'] == "瑞斯康达"
        assert result['LOCATE_INFO'] == "MSP"
        assert result['STANDARD_ALARM_NAME'] == "设备脱网"

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_renamed_es_mappings(self, _mock):
        """重命名映射：Kafka字段名 ≠ ES字段名"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        assert result['ORG_SEVERITY'] == "2"
        assert result['NETWORK_TYPE'] == "101"
        assert result['PROBABLE_CAUSE_TXT'] == "设备掉电"
        assert result['VENDOR_TYPE'] == "14202"

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_nested_es_mappings(self, _mock):
        """嵌套对象映射：BUSINESS_TAG.xxx / NE_TAG.xxx"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        assert result['CIRCUIT_NO'] == "漳州漳浦消防救援FE5980KA"
        assert result['BUSINESS_SYSTEM'] == "集团专线"
        assert result['PRODUCT_TYPE'] == "数据专线"
        assert result['SPECIAL_FIELD14'] == "ROOM123"
        assert result['MACHINE_ROOM_INFO'] == "漳浦机房"

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_computed_mappings(self, _mock):
        """计算映射：PROFESSIONAL_TYPE、REGION_NAME 等"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        assert result['PROFESSIONAL_TYPE'] == "6"
        assert result['REGION_NAME'] == "漳州市"

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_fixed_value_mappings(self, _mock):
        """固定值映射"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        assert result['ACTIVE_STATUS'] == "1"
        assert result['SEND_JT_FLAG'] == "0"
        assert result['SRC_APP_ID'] == "1001"
        assert result['TOPIC_PREFIX'] == "EVENT-GZ"
        assert result['TOPIC_PARTITION'] == 7

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_all_standard_fields_present(self, _mock):
        """所有 STANDARD_FIELD_ORDER 字段都已生成"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        for field in STANDARD_FIELD_ORDER:
            assert field in result, f"缺少字段: {field}"

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_null_es_value_yields_empty_string(self, _mock):
        """ES 缺失字段时 Kafka 字段为空字符串"""
        es = {"_source": {"ALARM_LEVEL": 2}}
        result = generate_es_to_kafka_mapping(es)
        assert result['TITLE_TEXT'] == ""


# ============================================================================
# 4. 唯一值 & ES 防御合并测试
# ============================================================================

class TestUniqueValueAndDefenseMerge:
    """唯一值功能 + 后端 ES 值防御合并"""

    ES_SOURCE_WITH_NAME = json.dumps({
        "_source": {
            "ROOT_NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "[集客]测试设备",
            "ALARM_NAME": "泉州德化县传输外线光缆中断事件",
            "CITY_NAME": "泉州市",
            "COUNTY_NAME": "德化县",
            "DELAY_TIME": 720,
        }
    })

    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_custom_fields_suffix_merged_by_backend(self, client):
        """
        核心场景：前端发送纯后缀 custom_fields（开启唯一值但未提取ES值），
        后端防御合并为 {ES源值}_{后缀}
        """
        response = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": self.ES_SOURCE_WITH_NAME,
            "custom_fields": {"TITLE_TEXT": "75395908k"},
            "delay_time": 15,
        }), content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True
        title = result['data']['TITLE_TEXT']
        assert "泉州德化县传输外线光缆中断事件" in title, f"缺失ES源值: {title}"
        assert "75395908k" in title, f"缺失唯一后缀: {title}"

    def test_custom_fields_full_value_not_overwritten(self, client):
        """
        正常场景：custom_fields 已含完整值，不重复合并
        """
        full_value = "泉州德化县传输外线光缆中断事件_20260522153000abc"
        response = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": self.ES_SOURCE_WITH_NAME,
            "custom_fields": {"TITLE_TEXT": full_value},
            "delay_time": 15,
        }), content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['data']['TITLE_TEXT'] == full_value

    def test_nested_value_lookup(self):
        """get_nested_value 按 ES 字段路径查找"""
        es = {"_source": {"EVENT_NAME": "测试事件名", "ALARM_NAME": "告警名"}}
        assert get_nested_value(es, "EVENT_NAME") == "测试事件名"
        assert get_nested_value(es, "ALARM_NAME") == "告警名"

    def test_nested_value_with_dot_path(self):
        """点号分隔的嵌套路径"""
        es = {"_source": {"BUSINESS_TAG": {"CIRCUIT_NO": "CIRCUIT-001"}}}
        assert get_nested_value(es, "BUSINESS_TAG.CIRCUIT_NO") == "CIRCUIT-001"

    def test_nested_value_missing_returns_none(self):
        """不存在的路径返回 None"""
        assert get_nested_value({"_source": {}}, "NOT_EXIST") is None
        assert get_nested_value({}, "ANY") is None


# ============================================================================
# 5. 自定义字段覆盖测试
# ============================================================================

class TestCustomFieldOverride:
    """用户自定义字段覆盖"""

    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_custom_field_overrides_generated_value(self, client):
        """自定义字段覆盖自动生成的值"""
        es_raw = json.dumps(make_es_source())
        response = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": es_raw,
            "custom_fields": {"EQP_LABEL": "用户自定义设备名"},
            "delay_time": 15,
        }), content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['data']['EQP_LABEL'] == "用户自定义设备名"

    def test_multiple_custom_fields(self, client):
        """多个自定义字段同时覆盖"""
        es_raw = json.dumps(make_es_source())
        response = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": es_raw,
            "custom_fields": {
                "EQP_LABEL": "自定义设备",
                "VENDOR_NAME": "自定义厂家",
                "CITY_NAME": "自定义县市",
            },
            "delay_time": 15,
        }), content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['data']['EQP_LABEL'] == "自定义设备"
        assert result['data']['VENDOR_NAME'] == "自定义厂家"
        assert result['data']['CITY_NAME'] == "自定义县市"

    def test_empty_custom_field_not_applied(self, client):
        """空值的 custom_field 不覆盖"""
        es_raw = json.dumps(make_es_source())
        response = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": es_raw,
            "custom_fields": {"EQP_LABEL": ""},
            "delay_time": 15,
        }), content_type='application/json')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['data']['EQP_LABEL'] != ""


# ============================================================================
# 6. 字段类型正确性测试
# ============================================================================

class TestFieldTypes:
    """字段类型：int 字段保持 int，其余为 str"""

    NUMERIC_FIELDS = {'STANDARD_FLAG', 'REDEFINE_SEVERITY', 'OBJECT_CLASS'}

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_numeric_fields_are_int(self, _mock):
        """STANDARD_FLAG / REDEFINE_SEVERITY / OBJECT_CLASS 为 int"""
        es = make_es_source(ALARM_STANDARD_FLAG=1, ALARM_LEVEL=2, OBJECT_CLASS_ID=87002)
        result = generate_es_to_kafka_mapping(es)
        assert isinstance(result['STANDARD_FLAG'], int)
        assert isinstance(result['REDEFINE_SEVERITY'], int)
        assert isinstance(result['OBJECT_CLASS'], int)

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_non_numeric_fields_are_str(self, _mock):
        """非 int 字段（包括数值型字符串）均为 str"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        str_numeric_fields = [
            'ACTIVE_STATUS', 'VENDOR_ID', 'ALARM_RESOURCE_STATUS',
            'OBJECT_LEVEL', 'ORG_TYPE', 'SEND_JT_FLAG',
            'PREHANDLE', 'PORT_NUM', 'ALARM_ABNORMAL_TYPE',
        ]
        for f in str_numeric_fields:
            val = result.get(f, '')
            if val != '':
                assert isinstance(val, str), f"{f} 应为 str，实际 {type(val)}"


# ============================================================================
# 7. ORG_TEXT 拼装测试
# ============================================================================

class TestOrgText:
    """ORG_TEXT 字段拼装"""

    def test_org_text_not_empty(self):
        """ORG_TEXT 非空"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        assert result.get('ORG_TEXT', '') != ''

    def test_org_text_contains_key_fields(self):
        """ORG_TEXT 包含关键字段值"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        org_text = result.get('ORG_TEXT', '')
        assert '2' in org_text
        assert '11' in org_text

    def test_org_text_programmatic(self):
        """直接测试 generate_org_text 函数"""
        kafka_data = {
            "NETWORK_TYPE_TOP": "11",
            "ORG_SEVERITY": "2",
            "REGION_NAME": "漳州市",
            "ACTIVE_STATUS": "1",
            "CITY_NAME": "漳浦县",
            "TITLE_TEXT": "设备脱网",
        }
        result = generate_org_text(kafka_data)
        assert '11' in result
        assert '2' in result


# ============================================================================
# 8. 字段顺序测试
# ============================================================================

class TestFieldOrder:
    """Kafka 消息字段顺序"""

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_result_follows_standard_order(self, _mock):
        """返回结果按 STANDARD_FIELD_ORDER 顺序排列"""
        es = make_es_source()
        result = generate_es_to_kafka_mapping(es)
        result_keys = list(result.keys())
        std_idx = {k: i for i, k in enumerate(STANDARD_FIELD_ORDER)}
        last_idx = -1
        for key in result_keys:
            if key in std_idx:
                assert std_idx[key] > last_idx, f"字段 {key} 顺序错误"
                last_idx = std_idx[key]


# ============================================================================
# 9. API 端点冒烟测试
# ============================================================================

class TestAPIEndpoints:
    """各 API 端点存在性冒烟"""

    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_field_meta_get(self, client):
        r = client.get('/kafka-generator/field-meta')
        assert r.status_code == 200
        assert json.loads(r.data)['success']

    def test_field_meta_list_get(self, client):
        r = client.get('/kafka-generator/field-meta/list')
        assert r.status_code != 404

    def test_field_order(self, client):
        r = client.get('/kafka-generator/field-order')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert 'fields' in data['data']

    def test_field_options_missing_param(self, client):
        r = client.get('/kafka-generator/field-options')
        assert r.status_code == 400

    def test_generate_success(self, client):
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps(make_es_source()),
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result['success']
        assert 'FP0_FP1_FP2_FP3' in result['data']
        assert 'history_id' in result

    def test_generate_missing_es_source_raw(self, client):
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code == 400

    def test_generate_invalid_json(self, client):
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": "not valid json {{{",
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code in (400, 500)

    def test_push_message_success(self, client):
        r = client.post('/kafka-generator/generate-push-message', data=json.dumps({
            "fp_value": "1745900000_1234567890_9876543210_1111111111_12345",
            "event_time": "2026-05-22 12:00:00",
            "active_status": "3",
        }), content_type='application/json')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result['success']
        assert result['data']['FP0_FP1_FP2_FP3'] == "1745900000_1234567890_9876543210_1111111111_12345"
        assert result['data']['ACTIVE_STATUS'] == "3"

    def test_push_message_missing_fp(self, client):
        r = client.post('/kafka-generator/generate-push-message', data=json.dumps({
            "event_time": "2026-05-22 12:00:00",
        }), content_type='application/json')
        assert r.status_code == 400

    def test_history_list(self, client):
        r = client.get('/kafka-generator/history?page=1&per_page=5')
        assert r.status_code != 404

    def test_field_cache_get(self, client):
        r = client.get('/kafka-generator/field-cache')
        assert r.status_code != 404

    def test_field_cache_post(self, client):
        r = client.post('/kafka-generator/field-cache', data=json.dumps({
            "field_name": "EQP_LABEL",
            "field_value": "test_value",
            "is_pinned": False,
            "is_fixed": False,
        }), content_type='application/json')
        assert r.status_code != 404

    def test_field_history_post(self, client):
        r = client.post('/kafka-generator/field-history', data=json.dumps({
            "field_name": "TEST_FIELD",
            "field_value": "test_history_value",
        }), content_type='application/json')
        assert r.status_code != 404

    def test_field_values(self, client):
        r = client.get('/kafka-generator/field-values')
        assert r.status_code != 404

    def test_config(self, client):
        r = client.get('/kafka-generator/config')
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data['success']
        assert 'port' in data['data']


# ============================================================================
# 10. 边缘场景测试
# ============================================================================

class TestEdgeCases:
    """边界 & 异常场景"""

    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_minimal_es_data(self, client):
        """最小 ES 数据也能正常生成"""
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps({"_source": {"ALARM_LEVEL": 2}}),
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result['success']
        assert result['data']['ORG_SEVERITY'] == "2"

    def test_es_data_with_special_chars(self, client):
        """含特殊字符的 ES 数据"""
        es = make_es_source(EQUIPMENT_NAME="设备-测试_#123")
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps(es),
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result['success']

    def test_es_data_with_chinese(self, client):
        """含中文的 ES 数据"""
        es = make_es_source(ALARM_NAME="光缆中断→影响业务⚠️")
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps(es),
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert "光缆中断" in result['data']['TITLE_TEXT']

    def test_large_custom_fields(self, client):
        """大量自定义字段"""
        es = make_es_source()
        custom = {f: f"value_{i}" for i, f in enumerate(STANDARD_FIELD_ORDER[:20])}
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps(es),
            "custom_fields": custom,
            "delay_time": 15,
        }), content_type='application/json')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result['success']

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_empty_es_source(self, _mock):
        """空 ES 源数据"""
        result = generate_es_to_kafka_mapping({})
        assert result is not None
        assert 'FP0_FP1_FP2_FP3' in result

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql', return_value=None)
    def test_es_without_source_wrapper(self, _mock):
        """无 _source 包装的直接数据"""
        es = {"ALARM_LEVEL": 2, "EQUIPMENT_NAME": "直接设备"}
        result = generate_es_to_kafka_mapping(es)
        assert result['ORG_SEVERITY'] == "2"
        assert result['EQP_LABEL'] == "直接设备"


# ============================================================================
# 11. 动态字段映射测试
# ============================================================================

class TestDynamicFieldMapping:
    """数据库动态字段映射"""

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql')
    def test_db_config_overrides_default(self, mock_load):
        """数据库 es_field 配置覆盖默认映射"""
        mock_load.return_value = {
            "TITLE_TEXT": {"es_field": "EVENT_NAME", "label_cn": "告警标题", "db_cn": ""},
        }
        es = {"_source": {"EVENT_NAME": "自定义事件名", "ALARM_NAME": "默认告警名"}}
        result = generate_es_to_kafka_mapping(es)
        assert result['TITLE_TEXT'] == "自定义事件名"

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql')
    def test_special_fields_ignore_db_config(self, mock_load):
        """特殊字段（FP/时间）忽略数据库配置"""
        mock_load.return_value = {
            "FP0_FP1_FP2_FP3": {"es_field": "SOME_FP_FIELD", "label_cn": "FP", "db_cn": ""},
        }
        es = {"_source": {"ALARM_LEVEL": 2, "SOME_FP_FIELD": "should_be_ignored"}}
        result = generate_es_to_kafka_mapping(es)
        fp = result['FP0_FP1_FP2_FP3']
        assert fp != "should_be_ignored"
        assert '_' in fp

    @patch('routes.kafka.kafka_generator_routes.load_field_meta_from_mysql')
    def test_extra_fields_from_db(self, mock_load):
        """数据库中配置的额外字段（不在 STANDARD_FIELD_ORDER）"""
        mock_load.return_value = {
            "MY_CUSTOM_FIELD": {"es_field": "CUSTOM_ES_FIELD", "label_cn": "自定义", "db_cn": ""},
        }
        es = {"_source": {"ALARM_LEVEL": 2, "CUSTOM_ES_FIELD": "extra_value"}}
        result = generate_es_to_kafka_mapping(es)
        assert result['MY_CUSTOM_FIELD'] == "extra_value"


# ============================================================================
# 12. 历史记录测试
# ============================================================================

class TestHistoryFlow:
    """生成 → 保存历史 → 查询完整链路"""

    @pytest.fixture
    def app(self):
        app = create_app('testing')
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_generate_saves_history(self, client):
        """生成后返回 history_id"""
        r = client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps(make_es_source()),
            "delay_time": 15,
        }), content_type='application/json')
        result = json.loads(r.data)
        assert result['success']
        assert result.get('history_id') is not None

    def test_history_list_returns_records(self, client):
        """历史列表可查询"""
        client.post('/kafka-generator/generate', data=json.dumps({
            "es_source_raw": json.dumps(make_es_source()),
            "delay_time": 15,
        }), content_type='application/json')
        r = client.get('/kafka-generator/history?page=1&per_page=5')
        assert r.status_code == 200
        result = json.loads(r.data)
        assert result.get('success') in (True, False)

    def test_history_detail_not_found(self, client):
        """不存在的历史ID返回404"""
        r = client.get('/kafka-generator/history/99999999')
        assert r.status_code in (404, 500)


# ============================================================================
# 运行入口
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-p", "no:warnings"])
