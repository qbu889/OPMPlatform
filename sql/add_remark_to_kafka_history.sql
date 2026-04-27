-- 为 kafka_generation_history 表添加备注字段
ALTER TABLE `knowledge_base`.`kafka_generation_history` 
ADD COLUMN `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注信息' AFTER `region_name`;

-- 为备注字段创建索引以支持模糊搜索
CREATE INDEX `idx_remark` ON `knowledge_base`.`kafka_generation_history` (`remark`(255));
