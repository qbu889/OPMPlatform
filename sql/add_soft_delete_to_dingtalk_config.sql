-- 为钉钉推送配置表添加软删除支持
ALTER TABLE dingtalk_push_config 
ADD COLUMN is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否已删除: 0-未删除, 1-已删除' AFTER enabled,
ADD COLUMN deleted_at DATETIME COMMENT '删除时间' AFTER is_deleted,
ADD COLUMN deleted_by VARCHAR(50) COMMENT '删除人' AFTER deleted_at;

-- 添加索引以优化查询性能
ALTER TABLE dingtalk_push_config 
ADD INDEX idx_is_deleted (is_deleted);

-- 更新现有数据（确保所有现有记录都是未删除状态）
UPDATE dingtalk_push_config SET is_deleted = 0 WHERE is_deleted IS NULL;

