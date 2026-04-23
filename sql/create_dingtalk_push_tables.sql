-- 钉钉智能推送系统 - 数据库初始化脚本
-- 创建时间: 2026-04-21

-- 1. 推送配置表
CREATE TABLE IF NOT EXISTS dingtalk_push_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
    name VARCHAR(100) NOT NULL COMMENT '任务名称',
    description VARCHAR(500) COMMENT '任务描述',
    
    -- Webhook 配置
    webhook_url TEXT NOT NULL COMMENT '加密后的 Webhook URL',
    secret_key VARCHAR(200) COMMENT '钉钉加签密钥（可选）',
    
    -- 推送对象
    at_mobiles JSON COMMENT '@指定人员手机号列表 ["13800138000"]',
    at_all BOOLEAN DEFAULT FALSE COMMENT '是否@所有人',
    
    -- 消息配置
    message_type VARCHAR(20) NOT NULL DEFAULT 'markdown' COMMENT '消息类型: markdown/actionCard/text',
    template_content TEXT NOT NULL COMMENT '消息模板内容（Jinja2 模板）',
    data_source_config JSON COMMENT '数据源配置 {type: "api/sql/static", config: {...}}',
    
    -- 调度配置
    schedule_config JSON NOT NULL COMMENT '调度配置 {type: "cron/daily/weekly", config: {...}}',
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai' COMMENT '时区',
    
    -- 执行配置
    enabled BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    category VARCHAR(50) DEFAULT 'general' COMMENT '分类: roster/alert/report',
    priority INT DEFAULT 0 COMMENT '优先级 (0-10, 越大越优先)',
    max_retries INT DEFAULT 3 COMMENT '最大重试次数',
    timeout_seconds INT DEFAULT 10 COMMENT '请求超时时间（秒）',
    
    -- 审计字段
    created_by VARCHAR(50) COMMENT '创建人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    INDEX idx_enabled (enabled),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送配置表';

-- 2. 推送历史表
CREATE TABLE IF NOT EXISTS dingtalk_push_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '历史记录ID',
    config_id INT NOT NULL COMMENT '配置ID',
    
    -- 执行信息
    trigger_time DATETIME NOT NULL COMMENT '触发时间',
    start_time DATETIME COMMENT '开始执行时间',
    end_time DATETIME COMMENT '结束执行时间',
    execution_duration_ms INT COMMENT '执行耗时（毫秒）',
    
    -- 执行结果
    status VARCHAR(20) NOT NULL COMMENT '状态: success/failed/retrying',
    response_data JSON COMMENT '钉钉 API 响应数据',
    error_message TEXT COMMENT '错误信息',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    
    -- 消息内容快照
    message_snapshot JSON COMMENT '实际发送的消息内容',
    
    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    
    FOREIGN KEY (config_id) REFERENCES dingtalk_push_config(id) ON DELETE CASCADE,
    INDEX idx_config_id (config_id),
    INDEX idx_trigger_time (trigger_time),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送历史表';

-- 3. 推送日志表
CREATE TABLE IF NOT EXISTS dingtalk_push_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    config_id INT NOT NULL COMMENT '配置ID',
    history_id BIGINT COMMENT '关联的历史记录ID',
    
    -- 日志信息
    log_level VARCHAR(10) NOT NULL COMMENT '日志级别: INFO/WARNING/ERROR',
    message TEXT NOT NULL COMMENT '日志消息',
    context_data JSON COMMENT '上下文数据',
    
    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '日志时间',
    
    FOREIGN KEY (config_id) REFERENCES dingtalk_push_config(id) ON DELETE CASCADE,
    INDEX idx_config_id (config_id),
    INDEX idx_history_id (history_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送日志表';

-- 插入示例配置（可选）
-- INSERT INTO dingtalk_push_config (name, description, webhook_url, message_type, template_content, schedule_config, enabled, category)
-- VALUES (
--     '每日排班推送',
--     '每天早上 8:00 推送当天和明天的排班信息',
--     'ENCRYPTED_WEBHOOK_URL_HERE',
--     'actionCard',
--     '# 📅 排班信息推送\n\n### **今天** {{ today }} ({{ weekday }})\n{% for slot in today_schedule %}\n- **{{ slot.time }}**: {{ slot.staff }}\n{% endfor %}',
--     '{"type": "daily", "config": {"times": ["08:00"], "weekdays": [1,2,3,4,5], "exclude_holidays": true}}',
--     TRUE,
--     'roster'
-- );
