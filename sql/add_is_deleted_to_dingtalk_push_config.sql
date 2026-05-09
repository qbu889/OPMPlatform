-- 为 dingtalk_push_config 表添加软删除字段
-- 执行时间: 2026-05-07

-- 添加 is_deleted 字段
ALTER TABLE dingtalk_push_config 
ADD COLUMN is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否已删除: 0-未删除, 1-已删除' AFTER enabled;

-- 添加 deleted_at 字段
ALTER TABLE dingtalk_push_config 
ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间' AFTER is_deleted;

-- 添加 deleted_by 字段
ALTER TABLE dingtalk_push_config 
ADD COLUMN deleted_by VARCHAR(50) NULL DEFAULT NULL COMMENT '删除人' AFTER deleted_at;

-- 添加索引以优化查询性能
ALTER TABLE dingtalk_push_config 
ADD INDEX idx_is_deleted (is_deleted);

-- 更新现有数据，确保 is_deleted 默认为 0
UPDATE dingtalk_push_config SET is_deleted = 0 WHERE is_deleted IS NULL;

