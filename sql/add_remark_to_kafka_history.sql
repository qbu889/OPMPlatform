-- 为 kafka_generation_history 表添加 remark 字段
-- 用于存储生成 Kafka 消息时的备注信息

ALTER TABLE `knowledge_base`.`kafka_generation_history` 
ADD COLUMN `remark` TEXT COMMENT '备注信息' 
AFTER `custom_fields`;
