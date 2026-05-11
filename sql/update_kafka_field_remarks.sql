-- ============================================================
-- Kafka 字段备注更新 SQL
-- 更新日期: 2026-05-11
-- 数据库: schedule
-- 表: kafka_field_meta
-- ============================================================

USE schedule;

-- 更新字段备注信息
UPDATE kafka_field_meta SET 
    db_cn = '事件来源',
    remark = '固定为20，表示来源于传输工作台'
WHERE kafka_field = 'EVENT_SOURCE';

UPDATE kafka_field_meta SET 
    db_cn = '消息类型',
    remark = '固定为1表示新增'
WHERE kafka_field = 'ACTIVE_STATUS';

UPDATE kafka_field_meta SET 
    db_cn = '一级专业分类',
    remark = '固定为4表示传输专业'
WHERE kafka_field = 'NETWORK_TYPE_TOP';

UPDATE kafka_field_meta SET 
    db_cn = '网管告警级别',
    remark = '敷设段光缆中断事件默认：2，表示二级事件'
WHERE kafka_field = 'ORG_SEVERITY';

UPDATE kafka_field_meta SET 
    db_cn = '地市ID',
    remark = '需按标准字典'
WHERE kafka_field = 'REGION_ID';

UPDATE kafka_field_meta SET 
    db_cn = '地市',
    remark = '敷设段所在地市，双端情况下（PROV_BACKBONE_ONLY=0），A端地市需和敷设段所在地市一致'
WHERE kafka_field = 'REGION_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '县市ID',
    remark = '需按标准字典'
WHERE kafka_field = 'CITY_ID';

UPDATE kafka_field_meta SET 
    db_cn = '区县',
    remark = '敷设段所在区县，双端情况下（PROV_BACKBONE_ONLY=0），A端区县需和敷设段所在地市一致'
WHERE kafka_field = 'CITY_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '网元名称',
    remark = '敷设段名称'
WHERE kafka_field = 'EQP_LABEL';

UPDATE kafka_field_meta SET 
    db_cn = '设备类型（ID）',
    remark = '敷设段类型ID，需要统一规范，在亿阳设备类型枚举基础上进行增加'
WHERE kafka_field = 'EQP_OBJECT_CLASS';

UPDATE kafka_field_meta SET 
    db_cn = '设备类型',
    remark = '敷设段类型'
WHERE kafka_field = 'EQP_OBJECT_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '定位信息',
    remark = '敷设段定位信息'
WHERE kafka_field = 'LOCATE_INFO';

UPDATE kafka_field_meta SET 
    db_cn = '敷设段中心经度',
    remark = NULL
WHERE kafka_field = 'LAY_SECTION_CENTER_LON';

UPDATE kafka_field_meta SET 
    db_cn = '敷设段中心纬度',
    remark = NULL
WHERE kafka_field = 'LAY_SECTION_CENTER_LAT';

UPDATE kafka_field_meta SET 
    db_cn = '事件标题',
    remark = '地市+区县+事件标准化名称'
WHERE kafka_field = 'TITLE_TEXT';

UPDATE kafka_field_meta SET 
    db_cn = '事件标准化名称',
    remark = '固定为：传输外线光缆中断事件'
WHERE kafka_field = 'STANDARD_ALARM_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '事件标准化ID',
    remark = '固定为：WLSJ-WL-CS-02-80-9001'
WHERE kafka_field = 'STANDARD_ALARM_ID';

UPDATE kafka_field_meta SET 
    db_cn = '事件发生时间',
    remark = NULL
WHERE kafka_field = 'EVENT_TIME';

UPDATE kafka_field_meta SET 
    db_cn = '事件清除时间',
    remark = NULL
WHERE kafka_field = 'CANCEL_TIME';

UPDATE kafka_field_meta SET 
    db_cn = '事件指纹fp',
    remark = '唯一流水号，不与亿阳的重复'
WHERE kafka_field = 'FP0_FP1_FP2_FP3';

