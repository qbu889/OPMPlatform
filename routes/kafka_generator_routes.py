#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka消息生成器路由
根据ES数据生成对应的Kafka消息
"""
from flask import Blueprint, render_template, request, jsonify
from flask_cors import CORS
import re
import uuid
from datetime import datetime, timedelta
import json


kafka_generator_bp = Blueprint('kafka_generator_bp', __name__, url_prefix='/kafka-generator')

def generate_unique_fp():
    """生成唯一的FP值"""
    # 基于当前时间和随机数生成
    timestamp = str(int(datetime.now().timestamp()))
    random_part = str(uuid.uuid4().int)[:10]
    return f"{timestamp}_{random_part}"

def generate_es_to_kafka_mapping(es_data):
    """将ES数据映射为Kafka消息"""
    kafka_message = {}
    
    # 基础字段映射
    field_mapping = {
        "ID": lambda: str(uuid.uuid4()),
        "NETWORK_TYPE_TOP": "_source.NETWORK_TYPE_ID",
        "ORG_SEVERITY": "_source.ALARM_LEVEL",
        "REGION_NAME": "_source.PROVINCE_NAME",
        "ACTIVE_STATUS": "1",  # 默认值
        "CITY_NAME": "_source.CITY_NAME",
        "EQP_LABEL": "_source.EQUIPMENT_NAME",
        "EQP_OBJECT_CLASS": "_source.OBJECT_CLASS_ID",
        "VENDOR_NAME": "_source.VENDOR_NAME",
        "VENDOR_ID": "_source.VENDOR_ID",
        "ALARM_RESOURCE_STATUS": "_source.ALARM_RESOURCE_STATUS",
        "LOCATE_INFO": "_source.EVENT_LOCATION",
        "NE_LABEL": "_source.NE_LABEL",
        "OBJECT_LEVEL": "",  # 默认空值
        "PROFESSIONAL_TYPE": "_source.MAIN_NET_SORT_ONE",
        "NETWORK_TYPE": "_source.NETWORK_SUB_TYPE_ID",
        "ORG_TYPE": "_source.ORG_TYPE",
        "VENDOR_TYPE": "_source.VENDOR_EVENT_TYPE",
        "SEND_JT_FLAG": "0",  # 默认值
        "TITLE_TEXT": "_source.ALARM_NAME",
        "STANDARD_ALARM_NAME": "_source.ALARM_STANDARD_NAME",
        "STANDARD_ALARM_ID": "_source.ALARM_STANDARD_ID",
        "STANDARD_FLAG": "_source.ALARM_STANDARD_FLAG",
        "VENDOR_SEVERITY": "_source.VENDOR_SEVERITY",
        "PROBABLE_CAUSE": "_source.EVENT_PROBABLE_CAUSE_TXT",
        "NMS_ALARM_ID": "_source.NMS_ALARM_ID",
        "PROBABLE_CAUSE_TXT": "_source.EVENT_PROBABLE_CAUSE_TXT",
        "PREPROCESS_MANNER": "",  # 默认空值
        "EVENT_TIME": lambda: (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
        "TIME_STAMP": lambda: str(int((datetime.now() - timedelta(minutes=15)).timestamp())),
        "FP0_FP1_FP2_FP3": generate_unique_fp,
        "CFP0_CFP1_CFP2_CFP3": generate_unique_fp,
        "MACHINE_ROOM_INFO": "_source.NE_TAG.MACHINE_ROOM_INFO",
        "INT_ID": "0",  # 默认值
        "REDEFINE_SEVERITY": "_source.ALARM_LEVEL",
        "TYPE_KEYCODE": "_source.TYPE_KEYCODE",
        "NE_LOCATION": "_source.NE_LOCATION",
        "ALARM_EXPLANATION": "_source.EVENT_EXPLANATION",
        "ALARM_EXPLANATION_ADDITION": "_source.EVENT_EXPLANATION_ADDITION",
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
        "GCSS_CLIENT": "_source.BUSINESS_TAG.GCSS_CLIENT",
        "GCSS_CLIENT_NAME": "_source.BUSINESS_TAG.GCSS_CLIENT_NAME",
        "GCSS_CLIENT_NUM": "_source.BUSINESS_TAG.GCSS_CLIENT_NUM",
        "GCSS_CLIENT_LEVEL": "_source.BUSINESS_TAG.GCSS_CLIENT_LEVEL",
        "GCSS_SERVICE": "_source.BUSINESS_TAG.GCSS_SERVICE",
        "GCSS_SERVICE_NUM": "_source.BUSINESS_TAG.GCSS_SERVICE_NUM",
        "GCSS_SERVICE_LEVEL": "_source.BUSINESS_TAG.GCSS_SERVICE_LEVEL",
        "GCSS_SERVICE_TYPE": "_source.BUSINESS_TAG.GCSS_SERVICE_TYPE",
        "BUSINESS_SYSTEM": "_source.BUSINESS_TAG.BUSINESS_SYSTEM",
        "NE_IP": "_source.EQUIPMENT_IP",
        "LAYER_RATE": "",  # 默认空值
        "CIRCUIT_ID": "_source.BUSINESS_TAG.CIRCUIT_NO",
        "ALARM_ABNORMAL_TYPE": "40",  # 默认值
        "PROJ_OA_FILE_ID": "",  # 默认空值
        "GCSS_CLIENT_GRADE": "_source.BUSINESS_TAG.GCSS_CLIENT_GRADE",
        "EFFECT_CIRCUIT_NUM": "_source.BUSINESS_TAG.EFFECT_CIRCUIT_NUM",
        "PREHANDLE": "0",  # 默认值
        "OBJECT_CLASS_TEXT": "_source.OBJECT_CLASS_TEXT",
        "BOARD_TYPE": "",  # 默认空值
        "OBJECT_CLASS": "_source.OBJECT_CLASS_ID",
        "LOGIC_ALARM_TYPE": "_source.LOGIC_ALARM_TYPE",
        "LOGIC_SUB_ALARM_TYPE": "_source.LOGIC_SUB_ALARM_TYPE",
        "EFFECT_NE": "_source.EFFECT_NE_NUM",
        "EFFECT_SERVICE": "_source.SATOTAL",
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
        "SRC_IS_TEST": 0,  # 默认值
        "SRC_APP_ID": "1001",  # 默认值
        "SRC_ORG_ID": generate_unique_fp,
        "ORG_TEXT": "",  # 需要特殊处理
        "TOPIC_PREFIX": "EVENT-GZ",  # 默认值
        "TOPIC_PARTITION": lambda: hash(str(uuid.uuid4())) % 50,  # 0-49的分区
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
        "industryCustType": "_source.INDUSTRY_CUST_TYPE",
        "strategicCustTypeFL": "",  # 默认空值
        "strategicCustTypeSL": "",  # 默认空值
        "FAULT_LOCATION": "_source.FAULT_LOCATION",
        "SPECIAL_FIELD0": "_source.ALARM_UNIQUE_ID",
        "EVENT_SOURCE": "_source.EVENT_SOURCE",
        "ORIG_ALARM_CLEAR_FP": generate_unique_fp,
        "ORIG_ALARM_FP": generate_unique_fp,
        "EVENT_ARRIVAL_TIME": lambda: (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"),
        "CREATION_EVENT_TIME": lambda: (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 处理每个字段
    for kafka_field, mapping_rule in field_mapping.items():
        try:
            if callable(mapping_rule):
                # 如果是函数，直接调用
                kafka_message[kafka_field] = mapping_rule()
            elif mapping_rule.startswith("_source."):
                # 如果是ES字段路径
                es_path = mapping_rule.replace("_source.", "")
                value = get_nested_value(es_data, es_path)
                kafka_message[kafka_field] = value if value is not None else ""
            else:
                # 如果是默认值
                kafka_message[kafka_field] = mapping_rule
        except Exception as e:
            print(f"处理字段 {kafka_field} 时出错: {e}")
            kafka_message[kafka_field] = ""
    
    # 特殊处理 ORG_TEXT 字段
    kafka_message["ORG_TEXT"] = generate_org_text(kafka_message)
    
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

def generate_org_text(kafka_data):
    """生成ORG_TEXT字段"""
    org_parts = []
    
    # 按照样例格式组装
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
        
        # 处理特殊字符 - 确保value是字符串后再操作
        if isinstance(value, str) and value:
            value = value.replace("_", "\\_")
        else:
            value = "_"
            
        org_parts.append(value)
    
    return "_;".join(org_parts) + "_"

@kafka_generator_bp.route('/')
def kafka_generator_page():
    """Kafka消息生成器页面"""
    return render_template('kafka_generator.html')

def fix_json_keys(raw_data):
    """修复JSON键名未加引号的问题
    将 {key: value} 格式转换为 {"key": value} 格式"""
    import re
    
    # 更精确的键名匹配模式
    # 匹配字母、数字、下划线组成的键名，前面是{或,
    pattern = r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:'
    
    def add_quotes(match):
        prefix = match.group(1)  # { 或 ,
        key = match.group(2)     # 键名
        return f'{prefix}"{key}":'
    
    # 执行替换
    fixed_data = re.sub(pattern, add_quotes, raw_data)
    
    # 统计修复的数量
    matches_before = re.findall(pattern, raw_data)
    matches_after = re.findall(pattern, fixed_data)
    
    if len(matches_before) > 0:
        print(f"检测到 {len(matches_before)} 个未加引号的键名:")
        for _, key in matches_before:
            print(f"  - {key}")
        print(f"已修复 {len(matches_before)} 个键名")
    
    return fixed_data

def preprocess_json_data(raw_data):
    """预处理JSON数据，修复常见格式问题
    专门针对包含三重引号、控制字符、多余括号等问题的JSON数据"""
    print("开始预处理JSON数据...")
    
    # 1. 移除BOM标记
    if raw_data.startswith('\ufeff'):
        raw_data = raw_data[1:]
        print("移除BOM标记")
    
    # 2. 处理三重引号和字符串内引号
    triple_quote_count = raw_data.count('"""')
    if triple_quote_count > 0:
        raw_data = raw_data.replace('"""', '"')
        print(f"处理了 {triple_quote_count} 个三重引号")
    
    # 处理字符串内的引号转义
    def escape_string_quotes(match):
        content = match.group(1)
        # 转义字符串内的双引号
        content = content.replace('"', '\\"')
        # 转义换行符和制表符
        content = content.replace('\n', '\\n')
        content = content.replace('\t', '\\t')
        # 修复无效转义
        content = re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\1', content)
        return f'"{content}"'
    
    raw_data = re.sub(r'"(.*?)"', escape_string_quotes, raw_data, flags=re.DOTALL)
    
    # 3. 处理HTML实体
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
            print(f"处理了 {count} 个 '{entity}' HTML实体")
    
    # 4. 特别处理字符串内的换行符和特殊字符（跳过，已在步骤2处理）
    
    # 5. 处理控制字符
    control_chars_removed = 0
    cleaned_data = ''
    problematic_positions = []
    
    for i, char in enumerate(raw_data):
        char_code = ord(char)
        # 允许: 制表符(9), 换行符(10), 回车符(13), 空格及以上(32+)
        if char_code == 9 or char_code == 10 or char_code == 13 or char_code >= 32:
            cleaned_data += char
        else:
            control_chars_removed += 1
            if control_chars_removed <= 20:  # 增加显示的数量
                problematic_positions.append((i, char_code, repr(char)))
            
    if control_chars_removed > 0:
        print(f"总共移除了 {control_chars_removed} 个控制字符")
        if problematic_positions:
            print("前20个控制字符位置:")
            for pos, code, char_repr in problematic_positions:
                print(f"  位置{pos}: ASCII码{code}, 字符{char_repr}")
        raw_data = cleaned_data
    
    # 6. 处理尾随逗号
    trailing_commas = len(re.findall(r',\s*([\}\]])', raw_data))
    if trailing_commas > 0:
        raw_data = re.sub(r',\s*([\}\]])', r'\1', raw_data)
        print(f"处理了 {trailing_commas} 个尾随逗号")
    
    # 7. 标准化换行符
    raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')
    
    # 8. 移除行尾空格
    lines = raw_data.split('\n')
    raw_data = '\n'.join(line.rstrip() for line in lines)
    
    # 9. 修复JSON键名未加引号的问题
    raw_data = fix_json_keys(raw_data)
    
    # 10. 最终JSON结构清理 - 最保守的方法
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
            print(f"清理末尾多余内容 ({len(extra_content)} 字符): {repr(extra_content[:30])}")
            raw_data = raw_data[:first_complete_end + 1]
    
    print("预处理完成")
    return raw_data

