#!/usr/bin/env python3
import json
import sys

# 右侧数据（数据2.json）
right_data = {
  "EVENT_SOURCE": "20",
  "ACTIVE_STATUS": "1",
  "NETWORK_TYPE_TOP": "4",
  "ORG_SEVERITY": "2",
  "REGION_ID": "350500",
  "REGION_NAME": "泉州市",
  "CITY_ID": "350503",
  "CITY_NAME": "丰泽区",
  "EQP_LABEL": "泉州市丰泽区鸣翠园005号井-泉州市丰泽区鸣翠园004号井管道段",
  "EQP_OBJECT_CLASS": "1100005",
  "EQP_OBJECT_NAME": "管道段",
  "LOCATE_INFO": "长度:17米;坐标:LINESTRING(118.619059342156 24.8955970985265,118.61892728207 24.8956934666972)",
  "LAY_SECTION_CENTER_LON": "118.618993312113",
  "LAY_SECTION_CENTER_LAT": "24.89564528261185",
  "TITLE_TEXT": "【高速高铁】泉州市丰泽区传输外线光缆中断事件",
  "STANDARD_ALARM_NAME": "传输外线光缆中断事件",
  "STANDARD_ALARM_ID": "WLSJ-WL-CS-02-80-9001",
  "CANCEL_TIME": "",
  "FP0_FP1_FP2_FP3": "135201000000001729274198_029",
  "CFP0_CFP1_CFP2_CFP3": "135201000000001729274198_029",
  "NMS_ALARM_ID": "578844411",
  "REMOTE_REGION_ID": "350500",
  "REMOTE_REGION_NAME": "泉州市",
  "REMOTE_CITY_ID": "350503",
  "REMOTE_CITY_NAME": "丰泽区",
  "BUSINESS_LAYER": "1005",
  "BUSINESS_LAYER_CN": "本地接入",
  "PROV_BACKBONE_ONLY": "0",
  "IS_EOTDR": "0",
  "REDEFINE_SEVERITY" : "2",
  "POS_REAL_LONGITUDE": "",
  "POS_REAL_LATITUDE": "",
  "POS_REAL_REGION_ID": "",
  "POS_REAL_REGION_NAME": "",
  "POS_REAL_CITY_ID": "",
  "POS_REAL_CITY_NAME": "",
  "POS_REAL_DESC": "",
  "HAS_FIBER_ADJUST_PLAN": "0",
  "IS_FIBER_ADJUST_FIRST": "0",
  "MAINTAIN_GROUP": "泉州丰泽嘉环公司传输线路维护组1",
  "ASSIGN_TENANCE_GROUP": "泉州丰泽嘉环公司传输线路维护组1",
  "FIBER_ADJUST_LABEL": "高速高铁",
  "CREATION_EVENT_TIME": "2026-05-13 09:50:12",
  "EVENT_TIME": "2026-05-13 09:50:12"
}

# 左侧数据（简化版，只包含部分字段用于测试）
left_data = {
  "ASSIGN_TENANCE_GROUP": "泉州丰泽嘉环公司传输线路维护组1",
  "FIBER_ADJUST_LABEL": "",
  "CANCEL_TIME": "2026-05-11 16:59:19",
  "CREATION_EVENT_TIME": "2026-05-13 17:15:19",
  "EVENT_TIME": "2026-05-13 17:15:19"
}

print("=== 测试对比结果 ===")
print(f"\n右侧 ASSIGN_TENANCE_GROUP: {repr(right_data.get('ASSIGN_TENANCE_GROUP'))}")
print(f"左侧 ASSIGN_TENANCE_GROUP: {repr(left_data.get('ASSIGN_TENANCE_GROUP'))}")
print(f"是否相同: {right_data.get('ASSIGN_TENANCE_GROUP') == left_data.get('ASSIGN_TENANCE_GROUP')}")

print(f"\n右侧 FIBER_ADJUST_LABEL: {repr(right_data.get('FIBER_ADJUST_LABEL'))}")
print(f"左侧 FIBER_ADJUST_LABEL: {repr(left_data.get('FIBER_ADJUST_LABEL'))}")
print(f"是否相同: {right_data.get('FIBER_ADJUST_LABEL') == left_data.get('FIBER_ADJUST_LABEL')}")

print(f"\n右侧 CANCEL_TIME: {repr(right_data.get('CANCEL_TIME'))}")
print(f"左侧 CANCEL_TIME: {repr(left_data.get('CANCEL_TIME'))}")
print(f"是否相同: {right_data.get('CANCEL_TIME') == left_data.get('CANCEL_TIME')}")
