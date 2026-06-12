-- ============================================================================
-- Kafka 字段通用字典表 - 仅创建表结构
-- 用途：统一管理所有 Kafka 字段的选项值
-- ============================================================================

USE schedule;

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

-- 添加一些示例数据
INSERT INTO kafka_field_dict (kafka_field, dict_key, dict_value, sort_order, is_enabled, remark) VALUES
('NETWORK_TYPE_TOP', '1', '核心层', 1, 1, '骨干网络'),
('NETWORK_TYPE_TOP', '2', '汇聚层', 2, 1, '区域汇聚'),
('NETWORK_TYPE_TOP', '3', '接入层', 3, 1, '用户接入'),
('EFFECT_NE', '1', '影响网元', 1, 1, '直接影响'),
('EFFECT_NE', '2', '不影响网元', 2, 1, '间接影响'),
('EFFECT_SERVICE', '1', '影响业务', 1, 1, '业务中断'),
('EFFECT_SERVICE', '2', '不影响业务', 2, 1, '业务正常')
ON DUPLICATE KEY UPDATE dict_value = VALUES(dict_value);

SELECT 'kafka_field_dict 表创建成功' AS status;
SELECT COUNT(*) AS total_records FROM kafka_field_dict;
