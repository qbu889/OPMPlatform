-- 调整因子管理数据库表初始化脚本
-- 在 MySQL 数据库中执行此脚本

USE knowledge_base;

-- 1. 创建调整因子主表
CREATE TABLE IF NOT EXISTS fpa_adjustment_factor (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增 ID',
    factor_name VARCHAR(255) NOT NULL COMMENT '因子名称',
    factor_category VARCHAR(100) COMMENT '因子分类（如：应用类型、质量特性等）',
    option_name TEXT COMMENT '选项名称',
    score_value DECIMAL(5,2) COMMENT '分值',
    formula TEXT COMMENT '计算公式',
    display_order INT DEFAULT 0 COMMENT '显示顺序',
    parent_id INT DEFAULT NULL COMMENT '父级 ID（用于层级关系）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_category (factor_category),
    INDEX idx_parent (parent_id),
    INDEX idx_order (display_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='FPA 调整因子表';

-- 2. 创建调整因子配置表（存储整体配置）
CREATE TABLE IF NOT EXISTS fpa_adjustment_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增 ID',
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(50) COMMENT '配置类型（scale_timing: 规模计数时机，application_type: 应用类型等）',
    description VARCHAR(500) COMMENT '配置描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_key (config_key),
    INDEX idx_type (config_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='FPA 调整因子配置表';

-- 3. 插入默认配置数据
INSERT INTO fpa_adjustment_config (config_key, config_value, config_type, description)
VALUES 
    ('scale_timing', '估算中期', 'scale_timing', '规模计数时机'),
    ('application_type_default', '业务处理', 'application_type', '默认应用类型')
ON DUPLICATE KEY UPDATE 
    config_value = VALUES(config_value),
    config_type = VALUES(config_type),
    description = VALUES(description),
    updated_at = CURRENT_TIMESTAMP;

-- 4. 验证表创建成功
SHOW TABLES LIKE 'fpa_adjustment_%';

-- 5. 查看表结构
DESCRIBE fpa_adjustment_factor;
DESCRIBE fpa_adjustment_config;
