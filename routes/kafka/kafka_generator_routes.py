#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka 消息生成器路由
根据 ES 数据生成对应的 Kafka 消息
"""
from flask import Blueprint, render_template, request, jsonify
from flask_cors import CORS
import re
import uuid
import random
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

kafka_generator_bp = Blueprint('kafka_generator_bp', __name__, url_prefix='/kafka-generator')

# 字段元数据配置（后续可以迁移到 MySQL）
# key 使用 Kafka 字段名（大写），便于与模板 allFields 对应
FIELD_META = {
    "NETWORK_TYPE_TOP": {
        "label_cn": "一级专业分类",
        "es_field": "NETWORK_TYPE_ID",
        "db_cn": "一级专业ID"
    },
    "ORG_SEVERITY": {
        "label_cn": "网管告警级别",
        "es_field": "ALARM_LEVEL",
        "db_cn": "网管告警级别"
    },
    "REGION_NAME": {
        "label_cn": "地区",
        "es_field": "CITY_NAME",
        "db_cn": "地市"
    },
    "ACTIVE_STATUS": {
        "label_cn": "告警清除状态",
        "es_field": "CANCEL_STATUS",
        "db_cn": "清除状态"
    },
    "CITY_NAME": {
        "label_cn": "县市",
        "es_field": "COUNTY_NAME",
        "db_cn": "区县"
    },
    "EQP_LABEL": {
        "label_cn": "网元名称",
        "es_field": "EQUIPMENT_NAME",
        "db_cn": "网元名称"
    },
    "EQP_OBJECT_CLASS": {
        "label_cn": "设备类型",
        "es_field": "EQP_OBJECT_ID",
        "db_cn": "设备类型ID"
    },
    "VENDOR_NAME": {
        "label_cn": "设备厂家名称",
        "es_field": "VENDOR_NAME",
        "db_cn": "设备厂家"
    },
    "VENDOR_ID": {
        "label_cn": "设备厂家ID",
        "es_field": "VENDOR_ID",
        "db_cn": "设备厂家"
    },
    "ALARM_RESOURCE_STATUS": {
        "label_cn": "告警工程状态",
        "es_field": "ALARM_RESOURCE_STATUS",
        "db_cn": "工程状态"
    },
    "LOCATE_INFO": {
        "label_cn": "定位信息",
        "es_field": "EVENT_LOCATION",
        "db_cn": "事件定位信息"
    },
    "NE_LABEL": {
        "label_cn": "告警对象网元名称",
        "es_field": "NE_LABEL",
        "db_cn": "告警对象网元名称"
    },
    "OBJECT_LEVEL": {
        "label_cn": "告警对象重要级别",
        "es_field": "OBJECT_LEVEL",
        "db_cn": "告警对象重要级别"
    },
    "PROFESSIONAL_TYPE": {
        "label_cn": "专业（旧概念）",
        "es_field": "PROFESSIONAL_TYPE",
        "db_cn": "专业（旧概念）"
    },
    "NETWORK_TYPE": {
        "label_cn": "二级专业分类",
        "es_field": "NETWORK_SUB_TYPE_ID",
        "db_cn": "二级专业"
    },
    "ORG_TYPE": {
        "label_cn": "告警类别",
        "es_field": "ORG_TYPE",
        "db_cn": "告警类别"
    },
    "VENDOR_TYPE": {
        "label_cn": "厂家原始告警类别",
        "es_field": "VENDOR_EVENT_TYPE",
        "db_cn": "厂家原始告警类别"
    },
    "SEND_JT_FLAG": {
        "label_cn": "是否需要上报集团",
        "es_field": "SEND_JT_FLAG",
        "db_cn": "是否需要上报集团"
    },
    "TITLE_TEXT": {
        "label_cn": "告警标题",
        "es_field": "ALARM_NAME",
        "db_cn": "告警标题"
    },
    "STANDARD_ALARM_NAME": {
        "label_cn": "告警标准名",
        "es_field": "ALARM_STANDARD_NAME",
        "db_cn": "告警标准化名称"
    },
    "STANDARD_ALARM_ID": {
        "label_cn": "告警标准化ID",
        "es_field": "ALARM_STANDARD_ID",
        "db_cn": "告警标准化ID"
    },
    "STANDARD_FLAG": {
        "label_cn": "标准化标志",
        "es_field": "ALARM_STANDARD_FLAG",
        "db_cn": "标准化标志"
    },
    "VENDOR_SEVERITY": {
        "label_cn": "厂家原始告警级别",
        "es_field": "VENDOR_SEVERITY",
        "db_cn": "厂家原始告警级别"
    },
    "PROBABLE_CAUSE": {
        "label_cn": "厂家告警号",
        "es_field": "PROBABLE_CAUSE",
        "db_cn": "厂家告警号"
    },
    "NMS_ALARM_ID": {
        "label_cn": "告警流水号",
        "es_field": "NMS_ALARM_ID",
        "db_cn": "网管告警ID"
    },
    "PROBABLE_CAUSE_TXT": {
        "label_cn": "告警可能原因描述",
        "es_field": "EVENT_PROBABLE_CAUSE_TXT",
        "db_cn": "事件可能原因描述"
    },
    "PREPROCESS_MANNER": {
        "label_cn": "预处理方式",
        "es_field": "PREPROCESS_MANNER",
        "db_cn": "预处理方式"
    },
    "EVENT_TIME": {
        "label_cn": "告警发生时间",
        "es_field": "EVENT_TIME",
        "db_cn": "事件发生时间"
    },
    "TIME_STAMP": {
        "label_cn": "告警发现时间",
        "es_field": "EVENT_COLLECTION_TIME",
        "db_cn": "事件采集时间"
    },
    "FP0_FP1_FP2_FP3": {
        "label_cn": "告警指纹FP",
        "es_field": "ORIG_ALARM_FP",
        "db_cn": "告警流水号"
    },
    "CFP0_CFP1_CFP2_CFP3": {
        "label_cn": "清除告警指纹FP",
        "es_field": "ORIG_ALARM_CLEAR_FP",
        "db_cn": "事件清除FP"
    },
    "MACHINE_ROOM_INFO": {
        "label_cn": "机房信息",
        "es_field": "MACHINE_ROOM_INFO",
        "db_cn": "机房信息"
    }
    # 其它字段可按需继续补充
}

# Kafka 字段 -> 维表名 映射 (用于前端"字典"弹窗和后端查询)
FIELD_DICT_TABLES = {
    "ALARM_RESOURCE_STATUS": "alarm_resource_status",
    "BUSINESS_LAYER": "business_layer",
    "CIRCUIT_LEVEL": "circuit_level",
    "EFFECT_NE": "effect_ne",
    "EFFECT_SERVICE": "effect_service",
    "EQP_OBJECT_CLASS": "eqp_object_class",
    "EXTRA_ID2": "extra_id2",
    "LOGIC_ALARM_TYPE": "logic_alarm_type",
    "NE_ADMIN_STATUS": "ne_admin_status",
    "NETWORK_TYPE": "network_type",
    "NETWORK_TYPE_TOP": "network_type_top",
    "ORG_SEVERITY": "org_severity",
    "ORG_TYPE": "org_type",
    "PORT_NUM": "port_num",
    "SUB_ALARM_TYPE": "sub_alarm_type",
}


def load_field_meta_from_mysql():
    """从 MySQL 加载字段元数据。

    读取表：kafka_field_meta
    返回结构：{ "NETWORK_TYPE_TOP": { "label_cn": "...", "es_field": "...", "db_cn": "..." }, ... }
    失败或无数据时返回 None，供调用方回退到内置 FIELD_META。
    """
    try:
        from utils.mysql_helper import get_mysql_conn_dict_cursor

        conn = get_mysql_conn_dict_cursor()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT kafka_field, es_field, db_cn, label_cn
                    FROM kafka_field_meta
                    WHERE is_enabled = 1
                    """
                )
                rows = cur.fetchall() or []
        finally:
            conn.close()

        if not rows:
            return None

        meta = {}
        for r in rows:
            k = (r.get("kafka_field") or "").strip().upper()
            if not k:
                continue
            meta[k] = {
                "label_cn": (r.get("label_cn") or "").strip(),
                "es_field": (r.get("es_field") or "").strip(),
                "db_cn": (r.get("db_cn") or "").strip(),
            }
        return meta or None
    except Exception:
        return None


def generate_unique_fp():
    """生成唯一的FP值"""
    # 基于当前时间和随机数生成
    timestamp = str(int(datetime.now().timestamp()))
    random_part = str(uuid.uuid4().int)[:10]
    return f"{timestamp}_{random_part}"


def generate_consistent_fp():
    """生成一致的FP值，确保同一请求中所有FP字段相同"""
    # 使用固定的格式生成FP值，确保一致性
    timestamp = str(int((datetime.now() - timedelta(minutes=15)).timestamp()))
    random_part1 = str(random.randint(1000000000, 9999999999))
    random_part2 = str(random.randint(1000000000, 9999999999))
    random_part3 = str(random.randint(1000000000, 9999999999))
    random_part4 = str(random.randint(10000, 99999))
    return f"{timestamp}_{random_part1}_{random_part2}_{random_part3}_{random_part4}"


