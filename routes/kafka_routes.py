# routes/kafka_routes.py
from flask import Blueprint, request, jsonify, render_template
import json
import time
import random
from datetime import datetime, timedelta
import logging

# 创建蓝图
kafka_bp = Blueprint('kafka', __name__)
logger = logging.getLogger(__name__)

# 基础Kafka消息模板
BASE_KAFKA_MSG = {
    "ID": "f1a6dd93-c657-4842-a256-43ef9f295399",
    "NETWORK_TYPE_TOP": "5",
    "ORG_SEVERITY": "3",
    "REGION_NAME": "莆田市",
    "ACTIVE_STATUS": "1",
    "CITY_NAME": "涵江区",
    "EQP_LABEL": "【测试】莆田涵江埭里局楼三楼310配电室机房",
    "EQP_OBJECT_CLASS": "30014",
    "VENDOR_NAME": "高新兴",
    "VENDOR_ID": "771",
    "ALARM_RESOURCE_STATUS": "1",
    "LOCATE_INFO": "基站_莆田市_全业务/汇聚节点_涵江区_中恒分立式ZHM15",
    "NE_LABEL": "【测试】莆田涵江埭里局楼三楼310配电室机房",
    "OBJECT_LEVEL": "",
    "PROFESSIONAL_TYPE": "4",
    "NETWORK_TYPE": "500",
    "ORG_TYPE": "1",
    "VENDOR_TYPE": "1",
    "SEND_JT_FLAG": "1",
    "TITLE_TEXT": "市电缺相",
    "STANDARD_ALARM_NAME": "市电缺相",
    "STANDARD_ALARM_ID": "0500-009-092-10-000026",
    "STANDARD_FLAG": "2",
    "VENDOR_SEVERITY": "三级告警",
    "PROBABLE_CAUSE": "006031",
    "NMS_ALARM_ID": "256980820",
    "PROBABLE_CAUSE_TXT": "0",
    "PREPROCESS_MANNER": "",
    "EVENT_TIME": "",  # 动态生成
    "TIME_STAMP": "1767061484",
    "FP0_FP1_FP2_FP3": "",  # 动态生成
    "CFP0_CFP1_CFP2_CFP3": "",  # 动态生成
    "MACHINE_ROOM_INFO": "",  # 前端输入
    "INT_ID": "7019298309868131851",
    "REDEFINE_SEVERITY": "1",
    "TYPE_KEYCODE": "关联到资源,OLT归属机房,",
    "NE_LOCATION": "无线设备：CBN-莆田涵江埭里局楼三楼310配电室机房-梧塘溪游村C-ZRHH-BBU01...",
    "ALARM_EXPLANATION": "交流输入故障或输入空开跳",
    "ALARM_EXPLANATION_ADDITION": "传输节点",
    "MAINTAIN_GROUP": "莆田动环维护组",
    "SITE_TYPE": "103",
    "SUB_ALARM_TYPE": "",
    "EVENT_CAT": "",
    "NMS_NAME": "高新兴动环系统",
    "CITY_ID": "59763252",
    "REMOTE_EQP_LABEL": "",
    "REMOTE_RESOURCE_STATUS": "",
    "REMOTE_PROJ_SUB_STATUS": "",
    "REMOTE_INT_ID": "",
    "PROJ_NAME": "",
    "PROJ_OA_FILE_CONTENT": "",
    "BUSINESS_REGION_IDS": "",
    "BUSINESS_REGIONS": "",
    "REMOTE_OBJECT_CLASS": "",
    "ALARM_REASON": "",
    "GCSS_CLIENT": "",
    "GCSS_CLIENT_NAME": "",
    "GCSS_CLIENT_NUM": "",
    "GCSS_CLIENT_LEVEL": "",
    "GCSS_SERVICE": "",
    "GCSS_SERVICE_NUM": "",
    "GCSS_SERVICE_LEVEL": "",
    "GCSS_SERVICE_TYPE": "",
    "BUSINESS_SYSTEM": "高兴新动力环境告警(旧)",
    "NE_IP": "",
    "LAYER_RATE": "",
    "CIRCUIT_ID": "006031,000,1.00",
    "ALARM_ABNORMAL_TYPE": "40",
    "PROJ_OA_FILE_ID": "",
    "GCSS_CLIENT_GRADE": "",
    "EFFECT_CIRCUIT_NUM": "",
    "PREHANDLE": "0",
    "OBJECT_CLASS_TEXT": "开关电源",
    "BOARD_TYPE": "",
    "OBJECT_CLASS": "30014",
    "LOGIC_ALARM_TYPE": "1112",
    "LOGIC_SUB_ALARM_TYPE": "0",
    "EFFECT_NE": "6",
    "EFFECT_SERVICE": "6",
    "SPECIAL_FIELD14": "",  # 填充ROOM_ID
    "SPECIAL_FIELD7": "",
    "SPECIAL_FIELD21": "609-006-00-006031",
    "ALARM_SOURCE": "高兴新动力环境告警(旧)",
    "BUSINESS_LAYER": "",
    "ALARM_TEXT": "<ALARMSTART>\nSystemName:高新兴动环系统\n...\n<ALARMEND>",
    "CIRCUIT_NO": "006031,000,1.00",
    "PRODUCT_TYPE": "",
    "CIRCUIT_LEVEL": "",
    "BUSINESS_TYPE": "",
    "IRMS_GRID_NAME": "",
    "ADMIN_GRID_ID": "",
    "HOME_CLIENT_NUM": "",
    "SRC_ID": "GZEVENT0000000828652147",
    "SRC_IS_TEST": 0,
    "SRC_APP_ID": "1001",
    "SRC_ORG_ID": "2480809218_1951576103_1632900523_2918980253_2",
    "ORG_TEXT": "...",
    "TOPIC_PREFIX": "EVENT-GZ",
    "TOPIC_PARTITION": 15,
    "SPECIAL_FIELD17": "【故障原因初判】由于停电告警导致\n【故障处理建议】请尽快上站发电，确保业务及时恢复。",
    "EXTRA_ID2": "",
    "EXTRA_STRING1": "",
    "PORT_NUM": "300103",
    "NE_ADMIN_STATUS": "",
    "SPECIAL_FIELD18": "",
    "SPECIAL_FIELD20": "",
    "TMSC_CAT": "",
    "ALARM_NE_STATUS": "",
    "ALARM_EQP_STATUS": "",
    "INTERFERENCE_FLAG": "0",
    "SPECIAL_FIELD2": "【是否干扰告警】：否。",
    "custGroupFeature": "",
    "industryCustType": "",
    "strategicCustTypeFL": "",
    "strategicCustTypeSL": "",
    "FAULT_LOCATION": "基站_莆田市_全业务/汇聚节点_涵江区_中恒分立式ZHM15",
    "EVENT_SOURCE": 2,
    "ORIG_ALARM_CLEAR_FP": "",  # 动态生成
    "ORIG_ALARM_FP": "",  # 动态生成
    "EVENT_ARRIVAL_TIME": "",  # 动态生成
    "CREATION_EVENT_TIME": ""  # 动态生成
}

