-- 为 kafka_generation_history 表添加 custom_fields 字段
-- 用于存储生成 Kafka 消息时的自定义字段数据

ALTER TABLE `knowledge_base`.`kafka_generation_history` 
ADD COLUMN `custom_fields` LONGTEXT COMMENT '自定义字段数据 (JSON 格式)' 
AFTER `region_name`;