# 定义标准字段顺序（严格按照预计返回顺序.json的顺序）
STANDARD_FIELD_ORDER = [
    "ID",
    "NETWORK_TYPE_TOP",
    "ORG_SEVERITY",
    "REGION_NAME",
    "ACTIVE_STATUS",
    "CITY_NAME",
    "EQP_LABEL",
    "EQP_OBJECT_CLASS",
    "VENDOR_NAME",
    "VENDOR_ID",
    "ALARM_RESOURCE_STATUS",
    "LOCATE_INFO",
    "NE_LABEL",
    "OBJECT_LEVEL",
    "PROFESSIONAL_TYPE",
    "NETWORK_TYPE",
    "ORG_TYPE",
    "VENDOR_TYPE",
    "SEND_JT_FLAG",
    "TITLE_TEXT",
    "STANDARD_ALARM_NAME",
    "STANDARD_ALARM_ID",
    "STANDARD_FLAG",
    "VENDOR_SEVERITY",
    "PROBABLE_CAUSE",
    "NMS_ALARM_ID",
    "PROBABLE_CAUSE_TXT",
    "PREPROCESS_MANNER",
    "EVENT_TIME",
    "TIME_STAMP",
    "FP0_FP1_FP2_FP3",
    "CFP0_CFP1_CFP2_CFP3",
    "MACHINE_ROOM_INFO",
    "INT_ID",
    "REDEFINE_SEVERITY",
    "TYPE_KEYCODE",
    "NE_LOCATION",
    "ALARM_EXPLANATION",
    "ALARM_EXPLANATION_ADDITION",
    "MAINTAIN_GROUP",
    "SITE_TYPE",
    "SUB_ALARM_TYPE",
    "EVENT_CAT",
    "NMS_NAME",
    "CITY_ID",
    "REMOTE_EQP_LABEL",
    "REMOTE_RESOURCE_STATUS",
    "REMOTE_PROJ_SUB_STATUS",
    "REMOTE_INT_ID",
    "PROJ_NAME",
    "PROJ_OA_FILE_CONTENT",
    "BUSINESS_REGION_IDS",
    "BUSINESS_REGIONS",
    "REMOTE_OBJECT_CLASS",
    "ALARM_REASON",
    "GCSS_CLIENT",
    "GCSS_CLIENT_NAME",
    "GCSS_CLIENT_NUM",
    "GCSS_CLIENT_LEVEL",
    "GCSS_SERVICE",
    "GCSS_SERVICE_NUM",
    "GCSS_SERVICE_LEVEL",
    "GCSS_SERVICE_TYPE",
    "BUSINESS_SYSTEM",
    "NE_IP",
    "LAYER_RATE",
    "CIRCUIT_ID",
    "ALARM_ABNORMAL_TYPE",
    "PROJ_OA_FILE_ID",
    "GCSS_CLIENT_GRADE",
    "EFFECT_CIRCUIT_NUM",
    "PREHANDLE",
    "OBJECT_CLASS_TEXT",
    "BOARD_TYPE",
    "OBJECT_CLASS",
    "LOGIC_ALARM_TYPE",
    "LOGIC_SUB_ALARM_TYPE",
    "EFFECT_NE",
    "EFFECT_SERVICE",
    "SPECIAL_FIELD14",
    "SPECIAL_FIELD7",
    "SPECIAL_FIELD21",
    "ALARM_SOURCE",
    "BUSINESS_LAYER",
    "ALARM_TEXT",
    "CIRCUIT_NO",
    "PRODUCT_TYPE",
    "CIRCUIT_LEVEL",
    "BUSINESS_TYPE",
    "IRMS_GRID_NAME",
    "ADMIN_GRID_ID",
    "HOME_CLIENT_NUM",
    "SRC_ID",
    "SRC_IS_TEST",
    "SRC_APP_ID",
    "SRC_ORG_ID",
    "ORG_TEXT",
    "TOPIC_PREFIX",
    "TOPIC_PARTITION",
    "SPECIAL_FIELD17",
    "EXTRA_ID2",
    "EXTRA_STRING1",
    "PORT_NUM",
    "NE_ADMIN_STATUS",
    "SPECIAL_FIELD18",
    "SPECIAL_FIELD20",
    "TMSC_CAT",
    "ALARM_NE_STATUS",
    "ALARM_EQP_STATUS",
    "INTERFERENCE_FLAG",
    "SPECIAL_FIELD2",
    "custGroupFeature",
    "industryCustType",
    "strategicCustTypeFL",
    "strategicCustTypeSL",
    "FAULT_LOCATION",
    "EVENT_SOURCE",
    "ORIG_ALARM_CLEAR_FP",
    "ORIG_ALARM_FP",
    "EVENT_ARRIVAL_TIME",
    "CREATION_EVENT_TIME"
]