UPDATE kafka_field_meta SET 
    db_cn = '清除事件指纹fp',
    remark = '用于清除对应，可以和流水号一致'
WHERE kafka_field = 'CFP0_CFP1_CFP2_CFP3';

UPDATE kafka_field_meta SET 
    db_cn = '厂家流水号',
    remark = '默认于事件指纹fp相同'
WHERE kafka_field = 'NMS_ALARM_ID';

UPDATE kafka_field_meta SET 
    db_cn = '对端地市ID',
    remark = '需按标准字典'
WHERE kafka_field = 'REMOTE_REGION_ID';

UPDATE kafka_field_meta SET 
    db_cn = '对端地市名称',
    remark = 'Z端地市名称'
WHERE kafka_field = 'REMOTE_REGION_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '对端区县ID',
    remark = '需按标准字典'
WHERE kafka_field = 'REMOTE_CITY_ID';

UPDATE kafka_field_meta SET 
    db_cn = '对端区县名称',
    remark = 'Z端区县名称'
WHERE kafka_field = 'REMOTE_CITY_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '业务层级',
    remark = '敷设段层级：按光缆级别就高，枚举值，见亿阳定义，需确认是否增加'
WHERE kafka_field = 'BUSINESS_LAYER';

UPDATE kafka_field_meta SET 
    db_cn = '业务层级名称',
    remark = '敷设段层级名称，需与BUSINESS_LAYER对应'
WHERE kafka_field = 'BUSINESS_LAYER_CN';

UPDATE kafka_field_meta SET 
    db_cn = '是否仅包含省干、骨干',
    remark = '枚举值 0：否，1：是 根据关联告警的业务层级（本端对端网元级别就低），OLT上联为汇聚，PON告警为接入'
WHERE kafka_field = 'PROV_BACKBONE_ONLY';

UPDATE kafka_field_meta SET 
    db_cn = '是否高速高铁',
    remark = '枚举值 0：否，1：是 默认：否'
WHERE kafka_field = 'IS_EFFECT_HIGHSPEED';

UPDATE kafka_field_meta SET 
    db_cn = '是否EOTDR',
    remark = '枚举值 0：否，1：是'
WHERE kafka_field = 'IS_EOTDR';

UPDATE kafka_field_meta SET 
    db_cn = '物理断点经度',
    remark = '断点位置经度（EOTDR结果）'
WHERE kafka_field = 'POS_REAL_LONGITUDE';

UPDATE kafka_field_meta SET 
    db_cn = '物理断点纬度',
    remark = '断点位置纬度（EOTDR结果）'
WHERE kafka_field = 'POS_REAL_LATITUDE';

UPDATE kafka_field_meta SET 
    db_cn = '物理断点所在地市ID',
    remark = '需按标准字典'
WHERE kafka_field = 'POS_REAL_REGION_ID';

UPDATE kafka_field_meta SET 
    db_cn = '物理断点所在地市',
    remark = 'EOTDR断点所在地市'
WHERE kafka_field = 'POS_REAL_REGION_NAME';

UPDATE kafka_field_meta SET 
    db_cn = '物理断点所在区县ID',
    remark = '需按标准字典'
WHERE kafka_field = 'POS_REAL_CITY_ID';

UPDATE kafka_field_meta SET 
    db_cn = '物理断点所在区县',
    remark = 'EOTDR断点所在区县'
WHERE kafka_field = 'POS_REAL_CITY_NAME';

UPDATE kafka_field_meta SET 
    db_cn = 'EOTDR估测结果明细',
    remark = NULL
WHERE kafka_field = 'POS_REAL_DESC';

UPDATE kafka_field_meta SET 
    db_cn = '是否具备调纤方案',
    remark = '枚举值 0：否，1：是 默认：否'
WHERE kafka_field = 'HAS_FIBER_ADJUST_PLAN';

UPDATE kafka_field_meta SET 
    db_cn = '是否优先进行调纤',
    remark = '枚举值 0：否，1：是 默认：否'
WHERE kafka_field = 'IS_FIBER_ADJUST_FIRST';

-- 验证更新结果
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
