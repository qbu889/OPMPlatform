# routes/kafka_routes.py
import uuid
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


@kafka_bp.route('/es-to-kafka', methods=['GET'])
def es_to_kafka_page():
    return render_template('es_to_kafka.html')


def load_es_data(es_type):
    logger.info(f"正在加载 ES 数据类型: {es_type}")
    # 模拟从数据库或API加载数据,区分类别
    if es_type == 'wireless':
        data = {
            "NETWORK_TYPE_TOP": "1",
            "ORG_SEVERITY": "2",
            "REGION_NAME": "福州市",
            "ACTIVE_STATUS": "1",
            "CITY_NAME": "鼓楼区",
            "EQP_LABEL": "福州鼓楼-鼓楼卫前街小站-NLH-64",
            "EQP_OBJECT_CLASS": "8104",
            "VENDOR_NAME": "诺基亚",
            "VENDOR_ID": "4",
            "ALARM_RESOURCE_STATUS": "1",
            "LOCATE_INFO": "460-00-131131-64",
            "NE_LABEL": "福州鼓楼-鼓楼卫前街小站-NLH-64",
            "OBJECT_LEVEL": "0",
            "PROFESSIONAL_TYPE": "1",
            "NETWORK_TYPE": "103",
            "ORG_TYPE": "1",
            "VENDOR_TYPE": "1",
            "SEND_JT_FLAG": "0",
            "TITLE_TEXT": "CELL FAULTY",
            "STANDARD_ALARM_NAME": "小区退服",
            "STANDARD_ALARM_ID": "0103-002-006-10-005522",
            "STANDARD_FLAG": "2",
            "VENDOR_SEVERITY": "1",
            "PROBABLE_CAUSE": "7653",
            "NMS_ALARM_ID": "4155657",
            "PROBABLE_CAUSE_TXT": "",
            "PREPROCESS_MANNER": "",
            "INT_ID": "4957522731775506774",
            "REDEFINE_SEVERITY": "2",
            "TYPE_KEYCODE": "关联到资源,",
            "NE_LOCATION": "",
            "ALARM_EXPLANATION": "一、告警解释：属于告警中指示的扇区的一个或多个单元中发生了严重故障。从告警的补充文本字段中检查故障原因。二、可能原因：1、模块软件下载失败 2、到某模块的连接丢失 3、单元同步失败 4、软件版本不兼容 5、模块闭锁 6、小区闭锁 7、POST测试失败 8、不能识别的单元 9、当前基站软件版本不支持该模块 10、FSM和FSP间由于缺失RP1时钟而出现错误 11、操作系统致命错误 12、天线断连 13、基站文件错误 14、通讯故障 15、基站硬件中无效的频率通道 16、第x基带总线配置拒绝",
            "ALARM_EXPLANATION_ADDITION": "ENodeB",
            "MAINTAIN_GROUP": "漳州龙文主城网格超讯基站维护组1",
            "SITE_TYPE": "109",
            "SUB_ALARM_TYPE": "",
            "EVENT_CAT": "",
            "NMS_NAME": "",
            "CITY_ID": "-170137045",
            "REMOTE_EQP_LABEL": "",
            "REMOTE_RESOURCE_STATUS": "",
            "REMOTE_PROJ_SUB_STATUS": "",
            "REMOTE_INT_ID": "",
            "PROJ_NAME": "",
            "PROJ_OA_FILE_CONTENT": "",
            "BUSINESS_REGION_IDS": "",
            "BUSINESS_REGIONS": "",
            "REMOTE_OBJECT_CLASS": "",
            "ALARM_REASON": "2",
            "GCSS_CLIENT": "",
            "GCSS_CLIENT_NAME": "",
            "GCSS_CLIENT_NUM": "",
            "GCSS_CLIENT_LEVEL": "",
            "GCSS_SERVICE": "",
            "GCSS_SERVICE_NUM": "",
            "GCSS_SERVICE_LEVEL": "",
            "GCSS_SERVICE_TYPE": "",
            "BUSINESS_SYSTEM": "网络管理系统",
            "NE_IP": "",
            "LAYER_RATE": "",
            "CIRCUIT_ID": "",
            "ALARM_ABNORMAL_TYPE": "40",
            "PROJ_OA_FILE_ID": "",
            "GCSS_CLIENT_GRADE": "",
            "EFFECT_CIRCUIT_NUM": "",
            "PREHANDLE": "0",
            "OBJECT_CLASS_TEXT": "Eutrancell",
            "BOARD_TYPE": "",
            "OBJECT_CLASS": "8105",
            "LOGIC_ALARM_TYPE": "1",
            "LOGIC_SUB_ALARM_TYPE": "",
            "EFFECT_NE": "5",
            "EFFECT_SERVICE": "4",
            "SPECIAL_FIELD14": "ROOM-7e1eb5b43d2f49f994352404faeb720c",
            "SPECIAL_FIELD7": "460-00-131131-64",
            "SPECIAL_FIELD21": "",
            "ALARM_SOURCE": "网络管理系统",
            "BUSINESS_LAYER": "",
            "ALARM_TEXT": "{\"alarmSeq\":8246971,\"alarmTitle\":\"CELL FAULTY\",\"alarmStatus\":1,\"alarmType\":\"QUALITYOFSERVICE\",\"origSeverity\":1,\"eventTime\":\"2026-02-06 18:24:42\",\"alarmId\":\"4155657\",\"specificProblemID\":\"7653\",\"specificProblem\":\"CELL FAULTY\",\"neUID\":\"3502NSWXCENB00013FD99\",\"neName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS\",\"neType\":\"ENB\",\"objectUID\":\"3502NSWXCCEL0000045859400131\",\"objectName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131\",\"objectType\":\"EutranCellTdd\",\"locationInfo\":\"PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131\",\"addInfo\":\"DIAGNOSTIC_INFO:10 unitName=FZFF path=/SMOD_R-1/rfext3_10g/RMOD_R-2 serial_no=10QYX10DA003175 additionalFaultID=3030;SUPPLEMENTARY_INFO:Failure in optical interface;USER_ADDITIONAL_INFO:;DN:PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131;deployment:LTE\",\"rNeUID\":\"3502NSWXCRRU0001740A4\",\"rNeName\":\"RMOD_R-2\",\"rNeType\":\"RRU-LTE\"}",
            "CIRCUIT_NO": "",
            "PRODUCT_TYPE": "",
            "CIRCUIT_LEVEL": "",
            "BUSINESS_TYPE": "",
            "IRMS_GRID_NAME": "",
            "ADMIN_GRID_ID": "",
            "HOME_CLIENT_NUM": "10",
            "SRC_ID": "GZEVENT0000000941556455",
            "SRC_IS_TEST": 0,
            "SRC_APP_ID": "1001",
            "SRC_ORG_ID": "3763383435_3204552333_262808553_1003444587_2026020604",
            "ORG_TEXT": "1_;2_;漳州市_;1_;龙文区_;福州鼓楼-鼓楼卫前街小站-NLH-64_;8104_;诺基亚_;4_;1_;460-00-131131-64_;福州鼓楼-鼓楼卫前街小站-NLH-64_;0_;1_;103_;1_;1_;0_;CELL FAULTY_;小区退服_;0103-002-006-10-005522_;2_;1_;7653_;4155657_;_;_;2026-02-06 18:24:42_;1770373485_;_;3763383435_3204552333_262808553_1003444587_;1616177685_4092288156_2879390775_3521197227_;漳州龙文国贸润园32幢一楼D03店面机房_;4957522731775506774_;2_;关联到资源,_;_;一、告警解释：属于告警中指示的扇区的一个或多个单元中发生了严重故障。从告警的补充文本字段中检查故障原因。二、可能原因：1、模块软件下载失败 2、到某模块的连接丢失 3、单元同步失败 4、软件版本不兼容 5、模块闭锁 6、小区闭锁 7、POST测试失败 8、不能识别的单元 9、当前基站软件版本不支持该模块 10、FSM和FSP间由于缺失RP1时钟而出现错误 11、操作系统致命错误 12、天线断连 13、基站文件错误 14、通讯故障 15、基站硬件中无效的频率通道 16、第x基带总线配置拒绝_;ENodeB_;漳州龙文主城网格超讯基站维护组1_;109_;_;_;_;-170137045_;_;_;_;_;_;_;_;_;_;_;2_;_;_;_;_;_;_;_;_;网络管理系统_;_;_;_;40_;_;_;_;0_;Eutrancell_;_;_;_;8105_;1_;_;5_;4_;ROOM-7e1eb5b43d2f49f994352404faeb720c_;460-00-131131-64_;_;网络管理系统_;_;0_;{\"alarmSeq\":8246971,\"alarmTitle\":\"CELL FAULTY\",\"alarmStatus\":1,\"alarmType\":\"QUALITYOFSERVICE\",\"origSeverity\":1,\"eventTime\":\"2026-02-06 18:24:42\",\"alarmId\":\"4155657\",\"specificProblemID\":\"7653\",\"specificProblem\":\"CELL FAULTY\",\"neUID\":\"3502NSWXCENB00013FD99\",\"neName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS\",\"neType\":\"ENB\",\"objectUID\":\"3502NSWXCCEL0000045859400131\",\"objectName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131\",\"objectType\":\"EutranCellTdd\",\"locationInfo\":\"PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131\",\"addInfo\":\"DIAGNOSTIC_INFO:10 unitName=FZFF path=/SMOD_R-1/rfext3_10g/RMOD_R-2 serial_no=10QYX10DA003175 additionalFaultID=3030;SUPPLEMENTARY_INFO:Failure in optical interface;USER_ADDITIONAL_INFO:;DN:PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131;deployment:LTE\",\"rNeUID\":\"3502NSWXCRRU0001740A4\",\"rNeName\":\"RMOD_R-2\",\"rNeType\":\"RRU-LTE\"}_;【故障原因初判】无线设备问题.\t【故障处理建议】请排查无线设备故障。_;_;_;_;_;_;_;10_;34_;_;4313_;16_;_;_;-1_;_;_;0_;【是否干扰告警】：否。_;_;_;_;_;PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131_;ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131_;\n",
            "TOPIC_PREFIX": "EVENT-GZ",
            "TOPIC_PARTITION": 44,
            "SPECIAL_FIELD17": "【故障原因初判】无线设备问题.\t【故障处理建议】请排查无线设备故障。",
            "EXTRA_ID2": "34",
            "EXTRA_STRING1": "",
            "PORT_NUM": "4313",
            "NE_ADMIN_STATUS": "16",
            "SPECIAL_FIELD18": "",
            "SPECIAL_FIELD20": "",
            "TMSC_CAT": "-1",
            "ALARM_NE_STATUS": "",
            "ALARM_EQP_STATUS": "",
            "INTERFERENCE_FLAG": "0",
            "SPECIAL_FIELD2": "【是否干扰告警】：否。",
            "custGroupFeature": "",
            "industryCustType": "",
            "strategicCustTypeFL": "",
            "strategicCustTypeSL": "",
            "FAULT_LOCATION": "PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131",
            "EVENT_SOURCE": 2,
            "ORIG_ALARM_CLEAR_FP": "3763383435_3204552333_262808553_1003444587_2026020604",
            "ORIG_ALARM_FP": "3763383435_3204552333_262808553_1003444587_2026020604",
            "EVENT_ARRIVAL_TIME": "2026-02-06 18:24:47",
            "CREATION_EVENT_TIME": "2026-02-06 18:48:13"
        }
    elif es_type == 'enterprise':
        data = {
            "ID": "ee0255e6-769c-476f-9e7d-68c6f006419b",
            "NETWORK_TYPE_TOP": "11",
            "ORG_SEVERITY": "2",
            "REGION_NAME": "漳州市",
            "ACTIVE_STATUS": "1",
            "CITY_NAME": "漳浦县",
            "EQP_LABEL": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
            "EQP_OBJECT_CLASS": "87002",
            "VENDOR_NAME": "瑞斯康达",
            "VENDOR_ID": "323",
            "ALARM_RESOURCE_STATUS": "1",
            "LOCATE_INFO": "MSP",
            "NE_LABEL": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
            "OBJECT_LEVEL": "",
            "PROFESSIONAL_TYPE": "6",
            "NETWORK_TYPE": "1100",
            "ORG_TYPE": "14104",
            "VENDOR_TYPE": "14202",
            "SEND_JT_FLAG": "",
            "TITLE_TEXT": "设备脱网(影响1条电路)",
            "STANDARD_ALARM_NAME": "设备脱网",
            "STANDARD_ALARM_ID": "1100-064-371-10-860022",
            "STANDARD_FLAG": "2",
            "VENDOR_SEVERITY": "1",
            "PROBABLE_CAUSE": "",
            "NMS_ALARM_ID": "2020740405373157376",
            "PROBABLE_CAUSE_TXT": "",
            "PREPROCESS_MANNER": "",
            "EVENT_TIME": "2026-02-09 14:03:50",
            "TIME_STAMP": "1770617097",
            "FP0_FP1_FP2_FP3": "1713996274_3872318956_2520283298_4136070826_2",
            "CFP0_CFP1_CFP2_CFP3": "1713996274_3872318956_2520283298_4136070826_2",
            "MACHINE_ROOM_INFO": "",
            "INT_ID": "0",
            "REDEFINE_SEVERITY": "2",
            "TYPE_KEYCODE": "预处理,",
            "NE_LOCATION": "62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
            "ALARM_EXPLANATION": "",
            "ALARM_EXPLANATION_ADDITION": "",
            "MAINTAIN_GROUP": "漳州漳浦集客铁通维护组",
            "SITE_TYPE": "",
            "SUB_ALARM_TYPE": "",
            "EVENT_CAT": "【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息",
            "NMS_NAME": "集客网管",
            "CITY_ID": "1740795524",
            "REMOTE_EQP_LABEL": "",
            "REMOTE_RESOURCE_STATUS": "",
            "REMOTE_PROJ_SUB_STATUS": "",
            "REMOTE_INT_ID": "",
            "PROJ_NAME": "",
            "PROJ_OA_FILE_CONTENT": "",
            "BUSINESS_REGION_IDS": "",
            "BUSINESS_REGIONS": "",
            "REMOTE_OBJECT_CLASS": "87002",
            "ALARM_REASON": "",
            "GCSS_CLIENT": "5916596304",
            "GCSS_CLIENT_NAME": "漳州市消防救援支队(5916596304)",
            "GCSS_CLIENT_NUM": "",
            "GCSS_CLIENT_LEVEL": "1",
            "GCSS_SERVICE": "1",
            "GCSS_SERVICE_NUM": "1",
            "GCSS_SERVICE_LEVEL": "2",
            "GCSS_SERVICE_TYPE": "1406",
            "BUSINESS_SYSTEM": "集团专线",
            "NE_IP": "5901351420250509296606",
            "LAYER_RATE": "",
            "CIRCUIT_ID": "漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA",
            "ALARM_ABNORMAL_TYPE": "40",
            "PROJ_OA_FILE_ID": "",
            "GCSS_CLIENT_GRADE": "1404",
            "EFFECT_CIRCUIT_NUM": "1",
            "PREHANDLE": "1",
            "OBJECT_CLASS_TEXT": "SSAP",
            "BOARD_TYPE": "",
            "OBJECT_CLASS": "87002",
            "LOGIC_ALARM_TYPE": "36",
            "LOGIC_SUB_ALARM_TYPE": "137",
            "EFFECT_NE": "6",
            "EFFECT_SERVICE": "2",
            "SPECIAL_FIELD14": "",
            "SPECIAL_FIELD7": "614a77ab-42b9-44de-8c33-205e7debd2f0",
            "SPECIAL_FIELD21": "UUID:614a77ab-42b9-44de-8c33-205e7debd2f0",
            "ALARM_SOURCE": "直真专线监控系统",
            "BUSINESS_LAYER": "",
            "ALARM_TEXT": "【发生时间】2026-02-09 14:03:50;\n【告警对象】MSP;\n【告警内容】设备脱网(影响1条电路);\n 【业务影响情况】1条业务;\n(1).数据专线(5901351420250509296606),漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA\n【归属客户】漳州市消防救援支队(5916596304)(金牌,非直服直管);\n【A端】福建省漳州漳浦县古雷镇古雷港经济开发区新港城裕民路801号;\n【业务信息】数据专线,本地专线,A;\n;【告警分析】设备脱网;\n【预定位信息】【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息\n\n【客户侧信息查询】1、客户侧网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1\n2、告警情况：客户侧无相关告警\n【对端故障信息查询】对端无故障\n【集客动环信息查询】1、故障网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1\n2、查询资源：初步核实归属机房名称为漳州漳浦消防救援(杜浔AG专职站)一楼办公室机房，归属站点名称为3、查询告警：经核实查询最近6小时无相关停电故障，设备所在机房动环运行正常;\n",
            "CIRCUIT_NO": "漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA",
            "PRODUCT_TYPE": "数据专线",
            "CIRCUIT_LEVEL": "1403",
            "BUSINESS_TYPE": "",
            "IRMS_GRID_NAME": "",
            "ADMIN_GRID_ID": "",
            "HOME_CLIENT_NUM": "",
            "SRC_ID": "GZEVENT0000000920396189",
            "SRC_IS_TEST": 0,
            "SRC_APP_ID": "1001",
            "SRC_ORG_ID": "1713996274_3872318956_2520283298_4136070826_2",
            "ORG_TEXT": "11_;2_;漳州市_;1_;漳浦县_;[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1_;87002_;瑞斯康达_;323_;1_;MSP_;[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1_;_;6_;1100_;14104_;14202_;_;设备脱网(影响1条电路)_;设备脱网_;1100-064-371-10-860022_;2_;1_;_;2020740405373157376_;_;_;2026-02-09 14:03:50_;1770617097_;_;1713996274_3872318956_2520283298_4136070826_;1713996274_3872318956_2520283298_4136070826_;_;0_;2_;预处理,_;62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1_;_;_;漳州漳浦集客铁通维护组_;_;_;【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息_;集客网管_;1740795524_;_;_;_;_;_;_;_;_;87002_;_;_;5916596304_;漳州市消防救援支队(5916596304)_;_;1_;1_;1_;2_;1406_;集团专线_;5901351420250509296606_;_;漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA_;40_;_;1404_;1_;1_;SSAP_;_;_;_;87002_;36_;137_;6_;2_;_;614a77ab-42b9-44de-8c33-205e7debd2f0_;UUID:614a77ab-42b9-44de-8c33-205e7debd2f0_;直真专线监控系统_;_;20_;【发生时间】2026-02-09 14:03:50;\n【告警对象】MSP;\n【告警内容】设备脱网(影响1条电路);\n 【业务影响情况】1条业务;\n(1).数据专线(5901351420250509296606),漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA\n【归属客户】漳州市消防救援支队(5916596304)(金牌,非直服直管);\n【A端】福建省漳州漳浦县古雷镇古雷港经济开发区新港城裕民路801号;\n【业务信息】数据专线,本地专线,A;\n;【告警分析】设备脱网;\n【预定位信息】【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息\n\n【客户侧信息查询】1、客户侧网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1\n2、告警情况：客户侧无相关告警\n【对端故障信息查询】对端无故障\n【集客动环信息查询】1、故障网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1\n2、查询资源：初步核实归属机房名称为漳州漳浦消防救援(杜浔AG专职站)一楼办公室机房，归属站点名称为3、查询告警：经核实查询最近6小时无相关停电故障，设备所在机房动环运行正常;\n_;经核实无工程操作、无传输故障，无光功率异常，无动环停电，初步判断为对端故障导致，请进一步核实。_;漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA_;数据专线_;1403_;_;_;_;_;_;_;300205_;_;_;_;_;_;_;0_;【是否干扰告警】：否。_;_;10_;_;_;【告警对象】MSP;\u003cbr\u003e_;2028480021_;\n",
            "TOPIC_PREFIX": "EVENT-GZ",
            "TOPIC_PARTITION": 12,
            "SPECIAL_FIELD17": "经核实无工程操作、无传输故障，无光功率异常，无动环停电，初步判断为对端故障导致，请进一步核实。",
            "EXTRA_ID2": "",
            "EXTRA_STRING1": "",
            "PORT_NUM": "300205",
            "NE_ADMIN_STATUS": "",
            "SPECIAL_FIELD18": "",
            "SPECIAL_FIELD20": "",
            "TMSC_CAT": "",
            "ALARM_NE_STATUS": "",
            "ALARM_EQP_STATUS": "",
            "INTERFERENCE_FLAG": "0",
            "SPECIAL_FIELD2": "【是否干扰告警】：否。",
            "custGroupFeature": "",
            "industryCustType": "10",
            "strategicCustTypeFL": "",
            "strategicCustTypeSL": "",
            "FAULT_LOCATION": "【告警对象】MSP;\u003cbr\u003e",
            "SPECIAL_FIELD0": "2028480021",
            "EVENT_SOURCE": 2,
            "ORIG_ALARM_CLEAR_FP": "1713996274_3872318956_2520283298_4136070826",
            "ORIG_ALARM_FP": "1713996274_3872318956_2520283298_4136070826",
            "EVENT_ARRIVAL_TIME": "2026-02-09 14:04:59"
        }
    elif es_type == 'home_broadband':
        data = {
            "NETWORK_TYPE_TOP": "12",
            "ORG_SEVERITY": "2",
            "REGION_NAME": "厦门市",
            "ACTIVE_STATUS": "1",
            "CITY_NAME": "湖里区",
            "EQP_LABEL": "XIMHL艾德花园-OLT002-C600,1-1-2-8,FTTH",
            "EQP_OBJECT_CLASS": "2010",
            "VENDOR_NAME": "中兴",
            "VENDOR_ID": "7",
            "ALARM_RESOURCE_STATUS": "1",
            "LOCATE_INFO": "2b207f79-b292-4f2a-9e8b-3a258113b2f2,Rack=1,Shelf=1,Slot=2,Port=8",
            "NE_LABEL": "XIMHL艾德花园-OLT002-C600,1-1-2-8,FTTH",
            "OBJECT_LEVEL": "",
            "PROFESSIONAL_TYPE": "3",
            "NETWORK_TYPE": "1201",
            "ORG_TYPE": "1",
            "VENDOR_TYPE": "14202",
            "SEND_JT_FLAG": "",
            "TITLE_TEXT": "[GPON告警]PON信号丢失[集中监控]影响资源用户数:32(家宽:31,企宽:1);影响在线用户数:28;故障预定位:主纤断;影响HDICT设备数:0(门禁0,充电桩0,视频监控0,道闸0)",
            "STANDARD_ALARM_NAME": "[GPON告警]PON信号丢失",
            "STANDARD_ALARM_ID": "208-121-00-801553",
            "STANDARD_FLAG": "2",
            "VENDOR_SEVERITY": "1",
            "PROBABLE_CAUSE": "",
            "NMS_ALARM_ID": "112020673973801172992",
            "PROBABLE_CAUSE_TXT": "影响小区数:1个;影响资源用户数:32个(家宽:31,企宽:1);影响在线用户:28个;截止2026-02-09 09:53:04投诉用户:0个",
            "PREPROCESS_MANNER": "",
            "INT_ID": "0",
            "REDEFINE_SEVERITY": "2",
            "TYPE_KEYCODE": "",
            "NE_LOCATION": "XIMHL艾德花园-OLT002-C600:1-1-2-8",
            "ALARM_EXPLANATION": "告警ID:112020673973801172992;告警时间:2026-02-09 09:39:50;告警网元:XIMHL艾德花园-OLT002-C600,1-1-2-8,FTTH;告警内容:[GPON告警]PON信号丢失;业务影响情况:影响小区数:1个(厦门市湖里区三建工程公司宿舍);影响资源用户数:32个(家宽:31,企宽:1);影响在线用户:28个;截止2026-02-09 09:53:04投诉用户:0个;故障预定位:主纤断;告警备注:PON网络大面积故障",
            "ALARM_EXPLANATION_ADDITION": "",
            "MAINTAIN_GROUP": "厦门OLT维护组",
            "SITE_TYPE": "105",
            "SUB_ALARM_TYPE": "",
            "EVENT_CAT": "",
            "NMS_NAME": "",
            "CITY_ID": "-416993354",
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
            "BUSINESS_SYSTEM": "网络管理系统",
            "NE_IP": "",
            "LAYER_RATE": "",
            "CIRCUIT_ID": "",
            "ALARM_ABNORMAL_TYPE": "40",
            "PROJ_OA_FILE_ID": "",
            "GCSS_CLIENT_GRADE": "",
            "EFFECT_CIRCUIT_NUM": "",
            "PREHANDLE": "0",
            "OBJECT_CLASS_TEXT": "PON口",
            "BOARD_TYPE": "",
            "OBJECT_CLASS": "2010",
            "LOGIC_ALARM_TYPE": "35",
            "LOGIC_SUB_ALARM_TYPE": "131",
            "EFFECT_NE": "4",
            "EFFECT_SERVICE": "2",
            "SPECIAL_FIELD14": "DEVICEROOM-0592-02796",
            "SPECIAL_FIELD7": "影响家宽用户数:32,影响家宽在线用户数:27,影响企宽用户数:1,影响企宽在线用户数:1,影响千兆用户数:14,影响千兆在线用户数:14",
            "SPECIAL_FIELD21": "",
            "ALARM_SOURCE": "网络管理系统",
            "BUSINESS_LAYER": "",
            "ALARM_TEXT": "告警ID:112020673973801172992;告警时间:2026-02-09 09:39:50;告警网元:XIMHL艾德花园-OLT002-C600,1-1-2-8,FTTH;告警内容:[GPON告警]PON信号丢失;业务影响情况:影响小区数:1个(厦门市湖里区三建工程公司宿舍);影响资源用户数:32个(家宽:31,企宽:1);影响在线用户:28个;截止2026-02-09 09:53:04投诉用户:0个;故障预定位:主纤断;告警备注:PON网络大面积故障",
            "CIRCUIT_NO": "",
            "PRODUCT_TYPE": "",
            "CIRCUIT_LEVEL": "",
            "BUSINESS_TYPE": "14",
            "IRMS_GRID_NAME": "",
            "ADMIN_GRID_ID": "",
            "HOME_CLIENT_NUM": "32",
            "SRC_ID": "GZEVENT0000000920042107",
            "SRC_IS_TEST": 0,
            "SRC_APP_ID": "1001",
            "SRC_ORG_ID": "2897707082_868501202_1941967160_119599883_2",
            "TOPIC_PREFIX": "EVENT-GZ",
            "TOPIC_PARTITION": 36,
            "SPECIAL_FIELD17": "NULL",
            "EXTRA_ID2": "",
            "EXTRA_STRING1": "",
            "PORT_NUM": "400104",
            "NE_ADMIN_STATUS": "",
            "SPECIAL_FIELD18": "0",
            "SPECIAL_FIELD20": "",
            "TMSC_CAT": "3",
            "ALARM_NE_STATUS": "",
            "ALARM_EQP_STATUS": "",
            "INTERFERENCE_FLAG": "0",
            "SPECIAL_FIELD2": "【是否干扰告警】：否。",
            "custGroupFeature": "",
            "industryCustType": "",
            "strategicCustTypeFL": "",
            "strategicCustTypeSL": "",
            "FAULT_LOCATION": "[GPON告警]PON信号丢失[集中监控]影响资源用户数:32(家宽:31,企宽:1);影响在线用户数:28;故障预定位:主纤断;影响HDICT设备数:0(门禁0,充电桩0,视频监控0,道闸0)",
            "EVENT_SOURCE": 2,
            "ORIG_ALARM_CLEAR_FP": "1864783980_2719618169_3016100575_3691238256",
            "ORIG_ALARM_FP": "2897707082_868501202_1941967160_119599883",
            "EVENT_ARRIVAL_TIME": "2026-02-09 09:53:06"
        }
    elif es_type == 'power_equipment':
        data = {
            "NETWORK_TYPE_TOP": "5",
            "ORG_SEVERITY": "2",
            "REGION_NAME": "漳州市",
            "ACTIVE_STATUS": "1",
            "CITY_NAME": "长泰县",
            "EQP_LABEL": "漳州长泰坂里三楼301号机房-智能门禁-1",
            "EQP_OBJECT_CLASS": "30013",
            "VENDOR_NAME": "高新兴",
            "VENDOR_ID": "771",
            "ALARM_RESOURCE_STATUS": "1",
            "LOCATE_INFO": "基站_漳州市_OLT机房_长泰区_机房门锁",
            "NE_LABEL": "漳州长泰坂里三楼301号机房-智能门禁-1",
            "OBJECT_LEVEL": "",
            "PROFESSIONAL_TYPE": "4",
            "NETWORK_TYPE": "500",
            "ORG_TYPE": "1",
            "VENDOR_TYPE": "14202",
            "SEND_JT_FLAG": "0",
            "TITLE_TEXT": "动环现场巡检调度告警",
            "STANDARD_ALARM_NAME": "动环现场巡检调度告警",
            "STANDARD_ALARM_ID": "0500-009-000-00-800001",
            "STANDARD_FLAG": "2",
            "VENDOR_SEVERITY": "二级告警",
            "PROBABLE_CAUSE": "800001",
            "NMS_ALARM_ID": "263909449",
            "PROBABLE_CAUSE_TXT": "0",
            "PREPROCESS_MANNER": "",
            "INT_ID": "3501077693931926912",
            "REDEFINE_SEVERITY": "2",
            "TYPE_KEYCODE": "关联到资源,",
            "NE_LOCATION": "无线设备：漳州长泰-坂里坂沙公路-HLH-BBU01、CBN-漳州长泰-坂里C-HRHH-BBU01、漳州长泰-坂里B-HRHH-BBU01...等，传输设备：61-928_坂里2、913-坂里、9124-漳州长泰坂里-ZX-PTN...等，家宽设备：ZHZCTAI坂里-OLT002-C300",
            "ALARM_EXPLANATION": "省内自定义管控告警",
            "ALARM_EXPLANATION_ADDITION": "传输节点",
            "MAINTAIN_GROUP": "漳州长泰农村网格超讯基站维护组2",
            "SITE_TYPE": "109",
            "SUB_ALARM_TYPE": "",
            "EVENT_CAT": "",
            "NMS_NAME": "高新兴动环系统",
            "CITY_ID": "273496711",
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
            "CIRCUIT_ID": "3,0,1",
            "ALARM_ABNORMAL_TYPE": "40",
            "PROJ_OA_FILE_ID": "",
            "GCSS_CLIENT_GRADE": "",
            "EFFECT_CIRCUIT_NUM": "",
            "PREHANDLE": "0",
            "OBJECT_CLASS_TEXT": "动环监控",
            "BOARD_TYPE": "",
            "OBJECT_CLASS": "30013",
            "LOGIC_ALARM_TYPE": "44",
            "LOGIC_SUB_ALARM_TYPE": "0",
            "EFFECT_NE": "6",
            "EFFECT_SERVICE": "6",
            "SPECIAL_FIELD14": "MONITOR-244293",
            "SPECIAL_FIELD7": "",
            "SPECIAL_FIELD21": "609-000-00-000001",
            "ALARM_SOURCE": "高兴新动力环境告警(旧)",
            "BUSINESS_LAYER": "",
            "ALARM_TEXT": "<ALARMSTART>\nSystemName:高新兴动环系统\nVendor_Name:机房门锁\nSpeciality:动环专业\nAlarmID:263909449\nIntID:47cddf9c-ac9c-4f1e-9f78-81975c741352\nAlarmEquipment:基站_漳州市_OLT机房_长泰区_机房门锁\nEquipmentClass:\nEventTime:2026-02-09 09:42:05\nVendor_Severity:一级告警\nAlarmTitle:触发值：1，告警区间为：1\nActiveStatus:1\nProbableCause:\nProbableCauseTxt:漳州长泰坂里三楼301号机房\\机房门锁\\触发值：1，告警区间为：1\nMaintainPropose:3,,1\nLocateInfo:基站_漳州市_OLT机房_长泰区_机房门锁\nClearID:263909449\nLocateName:基站>漳州市>OLT机房>长泰区\nVersion:\nAckUser:\nAckTerminal:\nDispatchFlag:0\nstandard_alarm_id:\nIRMS_CUID:MONITOR-244293\n</ALARMEND>",
            "CIRCUIT_NO": "3,0,1",
            "PRODUCT_TYPE": "",
            "CIRCUIT_LEVEL": "",
            "BUSINESS_TYPE": "",
            "IRMS_GRID_NAME": "",
            "ADMIN_GRID_ID": "",
            "HOME_CLIENT_NUM": "",
            "SRC_ID": "GZEVENT0000000920027138",
            "SRC_IS_TEST": 0,
            "SRC_APP_ID": "1001",
            "SRC_ORG_ID": "65747035_3570852678_1471027157_1318897267_2",
            "TOPIC_PREFIX": "EVENT-GZ",
            "TOPIC_PARTITION": 20,
            "SPECIAL_FIELD17": "【故障原因初判】动环设备问题.\t【故障处理建议】请排查动环设备故障。",
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
            "FAULT_LOCATION": "基站_漳州市_OLT机房_长泰区_机房门锁",
            "EVENT_SOURCE": 2,
            "ORIG_ALARM_CLEAR_FP": "3490818867_2208030639_614650942_1227973128",
            "ORIG_ALARM_FP": "65747035_3570852678_1471027157_1318897267",
            "EVENT_ARRIVAL_TIME": "2026-02-09 09:42:40"
        }
    else:
        logger.error(f"未知的ES数据类型: {es_type}")
        raise ValueError(f"未知的ES数据类型: {es_type}")

    logger.debug(f"加载的 ES 数据: {data}")
    return data


