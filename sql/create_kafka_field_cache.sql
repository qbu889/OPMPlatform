-- Kafka 生成器字段缓存表
CREATE TABLE IF NOT EXISTS `knowledge_base`.`kafka_field_cache` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `field_name` VARCHAR(100) NOT NULL UNIQUE COMMENT '字段名称',
  `field_value` TEXT COMMENT '字段值',
  `is_pinned` TINYINT(1) DEFAULT 0 COMMENT '是否置顶',
  `history_values` JSON COMMENT '历史值列表 (JSON 数组)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Kafka 生成器字段缓存表';

-- 创建索引提高查询性能
CREATE INDEX `idx_field_name` ON `knowledge_base`.`kafka_field_cache` (`field_name`);
CREATE INDEX `idx_is_pinned` ON `knowledge_base`.`kafka_field_cache` (`is_pinned`);