def generate_es_to_kafka_mapping(es_data, user_delay_time=None):
    """将 ES 数据映射为 Kafka 消息，保持字段顺序与理想输出一致
    
    Args:
        es_data: ES 源数据
        user_delay_time: 用户手动输入的 DELAY_TIME 值（可选），如果提供则优先使用
    """
    # 使用有序字典保持字段顺序
    from collections import OrderedDict
    kafka_message = OrderedDict()

    # 生成一致的FP值供所有FP字段使用
    consistent_fp_value = generate_consistent_fp()
    # 将FP值存储在函数属性中，供lambda函数访问
    generate_es_to_kafka_mapping.consistent_fp = consistent_fp_value

    # 基础字段映射
    field_mapping = {
        "ID": lambda: str(uuid.uuid4()),
        "NETWORK_TYPE_TOP": "_source.ROOT_NETWORK_TYPE_ID",  # 改为ROOT_NETWORK_TYPE_ID
        "ORG_SEVERITY": lambda: str(get_nested_value(es_data, "ALARM_LEVEL") or ""),
        "REGION_NAME": lambda: get_region_from_full_path(es_data),  # 从FULL_REGION_NAME提取地市
        "ACTIVE_STATUS": "1",  # 默认值
        "CITY_NAME": "_source.COUNTY_NAME",  # 使用COUNTY_NAME作为区县
        "EQP_LABEL": "_source.EQUIPMENT_NAME",
        "EQP_OBJECT_CLASS": lambda: str(get_nested_value(es_data, "OBJECT_CLASS_ID") or ""),
        "VENDOR_NAME": "_source.VENDOR_NAME",
        "VENDOR_ID": lambda: str(get_nested_value(es_data, "VENDOR_ID") or ""),
        "ALARM_RESOURCE_STATUS": "_source.ALARM_RESOURCE_STATUS",
        "LOCATE_INFO": "_source.EVENT_LOCATION",
        "NE_LABEL": "_source.NE_LABEL",
        "OBJECT_LEVEL": "0",  # 固定值，字符串类型
        "PROFESSIONAL_TYPE": lambda: map_professional_type(get_nested_value(es_data, "MAIN_NET_SORT_ONE")),  # 映射为数字代码
        "NETWORK_TYPE": "_source.NETWORK_SUB_TYPE_ID",
        "ORG_TYPE": lambda: str(get_nested_value(es_data, "ORG_TYPE") or ""),
        "VENDOR_TYPE": "_source.VENDOR_EVENT_TYPE",
        "SEND_JT_FLAG": "0",  # 默认值
        "TITLE_TEXT": "_source.ALARM_NAME",
        "STANDARD_ALARM_NAME": "_source.ALARM_STANDARD_NAME",
        "STANDARD_ALARM_ID": "0500-009-006-10-800007",  # 固定值
        "STANDARD_FLAG": lambda: get_nested_value(es_data, "ALARM_STANDARD_FLAG"),  # 保持 int 类型
        "VENDOR_SEVERITY": lambda: get_nested_value(es_data, "VENDOR_SEVERITY"),  # 从 ES 获取，保持 string 类型
        "PROBABLE_CAUSE": lambda: get_nested_value(es_data, "PROBABLE_CAUSE"),  # 厂家告警号
        "NMS_ALARM_ID": "_source.NMS_ALARM_ID",
        "PROBABLE_CAUSE_TXT": "_source.EVENT_PROBABLE_CAUSE_TXT",
        "PREPROCESS_MANNER": "",  # 默认空值
        "EVENT_TIME": lambda: (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
        "TIME_STAMP": lambda: str(int((datetime.now() - timedelta(minutes=15)).timestamp())),
        "FP0_FP1_FP2_FP3": lambda: generate_es_to_kafka_mapping.consistent_fp,
        "CFP0_CFP1_CFP2_CFP3": lambda: generate_es_to_kafka_mapping.consistent_fp,
        "MACHINE_ROOM_INFO": "_source.NE_TAG.MACHINE_ROOM_INFO",
        "INT_ID": "0",  # 默认值
        "REDEFINE_SEVERITY": lambda: get_nested_value(es_data, "ALARM_LEVEL"),  # 保持 int 类型
        "TYPE_KEYCODE": "_source.TYPE_KEYCODE",
        "NE_LOCATION": "_source.NE_LOCATION",
        "ALARM_EXPLANATION": "_source.EVENT_EXPLANATION",
        "ALARM_EXPLANATION_ADDITION": "传输节点",  # 固定值
        "MAINTAIN_GROUP": "_source.MAINTAIN_TEAM",
        "SITE_TYPE": "_source.SITE_TYPE",
        "SUB_ALARM_TYPE": "",  # 默认空值
        "EVENT_CAT": "_source.EVENT_CAT",
        "NMS_NAME": "_source.NMS_NAME",
        "CITY_ID": "_source.CITY_ID",
        "REMOTE_EQP_LABEL": "_source.REMOTE_EQUIPMENT_NAME",
        "REMOTE_RESOURCE_STATUS": "",  # 默认空值
        "REMOTE_PROJ_SUB_STATUS": "",  # 默认空值
        "REMOTE_INT_ID": "",  # 默认空值
        "PROJ_NAME": "",  # 默认空值
        "PROJ_OA_FILE_CONTENT": "",  # 默认空值
        "BUSINESS_REGION_IDS": "",  # 默认空值
        "BUSINESS_REGIONS": "",  # 默认空值
        "REMOTE_OBJECT_CLASS": "_source.REMOTE_OBJECT_CLASS",
        "ALARM_REASON": "_source.ALARM_REASON",
        "GCSS_CLIENT": "",  # 默认空值
        "GCSS_CLIENT_NAME": "",  # 默认空值
        "GCSS_CLIENT_NUM": "",  # 默认空值
        "GCSS_CLIENT_LEVEL": "",  # 默认空值
        "GCSS_SERVICE": "",  # 默认空值
        "GCSS_SERVICE_NUM": "",  # 默认空值
        "GCSS_SERVICE_LEVEL": "",  # 默认空值
        "GCSS_SERVICE_TYPE": "",  # 默认空值
        "BUSINESS_SYSTEM": "_source.BUSINESS_TAG.BUSINESS_SYSTEM",
        "NE_IP": "_source.EQUIPMENT_IP",
        "LAYER_RATE": "",  # 默认空值
        "CIRCUIT_ID": "_source.BUSINESS_TAG.CIRCUIT_NO",
        "ALARM_ABNORMAL_TYPE": "40",  # 默认值
        "PROJ_OA_FILE_ID": "",  # 默认空值
        "GCSS_CLIENT_GRADE": "",  # 默认空值
        "EFFECT_CIRCUIT_NUM": "",  # 默认空值
        "PREHANDLE": "0",  # 默认值
        "OBJECT_CLASS_TEXT": "_source.OBJECT_CLASS_TEXT",
        "BOARD_TYPE": "",  # 默认空值
        "OBJECT_CLASS": lambda: get_nested_value(es_data, "OBJECT_CLASS_ID"),  # 保持 int 类型
        "LOGIC_ALARM_TYPE": "",  # 默认空值
        "LOGIC_SUB_ALARM_TYPE": "",  # 默认空值
        "EFFECT_NE": lambda: get_nested_value(es_data, "EFFECT_NE_NUM"),  # 保持 int 类型
        "EFFECT_SERVICE": lambda: get_nested_value(es_data, "SATOTAL"),  # 保持 int 类型
        "SPECIAL_FIELD14": "_source.NE_TAG.ROOM_ID",
        "SPECIAL_FIELD7": "_source.BUSINESS_TAG.HOME_CLIENT_NUM",
        "SPECIAL_FIELD21": "",  # 默认空值
        "ALARM_SOURCE": "_source.ALARM_SOURCE",
        "BUSINESS_LAYER": "",  # 默认空值
        "ALARM_TEXT": "_source.SRC_ORG_ALARM_TEXT",
        "CIRCUIT_NO": "_source.BUSINESS_TAG.CIRCUIT_NO",
        "PRODUCT_TYPE": "_source.BUSINESS_TAG.PRODUCT_TYPE",
        "CIRCUIT_LEVEL": "_source.BUSINESS_TAG.CIRCUIT_LEVEL",
        "BUSINESS_TYPE": "_source.BUSINESS_TAG.BUSINESS_TYPE",
        "IRMS_GRID_NAME": "_source.BUSINESS_TAG.IRMS_GRID_NAME",
        "ADMIN_GRID_ID": "_source.BUSINESS_TAG.ADMIN_GRID_ID",
        "HOME_CLIENT_NUM": "_source.BUSINESS_TAG.HOME_CLIENT_NUM",
        "SRC_ID": lambda: f"GZEVENT{str(uuid.uuid4()).replace('-', '')[:16]}",
        "SRC_IS_TEST": lambda: get_nested_value(es_data, "IS_TEST"),  # 从 ES 获取，保持 int 类型
        "SRC_APP_ID": "1001",  # 默认值
        "SRC_ORG_ID": lambda: generate_es_to_kafka_mapping.consistent_fp,
        "ORG_TEXT": "",  # 需要特殊处理
        "TOPIC_PREFIX": "EVENT-GZ",  # 默认值
        "TOPIC_PARTITION": 7,  # 固定值7
        "SPECIAL_FIELD17": "_source.FAULT_DIAGNOSIS",
        "EXTRA_ID2": "_source.EXTRA_ID2",
        "EXTRA_STRING1": "_source.EXTRA_STRING1",
        "PORT_NUM": "_source.PORT_NUM",
        "NE_ADMIN_STATUS": "_source.NE_ADMIN_STATUS",
        "SPECIAL_FIELD18": "",  # 默认空值
        "SPECIAL_FIELD20": "",  # 默认空值
        "TMSC_CAT": "_source.TMSC_CAT",
        "ALARM_NE_STATUS": "",  # 默认空值
        "ALARM_EQP_STATUS": "",  # 默认空值
        "INTERFERENCE_FLAG": "_source.INTERFERENCE_FLAG",
        "SPECIAL_FIELD2": "_source.PROJ_INTERFERENCE_TYPE",
        "custGroupFeature": "",  # 默认空值
        "industryCustType": "",  # 默认空值
        "strategicCustTypeFL": "",  # 默认空值
        "strategicCustTypeSL": "",  # 默认空值
        "FAULT_LOCATION": "_source.FAULT_LOCATION",
        "EVENT_SOURCE": "_source.EVENT_SOURCE",
        "ORIG_ALARM_CLEAR_FP": lambda: generate_es_to_kafka_mapping.consistent_fp,
        "ORIG_ALARM_FP": lambda: generate_es_to_kafka_mapping.consistent_fp,
        "EVENT_ARRIVAL_TIME": lambda: (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
        "CREATION_EVENT_TIME": lambda: generate_creation_event_time(es_data, user_delay_time)
    }

    # 按照标准字段顺序处理每个字段
    for kafka_field in STANDARD_FIELD_ORDER:
        try:
            if kafka_field in field_mapping:
                mapping_rule = field_mapping[kafka_field]
                if callable(mapping_rule):
                    # 如果是函数，直接调用
                    kafka_message[kafka_field] = mapping_rule()
                elif isinstance(mapping_rule, str) and mapping_rule.startswith("_source."):
                    # 如果是 ES 字段路径
                    es_path = mapping_rule.replace("_source.", "")
                    value = get_nested_value(es_data, es_path)
                    # 关键修改：确保所有值都转换为字符串类型
                    if value is not None:
                        kafka_message[kafka_field] = str(value)
                    else:
                        kafka_message[kafka_field] = ""
                else:
                    # 如果是默认值，也转换为字符串
                    kafka_message[kafka_field] = str(mapping_rule) if mapping_rule is not None else ""
            else:
                # 如果不在映射中，设置默认空值
                kafka_message[kafka_field] = ""
        except Exception as e:
            logger.debug(f"处理字段 {kafka_field} 时出错：{e}")
            kafka_message[kafka_field] = ""

    # 重新生成ORG_TEXT字段（使用已按顺序排列的所有字段）
    kafka_message["ORG_TEXT"] = generate_org_text(dict(kafka_message))

    return kafka_message


def get_nested_value(data, path):
    """获取嵌套字典中的值"""
    # 如果数据本身就是_source对象，直接使用
    if isinstance(data, dict) and '_source' in data:
        source_data = data['_source']
        keys = path.split('.')
        current = source_data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    else:
        # 标准的嵌套字典查找
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current


def get_region_from_full_path(es_data):
    """从FULL_REGION_NAME中提取地市级信息
    FULL_REGION_NAME格式: "福建省/福州市/永泰县" -> 返回 "福州市"
    """
    full_region = get_nested_value(es_data, "FULL_REGION_NAME")
    if full_region and isinstance(full_region, str):
        parts = full_region.split('/')
        if len(parts) >= 2:
            return parts[1]  # 返回第二个部分（地市级）
    # 如果无法提取，回退到原来的PROVINCE_NAME
    return get_nested_value(es_data, "PROVINCE_NAME") or ""


def map_professional_type(main_net_sort):
    """将MAIN_NET_SORT_ONE映射为专业类型数字代码
    根据示例数据推测映射关系
    """
    professional_mapping = {
        "电源和配套设备": "4",
        "无线网": "1",
        "传输网": "2",
        "数据网": "3",
        "集团专线": "6",
        "家宽": "7"
        # 可以根据需要添加更多映射
    }

    if main_net_sort and isinstance(main_net_sort, str):
        return professional_mapping.get(main_net_sort.strip(), "")
    return ""


def generate_org_text(kafka_data):
    """生成 ORG_TEXT 字段 - 按照标准 Kafka 消息字段顺序"""
    org_parts = []

    # 按照标准格式组装字段顺序
    field_order = [
        "NETWORK_TYPE_TOP", "ORG_SEVERITY", "REGION_NAME", "ACTIVE_STATUS",
        "CITY_NAME", "EQP_LABEL", "EQP_OBJECT_CLASS", "VENDOR_NAME",
        "VENDOR_ID", "ALARM_RESOURCE_STATUS", "LOCATE_INFO", "NE_LABEL",
        "OBJECT_LEVEL", "PROFESSIONAL_TYPE", "NETWORK_TYPE", "ORG_TYPE",
        "VENDOR_TYPE", "SEND_JT_FLAG", "TITLE_TEXT", "STANDARD_ALARM_NAME",
        "STANDARD_ALARM_ID", "STANDARD_FLAG", "VENDOR_SEVERITY", "PROBABLE_CAUSE",
        "NMS_ALARM_ID", "PROBABLE_CAUSE_TXT", "PREPROCESS_MANNER", "EVENT_TIME",
        "TIME_STAMP", "FP0_FP1_FP2_FP3", "CFP0_CFP1_CFP2_CFP3", "MACHINE_ROOM_INFO",
        "INT_ID", "REDEFINE_SEVERITY", "TYPE_KEYCODE", "NE_LOCATION",
        "ALARM_EXPLANATION", "ALARM_EXPLANATION_ADDITION", "MAINTAIN_GROUP",
        "SITE_TYPE", "SUB_ALARM_TYPE", "EVENT_CAT", "NMS_NAME",
        "CITY_ID", "REMOTE_EQP_LABEL", "REMOTE_RESOURCE_STATUS",
        "REMOTE_PROJ_SUB_STATUS", "REMOTE_INT_ID", "PROJ_NAME",
        "PROJ_OA_FILE_CONTENT", "BUSINESS_REGION_IDS", "BUSINESS_REGIONS",
        "REMOTE_OBJECT_CLASS", "ALARM_REASON", "GCSS_CLIENT",
        "GCSS_CLIENT_NAME", "GCSS_CLIENT_NUM", "GCSS_CLIENT_LEVEL",
        "GCSS_SERVICE", "GCSS_SERVICE_NUM", "GCSS_SERVICE_LEVEL",
        "GCSS_SERVICE_TYPE", "BUSINESS_SYSTEM", "NE_IP",
        "LAYER_RATE", "CIRCUIT_ID", "ALARM_ABNORMAL_TYPE",
        "PROJ_OA_FILE_ID", "GCSS_CLIENT_GRADE", "EFFECT_CIRCUIT_NUM",
        "PREHANDLE", "OBJECT_CLASS_TEXT", "BOARD_TYPE",
        "OBJECT_CLASS", "LOGIC_ALARM_TYPE", "LOGIC_SUB_ALARM_TYPE",
        "EFFECT_NE", "EFFECT_SERVICE", "SPECIAL_FIELD14",
        "SPECIAL_FIELD7", "SPECIAL_FIELD21", "ALARM_SOURCE",
        "BUSINESS_LAYER", "ALARM_TEXT", "CIRCUIT_NO",
        "PRODUCT_TYPE", "CIRCUIT_LEVEL", "BUSINESS_TYPE",
        "IRMS_GRID_NAME", "ADMIN_GRID_ID", "HOME_CLIENT_NUM",
        "SRC_ID", "SRC_IS_TEST", "SRC_APP_ID", "SRC_ORG_ID"
    ]

    for field in field_order:
        # 确保值是字符串类型
        raw_value = kafka_data.get(field, "")
        if raw_value is None:
            value = ""
        else:
            value = str(raw_value)

        # 处理特殊字符 - 确保 value 是字符串后再操作
        if isinstance(value, str) and value:
            value = value.replace("_", "\\_")
        else:
            value = "_"

        org_parts.append(value)

    return "_;".join(org_parts) + "_"


def generate_creation_event_time(es_data, user_delay_time=None):
    """根据 DELAY_TIME 计算 CREATION_EVENT_TIME
    
    Args:
        es_data: ES 源数据
        user_delay_time: 用户手动输入的 DELAY_TIME 值（分钟），如果提供则优先使用
        
    Returns:
        str: 计算后的时间，格式：YYYY-MM-DD HH:MM:SS
    
    说明:
        - 从 ES 数据中提取 DELAY_TIME 字段（单位：分钟）
        - 将 DELAY_TIME 转换为小时数（DELAY_TIME / 60）
        - 使用当前时间减去小时数得到 CREATION_EVENT_TIME
        - 如果没有 DELAY_TIME，默认使用 15 小时
        
    示例:
        DELAY_TIME = 720 -> 720/60 = 12 小时 -> 当前时间 - 12 小时
    """
    # 默认延迟 15 小时
    delay_hours = 15
    
    # 优先使用用户输入的值
    if user_delay_time is not None:
        try:
            delay_hours = int(user_delay_time) / 60
            logger.info(f"使用用户输入的 DELAY_TIME: {user_delay_time} 分钟，转换为 {delay_hours} 小时")
        except (ValueError, TypeError) as e:
            logger.warning(f"用户输入的 DELAY_TIME 无效，使用默认值 15 小时：{e}")
    else:
        # 尝试从 ES 数据中提取 DELAY_TIME
        if isinstance(es_data, dict):
            source_data = es_data.get('_source', {})
            delay_time = None
            
            # 尝试从不同位置获取 DELAY_TIME
            if 'DELAY_TIME' in source_data:
                delay_time = source_data['DELAY_TIME']
            elif isinstance(source_data.get('BUSINESS_TAG'), dict) and 'DELAY_TIME' in source_data['BUSINESS_TAG']:
                delay_time = source_data['BUSINESS_TAG']['DELAY_TIME']
            elif isinstance(source_data.get('DISPATCH_INFO'), dict) and 'DELAY_TIME' in source_data['DISPATCH_INFO']:
                delay_time = source_data['DISPATCH_INFO']['DELAY_TIME']
            
            # 如果找到了 DELAY_TIME，转换为小时数
            if delay_time is not None:
                try:
                    # DELAY_TIME 的单位是分钟，需要转换为小时
                    # 例如：720 分钟 = 12 小时
                    delay_hours = int(delay_time) / 60
                    logger.info(f"从 ES 数据中提取 DELAY_TIME: {delay_time} 分钟，转换为 {delay_hours} 小时")
                except (ValueError, TypeError) as e:
                    logger.warning(f"DELAY_TIME 转换失败，使用默认值 15 小时：{e}")
    
    # 计算时间：当前时间 - DELAY_TIME 小时
    creation_time = (datetime.now() - timedelta(hours=delay_hours)).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"使用 DELAY_TIME: {delay_hours} 小时计算 CREATION_EVENT_TIME: {creation_time}")
    return creation_time


@kafka_generator_bp.route('/')
def kafka_generator_page():
    """Kafka消息生成器页面"""
    return render_template('kafka/kafka_generator.html')


@kafka_generator_bp.route('/field-meta')
def kafka_field_meta():
    """提供前端展示用的字段元数据

    当前版本从内存常量 FIELD_META 读取，后续可改为从 MySQL 读取：
    - 表结构示例：kafka_field_meta(kafka_field, es_field, db_cn, label_cn, remark...)
    """
    mysql_meta = load_field_meta_from_mysql()
    return jsonify({
        "success": True,
        "data": mysql_meta or FIELD_META
    })


@kafka_generator_bp.route('/field-options')
def kafka_field_options():
    """返回某个 Kafka 字段对应维表中的所有配置项

    请求参数:
      - kafka_field: 如 BUSINESS_LAYER / CIRCUIT_LEVEL 等
    """
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    import traceback

    kafka_field = (request.args.get("kafka_field") or "").strip().upper()
    if not kafka_field:
        return jsonify({"success": False, "message": "缺少 kafka_field 参数"}), 400

    table = FIELD_DICT_TABLES.get(kafka_field)
    if not table:
        logger.error(f"[ERROR] 字段 {kafka_field} 未配置维表。可用配置：{list(FIELD_DICT_TABLES.keys())}")
        return jsonify({"success": False, "message": f"字段 {kafka_field} 未配置维表"}), 400
    
    logger.info(f"[INFO] 查询维表：{table}, 字段：{kafka_field}")

    conn = get_mysql_conn_dict_cursor()
    if not conn:
        logger.error(f"[ERROR] MySQL 连接失败")
        return jsonify({"success": False, "message": "MySQL 未配置或不可用"}), 500

    try:
        table_escaped = table.replace("`", "``")
        with conn.cursor() as cur:
            # 简单限制一下返回行数，避免维表过大
            query = f"SELECT * FROM `{table_escaped}` LIMIT 500"
            logger.info(f"[INFO] 执行 SQL: {query}")
            cur.execute(query)
            rows = cur.fetchall() or []
            logger.info(f"[INFO] 查询成功，返回 {len(rows)} 行数据")
            if rows:
                logger.info(f"[INFO] 第一行数据示例：{rows[0]}")
    except Exception as e:
        logger.error(f"[ERROR] 查询失败：{e}")
        logger.error(f"[ERROR] 详细错误：{traceback.format_exc()}")
        return jsonify({
            "success": False,
            "message": f"数据库查询失败：{str(e)}",
            "table": table,
            "field": kafka_field
        }), 500
    finally:
        conn.close()

    # rows 为字典列表：[{col: val, ...}, ...]
    columns = list(rows[0].keys()) if rows else []
    
    logger.info(f"[INFO] 返回数据：{len(columns)} 列，{len(rows)} 行")

    return jsonify({
        "success": True,
        "data": {
            "columns": columns,
            "rows": rows,
        }
    })


def fix_json_keys(raw_data):
    """修复JSON键名未加引号的问题
    将 {key: value} 格式转换为 {"key": value} 格式"""
    import re

    # 更精确的键名匹配模式
    # 匹配字母、数字、下划线组成的键名，前面是{或,
    pattern = r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:'

    def add_quotes(match):
        prefix = match.group(1)  # { 或 ,
        key = match.group(2)  # 键名
        return f'{prefix}"{key}":'

    # 执行替换
    fixed_data = re.sub(pattern, add_quotes, raw_data)

    # 统计修复的数量
    matches_before = re.findall(pattern, raw_data)
    matches_after = re.findall(pattern, fixed_data)

    if len(matches_before) > 0:
        logger.debug(f"检测到 {len(matches_before)} 个未加引号的键名:")
        for key in matches_before:
            logger.debug(f"  - {key}")
        logger.debug(f"已修复 {len(matches_before)} 个键名")

    return fixed_data


def preprocess_json_data(raw_data):
    """预处理JSON数据，修复常见格式问题
    专门针对包含三重引号、控制字符、多余括号等问题的JSON数据"""
    logger.debug("开始预处理 JSON 数据...")

    # 1. 移除BOM标记
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        logger.debug("移除 BOM 标记")

    # 2. 处理三重引号 - 分两步处理
    triple_quote_count = raw_data.count('\"\"\"')
    if triple_quote_count > 0:
        logger.debug(f"检测到 {triple_quote_count} 个三重引号")

        # 【关键】在处理三重引号之前，先全局移除所有单个反斜杠
        # 因为三重引号内的 \中、\触等也需要被处理
        def remove_backslash(match):
            char = match.group(1)
            logger.debug(f"  移除：\\{char} -> {char}")
            return char
                
        raw_data = re.sub(r'\\([^nrtbf\\"/u])', remove_backslash, raw_data)
        logger.debug("已全局移除所有非法单斜杠\n")

        # 第一步：将三重引号替换为临时标记
        raw_data = raw_data.replace('\"\"\"', '__TEMP_TRIPLE_QUOTE__')

        # 第二步：处理嵌套 JSON 字符串内的双引号转义
        def escape_nested_quotes(match):
            content = match.group(1)
            # 只转义双引号和控制字符，不转义反斜杠（留给后面的 fix_invalid_escapes 处理）
            content = content.replace('"', '\\"')
            content = content.replace('\n', '\\n')
            content = content.replace('\r', '\\r')
            content = content.replace('\t', '\\t')
            return f'"{content}"'

        # 匹配临时标记包围的内容并进行转义处理
        raw_data = re.sub(r'__TEMP_TRIPLE_QUOTE__(.*?)__TEMP_TRIPLE_QUOTE__', escape_nested_quotes, raw_data,
                          flags=re.DOTALL)

        logger.debug(f"已完成三重引号处理和嵌套引号转义")

    # 3. 修复非法转义字符 - 新增关键步骤
    def fix_invalid_escapes(text):
        r"""修复非法的转义序列
        JSON 只允许：\\, \", \/, \b, \f, \n, \r, \t, \uXXXX
        其他如 \:, \(，\) 等都是非法的

        注意：此函数处理全局范围内的非法转义，包括字符串内外
        """
        logger.debug(f"\n【fix_invalid_escapes】开始处理，文本长度：{len(text)}")

        # 【关键修改】先处理字符串值内部的过度转义 (四重->双重)
        # 这样在后续保护合法转义时就不会丢失这些反斜杠信息
        def reduce_quadruple_backslashes(match):
            content = match.group(1)
            logger.debug(f"  处理前：{repr(content[:50])}...")
            # 将四个反斜杠减少为两个
            content = content.replace('\\\\\\\\', '\\\\')
            logger.debug(f"  处理后：{repr(content[:50])}...")
            return f'"{content}"'

        text = re.sub(r'"((?:[^"\\]|\\.)*)"', reduce_quadruple_backslashes, text)
        logger.debug("已处理字符串内的四重反斜杠")

        # 策略：先保护合法的转义，然后修复非法的

        # 第一步：临时替换合法的转义序列
        placeholders = {}
        valid_escapes = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']

        for i, escape_seq in enumerate(valid_escapes):
            placeholder = f'__VALID_ESCAPE_{i}__'
            placeholders[placeholder] = escape_seq
            text = text.replace(escape_seq, placeholder)

        # 第二步：处理 \uXXXX 格式
        def protect_unicode(match):
            return f'__UNICODE_{match.group(0)[1:]}__'

        text = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, text)

        # 第三步：【关键】处理多个连续反斜杠后跟 Unicode 的情况
        # 将 \\\uXXXX（三个反斜杠）转换为 \uXXXX（两个反斜杠 + Unicode）
        # 这样 \中 就会保持为 \中（合法的字面反斜杠）
        text = re.sub(r'\\{2,}(?=u[0-9a-fA-F]{4})', r'\\', text)

        # 第四步：【新增】修复所有剩余的单个反斜杠 + 非法字符
        # 这包括字符串内和字符串外的所有非法转义
        # 关键：直接移除单个反斜杠，而不是转换为双反斜杠
        def remove_backslash(match):
            char = match.group(1)
            logger.debug(f"  移除反斜杠：\\{char} -> {char}")
            return char
                
        text = re.sub(r'\\([^nrtbf\\"/u])', remove_backslash, text)
        logger.debug("已移除非法转义的单个反斜杠")

        # 第五步：恢复合法的转义序列
        for placeholder, escape_seq in placeholders.items():
            text = text.replace(placeholder, escape_seq)

        # 恢复 Unicode 转义
        text = re.sub(r'__UNICODE_([0-9a-fA-F]{4})__', r'\\u\1', text)

        return text

    # 应用转义修复
    raw_data = fix_invalid_escapes(raw_data)
    logger.debug("已修复非法转义字符")

    # 【调试】输出第 92 行附近的内容（仅用于开发调试）
    # lines = raw_data.split('\n')
    # if len(lines) >= 92:
    #     logger.debug(f"\n===【调试】第 92 行内容 ===")
    #     logger.debug(lines[91][400:500])
    #     logger.debug(f"========================\n")

    # 4. 处理普通的 JSON 字符串值
    def process_json_strings(text):
        """处理 JSON 字符串值，确保正确转义

        注意：从 curl 命令传来的数据可能包含过度转义
        例如：\\t 应该是 \t (两个字面反斜杠 + t,不是制表符)
        """
        # 匹配双引号包围的内容（非贪婪匹配）
        pattern = r'"((?:[^"\\]|\\.)*)"'

        def replace_string_content(match):
            content = match.group(1)
            original = content
            # 修复过度转义 - 按正确顺序：先处理四重反斜杠
            content = content.replace('\\\\\\\\', '\\\\')  # 四重 -> 双重
            # 然后处理其他过度转义 (这些是在字符串值内部的)
            content = content.replace('\\\\\\n', '\\n')  # \\n -> \n
            content = content.replace('\\\\\\r', '\\r')  # \\r -> \r
            content = content.replace('\\\\\\t', '\\t')  # \\t -> \t
            content = content.replace('\\\\\\"', '\\"')  # \\" -> \"

            # 关键修复：处理剩余的单个反斜杠 + 中文的情况
            # 例如：\中、\触等，这些在 JSON 中是非法的
            # 策略：将 \+ 非标准转义字符替换为 \\+ 该字符 (字面反斜杠)
            def fix_single_backslash(match):
                char = match.group(1)
                return '\\\\' + char  # 返回两个字面反斜杠 + 字符

            content = re.sub(r'\\([^nrtbf\\"/])', fix_single_backslash, content)

            if original != content:
                logger.debug(f"  修复字符串：{repr(original[:50])}... -> {repr(content[:50])}...")
            return f'"{content}"'

        result = re.sub(pattern, replace_string_content, text)
        logger.debug("process_json_strings 完成")
        return result

    # 应用字符串处理
    raw_data = process_json_strings(raw_data)
    logger.debug("已处理双重转义字符")

    # 5. 处理 HTML 实体
    html_entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }

    for entity, replacement in html_entities.items():
        count = raw_data.count(entity)
        if count > 0:
            raw_data = raw_data.replace(entity, replacement)
            logger.debug(f"处理了 {count} 个 '{entity}' HTML 实体")

    # 6. 处理控制字符
    control_chars_removed = 0
    cleaned_data = ''
    problematic_positions = []

    for i, char in enumerate(raw_data):
        char_code = ord(char)
        # 允许：制表符 (9), 换行符 (10), 回车符 (13), 空格及以上 (32+)
        if char_code == 9 or char_code == 10 or char_code == 13 or char_code >= 32:
            cleaned_data += char
        else:
            control_chars_removed += 1
            if control_chars_removed <= 20:
                problematic_positions.append((i, char_code, repr(char)))

    if control_chars_removed > 0:
        logger.debug(f"总共移除了 {control_chars_removed} 个控制字符")
        if problematic_positions:
            logger.debug("前 20 个控制字符位置:")
            for pos, code, char_repr in problematic_positions:
                logger.debug(f"  位置{pos}: ASCII 码{code}, 字符{char_repr}")
        raw_data = cleaned_data

    # 7. 处理尾随逗号
    trailing_commas = len(re.findall(r',\s*([\}\]])', raw_data))
    if trailing_commas > 0:
        raw_data = re.sub(r',\s*([\}\]])', r'\1', raw_data)
        logger.debug(f"处理了 {trailing_commas} 个尾随逗号")

    # 8. 标准化换行符
    raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')

    # 9. 移除行尾空格
    lines = raw_data.split('\n')
    raw_data = '\n'.join(line.rstrip() for line in lines)

    # 10. 修复 JSON 键名未加引号的问题
    def fix_json_keys(data):
        """修复未加引号的 JSON 键名，只处理结构层面的键，不处理字符串内的内容"""
        # 策略：先保护所有字符串，然后处理键名，最后恢复

        string_placeholders = {}
        counter = [0]

        def save_string(match):
            key = f'__STR{counter[0]}__'
            string_placeholders[key] = match.group(0)
            counter[0] += 1
            return key

        # 保护所有字符串
        data = re.sub(r'"(?:[^"\\]|\\.)*"', save_string, data)

        # 现在安全地处理键名（此时所有字符串都被保护了）
        # 关键：键名只能是字母、数字、下划线，不能是占位符
        # 使用负向前瞻排除占位符
        pattern = r'([{,]\s*)(?![a-zA-Z_$]*__[A-Z]+\d+__)([a-zA-Z_$][a-zA-Z0-9_$]*)(\s*:)'

        def add_quotes(match):
            prefix = match.group(1)
            key = match.group(2)
            after = match.group(3)
            return f'{prefix}"{key}"{after}'

        data = re.sub(pattern, add_quotes, data)

        # 恢复字符串（按逆序）
        for i in range(len(string_placeholders) - 1, -1, -1):
            key = f'__STR{i}__'
            if key in string_placeholders:
                data = data.replace(key, string_placeholders[key])

        return data

    raw_data = fix_json_keys(raw_data)

    # 11. 最终 JSON 结构清理
    # 找到第一个完整的JSON对象结束位置
    brace_count = 0
    first_complete_end = -1

    for i, char in enumerate(raw_data):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                first_complete_end = i
                break

    # 如果找到了第一个完整结束位置，只保留到该位置
    if first_complete_end != -1 and first_complete_end < len(raw_data) - 1:
        extra_content = raw_data[first_complete_end + 1:].strip()
        if extra_content:
            logger.debug(f"清理末尾多余内容 ({len(extra_content)} 字符): {repr(extra_content[:30])}")
            raw_data = raw_data[:first_complete_end + 1]

    logger.debug("预处理完成")
    return raw_data