# 生成Kafka消息
@kafka_bp.route('/es-to-kafka', methods=['POST'])
def es_to_kafka_msg():
    try:
        # 获取前端输入参数
        room_id = request.form.get('room_id', '').strip()
        machine_room_info = request.form.get('machine_room_info', '').strip()
        es_type = request.form.get('es_type', '').strip()

        logger.info(f"接收到请求参数: room_id={room_id}, machine_room_info={machine_room_info}, es_type={es_type}")

        # 校验必填字段
        if not room_id or not machine_room_info or not es_type:
            logger.warning("缺少必填字段: room_id, machine_room_info 或 es_type")
            return jsonify({
                'code': 400,
                'msg': '缺少必填字段: room_id, machine_room_info 或 es_type',
                'data': ''
            }), 400

        # 动态加载ES数据
        es_data = load_es_data(es_type)
        logger.debug(f"加载的 ES 数据: {es_data}")

        # 生成Kafka消息
        kafka_msg = generate_kafka_from_es(es_data, room_id, machine_room_info)
        logger.debug(f"生成的 Kafka 消息: {kafka_msg}")

        # 预处理数据确保JSON序列化安全
        kafka_msg = preprocess_for_json(kafka_msg)
        
        # 格式化JSON（缩进4个空格，保证可读性）
        kafka_msg_str = json.dumps(kafka_msg, ensure_ascii=False, indent=4)
        logger.info("成功生成Kafka消息")

        return jsonify({
            'code': 200,
            'msg': '生成成功',
            'data': kafka_msg_str
        })
    except Exception as e:
        logger.error(f"生成Kafka消息失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'msg': f'生成失败：{str(e)}',
            'data': ''
        }), 500


