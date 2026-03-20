#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka消息生成器测试脚本
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json

def test_kafka_generation():
    """测试Kafka消息生成功能"""
    # 测试用的ES数据
    test_es_data = {
        "_source" : {
          "HOME_BROAD_BAND_LIST" : [ ],
          "FULL_REGION_ID" : "35000/350600/350623",
          "EVENT_LEVEL" : 4,
          "ORG_TYPE" : 14104,
          "EVENT_LOCATION" : "MSP",
          "INDUSTRY_CUST_TYPE" : "10",
          "TOPIC_PREFIX" : "EVENT-GZ",
          "REMOTE_OBJECT_NAME" : "SSAP",
          "DISPATCH_INFO" : {
            "T1_PROCESSING_TIME" : 20,
            "T1_CONFIRMATION_TIME" : 30,
            "START_TIME" : "00:00:00",
            "IS_CALCULATE_DURATION" : 0,
            "RULE_NAME" : "生产规则-集客专业-二级告警派单-处理单",
            "CONFIRMATION_TIME" : 30,
            "DISPATCH_TYPE" : 0,
            "INST_ID" : 281381,
            "DISPATCH_LEVEL" : 4,
            "PROCESS_STATE" : 9,
            "END_TIME" : "23:59:59",
            "T2_CONFIRMATION_TIME" : 30,
            "PROCESS_TYPE" : 1,
            "DISPATCH_NIGHT" : "0",
            "ORDER_STATUS" : 1,
            "DISPATCH_FLAG" : 0,
            "DISPATCH_REASON" : "工单派发成功",
            "TIME_RULE_NAME" : "集客-工单时限规则-四级",
            "DISPATCH_STATUS_ID" : "1010",
            "APPEND_DELAY_TIME" : 30,
            "RULE_ID" : 1230,
            "DISPATCH_LEVEL_RULE_NAME" : "集客-工单派单级别-四级",
            "T2_PROCESSING_TIME" : 300,
            "DISPATCH_LEVEL_RULE_ID" : 9,
            "DELAY_TIME" : 12,
            "PROCESSING_TIME" : 300,
            "SUPPRESS_TYPE" : 0,
            "JT_DISPATCH_STATUS_ID" : 5,
            "JT_DISPATCH_STATUS_DESC" : "自动派单成功",
            "TIME_RULE_ID" : 47,
            "ORDER_ID" : "FJ-076-20260209-3320",
            "ORDER_TYPE" : 1,
            "ORDER_TIME" : "2026-02-09 14:17:11",
            "AUTO_RECEIPT_REASON" : "未匹配到自动回单规则",
            "AUTO_RECEIPT_STATE" : 0
          },
          "WARNING_INFO" : {
            "PROCESS_STATE" : 9,
            "DISPATCH_STATUS_ID" : "1001",
            "IS_CALCULATE_DURATION" : 0,
            "WARNING_REASON" : "未匹配规则",
            "PROCESS_TYPE" : 1,
            "ORDER_STATUS" : 0,
            "DISPATCH_FLAG" : 1
          },
          "RECOGNITION_RULE_NAME" : "集客-单条集客专线故障事件",
          "SITE_TYPE" : "",
          "EVENT_NUM" : 2,
          "EVENT_TIME" : "2026-02-09 14:03:50",
          "IS_TEST" : 0,
          "DETAIL_STATUS" : 2,
          "PORT_NUM_CN" : "集客直真",
          "EVENT_REASON" : "告警分析：设备脱网\n定位信息：MSP。",
          "VENDOR_ID" : 323,
          "REMOTE_EQUIPMENT_NAME" : "",
          "SRC_ORG_ALARM_TEXT" : """
【发生时间】2026-02-09 14:03:50;
【告警对象】MSP;
【告警内容】设备脱网(影响1条电路);
 【业务影响情况】1条业务;
(1).数据专线(5901351420250509296606),漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA
【归属客户】漳州市消防救援支队(5916596304)(金牌,非直服直管);
【A端】福建省漳州漳浦县古雷镇古雷港经济开发区新港城裕民路801号;
【业务信息】数据专线,本地专线,A;
;【告警分析】设备脱网;
【预定位信息】【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息

【客户侧信息查询】1、客户侧网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1
2、告警情况：客户侧无相关告警
【对端故障信息查询】对端无故障
【集客动环信息查询】1、故障网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1
2、查询资源：初步核实归属机房名称为漳州漳浦消防救援(杜浔AG专职站)一楼办公室机房，归属站点名称为3、查询告警：经核实查询最近6小时无相关停电故障，设备所在机房动环运行正常;

""",
          "ALARM_SOURCE" : "直真专线监控系统",
          "CITY_NAME" : "漳州市",
          "EQUIPMENT_NAME" : "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
          "NETWORK_SUB_TYPE_ID" : "1100",
          "EVENT_ID" : 311980616,
          "EVENT_TAG" : {
            "IS_MATCH_DISPATCH_RULES" : 1,
            "IS_MATCH_WARNING_RULES" : 0,
            "PREPROCESS_T1" : "否",
            "IS_MATCH_DANGER_RULES" : 0,
            "PREPROCESS_TIME" : 0
          },
          "CANCEL_STATUS" : 1,
          "DANGER_INFO" : {
            "PROCESS_TYPE" : 1,
            "DANGER_REASON" : "未匹配规则",
            "PROCESS_STATE" : 9,
            "ORDER_STATUS" : 0,
            "DISPATCH_STATUS_ID" : "1001"
          },
          "RECOGNITION_RULE_ID" : 1878,
          "PROJ_INTERFERENCE_FLAG" : 0,
          "ORIG_ALARM_CLEAR_FP" : "1713996274_3872318956_2520283298_4136070826",
          "ROOT_NETWORK_TYPE_ID" : "1",
          "NETWORK_SUB_TYPE_NAME" : "集客",
          "ALARM_STANDARD_NAME" : "设备脱网",
          "ALARM_STANDARD_FLAG" : 2,
          "MAINTAIN_TEAM" : "漳州漳浦集客铁通维护组",
          "EQP_OBJECT_ID" : "87002",
          "EVENT_ROOT_CATEGORY" : "客户侧故障",
          "EVENT_SOURCE" : 2,
          "EVENT_STATUS" : 0,
          "KEY_CELL" : "0",
          "NE_LABEL" : "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
          "TYPE_KEYCODE" : "预处理,",
          "EVENT_EXPLANATION" : "",
          "ALARM_RESOURCE_STATUS" : "1",
          "EFFECT_CLIENT_LEVEL" : "1",
          "SERVICE_ASSURANCE_LEVEL" : "2",
          "BUSINESS_TAG" : {
            "CIRCUIT_NO" : "漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA",
            "ADMIN_GRID_ID" : "",
            "GCSS_CLIENT" : "5916596304",
            "IRMS_GRID_NAME" : "",
            "GCSS_SERVICE_LEVEL_NAME" : "A",
            "GCSS_SERVICE_LEVEL" : "2",
            "GCSS_SERVICE_TYPE" : "1406",
            "GCSS_CLIENT_GRADE" : "1404",
            "GCSS_SERVICE" : "1",
            "BUSINESS_SYSTEM" : "集团专线",
            "ALARM_ANALYSIS" : "设备脱网",
            "PRODUCT_TYPE" : "数据专线",
            "HOME_CLIENT_NUM" : "",
            "CIRCUIT_LEVEL_NAME" : "本地专线",
            "EFFECT_CIRCUIT_NUM" : "1",
            "GCSS_CLIENT_NAME" : "漳州市消防救援支队(5916596304)",
            "BUSINESS_TYPE" : "",
            "CIRCUIT_LEVEL" : "1403",
            "GCSS_CLIENT_LEVEL" : "1",
            "GCSS_SERVICE_NUM" : "1"
          },
          "SUPPRESS_NIGHT" : "0",
          "NMS_ALARM_ID" : "2020740405373157376",
          "EXCEPTION_SUPPRESS_DISPATCH" : 0,
          "EVENT_NAME" : "单条集客A本地专线故障事件-设备脱网",
          "EQUIPMENT_IP" : "5901351420250509296606",
          "FAULT_LOCATION" : "【告警对象】MSP;<br>",
          "EVENT_COLLECTION_TIME" : "2026-02-09 14:04:57",
          "TOPIC_PARTITION" : 12,
          "SPECIFIC_PROBLEMS" : "631ed71a84cadfbeb9d29c7659232abf",
          "FULL_REGION_NAME" : "福建省/漳州市/漳浦县",
          "EXTRA_STRING1" : "",
          "IS_EFFECT_BUSINESS" : "是",
          "EVENT_CAT" : "【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息",
          "ALARM_UNIQUE_ID" : "2028480021",
          "ALARM_NAME" : "设备脱网(影响1条电路)",
          "VENDOR_NAME" : "瑞斯康达",
          "RECOGNITION_STANDARD_ID" : "WLSJ-YW-B-03-80-0032",
          "5G_CUSTOMER_LIST" : [ ],
          "EVENT_TYPE_ID" : "业务类",
          "MAIN_NET_SORT_ONE" : "集团专线",
          "EVENT_STANDARD_FLAG" : 2,
          "VENDOR_EVENT_TYPE" : "14202",
          "ALARM_REASON" : "",
          "OBJECT_CLASS_ID" : 87002,
          "PORT_NUM" : "300205",
          "COUNTY_ID" : "350623",
          "EVENT_LEVEL_NAME" : "四级",
          "ALARM_LEVEL_NAME" : "二级告警",
          "EVENT_EFFECT" : """
网络层面：[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1；
业务层面：影响集客业务1条，涉及客户：漳州市消防救援支队(5916596304)；
社会层面：无。
""",
          "EVENT_FP" : "1713996274_3872318956_2520283298_4136070826_2",
          "SERVICE_EFFECT_STATUS" : "有影响",
          "EVENT_ARRIVAL_TIME" : "2026-02-09 14:04:59",
          "FAULT_DIAGNOSIS" : "经核实无工程操作、无传输故障，无光功率异常，无动环停电，初步判断为对端故障导致，请进一步核实。",
          "EFFECT_SERVICE_LEVEL" : "2",
          "PROJ_INTERFERENCE_TYPE" : "【是否干扰告警】：否。",
          "TMSC_CAT" : "",
          "FAULT_TYPE_ID" : "设备",
          "GZ_EVENT_STATUS" : 2,
          "EVENT_PROVINCE_LEVEL" : "2",
          "NETWORK_TYPE_ID" : "11",
          "NE_ADMIN_STATUS" : "",
          "NMS_NAME" : "集客网管",
          "NETWORK_TYPE_NAME" : "集客",
          "FAULT_SUB_TYPE_ID" : "产品故障类",
          "PROVINCE_NAME" : "福建省",
          "EVENT_PROBABLE_CAUSE_TXT" : "",
          "OBJECT_CLASS_TEXT" : "SSAP",
          "ALARM_STANDARD_ID" : "1100-064-371-10-860022",
          "EXTRA_ID2" : "",
          "INTELLIGENT" : 0,
          "MAIN_NET_SORT_TWO" : "传输专线",
          "ORIG_ALARM_FP" : "1713996274_3872318956_2520283298_4136070826",
          "COUNTY_NAME" : "漳浦县",
          "SATOTAL" : 3,
          "EVENT_STANDARD_ID" : "WLSJ-YW-B-03-80-0032",
          "EFFECT_NE_NUM" : 1,
          "ROOT_NETWORK_TYPE_TOP" : "集客",
          "LAST_EVENT_TIME" : "2026-02-09 14:03:50",
          "EVENT_EXPLANATION_ADDITION" : "",
          "VENDOR_SEVERITY" : "1",
          "INTERFERENCE_FLAG" : "0",
          "EQP_OBJECT_NAME" : "SSAP",
          "OLD_EVENT_NAME" : "单条集客A本地专线故障事件-设备脱网",
          "EVENT_SUMMARY" : """
预处理步骤： 1.核查是否工程操作导致；
 2.核查是否动环停电故障导致；
 3.核查是否传输光缆故障导致；
 4.核查是否设备故障导致；
 5.核查是否客户下电导致。
""",
          "PROVINCE_ID" : "35000",
          "EVENT_CLEAR_FP" : "1713996274_3872318956_2520283298_4136070826_2",
          "GROUP_CUSTOMER_LINE_LIST" : "[]",
          "ALARM_LEVEL" : 2,
          "NE_TAG" : {
            "PORT_ID" : "UUID:614a77ab-42b9-44de-8c33-205e7debd2f0",
            "NE_ID" : "614a77ab-42b9-44de-8c33-205e7debd2f0",
            "MACHINE_ROOM_INFO" : ""
          },
          "EVENT_ROOT_CATEGORY_ID" : "11002",
          "EVENT_STANDARD_NAME" : "单条集客专线故障事件",
          "NE_LOCATION" : "62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
          "EFFECT_CIRCUIT_LEVEL" : "1403",
          "MAINTAIN_TEAM_SOURCE" : "1",
          "CITY_ID" : "350600",
          "REMOTE_OBJECT_CLASS" : "87002",
          "ORIG_EVENT_EXT" : {
            "SRC_ID" : "GZEVENT0000000920396189",
            "SRC_APP_ID" : "1001",
            "ACTIVE_STATUS" : 2,
            "MAINTAIN_GROUP" : "漳州漳浦集客铁通维护组",
            "SRC_ORG_ID" : "1713996274_3872318956_2520283298_4136070826_2"
          },
          "MAIN_NET_SORT_THREE" : "SSAP",
          "CUSTOMER_SERVICE_LEVEL" : "1",
          "CREATION_EVENT_TIME" : "2026-02-09 14:04:59",
          "FIRST_EVENT_TIME" : "2026-02-09 14:03:50",
          "SERV_EFFECT_TYPE" : "政企业务-集团专线",
          "MARK_SMART_RULE_ID" : null,
          "FIX_TIMEOUT_LIMIT" : null,
          "ORDER_ID" : "FJ-076-20260209-3320",
          "IS_ORDER_DELAY_APPLY" : 0,
          "CLEAR_CAPACITY_RULE_IDS" : null,
          "ORDER_STATUS" : 1,
          "CLEAR_CAPACITY_NAMES" : null,
          "ORDER_TIME" : "2026-02-09 14:17:11",
          "CLEAR_CAPACITY_DELAY_TIMES" : null,
          "OPDER_STATUS" : 1,
          "CANCEL_COLLECT_TIME" : "2026-02-09 14:33:59",
          "CANCEL_ARRIVAL_TIME" : "2026-02-09 14:33:59",
          "CLEAR_COLLECTION_TIME" : "2026-02-09 14:33:58",
          "CANCEL_TIME" : "2026-02-09 14:33:50"
        }
    }
    
    print("开始测试Kafka消息生成...")
    print("=" * 50)
    
    try:
        # 生成Kafka消息
        kafka_message = generate_es_to_kafka_mapping(test_es_data["_source"])
        
        print("生成的Kafka消息:")
        print(json.dumps(kafka_message, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 50)
        print("测试成功完成!")
        
        # 验证关键字段
        print("\n关键字段验证:")
        print(f"ID: {kafka_message.get('ID', 'N/A')}")
        print(f"NETWORK_TYPE_TOP: {kafka_message.get('NETWORK_TYPE_TOP', 'N/A')}")
        print(f"CITY_NAME: {kafka_message.get('CITY_NAME', 'N/A')}")
        print(f"EVENT_TIME: {kafka_message.get('EVENT_TIME', 'N/A')}")
        print(f"FP0_FP1_FP2_FP3: {kafka_message.get('FP0_FP1_FP2_FP3', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        return False

if __name__ == "__main__":
    test_kafka_generation()