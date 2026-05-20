-- 为 kafka_field_cache 表添加 is_fixed 字段
-- 执行时间: 2026-05-20

USE knowledge_base;

-- 检查字段是否已存在
SET @column_exists = (
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'knowledge_base' 
    AND TABLE_NAME = 'kafka_field_cache' 
    AND COLUMN_NAME = 'is_fixed'
);

-- 如果字段不存在，则添加
SET @sql = IF(@column_exists = 0,
    'ALTER TABLE knowledge_base.kafka_field_cache ADD COLUMN is_fixed TINYINT(1) DEFAULT 0 COMMENT "是否固定字段" AFTER is_pinned',
    'SELECT "Column is_fixed already exists" AS message'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 验证字段已添加
SELECT COLUMN_NAME, COLUMN_TYPE, COLUMN_DEFAULT, COLUMN_COMMENT 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'knowledge_base' 
AND TABLE_NAME = 'kafka_field_cache' 
AND COLUMN_NAME IN ('is_pinned', 'is_fixed');
