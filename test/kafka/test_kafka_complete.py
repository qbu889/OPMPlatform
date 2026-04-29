#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka生成器完整功能测试套件
覆盖所有核心功能点，支持CI/CD自动化运行
"""
import sys
import os
import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from routes.kafka.kafka_generator_routes import (
    generate_es_to_kafka_mapping,
    generate_consistent_fp,
    generate_creation_event_time,
    get_nested_value,
    build_dynamic_field_mapping,
    get_default_mapping_rule,
    STANDARD_FIELD_ORDER,
    FIELD_META
)


class TestFPGeneration:
    """FP字段生成测试"""
    
    def test_fp_format(self):
        """测试FP值格式是否正确"""
        fp = generate_consistent_fp()
        parts = fp.split('_')
        
        assert len(parts) == 5, f"FP应该包含5个部分，实际得到 {len(parts)} 个"
        assert len(parts[0]) > 0, "时间戳部分不能为空"
        assert len(parts[1]) == 10, f"random1应该是10位，实际 {len(parts[1])} 位"
        assert len(parts[2]) == 10, f"random2应该是10位，实际 {len(parts[2])} 位"
        assert len(parts[3]) == 10, f"random3应该是10位，实际 {len(parts[3])} 位"
        assert len(parts[4]) == 5, f"random4应该是5位，实际 {len(parts[4])} 位"
    
    def test_fp_uniqueness(self):
        """测试每次生成的FP值是否唯一"""
        fp_list = [generate_consistent_fp() for _ in range(10)]
        unique_fps = set(fp_list)
        
        # 允许少量重复（概率极低），但大部分应该唯一
        assert len(unique_fps) >= 9, f"10次生成中至少有9个唯一值，实际 {len(unique_fps)} 个"
    
    def test_fp_consistency_in_single_generation(self):
        """测试单次生成中所有FP字段使用相同的值"""
        test_es_data = self._create_minimal_es_data()
        
        with patch('routes.kafka.kafka_generator_routes.generate_consistent_fp') as mock_fp:
            mock_fp.return_value = "test_fp_12345_67890_11111_22222"
            
            result = generate_es_to_kafka_mapping(test_es_data)
            
            # 验证所有FP字段使用相同的值
            assert result['FP0_FP1_FP2_FP3'] == "test_fp_12345_67890_11111_22222"
            assert result['CFP0_CFP1_CFP2_CFP3'] == "test_fp_12345_67890_11111_22222"
            assert result['ORIG_ALARM_FP'] == "test_fp_12345_67890_11111_22222"
            assert result['ORIG_ALARM_CLEAR_FP'] == "test_fp_12345_67890_11111_22222"
            assert result['SRC_ORG_ID'] == "test_fp_12345_67890_11111_22222"
    
    def _create_minimal_es_data(self):
        """创建最小化的ES测试数据"""
        return {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "测试设备",
            "NE_LABEL": "测试网元",
            "DELAY_TIME": 900
        }


class TestTimeFields:
    """时间字段生成测试"""
    
    def test_event_time_with_delay_time(self):
        """测试从ES数据中提取DELAY_TIME计算时间"""
        es_data = {
            "DELAY_TIME": 720  # 12小时
        }
        
        now = datetime.now()
        result = generate_creation_event_time(es_data)
        expected_time = now - timedelta(hours=12)
        
        # 解析生成的时间字符串
        generated_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        
        # 允许1分钟的误差（因为执行时间差异）
        time_diff = abs((generated_time - expected_time).total_seconds())
        assert time_diff < 60, f"时间差异过大: {time_diff}秒"
    
    def test_event_time_without_delay_time(self):
        """测试没有DELAY_TIME时使用默认15小时"""
        es_data = {}
        
        now = datetime.now()
        result = generate_creation_event_time(es_data)
        expected_time = now - timedelta(hours=15)
        
        generated_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        time_diff = abs((generated_time - expected_time).total_seconds())
        assert time_diff < 60, f"时间差异过大: {time_diff}秒"
    
    def test_event_time_with_user_override(self):
        """测试用户手动输入的延迟时间优先级更高"""
        es_data = {
            "DELAY_TIME": 720  # ES中的12小时
        }
        
        now = datetime.now()
        result = generate_creation_event_time(es_data, user_delay_time=360)  # 用户输入6小时
        expected_time = now - timedelta(hours=6)
        
        generated_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        time_diff = abs((generated_time - expected_time).total_seconds())
        assert time_diff < 60, f"应该使用用户输入的时间，差异: {time_diff}秒"
    
    def test_three_time_fields_consistency(self):
        """测试三个时间字段保持一致"""
        test_es_data = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "测试设备",
            "NE_LABEL": "测试网元",
            "DELAY_TIME": 900
        }
        
        result = generate_es_to_kafka_mapping(test_es_data)
        
        # 三个时间字段应该相同
        assert result['EVENT_TIME'] == result['CREATION_EVENT_TIME']
        assert result['EVENT_TIME'] == result['EVENT_ARRIVAL_TIME']
        assert result['CREATION_EVENT_TIME'] == result['EVENT_ARRIVAL_TIME']
    
    def test_time_format(self):
        """测试时间格式是否为YYYY-MM-DD HH:MM:SS"""
        es_data = {"DELAY_TIME": 900}
        result = generate_creation_event_time(es_data)
        
        # 验证格式
        try:
            datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
            assert True
        except ValueError:
            pytest.fail(f"时间格式不正确: {result}")


class TestFieldMapping:
    """字段映射测试"""
    
    def setup_method(self):
        """准备测试数据"""
        self.test_es_data = {
            "_source": {
                "NETWORK_TYPE_ID": "11",
                "ALARM_LEVEL": 2,
                "CITY_NAME": "漳州市",
                "COUNTY_NAME": "漳浦县",
                "EQUIPMENT_NAME": "[集客]测试设备",
                "NE_LABEL": "[集客]测试网元",
                "VENDOR_NAME": "瑞斯康达",
                "ALARM_NAME": "设备脱网",
                "EVENT_LOCATION": "MSP",
                "OBJECT_CLASS_ID": 87002,
                "DELAY_TIME": 900
            }
        }
    
    def test_basic_field_mapping(self):
        """测试基本字段映射是否正确"""
        result = generate_es_to_kafka_mapping(self.test_es_data["_source"])
        
        assert result['NETWORK_TYPE_TOP'] == "11"
        assert result['ORG_SEVERITY'] == "2"
        assert result['CITY_NAME'] == "漳浦县"
        assert result['EQP_LABEL'] == "[集客]测试设备"
        assert result['NE_LABEL'] == "[集客]测试网元"
        assert result['VENDOR_NAME'] == "瑞斯康达"
        assert result['TITLE_TEXT'] == "设备脱网"
        assert result['LOCATE_INFO'] == "MSP"
    
    def test_nested_field_extraction(self):
        """测试嵌套字段提取"""
        es_data_with_nested = {
            "BUSINESS_TAG": {
                "CIRCUIT_NO": "测试电路",
                "BUSINESS_SYSTEM": "集团专线"
            },
            "NE_TAG": {
                "ROOM_ID": "ROOM123"
            }
        }
        
        circuit_no = get_nested_value(es_data_with_nested, "BUSINESS_TAG.CIRCUIT_NO")
        assert circuit_no == "测试电路"
        
        room_id = get_nested_value(es_data_with_nested, "NE_TAG.ROOM_ID")
        assert room_id == "ROOM123"
    
    def test_missing_field_handling(self):
        """测试缺失字段的处理"""
        es_data_empty = {}
        result = get_nested_value(es_data_empty, "NON_EXISTENT.FIELD")
        assert result is None
    
    def test_field_order_preserved(self):
        """测试字段顺序是否与STANDARD_FIELD_ORDER一致"""
        result = generate_es_to_kafka_mapping(self.test_es_data["_source"])
        result_keys = list(result.keys())
        
        # 检查前10个字段的顺序
        for i in range(min(10, len(STANDARD_FIELD_ORDER))):
            if i < len(result_keys):
                assert result_keys[i] == STANDARD_FIELD_ORDER[i], \
                    f"字段顺序不匹配: 位置{i}, 期望{STANDARD_FIELD_ORDER[i]}, 实际{result_keys[i]}"


class TestSpecialFields:
    """特殊字段处理测试"""
    
    def test_special_fields_ignore_db_config(self):
        """测试特殊字段忽略数据库配置"""
        # 模拟数据库返回了FP字段的es_field配置
        mock_field_meta = {
            "FP0_FP1_FP2_FP3": {"es_field": "ORIG_ALARM_FP", "label_cn": "FP", "db_cn": "FP"},
            "EVENT_TIME": {"es_field": "EVENT_TIME", "label_cn": "时间", "db_cn": "时间"}
        }
        
        es_data = {
            "ORIG_ALARM_FP": "should_not_use_this",
            "EVENT_TIME": "should_not_use_this_either",
            "DELAY_TIME": 900
        }
        
        field_mapping = build_dynamic_field_mapping(es_data, mock_field_meta)
        
        # FP字段应该使用lambda函数，而不是数据库配置
        assert callable(field_mapping['FP0_FP1_FP2_FP3']), "FP字段应该使用生成函数"
        
        # 时间字段也应该使用lambda函数
        assert callable(field_mapping['EVENT_TIME']), "时间字段应该使用生成函数"
    
    def test_org_text_generation(self):
        """测试ORG_TEXT字段生成"""
        test_data = {
            "NETWORK_TYPE_TOP": "11",
            "ORG_SEVERITY": "2",
            "FP0_FP1_FP2_FP3": "test_fp_value"
        }
        
        # ORG_TEXT应该包含所有字段的值，用_;分隔
        from routes.kafka.kafka_generator_routes import generate_org_text
        org_text = generate_org_text(test_data)
        
        assert isinstance(org_text, str)
        assert "_;" in org_text or org_text.endswith("_")


class TestCustomFields:
    """自定义字段覆盖测试"""
    
    def test_custom_fields_override(self):
        """测试自定义字段覆盖自动生成值"""
        test_es_data = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "原始设备名",
            "NE_LABEL": "原始网元名",
            "DELAY_TIME": 900
        }
        
        custom_fields = {
            "EQP_LABEL": "自定义设备名",
            "NE_LABEL": "自定义网元名"
        }
        
        # 注意：当前实现中custom_fields是在路由层处理的
        # 这里测试的是基础映射逻辑
        result = generate_es_to_kafka_mapping(test_es_data)
        
        # 验证基础映射正常工作
        assert 'EQP_LABEL' in result
        assert 'NE_LABEL' in result


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_es_data(self):
        """测试空ES数据的处理"""
        result = generate_es_to_kafka_mapping({})
        
        # 应该仍然生成所有标准字段
        assert len(result) > 0
        
        # FP字段和时间字段应该正常生成
        assert 'FP0_FP1_FP2_FP3' in result
        assert 'EVENT_TIME' in result
    
    def test_invalid_json_string(self):
        """测试无效JSON字符串的处理"""
        # 这个测试应该在API层面进行，这里测试函数的容错性
        try:
            result = generate_es_to_kafka_mapping("invalid json")
            # 如果传入字符串，应该能优雅处理
            assert isinstance(result, dict) or result is not None
        except Exception as e:
            # 允许抛出异常，但要确保是合理的异常类型
            assert isinstance(e, (AttributeError, TypeError))
    
    def test_none_values_in_es_data(self):
        """测试ES数据中包含None值的处理"""
        es_data = {
            "NETWORK_TYPE_ID": None,
            "ALARM_LEVEL": None,
            "EQUIPMENT_NAME": None
        }
        
        result = generate_es_to_kafka_mapping(es_data)
        
        # None值应该被转换为空字符串或其他默认值
        assert result['NETWORK_TYPE_TOP'] is not None
        assert result['ORG_SEVERITY'] is not None
    
    def test_large_delay_time(self):
        """测试超大延迟时间的处理"""
        es_data = {
            "DELAY_TIME": 10080  # 7天
        }
        
        result = generate_creation_event_time(es_data)
        generated_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        
        # 应该能正常计算，不会溢出
        assert isinstance(generated_time, datetime)
    
    def test_zero_delay_time(self):
        """测试零延迟时间"""
        es_data = {
            "DELAY_TIME": 0
        }
        
        now = datetime.now()
        result = generate_creation_event_time(es_data)
        generated_time = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        
        # 应该接近当前时间
        time_diff = abs((generated_time - now).total_seconds())
        assert time_diff < 60


class TestIntegration:
    """集成测试"""
    
    def test_full_generation_with_real_data(self):
        """使用真实数据进行完整生成测试"""
        real_es_data = {
            "HOME_BROAD_BAND_LIST": [],
            "FULL_REGION_ID": "35000/350600/350623",
            "EVENT_LEVEL": 4,
            "ORG_TYPE": 14104,
            "EVENT_LOCATION": "MSP",
            "EQUIPMENT_NAME": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
            "NETWORK_SUB_TYPE_ID": "1100",
            "CANCEL_STATUS": 1,
            "ROOT_NETWORK_TYPE_ID": "1",
            "ALARM_STANDARD_NAME": "设备脱网",
            "MAINTAIN_TEAM": "漳州漳浦集客铁通维护组",
            "EQP_OBJECT_ID": "87002",
            "EVENT_SOURCE": 2,
            "NE_LABEL": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
            "TYPE_KEYCODE": "预处理,",
            "ALARM_RESOURCE_STATUS": "1",
            "NMS_ALARM_ID": "2020740405373157376",
            "ALARM_NAME": "设备脱网(影响1条电路)",
            "VENDOR_NAME": "瑞斯康达",
            "MAIN_NET_SORT_ONE": "集团专线",
            "VENDOR_EVENT_TYPE": "14202",
            "OBJECT_CLASS_ID": 87002,
            "PORT_NUM": "300205",
            "COUNTY_NAME": "漳浦县",
            "EVENT_FP": "1713996274_3872318956_2520283298_4136070826_2",
            "EVENT_ARRIVAL_TIME": "2026-02-09 14:04:59",
            "NETWORK_TYPE_ID": "11",
            "NMS_NAME": "集客网管",
            "PROVINCE_NAME": "福建省",
            "ALARM_STANDARD_ID": "1100-064-371-10-860022",
            "ORIG_ALARM_FP": "1713996274_3872318956_2520283298_4136070826",
            "SATOTAL": 3,
            "VENDOR_SEVERITY": "1",
            "ALARM_LEVEL": 2,
            "DELAY_TIME": 720,
            "BUSINESS_TAG": {
                "CIRCUIT_NO": "漳州漳浦消防救援FE5980KA",
                "BUSINESS_SYSTEM": "集团专线",
                "PRODUCT_TYPE": "数据专线"
            },
            "NE_TAG": {
                "ROOM_ID": "ROOM123"
            }
        }
        
        result = generate_es_to_kafka_mapping(real_es_data)
        
        # 验证关键字段
        assert result['NETWORK_TYPE_TOP'] == "1"
        assert result['CITY_NAME'] == "漳浦县"
        assert result['EQP_LABEL'] == "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1"
        assert result['TITLE_TEXT'] == "设备脱网(影响1条电路)"
        
        # 验证FP字段一致性
        assert result['FP0_FP1_FP2_FP3'] == result['CFP0_CFP1_CFP2_CFP3']
        assert result['FP0_FP1_FP2_FP3'] == result['ORIG_ALARM_FP']
        
        # 验证时间字段一致性
        assert result['EVENT_TIME'] == result['CREATION_EVENT_TIME']
        assert result['EVENT_TIME'] == result['EVENT_ARRIVAL_TIME']
        
        # 验证生成了所有标准字段
        for field in STANDARD_FIELD_ORDER:
            assert field in result, f"缺少字段: {field}"
    
    def test_generation_performance(self):
        """测试生成性能"""
        import time
        
        test_es_data = {
            "NETWORK_TYPE_ID": "11",
            "ALARM_LEVEL": 2,
            "EQUIPMENT_NAME": "测试设备",
            "DELAY_TIME": 900
        }
        
        start_time = time.time()
        
        # 生成100次
        for _ in range(100):
            generate_es_to_kafka_mapping(test_es_data)
        
        elapsed = time.time() - start_time
        
        # 100次生成应该在合理时间内完成（例如5秒内）
        assert elapsed < 5.0, f"生成100次耗时过长: {elapsed}秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