@kafka_generator_bp.route('/generate', methods=['POST'])
def generate_kafka_message():
    """生成 Kafka 消息 API"""
    try:
        # 获取前端传入的参数
        es_source_raw = request.json.get('es_source_raw')
        custom_fields = request.json.get('custom_fields', {})
        delay_time = request.json.get('delay_time')  # 获取用户手动输入的 DELAY_TIME 值

        # 必须提供原始数据
        if not es_source_raw:
            return jsonify({
                "success": False,
                "message": "缺少必要的 es_source_raw 参数"
            }), 400
        
        # 如果 delay_time 是字符串，转换为整数
        if delay_time is not None and isinstance(delay_time, str):
            try:
                delay_time = int(delay_time)
            except (ValueError, TypeError):
                delay_time = None
        
        if delay_time is not None:
            logger.info(f"用户手动输入 DELAY_TIME: {delay_time} 分钟")

        logger.debug(f"\n==========【接收调试】==========")
        logger.debug(f"接收到原始数据，长度：{len(es_source_raw)} 字符")
        logger.debug(f"前 200 字符：{repr(es_source_raw[:200])}")

        # 直接尝试解析，看看到底是什么问题
        try:
            test_parse = json.loads(es_source_raw)
            logger.debug("✅ 直接解析成功!")
        except Exception as e:
            logger.error(f"❌ 直接解析失败：{e}")
            logger.error(f"错误类型：{type(e).__name__}")

        # 查找包含反斜杠的位置
        if '\\' in es_source_raw:
            pos = es_source_raw.find('\\中兴')
            if pos > 0:
                logger.debug(f"\n找到'\\中兴'在位置 {pos}")
                logger.debug(f"上下文：{repr(es_source_raw[max(0,pos-50):pos+50])}")
        logger.debug(f"==============================\n")

        # 预处理数据
        processed_data = preprocess_json_data(es_source_raw)
        
        logger.debug(f"预处理后数据长度：{len(processed_data)} 字符")

        # 尝试解析 JSON 数据
        try:
            es_source_data = json.loads(processed_data)
            logger.debug("✅ JSON 解析成功")
        except Exception as parse_error:
            # 如果还是失败，返回详细的错误信息
            error_msg = str(parse_error)
            logger.error(f"❌ JSON 解析失败：{error_msg}")

            # 尝试定位错误位置
            error_pos_match = re.search(r'line (\d+) column (\d+)', error_msg)
            if error_pos_match:
                line_num = int(error_pos_match.group(1))
                col_num = int(error_pos_match.group(2))
                lines = processed_data.split('\n')
                if line_num <= len(lines):
                    error_line = lines[line_num - 1]
                    context_start = max(0, col_num - 30)
                    context_end = min(len(error_line), col_num + 30)
                    context = error_line[context_start:context_end]
                    error_msg += f" (第{line_num}行附近: '{context}')"

            # 记录错误日志（生产环境可以改为 logger.error）
            import sys
            logger.error(f"\n❌【JSON_ERROR】JSON 解析失败！")
            logger.error(f"完整错误：{error_msg}\n", file=sys.stderr)

            return jsonify({
                "success": False,
                "message": f"JSON 数据格式错误：{error_msg}",
                "debug_info": {
                    "original_length": len(es_source_raw),
                    "processed_length": len(processed_data),
                    "original_preview": es_source_raw[:200],
                    "processed_preview": processed_data[:200]
                }
            }), 400

        # 生成基础 Kafka 消息
        kafka_message = generate_es_to_kafka_mapping(es_source_data, delay_time)

        # 应用自定义字段覆盖
        for field, value in custom_fields.items():
            if field in kafka_message and value:
                kafka_message[field] = value

        # 强制设置某些字段的固定值（不受前端custom_fields影响）
        kafka_message["TOPIC_PARTITION"] = 7  # 固定分区值

        # 按照标准字段顺序重新排列返回数据
        ordered_data = {}
        for field in STANDARD_FIELD_ORDER:
            if field in kafka_message:
                ordered_data[field] = kafka_message[field]
        
        # 添加 DELAY_TIME 信息到返回数据
        delay_time_value = delay_time  # 优先使用用户输入的值
        if delay_time_value is None:
            # 如果没有用户输入，尝试从 ES 数据中提取
            if isinstance(es_source_data, dict):
                source_data = es_source_data.get('_source', es_source_data)
                if 'DELAY_TIME' in source_data:
                    delay_time_value = source_data['DELAY_TIME']
                elif isinstance(source_data.get('BUSINESS_TAG'), dict) and 'DELAY_TIME' in source_data['BUSINESS_TAG']:
                    delay_time_value = source_data['BUSINESS_TAG']['DELAY_TIME']
                elif isinstance(source_data.get('DISPATCH_INFO'), dict) and 'DELAY_TIME' in source_data['DISPATCH_INFO']:
                    delay_time_value = source_data['DISPATCH_INFO']['DELAY_TIME']
        
        # 默认值 15 分钟
        if delay_time_value is None:
            delay_time_value = 15

        # 保存历史记录到数据库
        save_generation_history(es_source_data, ordered_data)
        
        # 使用自定义 JSON 序列化确保字段顺序
        import json as json_lib
        response_data = {
            "success": True,
            "data": ordered_data,
            "delay_time": delay_time_value,  # 返回 DELAY_TIME 值
            "message": "Kafka 消息生成成功",
            "debug_info": {
                "fields_count": len(ordered_data),
                "processed_length": len(processed_data)
            }
        }

        # 手动序列化JSON并保持顺序
        json_response = json_lib.dumps(response_data, ensure_ascii=False, separators=(',', ':'))
        from flask import Response
        return Response(json_response, mimetype='application/json')

    except Exception as e:
        logger.error(f"处理过程中发生错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"生成 Kafka 消息失败：{str(e)}"
        }), 500