# 生成FP相关字段的唯一值（格式：数字_数字_数字_数字_数字）
def generate_unique_fp():
    ts = int(time.time() * 1000)  # 毫秒时间戳
    r1 = random.randint(1000000000, 9999999999)
    r2 = random.randint(1000000000, 9999999999)
    r3 = random.randint(1000000000, 9999999999)
    r4 = random.randint(10000, 99999)
    return f"{ts}_{r1}_{r2}_{r3}_{r4}"

# 统一时间处理函数
def get_formatted_time(offset_minutes=0):
    """获取格式化时间，支持偏移分钟数"""
    adjusted_time = datetime.now() - timedelta(minutes=offset_minutes)
    return adjusted_time.strftime("%Y-%m-%d %H:%M:%S")

# 获取当前时间减去指定分钟数的时间
def get_time_minus_minutes(minutes):
    return (datetime.now() - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")


@kafka_bp.route('/generate_kafka_msg', methods=['GET'])
def generate_kafka_page():
    return render_template('generate_kafka.html')

@kafka_bp.route('/generate_kafka_msg', methods=['POST'])
def generate_kafka_msg():
        # 处理 POST 请求
        try:
            # 获取前端输入参数
            room_id = request.form.get('room_id', '').strip()
            machine_room_info = request.form.get('machine_room_info', '').strip()

            # 校验必填字段
            if not room_id or not machine_room_info:
                logger.warning("缺少必填字段: room_id 或 machine_room_info")
                return jsonify({
                    'code': 400,
                    'msg': '缺少必填字段: room_id 或 machine_room_info',
                    'data': ''
                }), 400

            # 生成唯一FP值
            fp_value = generate_unique_fp()

            # 获取时间字段
            today_time = get_formatted_time()
            creation_time = get_formatted_time(offset_minutes=12)

            # 复制基础模板并替换动态字段
            kafka_msg = BASE_KAFKA_MSG.copy()
            kafka_msg.update({
                'SPECIAL_FIELD14': room_id,
                'MACHINE_ROOM_INFO': machine_room_info,
                'FP0_FP1_FP2_FP3': fp_value,
                'CFP0_CFP1_CFP2_CFP3': fp_value,
                'ORIG_ALARM_FP': fp_value,
                'ORIG_ALARM_CLEAR_FP': fp_value,
                'EVENT_TIME': today_time,
                'CREATION_EVENT_TIME': creation_time,
                'EVENT_ARRIVAL_TIME': today_time
            })

            # 格式化JSON（缩进4个空格，保证可读性）
            kafka_msg_str = json.dumps(kafka_msg, ensure_ascii=False, indent=4)
            logger.info("成功生成Kafka消息")

            return jsonify({
                'code': 200,
                'msg': '生成成功',
                'data': kafka_msg_str
            })
        except Exception as e:
            logger.error(f"生成Kafka消息失败: {str(e)}")
            return jsonify({
                'code': 500,
                'msg': f'生成失败：{str(e)}',
                'data': ''
            }), 500

