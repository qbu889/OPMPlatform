# 请求地址：
http://localhost:5173/word-to-md
# 架构要求
1. 基于目前的flask服务
2. 开发vue页面
3. 在首页和顶部的菜单添加入口。
# 前置条件
## ES查询结果
{
  "took" : 18,
  "timed_out" : false,
  "_shards" : {
    "total" : 12,
    "successful" : 12,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 3,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "mw_em_master",
        "_type" : "_doc",
        "_id" : "330937543",
        "_score" : 1.0,
        "_source" : {
          "HOME_BROAD_BAND_LIST" : [ ],
          "FULL_REGION_ID" : "35000/350100/350105",
          "EVENT_LEVEL" : 4,
          "SEND_JT_FLAG" : 0,
          "ORG_TYPE" : 1,
          "EVENT_LOCATION" : "基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH",
          "TOPIC_PREFIX" : "EVENT-GZ",
          "DISPATCH_INFO" : {
            "T1_PROCESSING_TIME" : 120,
            "T1_CONFIRMATION_TIME" : 60,
            "START_TIME" : "00:00:00",
            "IS_CALCULATE_DURATION" : 0,
            "RULE_NAME" : "动环二级告警派单",
            "CONFIRMATION_TIME" : 60,
            "DISPATCH_TYPE" : 0,
            "INST_ID" : 280646,
            "DISPATCH_LEVEL" : 2,
            "PROCESS_STATE" : 4,
            "END_TIME" : "23:59:59",
            "T2_CONFIRMATION_TIME" : 60,
            "PROCESS_TYPE" : 1,
            "DISPATCH_NIGHT" : "0",
            "ORDER_STATUS" : 1,
            "IS_NEW_EFFECT_UPDATE" : 1,
            "DISPATCH_FLAG" : 0,
            "DISPATCH_REASON" : "同源合并成功",
            "TIME_RULE_NAME" : "电源和配套设备-机房动环",
            "DISPATCH_STATUS_ID" : "1011",
            "APPEND_DELAY_TIME" : 30,
            "RULE_ID" : 1195,
            "BUSINESS_EFFECT_RANGE_RATIO" : 30.0,
            "DISPATCH_LEVEL_RULE_NAME" : "电源和配套设备-机房动环",
            "T2_PROCESSING_TIME" : 720,
            "IS_BUSINESS_EFFECT_RANGE" : 1,
            "DISPATCH_LEVEL_RULE_ID" : 78,
            "DELAY_TIME" : 12,
            "PROCESSING_TIME" : 720,
            "SUPPRESS_TYPE" : 0,
            "JT_DISPATCH_STATUS_ID" : 10,
            "JT_DISPATCH_STATUS_DESC" : "追单派单成功",
            "TIME_RULE_ID" : 87,
            "IS_ROOT_EQP_LABEL_CHANGE" : 1,
            "ORDER_ID" : "FJ-076-20260414-4243",
            "ORDER_TYPE" : 2,
            "ORDER_TIME" : "2026-04-14 16:55:12"
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
          "RECOGNITION_RULE_NAME" : "动环电池组故障事件",
          "SITE_TYPE" : "109",
          "EVENT_NUM" : 1,
          "EVENT_TIME" : "2026-04-14 16:40:49",
          "IS_TEST" : 0,
          "DETAIL_STATUS" : 11,
          "PORT_NUM_CN" : "高兴新动力环境告警",
          "EVENT_REASON" : "定界结果：初判为电池故障导致；\n定位结论：基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH。",
          "VENDOR_ID" : 771,
          "REMOTE_EQUIPMENT_NAME" : "",
          "SRC_ORG_ALARM_TEXT" : """
<ALARMSTART>
SystemName:高新兴动环系统
Vendor_Name:1#南都电池组1000AH
Speciality:动环专业
AlarmID:273160988
IntID:c6b14463511c45e9934ce3dabff4a3c1
AlarmEquipment:基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH
EquipmentClass:
EventTime:2026-04-14 16:40:49
Vendor_Severity:三级告警
AlarmTitle:05#单体电压高于设定告警阈值
ActiveStatus:1
ProbableCause:
ProbableCauseTxt:福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房\1#南都电池组1000AH\05#单体电压高于设定告警阈值
MaintainPropose:007004,005,2.38
LocateInfo:基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH
ClearID:273160988
LocateName:基站>福州市>BBU池基站>马尾区
Version:
AckUser:
AckTerminal:
DispatchFlag:0
standard_alarm_id:0500-002-007-10-007004
IRMS_CUID:ACCUMULATOR-90046
<ALARMEND>
""",
          "ALARM_SOURCE" : "高兴新动力环境告警(旧)",
          "CITY_NAME" : "福州市",
          "EQUIPMENT_NAME" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1",
          "NETWORK_SUB_TYPE_ID" : "500",
          "EVENT_ID" : 330937543,
          "EVENT_TAG" : {
            "IS_MATCH_DISPATCH_RULES" : 1,
            "IS_MATCH_WARNING_RULES" : 0,
            "PREPROCESS_T1" : "否",
            "IS_MATCH_DANGER_RULES" : 0,
            "PREPROCESS_TIME" : 0
          },
          "CANCEL_STATUS" : 0,
          "DANGER_INFO" : {
            "PROCESS_TYPE" : 1,
            "DANGER_REASON" : "未匹配规则",
            "PROCESS_STATE" : 9,
            "ORDER_STATUS" : 0,
            "DISPATCH_STATUS_ID" : "1001"
          },
          "RECOGNITION_RULE_ID" : 1749,
          "FAULT_ROOT_CAUSE_SOURCE" : 1,
          "PROJ_INTERFERENCE_FLAG" : 0,
          "ORIG_ALARM_CLEAR_FP" : "2718601683_101722914_347631486_1348703620",
          "ROOT_NETWORK_TYPE_ID" : "5",
          "MARK_SMART_RULE_ID" : 29,
          "NETWORK_SUB_TYPE_NAME" : "动环",
          "ALARM_STANDARD_NAME" : "单体XX电压过高告警",
          "ALARM_STANDARD_FLAG" : 2,
          "MAINTAIN_TEAM" : "福州马尾主城区网格虹信基站维护组2",
          "EQP_OBJECT_ID" : "30008",
          "EVENT_ROOT_CATEGORY" : "蓄电池故障",
          "EVENT_SOURCE" : 2,
          "EVENT_STATUS" : 0,
          "KEY_CELL" : "0",
          "NE_LABEL" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1",
          "TYPE_KEYCODE" : "关联到资源,",
          "EVENT_EXPLANATION" : "一、告警解释：蓄电池单只电池电压高于保护阀值。二、可能原因：1、电池组充电电压过高。",
          "ALARM_RESOURCE_STATUS" : "1",
          "SERVICE_ASSURANCE_LEVEL" : "",
          "MARK_SMART_RULE_NAME" : "动环-非停电智能调度场景",
          "BUSINESS_TAG" : {
            "CIRCUIT_NO" : "007004,005,2.38",
            "ADMIN_GRID_ID" : "",
            "IRMS_GRID_NAME" : "",
            "BUSINESS_SYSTEM" : "高兴新动力环境告警(旧)",
            "PRODUCT_TYPE" : "",
            "HOME_CLIENT_NUM" : "",
            "BUSINESS_TYPE" : "",
            "CIRCUIT_LEVEL" : ""
          },
          "SUPPRESS_NIGHT" : "1",
          "NMS_ALARM_ID" : "273160988",
          "EXCEPTION_SUPPRESS_DISPATCH" : 0,
          "FAULT_DISPOSAL_METHOD" : "现场人工处置,现场更换设备",
          "EVENT_NAME" : "动环电池组故障事件-单体XX电压过高告警",
          "EQUIPMENT_IP" : "",
          "FAULT_LOCATION" : "基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH",
          "EVENT_COLLECTION_TIME" : "2026-04-14 16:43:03",
          "TOPIC_PARTITION" : 61,
          "SPECIFIC_PROBLEMS" : "48445545781a5d37ab94e21155470f00",
          "FULL_REGION_NAME" : "福建省/福州市/马尾区",
          "TRIGGER_NE_LATITUDE" : "26.02462",
          "EXTRA_STRING1" : "",
          "IS_EFFECT_BUSINESS" : "否",
          "EVENT_CAT" : "",
          "ALARM_UNIQUE_ID" : "",
          "ALARM_NAME" : "单体XX电压过高告警",
          "VENDOR_NAME" : "高新兴",
          "RECOGNITION_STANDARD_ID" : "WLSJ-WL-DH-04-80-0052",
          "5G_CUSTOMER_LIST" : [ ],
          "EVENT_TYPE_ID" : "网络类",
          "MAIN_NET_SORT_ONE" : "电源和配套设备",
          "EVENT_STANDARD_FLAG" : 2,
          "VENDOR_EVENT_TYPE" : "1",
          "ALARM_REASON" : "",
          "OBJECT_CLASS_ID" : 30008,
          "PORT_NUM" : "300103",
          "COUNTY_ID" : "350105",
          "EVENT_LEVEL_NAME" : "四级事件",
          "FIX_TIMEOUT_LIMIT" : 30,
          "ALARM_LEVEL_NAME" : "二级告警",
          "EVENT_EFFECT" : """
网络影响：福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1；
机房下挂业务设备：无线设备：福州马尾-马尾快安名城五区西路-NLH-BBU01、福州马尾快安名郡一期-HHM-G-BBU01、福州马尾-马尾快安宗棠路边防大队-NLS-BBU-01...等，传输设备：18023-福州马尾凯隆橙仕公馆(BBU池)-HW-SPN、14-2014-福州-马尾-快安凯隆橙仕公馆2号楼负一楼-HW-HUB、22196-福州马尾凯隆橙仕公馆-ZX-PTN-1...等，家宽设备：FZMW凯隆橙仕公馆-OLT001-C650(下沉)
社会影响：暂无投诉。
""",
          "FAULT_CAUSE_CATEGORY2" : "蓄电池故障",
          "FAULT_CAUSE_CATEGORY1" : "设备故障",
          "EVENT_FP" : "1821276491_2998015541_1819582473_803382798_2",
          "SERVICE_EFFECT_STATUS" : "无影响",
          "EVENT_ARRIVAL_TIME" : "2026-04-14 16:43:05",
          "FAULT_DIAGNOSIS" : "【故障原因初判】由于停电/电池单体故障导致\n【故障处理建议】请尽快核实具体原因，尽快上站处理。",
          "PROJ_INTERFERENCE_TYPE" : "【是否干扰告警】：否。",
          "TMSC_CAT" : "",
          "FAULT_TYPE_ID" : "设备",
          "GZ_EVENT_STATUS" : 1,
          "EVENT_PROVINCE_LEVEL" : "2",
          "NETWORK_TYPE_ID" : "5",
          "NE_ADMIN_STATUS" : "",
          "NMS_NAME" : "高新兴动环系统",
          "NETWORK_TYPE_NAME" : "动环",
          "TRIGGER_COORDINATE_TYPE" : "1",
          "FAULT_DISPOSAL_PLAN" : "处置机房电池组故障",
          "FAULT_SUB_TYPE_ID" : "电源开关设备类",
          "PROVINCE_NAME" : "福建省",
          "EVENT_PROBABLE_CAUSE_TXT" : "0",
          "OBJECT_CLASS_TEXT" : "铅酸电池",
          "ALARM_STANDARD_ID" : "0500-009-007-10-000022",
          "EXTRA_ID2" : "",
          "INTELLIGENT" : 1,
          "MAIN_NET_SORT_TWO" : "机房动环",
          "TRIGGER_NE_LONGITUDE" : "119.39477",
          "ORIG_ALARM_FP" : "1821276491_2998015541_1819582473_803382798",
          "COUNTY_NAME" : "马尾区",
          "SATOTAL" : 1,
          "EVENT_STANDARD_ID" : "WLSJ-WL-DH-04-80-0052",
          "EFFECT_NE_NUM" : 0,
          "ROOT_NETWORK_TYPE_TOP" : "动环",
          "LAST_EVENT_TIME" : "2026-04-14 16:40:49",
          "EVENT_EXPLANATION_ADDITION" : "传输节点",
          "VENDOR_SEVERITY" : "二级告警",
          "INTERFERENCE_FLAG" : "0",
          "FAULT_KEEPALIVE_STATUS" : "否",
          "EQP_OBJECT_NAME" : "铅酸电池",
          "OLD_EVENT_NAME" : "动环电池组故障事件-单体XX电压过高告警",
          "FAULT_PROCESS_STATUS" : "正常",
          "EVENT_SUMMARY" : "1、核查是否工程操作；2、核查是否有动环监控设备通信异常告警；3.核实是否动环监控电池电压值门限异常；4、若以上条件均不满足，判断为电池故障导致。",
          "PROVINCE_ID" : "35000",
          "EVENT_CLEAR_FP" : "2718601683_101722914_347631486_1348703620_2",
          "GROUP_CUSTOMER_LINE_LIST" : "[]",
          "ALARM_LEVEL" : 2,
          "NE_TAG" : {
            "MACHINE_ROOM_ADDRESS" : "福建省福州市马尾区马尾镇宗棠路18号凯隆橙仕公馆2号楼负一楼185号车位后面设备间",
            "HAS_FIXED_GENERATOR" : "0",
            "NE_ID" : "ACCUMULATOR-90046",
            "MANAGER_ROOM_ADMIN_ACCOUNT" : "jianghong",
            "BUILD_ID" : "STATION-NMS-0591-07267",
            "MANAGER_ROOM_ADMIN_TEL" : "13799327891",
            "ROOM_ID" : "DEVICEROOM-NMS-0591-08107",
            "PORT_ID" : "0500-002-007-10-007004",
            "IS_AGG_ROOM" : 1,
            "IS_CORE_ROOM" : 0,
            "MACHINE_ROOM_GRADE" : "汇聚（综合业务接入）",
            "MACHINE_ROOM_INFO" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房",
            "ROOM_DEPT" : "业主",
            "MANAGER_ROOM_ADMIN_NAME" : "江泓"
          },
          "EVENT_ROOT_CATEGORY_ID" : "5017",
          "SCENCE_NAME" : "11000,dh_non_power",
          "EVENT_STANDARD_NAME" : "动环电池组故障事件",
          "NE_LOCATION" : "无线设备：福州马尾-马尾快安名城五区西路-NLH-BBU01、福州马尾快安名郡一期-HHM-G-BBU01、福州马尾-马尾快安宗棠路边防大队-NLS-BBU-01...等，传输设备：18023-福州马尾凯隆橙仕公馆(BBU池)-HW-SPN、14-2014-福州-马尾-快安凯隆橙仕公馆2号楼负一楼-HW-HUB、22196-福州马尾凯隆橙仕公馆-ZX-PTN-1...等，家宽设备：FZMW凯隆橙仕公馆-OLT001-C650(下沉)",
          "EFFECT_CIRCUIT_LEVEL" : "",
          "MAINTAIN_TEAM_SOURCE" : "1",
          "CITY_ID" : "350100",
          "REMOTE_OBJECT_CLASS" : "",
          "ORIG_EVENT_EXT" : {
            "SRC_ID" : "GZEVENT0000001054468620",
            "SRC_APP_ID" : "1001",
            "ACTIVE_STATUS" : 1,
            "MAINTAIN_GROUP" : "福州马尾主城区网格虹信基站维护组2",
            "SRC_ORG_ID" : "1821276491_2998015541_1819582473_803382798_2"
          },
          "MAIN_NET_SORT_THREE" : "铅酸电池",
          "CUSTOMER_SERVICE_LEVEL" : "",
          "CREATION_EVENT_TIME" : "2026-04-14 16:43:05",
          "FIRST_EVENT_TIME" : "2026-04-14 16:40:49",
          "SERV_EFFECT_TYPE" : "无",
          "ORDER_ID" : "FJ-076-20260414-4243",
          "IS_ORDER_DELAY_APPLY" : 0,
          "ORDER_STATUS" : 1,
          "ORDER_TIME" : "2026-04-14 16:55:12",
          "OPDER_STATUS" : 1
        }
      },
      {
        "_index" : "mw_em_master",
        "_type" : "_doc",
        "_id" : "330936162",
        "_score" : 1.0,
        "_source" : {
          "HOME_BROAD_BAND_LIST" : [ ],
          "FULL_REGION_ID" : "35000/350100/350105",
          "EVENT_LEVEL" : 4,
          "SEND_JT_FLAG" : 0,
          "ORG_TYPE" : 1,
          "EVENT_LOCATION" : "基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH",
          "TOPIC_PREFIX" : "EVENT-GZ",
          "DISPATCH_INFO" : {
            "T1_PROCESSING_TIME" : 120,
            "T1_CONFIRMATION_TIME" : 60,
            "START_TIME" : "00:00:00",
            "IS_CALCULATE_DURATION" : 0,
            "RULE_NAME" : "动环二级告警派单",
            "CONFIRMATION_TIME" : 60,
            "DISPATCH_TYPE" : 0,
            "INST_ID" : 280646,
            "DISPATCH_LEVEL" : 2,
            "PROCESS_STATE" : 4,
            "END_TIME" : "23:59:59",
            "T2_CONFIRMATION_TIME" : 60,
            "PROCESS_TYPE" : 1,
            "DISPATCH_NIGHT" : "0",
            "ORDER_STATUS" : 1,
            "IS_NEW_EFFECT_UPDATE" : 1,
            "DISPATCH_FLAG" : 0,
            "DISPATCH_REASON" : "工单派发成功",
            "TIME_RULE_NAME" : "电源和配套设备-机房动环",
            "DISPATCH_STATUS_ID" : "1010",
            "APPEND_DELAY_TIME" : 30,
            "RULE_ID" : 1195,
            "BUSINESS_EFFECT_RANGE_RATIO" : 30.0,
            "DISPATCH_LEVEL_RULE_NAME" : "电源和配套设备-机房动环",
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
            "ORDER_ID" : "FJ-076-20260414-4243",
            "ORDER_TYPE" : 1,
            "ORDER_TIME" : "2026-04-14 16:50:09"
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
          "RECOGNITION_RULE_NAME" : "动环电池组故障事件",
          "SITE_TYPE" : "109",
          "EVENT_NUM" : 1,
          "EVENT_TIME" : "2026-04-14 16:35:06",
          "IS_TEST" : 0,
          "DETAIL_STATUS" : 11,
          "PORT_NUM_CN" : "高兴新动力环境告警",
          "EVENT_REASON" : "定界结果：初判为电池故障导致；\n定位结论：基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH。",
          "VENDOR_ID" : 771,
          "REMOTE_EQUIPMENT_NAME" : "",
          "SRC_ORG_ALARM_TEXT" : """
<ALARMSTART>
SystemName:高新兴动环系统
Vendor_Name:1#南都电池组1000AH
Speciality:动环专业
AlarmID:273160272
IntID:3f0e6efc7d2445a39beda8313e3b6396
AlarmEquipment:基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH
EquipmentClass:
EventTime:2026-04-14 16:35:06
Vendor_Severity:三级告警
AlarmTitle:01#单体电压高于设定告警阈值
ActiveStatus:1
ProbableCause:
ProbableCauseTxt:福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房\1#南都电池组1000AH\01#单体电压高于设定告警阈值
MaintainPropose:007004,001,2.38
LocateInfo:基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH
ClearID:273160272
LocateName:基站>福州市>BBU池基站>马尾区
Version:
AckUser:
AckTerminal:
DispatchFlag:0
standard_alarm_id:0500-002-007-10-007004
IRMS_CUID:ACCUMULATOR-90046
<ALARMEND>
""",
          "ALARM_SOURCE" : "高兴新动力环境告警(旧)",
          "CITY_NAME" : "福州市",
          "EQUIPMENT_NAME" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1",
          "NETWORK_SUB_TYPE_ID" : "500",
          "EVENT_ID" : 330936162,
          "EVENT_TAG" : {
            "IS_MATCH_DISPATCH_RULES" : 1,
            "IS_MATCH_WARNING_RULES" : 0,
            "PREPROCESS_T1" : "否",
            "IS_MATCH_DANGER_RULES" : 0,
            "PREPROCESS_TIME" : 0
          },
          "CANCEL_STATUS" : 0,
          "DANGER_INFO" : {
            "PROCESS_TYPE" : 1,
            "DANGER_REASON" : "未匹配规则",
            "PROCESS_STATE" : 9,
            "ORDER_STATUS" : 0,
            "DISPATCH_STATUS_ID" : "1001"
          },
          "RECOGNITION_RULE_ID" : 1749,
          "FAULT_ROOT_CAUSE_SOURCE" : 1,
          "PROJ_INTERFERENCE_FLAG" : 0,
          "ORIG_ALARM_CLEAR_FP" : "3473649843_929116286_1819092634_2690859019",
          "ROOT_NETWORK_TYPE_ID" : "5",
          "MARK_SMART_RULE_ID" : 29,
          "NETWORK_SUB_TYPE_NAME" : "动环",
          "ALARM_STANDARD_NAME" : "单体XX电压过高告警",
          "ALARM_STANDARD_FLAG" : 2,
          "MAINTAIN_TEAM" : "福州马尾主城区网格虹信基站维护组2",
          "EQP_OBJECT_ID" : "30008",
          "EVENT_ROOT_CATEGORY" : "蓄电池故障",
          "EVENT_SOURCE" : 2,
          "EVENT_STATUS" : 0,
          "KEY_CELL" : "0",
          "NE_LABEL" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1",
          "TYPE_KEYCODE" : "关联到资源,",
          "EVENT_EXPLANATION" : "一、告警解释：蓄电池单只电池电压高于保护阀值。二、可能原因：1、电池组充电电压过高。",
          "ALARM_RESOURCE_STATUS" : "1",
          "SERVICE_ASSURANCE_LEVEL" : "",
          "MARK_SMART_RULE_NAME" : "动环-非停电智能调度场景",
          "BUSINESS_TAG" : {
            "CIRCUIT_NO" : "007004,001,2.38",
            "ADMIN_GRID_ID" : "",
            "IRMS_GRID_NAME" : "",
            "BUSINESS_SYSTEM" : "高兴新动力环境告警(旧)",
            "PRODUCT_TYPE" : "",
            "HOME_CLIENT_NUM" : "",
            "BUSINESS_TYPE" : "",
            "CIRCUIT_LEVEL" : ""
          },
          "SUPPRESS_NIGHT" : "1",
          "NMS_ALARM_ID" : "273160272",
          "EXCEPTION_SUPPRESS_DISPATCH" : 0,
          "FAULT_DISPOSAL_METHOD" : "现场人工处置,现场更换设备",
          "EVENT_NAME" : "动环电池组故障事件-单体XX电压过高告警",
          "EQUIPMENT_IP" : "",
          "FAULT_LOCATION" : "基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH",
          "EVENT_COLLECTION_TIME" : "2026-04-14 16:38:02",
          "TOPIC_PARTITION" : 47,
          "SPECIFIC_PROBLEMS" : "9fc1f27d214c71383c7204a889e2f429",
          "FULL_REGION_NAME" : "福建省/福州市/马尾区",
          "TRIGGER_NE_LATITUDE" : "26.02462",
          "EXTRA_STRING1" : "",
          "IS_EFFECT_BUSINESS" : "否",
          "EVENT_CAT" : "",
          "ALARM_UNIQUE_ID" : "",
          "ALARM_NAME" : "单体XX电压过高告警",
          "VENDOR_NAME" : "高新兴",
          "RECOGNITION_STANDARD_ID" : "WLSJ-WL-DH-04-80-0052",
          "5G_CUSTOMER_LIST" : [ ],
          "EVENT_TYPE_ID" : "网络类",
          "MAIN_NET_SORT_ONE" : "电源和配套设备",
          "EVENT_STANDARD_FLAG" : 2,
          "VENDOR_EVENT_TYPE" : "1",
          "ALARM_REASON" : "",
          "OBJECT_CLASS_ID" : 30008,
          "PORT_NUM" : "300103",
          "COUNTY_ID" : "350105",
          "EVENT_LEVEL_NAME" : "四级事件",
          "FIX_TIMEOUT_LIMIT" : 30,
          "ALARM_LEVEL_NAME" : "二级告警",
          "EVENT_EFFECT" : """
网络影响：福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1；
机房下挂业务设备：无线设备：福州马尾-马尾快安名城五区西路-NLH-BBU01、福州马尾快安名郡一期-HHM-G-BBU01、福州马尾-马尾快安宗棠路边防大队-NLS-BBU-01...等，传输设备：18023-福州马尾凯隆橙仕公馆(BBU池)-HW-SPN、14-2014-福州-马尾-快安凯隆橙仕公馆2号楼负一楼-HW-HUB、22196-福州马尾凯隆橙仕公馆-ZX-PTN-1...等，家宽设备：FZMW凯隆橙仕公馆-OLT001-C650(下沉)
社会影响：暂无投诉。
""",
          "FAULT_CAUSE_CATEGORY2" : "蓄电池故障",
          "FAULT_CAUSE_CATEGORY1" : "设备故障",
          "EVENT_FP" : "3306118179_2013949611_3622437094_1593090642_2",
          "SERVICE_EFFECT_STATUS" : "无影响",
          "EVENT_ARRIVAL_TIME" : "2026-04-14 16:38:04",
          "FAULT_DIAGNOSIS" : "【故障原因初判】由于停电/电池单体故障导致\n【故障处理建议】请尽快核实具体原因，尽快上站处理。",
          "PROJ_INTERFERENCE_TYPE" : "【是否干扰告警】：否。",
          "TMSC_CAT" : "",
          "FAULT_TYPE_ID" : "设备",
          "GZ_EVENT_STATUS" : 1,
          "EVENT_PROVINCE_LEVEL" : "2",
          "NETWORK_TYPE_ID" : "5",
          "NE_ADMIN_STATUS" : "",
          "NMS_NAME" : "高新兴动环系统",
          "NETWORK_TYPE_NAME" : "动环",
          "TRIGGER_COORDINATE_TYPE" : "1",
          "FAULT_DISPOSAL_PLAN" : "处置机房电池组故障",
          "FAULT_SUB_TYPE_ID" : "电源开关设备类",
          "PROVINCE_NAME" : "福建省",
          "EVENT_PROBABLE_CAUSE_TXT" : "0",
          "OBJECT_CLASS_TEXT" : "铅酸电池",
          "ALARM_STANDARD_ID" : "0500-009-007-10-000022",
          "EXTRA_ID2" : "",
          "INTELLIGENT" : 1,
          "MAIN_NET_SORT_TWO" : "机房动环",
          "TRIGGER_NE_LONGITUDE" : "119.39477",
          "ORIG_ALARM_FP" : "3306118179_2013949611_3622437094_1593090642",
          "COUNTY_NAME" : "马尾区",
          "SATOTAL" : 1,
          "EVENT_STANDARD_ID" : "WLSJ-WL-DH-04-80-0052",
          "EFFECT_NE_NUM" : 0,
          "ROOT_NETWORK_TYPE_TOP" : "动环",
          "LAST_EVENT_TIME" : "2026-04-14 16:35:06",
          "EVENT_EXPLANATION_ADDITION" : "传输节点",
          "VENDOR_SEVERITY" : "二级告警",
          "INTERFERENCE_FLAG" : "0",
          "FAULT_KEEPALIVE_STATUS" : "否",
          "EQP_OBJECT_NAME" : "铅酸电池",
          "OLD_EVENT_NAME" : "动环电池组故障事件-单体XX电压过高告警",
          "FAULT_PROCESS_STATUS" : "正常",
          "EVENT_SUMMARY" : "1、核查是否工程操作；2、核查是否有动环监控设备通信异常告警；3.核实是否动环监控电池电压值门限异常；4、若以上条件均不满足，判断为电池故障导致。",
          "PROVINCE_ID" : "35000",
          "EVENT_CLEAR_FP" : "3473649843_929116286_1819092634_2690859019_2",
          "GROUP_CUSTOMER_LINE_LIST" : "[]",
          "ALARM_LEVEL" : 2,
          "NE_TAG" : {
            "MACHINE_ROOM_ADDRESS" : "福建省福州市马尾区马尾镇宗棠路18号凯隆橙仕公馆2号楼负一楼185号车位后面设备间",
            "HAS_FIXED_GENERATOR" : "0",
            "NE_ID" : "ACCUMULATOR-90046",
            "MANAGER_ROOM_ADMIN_ACCOUNT" : "jianghong",
            "BUILD_ID" : "STATION-NMS-0591-07267",
            "MANAGER_ROOM_ADMIN_TEL" : "13799327891",
            "ROOM_ID" : "DEVICEROOM-NMS-0591-08107",
            "PORT_ID" : "0500-002-007-10-007004",
            "IS_AGG_ROOM" : 1,
            "IS_CORE_ROOM" : 0,
            "MACHINE_ROOM_GRADE" : "汇聚（综合业务接入）",
            "MACHINE_ROOM_INFO" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房",
            "ROOM_DEPT" : "业主",
            "MANAGER_ROOM_ADMIN_NAME" : "江泓"
          },
          "EVENT_ROOT_CATEGORY_ID" : "5017",
          "SCENCE_NAME" : "11000,dh_non_power",
          "EVENT_STANDARD_NAME" : "动环电池组故障事件",
          "NE_LOCATION" : "无线设备：福州马尾-马尾快安名城五区西路-NLH-BBU01、福州马尾快安名郡一期-HHM-G-BBU01、福州马尾-马尾快安宗棠路边防大队-NLS-BBU-01...等，传输设备：18023-福州马尾凯隆橙仕公馆(BBU池)-HW-SPN、14-2014-福州-马尾-快安凯隆橙仕公馆2号楼负一楼-HW-HUB、22196-福州马尾凯隆橙仕公馆-ZX-PTN-1...等，家宽设备：FZMW凯隆橙仕公馆-OLT001-C650(下沉)",
          "EFFECT_CIRCUIT_LEVEL" : "",
          "MAINTAIN_TEAM_SOURCE" : "1",
          "CITY_ID" : "350100",
          "REMOTE_OBJECT_CLASS" : "",
          "ORIG_EVENT_EXT" : {
            "SRC_ID" : "GZEVENT0000001054460244",
            "SRC_APP_ID" : "1001",
            "ACTIVE_STATUS" : 1,
            "MAINTAIN_GROUP" : "福州马尾主城区网格虹信基站维护组2",
            "SRC_ORG_ID" : "3306118179_2013949611_3622437094_1593090642_2"
          },
          "MAIN_NET_SORT_THREE" : "铅酸电池",
          "CUSTOMER_SERVICE_LEVEL" : "",
          "CREATION_EVENT_TIME" : "2026-04-14 16:38:04",
          "FIRST_EVENT_TIME" : "2026-04-14 16:35:06",
          "SERV_EFFECT_TYPE" : "无",
          "ORDER_ID" : "FJ-076-20260414-4243",
          "IS_ORDER_DELAY_APPLY" : 0,
          "ORDER_STATUS" : 1,
          "ORDER_TIME" : "2026-04-14 16:50:09",
          "OPDER_STATUS" : 1,
          "FAULT_CARRY_TOOLS" : "高精度数字万用表、直流钳形电流表、电池内阻测试仪、绝缘螺丝刀与扳手套装、绝缘手套、点温枪等",
          "TODO_LIST_ID" : "DH2026041403424"
        }
      },
      {
        "_index" : "mw_em_master",
        "_type" : "_doc",
        "_id" : "330937006",
        "_score" : 1.0,
        "_source" : {
          "HOME_BROAD_BAND_LIST" : [ ],
          "FULL_REGION_ID" : "35000/350100/350105",
          "EVENT_LEVEL" : 4,
          "SEND_JT_FLAG" : 0,
          "ORG_TYPE" : 1,
          "EVENT_LOCATION" : "基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH",
          "TOPIC_PREFIX" : "EVENT-GZ",
          "DISPATCH_INFO" : {
            "T1_PROCESSING_TIME" : 120,
            "T1_CONFIRMATION_TIME" : 60,
            "START_TIME" : "00:00:00",
            "IS_CALCULATE_DURATION" : 0,
            "RULE_NAME" : "动环二级告警派单",
            "CONFIRMATION_TIME" : 60,
            "DISPATCH_TYPE" : 0,
            "INST_ID" : 280646,
            "DISPATCH_LEVEL" : 2,
            "PROCESS_STATE" : 4,
            "END_TIME" : "23:59:59",
            "T2_CONFIRMATION_TIME" : 60,
            "PROCESS_TYPE" : 1,
            "DISPATCH_NIGHT" : "0",
            "ORDER_STATUS" : 1,
            "IS_NEW_EFFECT_UPDATE" : 1,
            "DISPATCH_FLAG" : 0,
            "DISPATCH_REASON" : "同源合并成功",
            "TIME_RULE_NAME" : "电源和配套设备-机房动环",
            "DISPATCH_STATUS_ID" : "1011",
            "APPEND_DELAY_TIME" : 30,
            "RULE_ID" : 1195,
            "BUSINESS_EFFECT_RANGE_RATIO" : 30.0,
            "DISPATCH_LEVEL_RULE_NAME" : "电源和配套设备-机房动环",
            "T2_PROCESSING_TIME" : 720,
            "IS_BUSINESS_EFFECT_RANGE" : 1,
            "DISPATCH_LEVEL_RULE_ID" : 78,
            "DELAY_TIME" : 12,
            "PROCESSING_TIME" : 720,
            "SUPPRESS_TYPE" : 0,
            "JT_DISPATCH_STATUS_ID" : 10,
            "JT_DISPATCH_STATUS_DESC" : "追单派单成功",
            "TIME_RULE_ID" : 87,
            "IS_ROOT_EQP_LABEL_CHANGE" : 1,
            "ORDER_ID" : "FJ-076-20260414-4243",
            "ORDER_TYPE" : 2,
            "ORDER_TIME" : "2026-04-14 16:53:11"
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
          "RECOGNITION_RULE_NAME" : "动环电池组故障事件",
          "SITE_TYPE" : "109",
          "EVENT_NUM" : 1,
          "EVENT_TIME" : "2026-04-14 16:38:55",
          "IS_TEST" : 0,
          "DETAIL_STATUS" : 11,
          "PORT_NUM_CN" : "高兴新动力环境告警",
          "EVENT_REASON" : "定界结果：初判为电池故障导致；\n定位结论：基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH。",
          "VENDOR_ID" : 771,
          "REMOTE_EQUIPMENT_NAME" : "",
          "SRC_ORG_ALARM_TEXT" : """
<ALARMSTART>
SystemName:高新兴动环系统
Vendor_Name:1#南都电池组1000AH
Speciality:动环专业
AlarmID:273160692
IntID:9a08911b34ed4b749c5c1b847be90231
AlarmEquipment:基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH
EquipmentClass:
EventTime:2026-04-14 16:38:55
Vendor_Severity:三级告警
AlarmTitle:03#单体电压高于设定告警阈值
ActiveStatus:1
ProbableCause:
ProbableCauseTxt:福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房\1#南都电池组1000AH\03#单体电压高于设定告警阈值
MaintainPropose:007004,003,2.38
LocateInfo:基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH
ClearID:273160692
LocateName:基站>福州市>BBU池基站>马尾区
Version:
AckUser:
AckTerminal:
DispatchFlag:0
standard_alarm_id:0500-002-007-10-007004
IRMS_CUID:ACCUMULATOR-90046
<ALARMEND>
""",
          "ALARM_SOURCE" : "高兴新动力环境告警(旧)",
          "CITY_NAME" : "福州市",
          "EQUIPMENT_NAME" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1",
          "NETWORK_SUB_TYPE_ID" : "500",
          "EVENT_ID" : 330937006,
          "EVENT_TAG" : {
            "IS_MATCH_DISPATCH_RULES" : 1,
            "IS_MATCH_WARNING_RULES" : 0,
            "PREPROCESS_T1" : "否",
            "IS_MATCH_DANGER_RULES" : 0,
            "PREPROCESS_TIME" : 0
          },
          "CANCEL_STATUS" : 0,
          "DANGER_INFO" : {
            "PROCESS_TYPE" : 1,
            "DANGER_REASON" : "未匹配规则",
            "PROCESS_STATE" : 9,
            "ORDER_STATUS" : 0,
            "DISPATCH_STATUS_ID" : "1001"
          },
          "RECOGNITION_RULE_ID" : 1749,
          "FAULT_ROOT_CAUSE_SOURCE" : 1,
          "PROJ_INTERFERENCE_FLAG" : 0,
          "ORIG_ALARM_CLEAR_FP" : "1085072162_627711192_1595214085_337578075",
          "ROOT_NETWORK_TYPE_ID" : "5",
          "MARK_SMART_RULE_ID" : 29,
          "NETWORK_SUB_TYPE_NAME" : "动环",
          "ALARM_STANDARD_FLAG" : 2,
          "ALARM_STANDARD_NAME" : "单体XX电压过高告警",
          "EQP_OBJECT_ID" : "30008",
          "MAINTAIN_TEAM" : "福州马尾主城区网格虹信基站维护组2",
          "EVENT_ROOT_CATEGORY" : "蓄电池故障",
          "EVENT_SOURCE" : 2,
          "EVENT_STATUS" : 0,
          "KEY_CELL" : "0",
          "TYPE_KEYCODE" : "关联到资源,",
          "NE_LABEL" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1",
          "EVENT_EXPLANATION" : "一、告警解释：蓄电池单只电池电压高于保护阀值。二、可能原因：1、电池组充电电压过高。",
          "ALARM_RESOURCE_STATUS" : "1",
          "SERVICE_ASSURANCE_LEVEL" : "",
          "MARK_SMART_RULE_NAME" : "动环-非停电智能调度场景",
          "BUSINESS_TAG" : {
            "CIRCUIT_NO" : "007004,003,2.38",
            "ADMIN_GRID_ID" : "",
            "IRMS_GRID_NAME" : "",
            "BUSINESS_SYSTEM" : "高兴新动力环境告警(旧)",
            "PRODUCT_TYPE" : "",
            "HOME_CLIENT_NUM" : "",
            "BUSINESS_TYPE" : "",
            "CIRCUIT_LEVEL" : ""
          },
          "NMS_ALARM_ID" : "273160692",
          "SUPPRESS_NIGHT" : "1",
          "EXCEPTION_SUPPRESS_DISPATCH" : 0,
          "EVENT_NAME" : "动环电池组故障事件-单体XX电压过高告警",
          "FAULT_DISPOSAL_METHOD" : "现场人工处置,现场更换设备",
          "EQUIPMENT_IP" : "",
          "FAULT_LOCATION" : "基站_福州市_BBU池基站_马尾区_1#南都电池组1000AH",
          "EVENT_COLLECTION_TIME" : "2026-04-14 16:41:02",
          "TOPIC_PARTITION" : 45,
          "SPECIFIC_PROBLEMS" : "26ef6bdaa672e3ff5ca8358f2e796225",
          "FULL_REGION_NAME" : "福建省/福州市/马尾区",
          "TRIGGER_NE_LATITUDE" : "26.02462",
          "EXTRA_STRING1" : "",
          "IS_EFFECT_BUSINESS" : "否",
          "EVENT_CAT" : "",
          "ALARM_UNIQUE_ID" : "",
          "ALARM_NAME" : "单体XX电压过高告警",
          "VENDOR_NAME" : "高新兴",
          "RECOGNITION_STANDARD_ID" : "WLSJ-WL-DH-04-80-0052",
          "5G_CUSTOMER_LIST" : [ ],
          "MAIN_NET_SORT_ONE" : "电源和配套设备",
          "EVENT_TYPE_ID" : "网络类",
          "EVENT_STANDARD_FLAG" : 2,
          "VENDOR_EVENT_TYPE" : "1",
          "ALARM_REASON" : "",
          "OBJECT_CLASS_ID" : 30008,
          "COUNTY_ID" : "350105",
          "PORT_NUM" : "300103",
          "EVENT_LEVEL_NAME" : "四级事件",
          "FIX_TIMEOUT_LIMIT" : 30,
          "ALARM_LEVEL_NAME" : "二级告警",
          "EVENT_EFFECT" : """
网络影响：福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房-铅酸电池-1；
机房下挂业务设备：无线设备：福州马尾-马尾快安名城五区西路-NLH-BBU01、福州马尾快安名郡一期-HHM-G-BBU01、福州马尾-马尾快安宗棠路边防大队-NLS-BBU-01...等，传输设备：18023-福州马尾凯隆橙仕公馆(BBU池)-HW-SPN、14-2014-福州-马尾-快安凯隆橙仕公馆2号楼负一楼-HW-HUB、22196-福州马尾凯隆橙仕公馆-ZX-PTN-1...等，家宽设备：FZMW凯隆橙仕公馆-OLT001-C650(下沉)
社会影响：暂无投诉。
""",
          "FAULT_CAUSE_CATEGORY2" : "蓄电池故障",
          "FAULT_CAUSE_CATEGORY1" : "设备故障",
          "EVENT_FP" : "2565245712_975644329_2247930178_2286092356_2",
          "SERVICE_EFFECT_STATUS" : "无影响",
          "EVENT_ARRIVAL_TIME" : "2026-04-14 16:41:04",
          "FAULT_DIAGNOSIS" : "【故障原因初判】由于停电/电池单体故障导致\n【故障处理建议】请尽快核实具体原因，尽快上站处理。",
          "PROJ_INTERFERENCE_TYPE" : "【是否干扰告警】：否。",
          "FAULT_TYPE_ID" : "设备",
          "TMSC_CAT" : "",
          "GZ_EVENT_STATUS" : 1,
          "EVENT_PROVINCE_LEVEL" : "2",
          "NETWORK_TYPE_ID" : "5",
          "NE_ADMIN_STATUS" : "",
          "NETWORK_TYPE_NAME" : "动环",
          "NMS_NAME" : "高新兴动环系统",
          "TRIGGER_COORDINATE_TYPE" : "1",
          "FAULT_SUB_TYPE_ID" : "电源开关设备类",
          "FAULT_DISPOSAL_PLAN" : "处置机房电池组故障",
          "PROVINCE_NAME" : "福建省",
          "EVENT_PROBABLE_CAUSE_TXT" : "0",
          "ALARM_STANDARD_ID" : "0500-009-007-10-000022",
          "OBJECT_CLASS_TEXT" : "铅酸电池",
          "EXTRA_ID2" : "",
          "INTELLIGENT" : 1,
          "MAIN_NET_SORT_TWO" : "机房动环",
          "TRIGGER_NE_LONGITUDE" : "119.39477",
          "ORIG_ALARM_FP" : "2565245712_975644329_2247930178_2286092356",
          "SATOTAL" : 1,
          "COUNTY_NAME" : "马尾区",
          "EVENT_STANDARD_ID" : "WLSJ-WL-DH-04-80-0052",
          "EFFECT_NE_NUM" : 0,
          "ROOT_NETWORK_TYPE_TOP" : "动环",
          "LAST_EVENT_TIME" : "2026-04-14 16:38:55",
          "EVENT_EXPLANATION_ADDITION" : "传输节点",
          "VENDOR_SEVERITY" : "二级告警",
          "INTERFERENCE_FLAG" : "0",
          "FAULT_KEEPALIVE_STATUS" : "否",
          "EQP_OBJECT_NAME" : "铅酸电池",
          "OLD_EVENT_NAME" : "动环电池组故障事件-单体XX电压过高告警",
          "FAULT_PROCESS_STATUS" : "正常",
          "EVENT_SUMMARY" : "1、核查是否工程操作；2、核查是否有动环监控设备通信异常告警；3.核实是否动环监控电池电压值门限异常；4、若以上条件均不满足，判断为电池故障导致。",
          "PROVINCE_ID" : "35000",
          "EVENT_CLEAR_FP" : "1085072162_627711192_1595214085_337578075_2",
          "GROUP_CUSTOMER_LINE_LIST" : "[]",
          "ALARM_LEVEL" : 2,
          "NE_TAG" : {
            "MACHINE_ROOM_ADDRESS" : "福建省福州市马尾区马尾镇宗棠路18号凯隆橙仕公馆2号楼负一楼185号车位后面设备间",
            "HAS_FIXED_GENERATOR" : "0",
            "NE_ID" : "ACCUMULATOR-90046",
            "MANAGER_ROOM_ADMIN_ACCOUNT" : "jianghong",
            "BUILD_ID" : "STATION-NMS-0591-07267",
            "MANAGER_ROOM_ADMIN_TEL" : "13799327891",
            "ROOM_ID" : "DEVICEROOM-NMS-0591-08107",
            "PORT_ID" : "0500-002-007-10-007004",
            "IS_AGG_ROOM" : 1,
            "IS_CORE_ROOM" : 0,
            "MACHINE_ROOM_GRADE" : "汇聚（综合业务接入）",
            "MACHINE_ROOM_INFO" : "福州马尾快安凯隆橙仕公馆2号楼负一楼185号车位后面设备间机房",
            "ROOM_DEPT" : "业主",
            "MANAGER_ROOM_ADMIN_NAME" : "江泓"
          },
          "EVENT_ROOT_CATEGORY_ID" : "5017",
          "SCENCE_NAME" : "11000,dh_non_power",
          "EVENT_STANDARD_NAME" : "动环电池组故障事件",
          "NE_LOCATION" : "无线设备：福州马尾-马尾快安名城五区西路-NLH-BBU01、福州马尾快安名郡一期-HHM-G-BBU01、福州马尾-马尾快安宗棠路边防大队-NLS-BBU-01...等，传输设备：18023-福州马尾凯隆橙仕公馆(BBU池)-HW-SPN、14-2014-福州-马尾-快安凯隆橙仕公馆2号楼负一楼-HW-HUB、22196-福州马尾凯隆橙仕公馆-ZX-PTN-1...等，家宽设备：FZMW凯隆橙仕公馆-OLT001-C650(下沉)",
          "EFFECT_CIRCUIT_LEVEL" : "",
          "MAINTAIN_TEAM_SOURCE" : "1",
          "CITY_ID" : "350100",
          "ORIG_EVENT_EXT" : {
            "SRC_ID" : "GZEVENT0000001054465342",
            "SRC_APP_ID" : "1001",
            "ACTIVE_STATUS" : 1,
            "MAINTAIN_GROUP" : "福州马尾主城区网格虹信基站维护组2",
            "SRC_ORG_ID" : "2565245712_975644329_2247930178_2286092356_2"
          },
          "REMOTE_OBJECT_CLASS" : "",
          "MAIN_NET_SORT_THREE" : "铅酸电池",
          "CUSTOMER_SERVICE_LEVEL" : "",
          "CREATION_EVENT_TIME" : "2026-04-14 16:41:04",
          "FIRST_EVENT_TIME" : "2026-04-14 16:38:55",
          "SERV_EFFECT_TYPE" : "无",
          "ORDER_ID" : "FJ-076-20260414-4243",
          "IS_ORDER_DELAY_APPLY" : 0,
          "ORDER_STATUS" : 1,
          "ORDER_TIME" : "2026-04-14 16:53:11",
          "OPDER_STATUS" : 1
        }
      }
    ]
  }
}

## 需求
1. 根据ES查询的结果，提取es查询结果中的：EVENT_FP
2. 根据event_fp进行去重，统计不同event_fp的数量,生成推送消息，按上面的es数据中是3个event_fp所以是生成3条数据，格式如下：
{"ACTIVE_STATUS":"3","CFP0_CFP1_CFP2_CFP3":"1821276491_2998015541_1819582473_803382798_2","EVENT_TIME":"2026-04-14 17:16:55","FP0_FP1_FP2_FP3":"1821276491_2998015541_1819582473_803382798_2"}
{"ACTIVE_STATUS":"3","CFP0_CFP1_CFP2_CFP3":"2565245712_975644329_2247930178_2286092356_2","EVENT_TIME":"2026-04-14 17:16:55","FP0_FP1_FP2_FP3":"2565245712_975644329_2247930178_2286092356_2"}
{"ACTIVE_STATUS":"3","CFP0_CFP1_CFP2_CFP3":"3306118179_2013949611_3622437094_1593090642_2","EVENT_TIME":"2026-04-14 17:16:55","FP0_FP1_FP2_FP3":"3306118179_2013949611_3622437094_1593090642_2"}
3.提供复制的功能

