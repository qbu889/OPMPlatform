-- ============================================================
-- Kafka 字段补充插入 SQL
-- 更新日期: 2026-05-11
-- 数据库: schedule
-- 表: kafka_field_meta
-- ============================================================

USE schedule;

-- 检查并插入缺失的字段
INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'EVENT_SOURCE', '事件来源', '', '', '固定为20，表示来源于传输工作台'
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'EVENT_SOURCE');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'REGION_ID', '地市ID', '', '', '需按标准字典'
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'REGION_ID');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'LAY_SECTION_CENTER_LON', '敷设段中心经度', '', '', NULL
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'LAY_SECTION_CENTER_LON');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'LAY_SECTION_CENTER_LAT', '敷设段中心纬度', '', '', NULL
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'LAY_SECTION_CENTER_LAT');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'POS_REAL_LONGITUDE', '物理断点经度', '', '', '断点位置经度（EOTDR结果）'
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'POS_REAL_LONGITUDE');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'POS_REAL_LATITUDE', '物理断点纬度', '', '', '断点位置纬度（EOTDR结果）'
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'POS_REAL_LATITUDE');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'POS_REAL_REGION_ID', '物理断点所在地市ID', '', '', '需按标准字典'
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'POS_REAL_REGION_ID');

INSERT INTO kafka_field_meta (kafka_field, db_cn, es_field, label_cn, remark) 
SELECT 'POS_REAL_CITY_ID', '物理断点所在区县ID', '', '', '需按标准字典'
WHERE NOT EXISTS (SELECT 1 FROM kafka_field_meta WHERE kafka_field = 'POS_REAL_CITY_ID');

-- 验证结果
SELECT 
    kafka_field AS '字段名称',
    db_cn AS '中文解释',
    remark AS '备注'
FROM kafka_field_meta 
WHERE kafka_field IN (
    'EVENT_SOURCE', 'ACTIVE_STATUS', 'NETWORK_TYPE_TOP', 'ORG_SEVERITY',
    'REGION_ID', 'REGION_NAME', 'CITY_ID', 'CITY_NAME', 'EQP_LABEL',
    'EQP_OBJECT_CLASS', 'EQP_OBJECT_NAME', 'LOCATE_INFO', 
    'LAY_SECTION_CENTER_LON', 'LAY_SECTION_CENTER_LAT', 'TITLE_TEXT',
    'STANDARD_ALARM_NAME', 'STANDARD_ALARM_ID', 'EVENT_TIME', 'CANCEL_TIME',
    'FP0_FP1_FP2_FP3', 'CFP0_CFP1_CFP2_CFP3', 'NMS_ALARM_ID',
    'REMOTE_REGION_ID', 'REMOTE_REGION_NAME', 'REMOTE_CITY_ID', 'REMOTE_CITY_NAME',
    'BUSINESS_LAYER', 'BUSINESS_LAYER_CN', 'PROV_BACKBONE_ONLY',
    'IS_EFFECT_HIGHSPEED', 'IS_EOTDR', 'POS_REAL_LONGITUDE', 'POS_REAL_LATITUDE',
    'POS_REAL_REGION_ID', 'POS_REAL_REGION_NAME', 'POS_REAL_CITY_ID', 'POS_REAL_CITY_NAME',
    'POS_REAL_DESC', 'HAS_FIBER_ADJUST_PLAN', 'IS_FIBER_ADJUST_FIRST'
)
ORDER BY id;
