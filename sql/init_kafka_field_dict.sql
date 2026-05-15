-- ============================================================================
-- Kafka 字段通用字典表
-- 用途：统一管理所有 Kafka 字段的选项值，替代原来的多个独立维表
-- 优势：
--   1. 可扩展性强：新增字段无需创建新表
--   2. 结构统一：所有字段使用相同的字典结构
--   3. 易于管理：通过 API 即可增删改查
-- ============================================================================

CREATE TABLE IF NOT EXISTS kafka_field_dict (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    kafka_field VARCHAR(100) NOT NULL COMMENT 'Kafka字段名（大写）',
    dict_key VARCHAR(200) NOT NULL COMMENT '字典键值',
    dict_value VARCHAR(500) NOT NULL COMMENT '字典显示值',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用（0:禁用, 1:启用）',
    remark TEXT COMMENT '备注说明',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 联合索引，加速查询
    INDEX idx_field_enabled (kafka_field, is_enabled),
    INDEX idx_field_sort (kafka_field, sort_order),
    UNIQUE KEY uk_field_key (kafka_field, dict_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Kafka字段通用字典表';

-- ============================================================================
-- 迁移现有数据到通用字典表（从旧的维表迁移）
-- ============================================================================

-- 示例：从 network_type_top 表迁移数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled)
SELECT 
    'NETWORK_TYPE_TOP' as kafka_field,
    id as dict_key,
    name as dict_value,
    CAST(id AS UNSIGNED) as sort_order,
    1 as is_enabled
FROM network_type_top
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

-- 示例：从 effect_ne 表迁移数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled)
SELECT 
    'EFFECT_NE' as kafka_field,
    id as dict_key,
    name as dict_value,
    CAST(id AS UNSIGNED) as sort_order,
    1 as is_enabled
FROM effect_ne
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

-- 示例：从 effect_service 表迁移数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled)
SELECT 
    'EFFECT_SERVICE' as kafka_field,
    id as dict_key,
    name as dict_value,
    CAST(id AS UNSIGNED) as sort_order,
    1 as is_enabled
FROM effect_service
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

-- ============================================================================
-- 手动添加示例数据（如果旧表不存在或为空）
-- ============================================================================

-- NETWORK_TYPE_TOP 示例数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled, remark) VALUES
('NETWORK_TYPE_TOP', '1', '核心层', 1, 1, '骨干网络'),
('NETWORK_TYPE_TOP', '2', '汇聚层', 2, 1, '区域汇聚'),
('NETWORK_TYPE_TOP', '3', '接入层', 3, 1, '用户接入')
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

-- EFFECT_NE 示例数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled, remark) VALUES
('EFFECT_NE', '1', '影响网元', 1, 1, '直接影响'),
('EFFECT_NE', '2', '不影响网元', 2, 1, '间接影响')
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

-- EFFECT_SERVICE 示例数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled, remark) VALUES
('EFFECT_SERVICE', '1', '影响业务', 1, 1, '业务中断'),
('EFFECT_SERVICE', '2', '不影响业务', 2, 1, '业务正常')
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

-- ============================================================================
-- 验证数据
-- ============================================================================

-- 查看所有字段的字典数量
SELECT 
    kafka_field,
    COUNT(*) as dict_count,
    SUM(is_enabled) as enabled_count
FROM kafka_field_dict
GROUP BY kafka_field
ORDER BY kafka_field;

-- 查看某个字段的所有字典项
SELECT * FROM kafka_field_dict 
WHERE kafka_field = 'NETWORK_TYPE_TOP' AND is_enabled = 1
ORDER BY sort_order ASC;
