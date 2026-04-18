-- 钉钉定时推送配置表
CREATE TABLE IF NOT EXISTS dingtalk_schedule_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
    webhook_url VARCHAR(500) NOT NULL COMMENT '钉钉机器人Webhook地址',
    time_slots TEXT COMMENT '推送时段列表（JSON格式）',
    schedule_times TEXT NOT NULL COMMENT '推送时间点列表（JSON格式），如 ["08:00", "09:00", "18:00"]',
    enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用：1-启用，0-禁用',
    description VARCHAR(200) COMMENT '配置描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_enabled (enabled),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉定时推送配置表';

-- 插入示例配置（可选）
-- INSERT INTO dingtalk_schedule_config 
-- (webhook_url, time_slots, schedule_times, enabled, description)
-- VALUES 
-- ('https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN', 
--  '["8:00～9:00", "9:00～12:00", "13:30～18:00", "18:00～21:00"]',
--  '["08:00", "09:00", "18:00"]',
--  1,
-- '工作日早晚排班提醒');
