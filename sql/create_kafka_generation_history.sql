-- Kafka 生成历史记录表
CREATE TABLE IF NOT EXISTS `knowledge_base`.`kafka_generation_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键 ID',
  `es_source_raw` LONGTEXT COMMENT '原始 ES 数据',
  `kafka_message` LONGTEXT COMMENT '生成的 Kafka 消息',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `created_by` VARCHAR(100) DEFAULT 'system' COMMENT '创建者',
  `fp_value` VARCHAR(200) COMMENT 'FP 值 (用于快速检索)',
  `alarm_name` VARCHAR(500) COMMENT '告警名称',
  `alarm_level` VARCHAR(50) COMMENT '告警级别',
  `region_name` VARCHAR(200) COMMENT '地区名称'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Kafka 生成历史记录表';

-- 创建索引提高查询性能
CREATE INDEX `idx_created_at` ON `knowledge_base`.`kafka_generation_history` (`created_at`);
CREATE INDEX `idx_fp_value` ON `knowledge_base`.`kafka_generation_history` (`fp_value`);
CREATE INDEX `idx_alarm_name` ON `knowledge_base`.`kafka_generation_history` (`alarm_name`);