def save_generation_history(es_data, kafka_message):
    """保存生成历史记录到数据库"""
    try:
        from utils.mysql_helper import get_mysql_conn_dict_cursor
        
        conn = get_mysql_conn_dict_cursor()
        if not conn:
            logger.warning("MySQL 未配置，跳过历史记录保存")
            return
        
        try:
            # 提取关键信息
            fp_value = kafka_message.get('FP0_FP1_FP2_FP3', '')
            alarm_name = kafka_message.get('TITLE_TEXT', '')
            alarm_level = kafka_message.get('ORG_SEVERITY', '')
            region_name = kafka_message.get('REGION_NAME', '')
            
            with conn.cursor() as cur:
                query = """
                    INSERT INTO knowledge_base.kafka_generation_history 
                    (es_source_raw, kafka_message, fp_value, alarm_name, alarm_level, region_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(query, (
                    json.dumps(es_data, ensure_ascii=False),
                    json.dumps(kafka_message, ensure_ascii=False),
                    fp_value,
                    alarm_name,
                    alarm_level,
                    region_name
                ))
                conn.commit()
                logger.info(f"历史记录已保存：FP={fp_value}, 告警={alarm_name}")
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"保存历史记录失败：{e}")


@kafka_generator_bp.route('/history', methods=['GET'])
def get_generation_history():
    """获取生成历史记录（支持搜索 ES 源数据和 Kafka 消息）"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        keyword = request.args.get('keyword', '', type=str)
        
        conn = get_mysql_conn_dict_cursor()
        if not conn:
            return jsonify({"success": False, "message": "MySQL 未配置"}), 500
        
        try:
            with conn.cursor() as cur:
                # 构建查询条件
                where_clause = "WHERE 1=1"
                params = []
                
                if keyword:
                    # ★★★★★ 关键修复：支持搜索 Kafka 消息中的字段名和字段值
                    # 使用 JSON_CONTAINS_PATH 或 LIKE 搜索 kafka_message 中的字段
                    where_clause += """ 
                        AND (
                            alarm_name LIKE %s 
                            OR fp_value LIKE %s 
                            OR region_name LIKE %s 
                            OR es_source_raw LIKE %s 
                            OR kafka_message LIKE %s
                        )
                    """
                    keyword_pattern = f"%{keyword}%"
                    params.extend([
                        keyword_pattern, keyword_pattern, keyword_pattern, 
                        keyword_pattern, keyword_pattern
                    ])
                    
                    logger.info(f"[HISTORY SEARCH] 关键字: {keyword}, 将搜索 alarm_name, fp_value, region_name, es_source_raw, kafka_message")
                
                # 查询总数
                count_query = f"SELECT COUNT(*) as total FROM knowledge_base.kafka_generation_history {where_clause}"
                cur.execute(count_query, params)
                total = cur.fetchone()['total']
                
                # 查询数据 (分页)
                offset = (page - 1) * per_page
                data_query = f"""
                    SELECT id, created_at, fp_value, alarm_name, alarm_level, region_name, 
                           es_source_raw, kafka_message
                    FROM knowledge_base.kafka_generation_history 
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                cur.execute(data_query, params + [per_page, offset])
                rows = cur.fetchall() or []
                
                # 格式化返回数据
                history_list = []
                for row in rows:
                    kafka_msg = row.get('kafka_message')
                    es_raw = row.get('es_source_raw')
                    
                    # es_source_raw 保持原始字符串格式，但进行格式化
                    if es_raw and isinstance(es_raw, str):
                        try:
                            # 尝试解析并格式化 JSON
                            es_parsed = json.loads(es_raw)
                            es_raw_str = json.dumps(es_parsed, ensure_ascii=False, indent=2)
                        except:
                            # 如果解析失败，保持原始字符串
                            es_raw_str = es_raw
                    elif es_raw:
                        es_raw_str = json.dumps(es_raw, ensure_ascii=False, indent=2)
                    else:
                        es_raw_str = None
                    
                    # kafka_message 保持原始字符串格式，但进行格式化
                    if kafka_msg and isinstance(kafka_msg, str):
                        try:
                            # 尝试解析并格式化 JSON
                            kafka_parsed = json.loads(kafka_msg)
                            kafka_msg_str = json.dumps(kafka_parsed, ensure_ascii=False, indent=2)
                        except:
                            # 如果解析失败，保持原始字符串
                            kafka_msg_str = kafka_msg
                    elif kafka_msg:
                        kafka_msg_str = json.dumps(kafka_msg, ensure_ascii=False, indent=2)
                    else:
                        kafka_msg_str = None
                    
                    history_list.append({
                        'id': row['id'],
                        'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else '',
                        'fp_value': row['fp_value'] or '',
                        'alarm_name': row['alarm_name'] or '',
                        'alarm_level': row['alarm_level'] or '',
                        'region_name': row['region_name'] or '',
                        'es_source_raw': es_raw_str,  # 格式化后的 JSON 字符串
                        'kafka_message': kafka_msg_str  # 格式化后的 JSON 字符串
                    })
                
                return jsonify({
                    "success": True,
                    "data": {
                        "list": history_list,
                        "total": total,
                        "page": page,
                        "per_page": per_page
                    },
                    "message": "查询成功"
                })
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"获取历史记录失败：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@kafka_generator_bp.route('/history/<int:history_id>', methods=['GET'])
def get_generation_history_detail(history_id):
    """获取单条历史记录的详细信息"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    try:
        conn = get_mysql_conn_dict_cursor()
        if not conn:
            return jsonify({"success": False, "message": "MySQL 未配置"}), 500
        
        try:
            with conn.cursor() as cur:
                query = """
                    SELECT id, created_at, es_source_raw, kafka_message, fp_value, alarm_name, alarm_level, region_name
                    FROM knowledge_base.kafka_generation_history
                    WHERE id = %s
                """
                cur.execute(query, (history_id,))
                row = cur.fetchone()
                
                if not row:
                    return jsonify({"success": False, "message": "记录不存在"}), 404
                
                # 格式化返回数据
                kafka_msg = row.get('kafka_message')
                es_raw = row.get('es_source_raw')
                
                if kafka_msg and isinstance(kafka_msg, str):
                    try:
                        kafka_msg = json.loads(kafka_msg)
                    except:
                        pass
                
                if es_raw and isinstance(es_raw, str):
                    try:
                        es_raw = json.loads(es_raw)
                    except:
                        pass
                
                return jsonify({
                    "success": True,
                    "data": {
                        'id': row['id'],
                        'created_at': row['created_at'].strftime('%Y-%m-%d %H:%M:%S') if row['created_at'] else '',
                        'fp_value': row['fp_value'] or '',
                        'alarm_name': row['alarm_name'] or '',
                        'alarm_level': row['alarm_level'] or '',
                        'region_name': row['region_name'] or '',
                        'es_source_raw': es_raw,
                        'kafka_message': kafka_msg
                    }
                })
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"获取历史记录详情失败：{e}")
        return jsonify({"success": False, "message": str(e)}), 500