@kafka_bp.route('/generate_kafka_msg', methods=['GET'])
def generate_kafka_page():
    return render_template('generate_kafka.html')


def preprocess_for_json(data):
    """
    预处理数据以确保可以正确序列化为JSON
    :param data: 要处理的数据
    :return: 处理后的数据
    """
    if isinstance(data, dict):
        return {key: preprocess_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [preprocess_for_json(item) for item in data]
    elif isinstance(data, (int, float, bool)):
        return data
    elif data is None:
        return ""
    else:
        # 将所有其他类型转换为字符串
        str_value = str(data)
        # 处理特殊字符
        str_value = str_value.replace('\u003c', '<').replace('\u003e', '>')
        return str_value


def generate_kafka_from_es(es_data, room_id, machine_room_info):
    """
    根据ES数据生成Kafka消息
    :param es_data: ES数据字典
    :param room_id: ROOM_ID
    :param machine_room_info: MACHINE_ROOM_INFO
    :return: 生成的Kafka消息
    """
    logger.info(f"开始生成 Kafka 消息: room_id={room_id}, machine_room_info={machine_room_info}")

    # 生成唯一FP值
    fp_value = generate_unique_fp()
    logger.debug(f"生成的 FP 值: {fp_value}")

    # 获取时间字段（当前时间减15分钟）
    event_time = get_time_minus_minutes(15)
    creation_time = get_time_minus_minutes(15)
    arrival_time = get_time_minus_minutes(15)
    logger.debug(f"生成的时间字段: event_time={event_time}, creation_time={creation_time}, arrival_time={arrival_time}")

    # 构造Kafka消息基础字段
    kafka_msg = {
        "ID": str(uuid.uuid4()),
        "SPECIAL_FIELD14": room_id,
        "MACHINE_ROOM_INFO": machine_room_info,
        "FP0_FP1_FP2_FP3": fp_value,
        "CFP0_CFP1_CFP2_CFP3": fp_value,
        "ORIG_ALARM_CLEAR_FP": fp_value,
        "ORIG_ALARM_FP": fp_value,
        "EVENT_TIME": event_time,
        "EVENT_ARRIVAL_TIME": arrival_time,
        "CREATION_EVENT_TIME": creation_time
    }
    # 打印 SPECIAL_FIELD14 的值
    logger.info(f"SPECIAL_FIELD14 的值为: {room_id}")
    # 动态合并 es_data 字段，并跳过 SPECIAL_FIELD14 和 MACHINE_ROOM_INFO
    for key, value in es_data.items():
        if key not in ["SPECIAL_FIELD14", "MACHINE_ROOM_INFO"]:  # 排除这两个字段
            kafka_msg[key] = value if value is not None else ""
    
    # 对整个消息进行预处理，确保JSON序列化安全
    kafka_msg = preprocess_for_json(kafka_msg)

    logger.debug(f"生成的 Kafka 消息: {kafka_msg}")
    logger.info("Kafka 消息构造完成")
    return kafka_msg


@kafka_bp.route('/generate_kafka_msg', methods=['POST'])
def generate_kafka_msg():
    try:
        # 获取前端输入参数
        room_id = request.form.get('room_id', '').strip()
        machine_room_info = request.form.get('machine_room_info', '').strip()

        logger.info(f"接收到请求参数: room_id={room_id}, machine_room_info={machine_room_info}")

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
        logger.debug(f"生成的 FP 值: {fp_value}")

        # 获取时间字段
        today_time = get_formatted_time()
        creation_time = get_formatted_time(offset_minutes=12)
        logger.debug(f"生成的时间字段: today_time={today_time}, creation_time={creation_time}")

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
        # 打印 SPECIAL_FIELD14 的值
        logger.info(f"SPECIAL_FIELD14 的值为: {room_id}")
        logger.debug(f"生成的 Kafka 消息: {kafka_msg}")

        # 格式化JSON（缩进4个空格，保证可读性）
        kafka_msg_str = json.dumps(kafka_msg, ensure_ascii=False, indent=4)
        logger.info("成功生成Kafka消息")

        return jsonify({
            'code': 200,
            'msg': '生成成功',
            'data': kafka_msg_str
        })
    except Exception as e:
        logger.error(f"生成Kafka消息失败: {str(e)}", exc_info=True)
        return jsonify({
            'code': 500,
            'msg': f'生成失败：{str(e)}',
            'data': ''
        }), 500


if __name__ == '__main__':
    # 示例测试数据
    es_data = {
        "NETWORK_TYPE_TOP": "1",
        "ORG_SEVERITY": "2",
        "REGION_NAME": "福州市",
        "ACTIVE_STATUS": "1",
        "CITY_NAME": "鼓楼区",
        "EQP_LABEL": "福州鼓楼-鼓楼卫前街小站-NLH-64",
        "EQP_OBJECT_CLASS": "8104",
        "VENDOR_NAME": "诺基亚",
        "VENDOR_ID": "4",
        "ALARM_RESOURCE_STATUS": "1",
        "LOCATE_INFO": "460-00-131131-64",
        "NE_LABEL": "福州鼓楼-鼓楼卫前街小站-NLH-64",
        "OBJECT_LEVEL": "0",
        "PROFESSIONAL_TYPE": "1",
        "NETWORK_TYPE": "103",
        "ORG_TYPE": "1",
        "VENDOR_TYPE": "1",
        "SEND_JT_FLAG": "0",
        "TITLE_TEXT": "CELL FAULTY",
        "STANDARD_ALARM_NAME": "小区退服",
        "STANDARD_ALARM_ID": "0103-002-006-10-005522",
        "STANDARD_FLAG": "2",
        "VENDOR_SEVERITY": "1",
        "PROBABLE_CAUSE": "7653",
        "NMS_ALARM_ID": "4155657",
        "PROBABLE_CAUSE_TXT": "",
        "PREPROCESS_MANNER": "",
        "INT_ID": "4957522731775506774",
        "REDEFINE_SEVERITY": "2",
        "TYPE_KEYCODE": "关联到资源,",
        "NE_LOCATION": "",
        "ALARM_EXPLANATION": "一、告警解释：属于告警中指示的扇区的一个或多个单元中发生了严重故障。从告警的补充文本字段中检查故障原因。二、可能原因：1、模块软件下载失败 2、到某模块的连接丢失 3、单元同步失败 4、软件版本不兼容 5、模块闭锁 6、小区闭锁 7、POST测试失败 8、不能识别的单元 9、当前基站软件版本不支持该模块 10、FSM和FSP间由于缺失RP1时钟而出现错误 11、操作系统致命错误 12、天线断连 13、基站文件错误 14、通讯故障 15、基站硬件中无效的频率通道 16、第x基带总线配置拒绝",
        "ALARM_EXPLANATION_ADDITION": "ENodeB",
        "MAINTAIN_GROUP": "漳州龙文主城网格超讯基站维护组1",
        "SITE_TYPE": "109",
        "SUB_ALARM_TYPE": "",
        "EVENT_CAT": "",
        "NMS_NAME": "",
        "CITY_ID": "-170137045",
        "REMOTE_EQP_LABEL": "",
        "REMOTE_RESOURCE_STATUS": "",
        "REMOTE_PROJ_SUB_STATUS": "",
        "REMOTE_INT_ID": "",
        "PROJ_NAME": "",
        "PROJ_OA_FILE_CONTENT": "",
        "BUSINESS_REGION_IDS": "",
        "BUSINESS_REGIONS": "",
        "REMOTE_OBJECT_CLASS": "",
        "ALARM_REASON": "2",
        "GCSS_CLIENT": "",
        "GCSS_CLIENT_NAME": "",
        "GCSS_CLIENT_NUM": "",
        "GCSS_CLIENT_LEVEL": "",
        "GCSS_SERVICE": "",
        "GCSS_SERVICE_NUM": "",
        "GCSS_SERVICE_LEVEL": "",
        "GCSS_SERVICE_TYPE": "",
        "BUSINESS_SYSTEM": "网络管理系统",
        "NE_IP": "",
        "LAYER_RATE": "",
        "CIRCUIT_ID": "",
        "ALARM_ABNORMAL_TYPE": "40",
        "PROJ_OA_FILE_ID": "",
        "GCSS_CLIENT_GRADE": "",
        "EFFECT_CIRCUIT_NUM": "",
        "PREHANDLE": "0",
        "OBJECT_CLASS_TEXT": "Eutrancell",
        "BOARD_TYPE": "",
        "OBJECT_CLASS": "8105",
        "LOGIC_ALARM_TYPE": "1",
        "LOGIC_SUB_ALARM_TYPE": "",
        "EFFECT_NE": "5",
        "EFFECT_SERVICE": "4",
        "SPECIAL_FIELD14": "ROOM-7e1eb5b43d2f49f994352404faeb720c",
        "SPECIAL_FIELD7": "460-00-131131-64",
        "SPECIAL_FIELD21": "",
        "ALARM_SOURCE": "网络管理系统",
        "BUSINESS_LAYER": "",
        "ALARM_TEXT": "{\"alarmSeq\":8246971,\"alarmTitle\":\"CELL FAULTY\",\"alarmStatus\":1,\"alarmType\":\"QUALITYOFSERVICE\",\"origSeverity\":1,\"eventTime\":\"2026-02-06 18:24:42\",\"alarmId\":\"4155657\",\"specificProblemID\":\"7653\",\"specificProblem\":\"CELL FAULTY\",\"neUID\":\"3502NSWXCENB00013FD99\",\"neName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS\",\"neType\":\"ENB\",\"objectUID\":\"3502NSWXCCEL0000045859400131\",\"objectName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131\",\"objectType\":\"EutranCellTdd\",\"locationInfo\":\"PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131\",\"addInfo\":\"DIAGNOSTIC_INFO:10 unitName=FZFF path=/SMOD_R-1/rfext3_10g/RMOD_R-2 serial_no=10QYX10DA003175 additionalFaultID=3030;SUPPLEMENTARY_INFO:Failure in optical interface;USER_ADDITIONAL_INFO:;DN:PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131;deployment:LTE\",\"rNeUID\":\"3502NSWXCRRU0001740A4\",\"rNeName\":\"RMOD_R-2\",\"rNeType\":\"RRU-LTE\"}",
        "CIRCUIT_NO": "",
        "PRODUCT_TYPE": "",
        "CIRCUIT_LEVEL": "",
        "BUSINESS_TYPE": "",
        "IRMS_GRID_NAME": "",
        "ADMIN_GRID_ID": "",
        "HOME_CLIENT_NUM": "10",
        "SRC_ID": "GZEVENT0000000941556455",
        "SRC_IS_TEST": 0,
        "SRC_APP_ID": "1001",
        "SRC_ORG_ID": "3763383435_3204552333_262808553_1003444587_2026020604",
        "ORG_TEXT": "1_;2_;漳州市_;1_;龙文区_;福州鼓楼-鼓楼卫前街小站-NLH-64_;8104_;诺基亚_;4_;1_;460-00-131131-64_;福州鼓楼-鼓楼卫前街小站-NLH-64_;0_;1_;103_;1_;1_;0_;CELL FAULTY_;小区退服_;0103-002-006-10-005522_;2_;1_;7653_;4155657_;_;_;2026-02-06 18:24:42_;1770373485_;_;3763383435_3204552333_262808553_1003444587_;1616177685_4092288156_2879390775_3521197227_;漳州龙文国贸润园32幢一楼D03店面机房_;4957522731775506774_;2_;关联到资源,_;_;一、告警解释：属于告警中指示的扇区的一个或多个单元中发生了严重故障。从告警的补充文本字段中检查故障原因。二、可能原因：1、模块软件下载失败 2、到某模块的连接丢失 3、单元同步失败 4、软件版本不兼容 5、模块闭锁 6、小区闭锁 7、POST测试失败 8、不能识别的单元 9、当前基站软件版本不支持该模块 10、FSM和FSP间由于缺失RP1时钟而出现错误 11、操作系统致命错误 12、天线断连 13、基站文件错误 14、通讯故障 15、基站硬件中无效的频率通道 16、第x基带总线配置拒绝_;ENodeB_;漳州龙文主城网格超讯基站维护组1_;109_;_;_;_;-170137045_;_;_;_;_;_;_;_;_;_;_;2_;_;_;_;_;_;_;_;_;网络管理系统_;_;_;_;40_;_;_;_;0_;Eutrancell_;_;_;_;8105_;1_;_;5_;4_;ROOM-7e1eb5b43d2f49f994352404faeb720c_;460-00-131131-64_;_;网络管理系统_;_;0_;{\"alarmSeq\":8246971,\"alarmTitle\":\"CELL FAULTY\",\"alarmStatus\":1,\"alarmType\":\"QUALITYOFSERVICE\",\"origSeverity\":1,\"eventTime\":\"2026-02-06 18:24:42\",\"alarmId\":\"4155657\",\"specificProblemID\":\"7653\",\"specificProblem\":\"CELL FAULTY\",\"neUID\":\"3502NSWXCENB00013FD99\",\"neName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS\",\"neType\":\"ENB\",\"objectUID\":\"3502NSWXCCEL0000045859400131\",\"objectName\":\"ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131\",\"objectType\":\"EutranCellTdd\",\"locationInfo\":\"PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131\",\"addInfo\":\"DIAGNOSTIC_INFO:10 unitName=FZFF path=/SMOD_R-1/rfext3_10g/RMOD_R-2 serial_no=10QYX10DA003175 additionalFaultID=3030;SUPPLEMENTARY_INFO:Failure in optical interface;USER_ADDITIONAL_INFO:;DN:PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131;deployment:LTE\",\"rNeUID\":\"3502NSWXCRRU0001740A4\",\"rNeName\":\"RMOD_R-2\",\"rNeType\":\"RRU-LTE\"}_;【故障原因初判】无线设备问题.\t【故障处理建议】请排查无线设备故障。_;_;_;_;_;_;_;10_;34_;_;4313_;16_;_;_;-1_;_;_;0_;【是否干扰告警】：否。_;_;_;_;_;PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131_;ZhangZhouLongWen-ShiJiJiaYuanErQiShiFenLouJianDuiDa2-NLS-131_;\n",
        "TOPIC_PREFIX": "EVENT-GZ",
        "TOPIC_PARTITION": 44,
        "SPECIAL_FIELD17": "【故障原因初判】无线设备问题.\t【故障处理建议】请排查无线设备故障。",
        "EXTRA_ID2": "34",
        "EXTRA_STRING1": "",
        "PORT_NUM": "4313",
        "NE_ADMIN_STATUS": "16",
        "SPECIAL_FIELD18": "",
        "SPECIAL_FIELD20": "",
        "TMSC_CAT": "-1",
        "ALARM_NE_STATUS": "",
        "ALARM_EQP_STATUS": "",
        "INTERFERENCE_FLAG": "0",
        "SPECIAL_FIELD2": "【是否干扰告警】：否。",
        "custGroupFeature": "",
        "industryCustType": "",
        "strategicCustTypeFL": "",
        "strategicCustTypeSL": "",
        "FAULT_LOCATION": "PLMN-PLMN/MRBTS-458594/LNBTS-458594/LNCEL-131",
        "EVENT_SOURCE": 2,
        "ORIG_ALARM_CLEAR_FP": "3763383435_3204552333_262808553_1003444587_2026020604",
        "ORIG_ALARM_FP": "3763383435_3204552333_262808553_1003444587_2026020604",
        "EVENT_ARRIVAL_TIME": "2026-02-06 18:24:47",
        "CREATION_EVENT_TIME": "2026-02-06 18:48:13"
    }

    room_id = "TEST-ROOM-ID"
    machine_room_info = "测试机房信息"

    # 调用函数生成 Kafka 消息
    kafka_msg = generate_kafka_from_es(es_data, room_id, machine_room_info)

    # 打印生成的 Kafka 消息
    print(json.dumps(kafka_msg, ensure_ascii=False, indent=4))
