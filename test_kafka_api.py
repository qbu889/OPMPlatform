#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 ES 数据转 Kafka 消息"""

import requests
import json

# 读取 curl 命令中的原始数据
es_source_raw = r'''{
          "HOME_BROAD_BAND_LIST" : [ ],
          "FULL_REGION_ID" : "35000/350100/350122",
          "EVENT_LEVEL" : 4,
          "CLEAR_CAPACITY_DELAY_TIMES" : "1",
          "SEND_JT_FLAG" : 0,
          "ORG_TYPE" : 1,
          "CLEAR_CAPACITY_RULE_IDS" : "159",
          "EVENT_LOCATION" : "基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房 1_中兴 DU68 开关电源",
          "TOPIC_PREFIX" : "EVENT-GZ",
          "DISPATCH_INFO" : {
            "T1_PROCESSING_TIME" : 120,
            "T1_CONFIRMATION_TIME" : 60,
            "START_TIME" : "00:00:00",
            "IS_CALCULATE_DURATION" : 0,
            "RULE_NAME" : "动环二级告警派单",
            "CONFIRMATION_TIME" : 60,
            "DISPATCH_TYPE" : 3,
            "INST_ID" : 280646,
            "DISPATCH_LEVEL" : 2,
            "PROCESS_STATE" : 9,
            "END_TIME" : "23:59:59",
            "T2_CONFIRMATION_TIME" : 60,
            "PROCESS_TYPE" : 1,
            "DISPATCH_NIGHT" : "0",
            "ORDER_STATUS" : 1,
            "IS_NEW_EFFECT_UPDATE" : 1,
            "DISPATCH_FLAG" : 0,
            "DISPATCH_REASON" : "工单派发成功",
            "TIME_RULE_NAME" : "电源和配套设备 - 机房动环",
            "DISPATCH_STATUS_ID" : "1010",
            "APPEND_DELAY_TIME" : 30,
            "RULE_ID" : 1195,
            "BUSINESS_EFFECT_RANGE_RATIO" : 30.0,
            "DISPATCH_LEVEL_RULE_NAME" : "电源和配套设备 - 机房动环",
            "T2_PROCESSING_TIME" : 720,
            "IS_BUSINESS_EFFECT_RANGE" : 1,
            "DISPATCH_LEVEL_RULE_ID" : 78,
            "DELAY_TIME" : 12,
            "PROCESSING_TIME" : 720,
            "SUPPRESS_TYPE" : 0,
            "JT_DISPATCH_STATUS_ID" : 5,
            "JT_DISPATCH_STATUS_DESC" : "自动派单成功",
            "TIME_RULE_ID" : 87,
            "IS_ROOT_EQP_LABEL_CHANGE" : 1,
            "ORDER_ID" : "FJ-080-20260320-1571",
            "ORDER_TYPE" : 1,
            "ORDER_TIME" : "2026-03-19 18:51:09",
            "AUTO_RECEIPT_REASON" : "未匹配到自动回单规则",
            "AUTO_RECEIPT_STATE" : 0,
            "SYNC_OPERATE_DESC" : "入遗留库",
            "TODO_LIST_ID" : "DH2026031903092",
            "PROCESS_ORDER_ID" : "FJ-076-20260319-4349",
            "PROCESS_ORDER_TIME" : "2026-03-20 10:01:47",
            "SYNC_LAST_TIME" : "2026-03-20 10:01:47"
          },
          "WARNING_INFO" : {
            "START_TIME" : "00:00:00",
            "DISPATCH_STATUS_ID" : "1003",
            "RULE_ID" : 13,
            "RECOVERY_DELAY_TIME" : 10,
            "BUSINESS_EFFECT_RANGE_RATIO" : 30.0,
            "WARNING_REASON" : "事件已清除",
            "IS_CALCULATE_DURATION" : 0,
            "RULE_NAME" : "预 A-动环 - 停电 - 动环停电事件 -60 分钟",
            "IS_BUSINESS_EFFECT_RANGE" : 1,
            "WARNING_TYPE" : "动力 - 停电",
            "DISPATCH_DELAY_TIME" : 60,
            "INST_ID" : 281229,
            "CONTENT_TEMPLATE_ID" : 1,
            "PROCESS_STATE" : 9,
            "END_TIME" : "23:59:59",
            "RULE_TYPE" : "1",
            "PROCESS_TYPE" : 1,
            "ORDER_STATUS" : 0,
            "IS_NEW_EFFECT_UPDATE" : 1,
            "DISPATCH_FLAG" : 1,
            "WARNING_LEVEL" : 101,
            "PROCESSING_TIME" : 120
          },
          "RECOGNITION_RULE_NAME" : "动环停电事件",
          "SITE_TYPE" : "105",
          "EVENT_NUM" : 1,
          "EVENT_TIME" : "2026-03-19 18:37:05",
          "CLEAR_CAPACITY_NAMES" : "动环停电三相交流电压质检",
          "IS_TEST" : 0,
          "DETAIL_STATUS" : 3,
          "PORT_NUM_CN" : "高新兴动力环境告警",
          "EVENT_REASON" : """
定界结果：初判为市电停电导致；
定位结论：基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房 1_中兴 DU68 开关电源。
是否配备油机：是
机房续航情况：组合式开关电源 2(TOSWITCH-33004),理论续航时长 5.74H,剩余续航时长 5.74H;组合式开关电源 1(TOSWITCH-93628),理论续航时长 8.0H,剩余续航时长 8.0H;
温度：11.6
电压电流情况：组合式开关电源 2-电压（52）电流（64.3）；组合式开关电源 1-电压（54）电流（94.3）；
""",
          "VENDOR_ID" : 771,
          "REMOTE_EQUIPMENT_NAME" : "",
          "SRC_ORG_ALARM_TEXT" : """
<ALARMSTART>
SystemName:高新兴动环系统
Vendor_Name:中兴 DU68 开关电源
Speciality:动环专业
AlarmID:268994297
IntID:c4ce8047-c267-44e5-9e3f-277b015e075c
AlarmEquipment:基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房 1_中兴 DU68 开关电源
EquipmentClass:
EventTime:2026-03-19 18:37:05
Vendor_Severity:二级告警
AlarmTitle:触发值：1，告警区间为：1
ActiveStatus:1
ProbableCause:
ProbableCauseTxt:福州连江坪垱后山山头移动自建房二楼设备间机房\中兴 DU68 开关电源\触发值：1，告警区间为：1
MaintainPropose:006007,003,1
LocateInfo:基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房 1_中兴 DU68 开关电源
ClearID:268994297
LocateName:基站>福州市>汇聚机房>连江县>福州连江坪垱后山山头移动自建房二楼设备间机房 1
Version:
AckUser:
AckTerminal:
DispatchFlag:0
standard_alarm_id:609-006-00-006095
IRMS_CUID:TOSWITCH-33004
<ALARMEND>
""",
          "ALARM_SOURCE" : "高新兴动力环境告警 (旧)",
          "CITY_NAME" : "福州市",
          "EQUIPMENT_NAME" : "福州连江丹阳对面原 48 号厂房西侧 20 米处自建房二楼设备间机房 - 开关电源 -2",
          "NETWORK_SUB_TYPE_ID" : "500",
          "EVENT_ID" : 322322790,
          "EVENT_TAG" : {
            "IS_MATCH_DISPATCH_RULES" : 1,
            "IS_MATCH_WARNING_RULES" : 1,
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
          "RECOGNITION_RULE_ID" : 1735,
          "FAULT_ROOT_CAUSE_SOURCE" : 0,
          "PROJ_INTERFERENCE_FLAG" : 0,
          "ORIG_ALARM_CLEAR_FP" : "2849831046_3186102817_2250992937_2055923267",
          "ROOT_NETWORK_TYPE_ID" : "5",
          "MARK_SMART_RULE_ID" : 5,
          "NETWORK_SUB_TYPE_NAME" : "动环",
          "ALARM_STANDARD_FLAG" : 2,
          "ALARM_STANDARD_NAME" : "电池放电告警",
          "EQP_OBJECT_ID" : "30014",
          "MAINTAIN_TEAM" : "福州连江农村网格虹信基站维护组 2",
          "EVENT_ROOT_CATEGORY" : "外部供电故障",
          "EVENT_SOURCE" : 2,
          "EVENT_STATUS" : 0,
          "KEY_CELL" : "0",
          "TYPE_KEYCODE" : "关联到资源,",
          "NE_LABEL" : "福州连江丹阳对面原 48 号厂房西侧 20 米处自建房二楼设备间机房 - 开关电源 -2",
          "EVENT_EXPLANATION" : "电池处于放电状态",
          "ALARM_RESOURCE_STATUS" : "1",
          "SERVICE_ASSURANCE_LEVEL" : "",
          "MARK_SMART_RULE_NAME" : "动环 - 停电、油机智能标识",
          "BUSINESS_TAG" : {
            "CIRCUIT_NO" : "006007,003,1",
            "ADMIN_GRID_ID" : "",
            "IRMS_GRID_NAME" : "",
            "BUSINESS_SYSTEM" : "高新兴动力环境告警 (旧)",
            "PRODUCT_TYPE" : "",
            "HOME_CLIENT_NUM" : "",
            "BUSINESS_TYPE" : "",
            "CIRCUIT_LEVEL" : ""
          },
          "NMS_ALARM_ID" : "268994297",
          "SUPPRESS_NIGHT" : "0",
          "EXCEPTION_SUPPRESS_DISPATCH" : 0,
          "EVENT_NAME" : "动环停电事件 - 电池放电告警",
          "EQUIPMENT_IP" : "",
          "FAULT_LOCATION" : "基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房 1_中兴 DU68 开关电源",
          "EVENT_COLLECTION_TIME" : "2026-03-19 18:39:01",
          "TOPIC_PARTITION" : 58,
          "SPECIFIC_PROBLEMS" : "35ceda4fa8321a114e2abf65adf7296d",
          "FULL_REGION_NAME" : "福建省/福州市/连江县",
          "TRIGGER_NE_LATITUDE" : "26.350132",
          "EXTRA_STRING1" : "",
          "IS_EFFECT_BUSINESS" : "否",
          "EVENT_CAT" : "",
          "ALARM_UNIQUE_ID" : "",
          "ALARM_NAME" : "电池放电告警",
          "VENDOR_NAME" : "高新兴",
          "RECOGNITION_STANDARD_ID" : "WLSJ-WL-DH-04-80-0043",
          "5G_CUSTOMER_LIST" : [ ],
          "MAIN_NET_SORT_ONE" : "电源和配套设备",
          "EVENT_TYPE_ID" : "网络类",
          "EVENT_STANDARD_FLAG" : 2,
          "VENDOR_EVENT_TYPE" : "1",
          "ALARM_REASON" : "",
          "OBJECT_CLASS_ID" : 30014,
          "COUNTY_ID" : "350122",
          "PORT_NUM" : "300103",
          "EVENT_LEVEL_NAME" : "四级",
          "FIX_TIMEOUT_LIMIT" : 30,
          "ALARM_LEVEL_NAME" : "三级告警",
          "EVENT_EFFECT" : """
网络影响：福州连江丹阳对面原 48 号厂房西侧 20 米处自建房二楼设备间机房 - 开关电源 -2；
机房下挂业务设备：无线设备：福州连江 - 丹阳 WJ 后山 B-HRHH-BBU-1、CBN-福州连江 - 丹阳虎山 C-HRHH-BBU-1、福州连江 - 蓬沿朱公 B-HRHH-BBU-1...等，传输设备：14079-连江丹阳街道（重要）、9190-连江丹阳汇聚环三-HW-OTM、1422-福州连江丹阳坪垱顶-HW-SPN(汇聚)...等，家宽设备：FZLJ 丹阳-OLT002-AN5516-01、FZLJ 丹阳-OLT001-AN5516-01
社会影响：暂无投诉。
""",
          "EVENT_FP" : "3667335322_2064221507_2850463975_367294279_2",
          "SERVICE_EFFECT_STATUS" : "无影响",
          "EVENT_ARRIVAL_TIME" : "2026-03-19 18:39:03",
          "FAULT_DIAGNOSIS" : "【故障原因初判】动环设备问题.\t【故障处理建议】请排查动环设备故障。",
          "PROJ_INTERFERENCE_TYPE" : "【是否干扰告警】：否。",
          "FAULT_TYPE_ID" : "设备",
          "TMSC_CAT" : "",
          "GZ_EVENT_STATUS" : 3,
          "EVENT_PROVINCE_LEVEL" : 2,
          "NETWORK_TYPE_ID" : "5",
          "NE_ADMIN_STATUS" : "",
          "NETWORK_TYPE_NAME" : "动环",
          "NMS_NAME" : "高新兴动环系统",
          "TRIGGER_COORDINATE_TYPE" : "1",
          "FAULT_SUB_TYPE_ID" : "停电类",
          "PROVINCE_NAME" : "福建省",
          "EVENT_PROBABLE_CAUSE_TXT" : "0",
          "ALARM_STANDARD_ID" : "0500-009-006-10-800006",
          "OBJECT_CLASS_TEXT" : "开关电源",
          "EXTRA_ID2" : "",
          "INTELLIGENT" : 1,
          "MAIN_NET_SORT_TWO" : "机房动环",
          "TRIGGER_NE_LONGITUDE" : "119.478012",
          "ORIG_ALARM_FP" : "3667335322_2064221507_2850463975_367294279",
          "SATOTAL" : 3,
          "COUNTY_NAME" : "连江县",
          "EVENT_STANDARD_ID" : "WLSJ-WL-DH-04-80-0043",
          "EFFECT_NE_NUM" : 0,
          "ROOT_NETWORK_TYPE_TOP" : "动环",
          "LAST_EVENT_TIME" : "2026-03-19 18:37:05",
          "EVENT_EXPLANATION_ADDITION" : "传输节点",
          "VENDOR_SEVERITY" : "三级告警",
          "INTERFERENCE_FLAG" : "0",
          "EQP_OBJECT_NAME" : "开关电源",
          "OLD_EVENT_NAME" : "动环停电事件 - 电池放电告警",
          "EVENT_SUMMARY" : "1、核查是否工程操作；2、核查是否有动环监控设备通信异常告警；3.核实是否动环监控三相电压值门限异常；4、若以上条件均不满足，判断为外部供电中断导致",
          "PROVINCE_ID" : "35000",
          "EVENT_CLEAR_FP" : "2849831046_3186102817_2250992937_2055923267_2",
          "GROUP_CUSTOMER_LINE_LIST" : "[]",
          "ALARM_LEVEL" : 3,
          "NE_TAG" : {
            "MACHINE_ROOM_ADDRESS" : "福建省福州市连江县丹阳镇丹阳村对面原 48 号厂房西侧 20 米处移动自建房二楼设备间",
            "HAS_FIXED_GENERATOR" : "1",
            "NE_ID" : "TOSWITCH-33004",
            "MANAGER_ROOM_ADMIN_ACCOUNT" : "lushenghan",
            "BUILD_ID" : "STATION-NMS-0591-04774",
            "MANAGER_ROOM_ADMIN_TEL" : "13799726941",
            "ROOM_ID" : "DEVICEROOM-NMS-0591-04774",
            "PORT_ID" : "609-006-00-006095",
            "IS_AGG_ROOM" : 1,
            "IS_CORE_ROOM" : 0,
            "MACHINE_ROOM_GRADE" : "汇聚（普通汇聚）",
            "MACHINE_ROOM_INFO" : "福州连江丹阳对面原 48 号厂房西侧 20 米处自建房二楼设备间机房",
            "ROOM_DEPT" : "天面铁塔",
            "MANAGER_ROOM_ADMIN_NAME" : "卢声汉"
          },
          "EVENT_ROOT_CATEGORY_ID" : "5015",
          "SCENCE_NAME" : "10000",
          "EVENT_STANDARD_NAME" : "动环停电事件",
          "NE_LOCATION" : "无线设备：福州连江 - 丹阳 WJ 后山 B-HRHH-BBU-1、CBN-福州连江 - 丹阳虎山 C-HRHH-BBU-1、福州连江 - 蓬沿朱公 B-HRHH-BBU-1...等，传输设备：14079-连江丹阳街道（重要）、9190-连江丹阳汇聚环三-HW-OTM、1422-福州连江丹阳坪垱顶-HW-SPN(汇聚)...等，家宽设备：FZLJ 丹阳-OLT002-AN5516-01、FZLJ 丹阳-OLT001-AN5516-01",
          "EFFECT_CIRCUIT_LEVEL" : "",
          "MAINTAIN_TEAM_SOURCE" : "1",
          "CITY_ID" : "350100",
          "ORIG_EVENT_EXT" : {
            "SRC_ID" : "GZEVENT0000000995504450",
            "SRC_APP_ID" : "1001",
            "ACTIVE_STATUS" : 3,
            "MAINTAIN_GROUP" : "福州连江农村网格虹信基站维护组 2",
            "SRC_ORG_ID" : "3667335322_2064221507_2850463975_367294279_2"
          },
          "REMOTE_OBJECT_CLASS" : "",
          "MAIN_NET_SORT_THREE" : "开关电源",
          "CUSTOMER_SERVICE_LEVEL" : "",
          "CREATION_EVENT_TIME" : "2026-03-19 18:39:03",
          "FIRST_EVENT_TIME" : "2026-03-19 18:37:05",
          "SERV_EFFECT_TYPE" : "无" 
}'''

# 发送请求
url = 'http://127.0.0.1:5001/kafka-generator/generate'
headers = {'Content-Type': 'application/json'}
data = {
    'es_source_raw': es_source_raw,
    'custom_fields': {}
}

print(f"发送请求到：{url}")
print(f"数据长度：{len(es_source_raw)} 字符")
print("-" * 80)

try:
    response = requests.post(url, json=data, headers=headers)
    
    print(f"状态码：{response.status_code}")
    print(f"响应内容：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
except Exception as e:
    print(f"请求失败：{e}")
