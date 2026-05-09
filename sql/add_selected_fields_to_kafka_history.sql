-- 为 kafka_generation_history 表添加 selected_fields 字段
-- 用于存储生成 Kafka 消息时用户选中的字段列表

ALTER TABLE `knowledge_base`.`kafka_generation_history` 
ADD COLUMN `selected_fields` LONGTEXT COMMENT '用户选中的字段列表 (JSON 数组格式)' 
AFTER `custom_fields`;