@kafka_generator_bp.route('/generate-push-message', methods=['POST'])
def generate_push_message():
    """生成推送消息 API"""
    try:
        # 获取前端传入的参数
        fp_value = request.json.get('fp_value')
        event_time = request.json.get('event_time')
        active_status = request.json.get('active_status', '3')
        
        # 验证必要参数
        if not fp_value:
            return jsonify({
                "success": False,
                "message": "缺少必要的 fp_value 参数"
            }), 400
        
        # 如果没有提供事件时间，使用当前时间
        if not event_time:
            event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建推送消息
        push_message = {
            "ACTIVE_STATUS": str(active_status),
            "CFP0_CFP1_CFP2_CFP3": fp_value,
            "EVENT_TIME": event_time,
            "FP0_FP1_FP2_FP3": fp_value
        }
        
        logger.info(f"推送消息生成成功：FP={fp_value}")
        
        return jsonify({
            "success": True,
            "data": push_message,
            "message": "推送消息生成成功"
        })
        
    except Exception as e:
        logger.error(f"生成推送消息失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"生成推送消息失败：{str(e)}"
        }), 500


def save_generation_history(es_data, kafka_message):
    """保存生成历史记录到数据库"""
    try:
        from utils.mysql_helper import get_mysql_conn_dict_cursor
        
        conn = get_mysql_conn_dict_cursor()
        if not conn:
            logger.warning("MySQL 未配置，跳过历史记录保存")
            return
        
        try:
            # 提取关键信息
            fp_value = kafka_message.get('FP0_FP1_FP2_FP3', '')
            alarm_name = kafka_message.get('TITLE_TEXT', '')
            alarm_level = kafka_message.get('ORG_SEVERITY', '')
            region_name = kafka_message.get('REGION_NAME', '')
            
            with conn.cursor() as cur:
                query = """
                    INSERT INTO knowledge_base.kafka_generation_history 
                    (es_source_raw, kafka_message, fp_value, alarm_name, alarm_level, region_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cur.execute(query, (
                    json.dumps(es_data, ensure_ascii=False),
                    json.dumps(kafka_message, ensure_ascii=False),
                    fp_value,
                    alarm_name,
                    alarm_level,
                    region_name
                ))
                conn.commit()
                logger.info(f"历史记录已保存：FP={fp_value}, 告警={alarm_name}")
        finally:
            conn.close()
    except Exception as e:
        logger.error(f"保存历史记录失败：{e}")


@kafka_generator_bp.route('/config')
def get_config():
    """获取应用配置信息 1"""
    import os
    port = os.environ.get("PORT", 5002)
    return jsonify({
        "success": True,
        "data": {
            "port": port,
            "host": "127.0.0.1"
        }
    })


@kafka_generator_bp.route('/field-cache', methods=['GET'])
def get_field_cache():
    """获取所有字段缓存（包括置顶状态和历史值）"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        return jsonify({"success": False, "message": "MySQL 未配置"}), 500
    
    try:
        with conn.cursor() as cur:
            query = "SELECT field_name, field_value, is_pinned, history_values FROM knowledge_base.kafka_field_cache"
            cur.execute(query)
            rows = cur.fetchall()
            
            logger.info(f"查询到 {len(rows)} 条缓存记录")
            
            cache_data = {}
            pinned_fields = []
            history_data = {}
            
            for row in rows:
                if row['field_value']:
                    cache_data[row['field_name']] = row['field_value']
                if row['is_pinned']:
                    pinned_fields.append(row['field_name'])
                
                # 处理历史值
                history_val = row['history_values']
                if history_val:
                    try:
                        # 如果是字符串，解析 JSON
                        if isinstance(history_val, str):
                            parsed = json.loads(history_val)
                            history_data[row['field_name']] = parsed
                            logger.info(f"字段 {row['field_name']} 历史值 (字符串解析): {parsed}")
                        elif isinstance(history_val, (list, tuple)):
                            # 如果已经是列表或元组
                            history_data[row['field_name']] = list(history_val)
                            logger.info(f"字段 {row['field_name']} 历史值 (列表): {history_val}")
                        else:
                            # 其他类型，尝试直接转换
                            history_data[row['field_name']] = history_val
                            logger.warning(f"字段 {row['field_name']} 历史值未知类型：{type(history_val)}")
                    except Exception as e:
                        logger.error(f"解析 {row['field_name']} 历史值失败：{e}, 原始值：{history_val}")
                        history_data[row['field_name']] = []
            
            logger.info(f"返回缓存数据：{len(cache_data)} 个字段值，{len(pinned_fields)} 个置顶，{len(history_data)} 个历史值")
            
            return jsonify({
                "success": True,
                "data": {
                    "field_cache": cache_data,
                    "pinned_fields": pinned_fields,
                    "history_values": history_data
                }
            })
    except Exception as e:
        logger.error(f"获取字段缓存失败：{e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@kafka_generator_bp.route('/field-cache', methods=['POST'])
def save_field_cache():
    """保存字段值和置顶状态"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "缺少数据"}), 400
    
    field_name = data.get('field_name', '').strip().upper()
    field_value = data.get('field_value', '')
    is_pinned = 1 if data.get('is_pinned', False) else 0
    
    if not field_name:
        return jsonify({"success": False, "message": "缺少字段名称"}), 400
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        return jsonify({"success": False, "message": "MySQL 未配置"}), 500
    
    try:
        with conn.cursor() as cur:
            # 使用 INSERT ... ON DUPLICATE KEY UPDATE
            query = """
                INSERT INTO knowledge_base.kafka_field_cache (field_name, field_value, is_pinned)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    field_value = VALUES(field_value),
                    is_pinned = VALUES(is_pinned),
                    updated_at = CURRENT_TIMESTAMP
            """
            cur.execute(query, (field_name, field_value, is_pinned))
            conn.commit()
            
            return jsonify({"success": True, "message": "保存成功"})
    except Exception as e:
        logger.error(f"保存字段缓存失败：{e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@kafka_generator_bp.route('/field-cache/batch', methods=['POST'])
def save_batch_field_cache():
    """批量保存字段缓存（用于页面卸载时）"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "缺少数据"}), 400
    
    field_cache = data.get('field_cache', {})
    pinned_fields = data.get('pinned_fields', [])
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        return jsonify({"success": False, "message": "MySQL 未配置"}), 500
    
    try:
        with conn.cursor() as cur:
            # 保存字段值
            for field_name, field_value in field_cache.items():
                field_name = field_name.strip().upper()
                is_pinned = 1 if field_name in pinned_fields else 0
                
                query = """
                    INSERT INTO knowledge_base.kafka_field_cache (field_name, field_value, is_pinned)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        field_value = VALUES(field_value),
                        is_pinned = VALUES(is_pinned),
                        updated_at = CURRENT_TIMESTAMP
                """
                cur.execute(query, (field_name, field_value if field_value else None, is_pinned))
            
            conn.commit()
            return jsonify({"success": True, "message": "批量保存成功"})
    except Exception as e:
        logger.error(f"批量保存字段缓存失败：{e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@kafka_generator_bp.route('/field-history', methods=['POST'])
def save_field_history():
    """保存字段历史值"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "缺少数据"}), 400
    
    field_name = data.get('field_name', '').strip().upper()
    field_value = data.get('field_value', '').strip()
    
    if not field_name or not field_value:
        return jsonify({"success": False, "message": "缺少字段名称或值"}), 400
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        return jsonify({"success": False, "message": "MySQL 未配置"}), 500
    
    try:
        with conn.cursor() as cur:
            # 先获取现有历史值
            cur.execute("SELECT history_values FROM knowledge_base.kafka_field_cache WHERE field_name = %s", (field_name,))
            row = cur.fetchone()
            
            if row and row['history_values']:
                try:
                    history = json.loads(row['history_values'])
                except:
                    history = []
            else:
                history = []
            
            # 如果值已存在，移到最前面
            if field_value in history:
                history.remove(field_value)
            
            # 添加到最前面
            history.insert(0, field_value)
            
            # 只保留最近 20 条记录
            history = history[:20]
            
            # 更新数据库
            query = """
                INSERT INTO knowledge_base.kafka_field_cache (field_name, history_values)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE 
                    history_values = VALUES(history_values),
                    updated_at = CURRENT_TIMESTAMP
            """
            cur.execute(query, (field_name, json.dumps(history, ensure_ascii=False)))
            conn.commit()
            
            return jsonify({"success": True, "message": "历史值已保存"})
    except Exception as e:
        logger.error(f"保存字段历史值失败：{e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


@kafka_generator_bp.route('/field-history', methods=['DELETE'])
def delete_field_history():
    """删除字段的历史值"""
    from utils.mysql_helper import get_mysql_conn_dict_cursor
    
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "缺少数据"}), 400
    
    field_name = data.get('field_name', '').strip().upper()
    value_to_delete = data.get('value', '').strip()
    
    if not field_name:
        return jsonify({"success": False, "message": "缺少字段名称"}), 400
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        return jsonify({"success": False, "message": "MySQL 未配置"}), 500
    
    try:
        with conn.cursor() as cur:
            # 获取现有历史值
            cur.execute("SELECT history_values FROM knowledge_base.kafka_field_cache WHERE field_name = %s", (field_name,))
            row = cur.fetchone()
            
            if row and row['history_values']:
                try:
                    history = json.loads(row['history_values'])
                    # 删除指定的值
                    if value_to_delete in history:
                        history.remove(value_to_delete)
                        # 更新数据库
                        cur.execute("""
                            UPDATE knowledge_base.kafka_field_cache 
                            SET history_values = %s, updated_at = CURRENT_TIMESTAMP 
                            WHERE field_name = %s
                        """, (json.dumps(history, ensure_ascii=False), field_name))
                        conn.commit()
                except Exception as e:
                    logger.error(f"解析历史值失败：{e}")
            
            return jsonify({"success": True, "message": "历史值已删除"})
    except Exception as e:
        logger.error(f"删除字段历史值失败：{e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()