@kafka_generator_bp.route('/generate', methods=['POST'])
def generate_kafka_message():
    """生成Kafka消息API"""
    try:
        # 获取前端传入的参数
        es_source_raw = request.json.get('es_source_raw')
        custom_fields = request.json.get('custom_fields', {})
        
        # 必须提供原始数据
        if not es_source_raw:
            return jsonify({
                "success": False,
                "message": "缺少必要的es_source_raw参数"
            }), 400
        
        # 预处理数据
        processed_data = preprocess_json_data(es_source_raw)
        
        # 尝试解析JSON数据
        try:
            es_source_data = json.loads(processed_data)
            print("JSON解析成功")
        except Exception as parse_error:
            # 如果还是失败，返回详细的错误信息
            error_msg = str(parse_error)
            print(f"JSON解析失败: {error_msg}")
            
            # 尝试定位错误位置
            error_pos_match = re.search(r'line (\d+) column (\d+)', error_msg)
            if error_pos_match:
                line_num = int(error_pos_match.group(1))
                col_num = int(error_pos_match.group(2))
                lines = processed_data.split('\n')
                if line_num <= len(lines):
                    error_line = lines[line_num - 1]
                    context_start = max(0, col_num - 20)
                    context_end = min(len(error_line), col_num + 20)
                    context = error_line[context_start:context_end]
                    error_msg += f" (第{line_num}行附近: '{context}')"
            
            return jsonify({
                "success": False,
                "message": f"JSON数据格式错误: {error_msg}",
                "debug_info": {
                    "original_length": len(es_source_raw),
                    "processed_length": len(processed_data)
                }
            }), 400
        
        # 生成基础Kafka消息
        kafka_message = generate_es_to_kafka_mapping(es_source_data)
        
        # 应用自定义字段覆盖
        for field, value in custom_fields.items():
            if field in kafka_message and value:
                kafka_message[field] = value
        
        return jsonify({
            "success": True,
            "data": kafka_message,
            "message": "Kafka消息生成成功"
        })
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"生成Kafka消息失败: {str(e)}"
        }), 500

@kafka_generator_bp.route('/fixer')
def json_fixer_page():
    return render_template('json_fixer.html')

@kafka_generator_bp.route('/config')
def get_config():
    """获取应用配置信息"""
    import os
    port = os.environ.get("PORT", 5002)
    return jsonify({
        "success": True,
        "data": {
            "port": port,
            "host": "127.0.0.1"
        }
    })