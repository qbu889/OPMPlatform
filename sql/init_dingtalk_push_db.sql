-- 钉钉推送系统数据库初始化脚本

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS dingtalk_push 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE dingtalk_push;

-- 2. 创建配置表
CREATE TABLE IF NOT EXISTS dingtalk_push_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
    name VARCHAR(100) NOT NULL COMMENT '配置名称',
    category VARCHAR(50) DEFAULT 'default' COMMENT '配置分类',
    webhook_url TEXT NOT NULL COMMENT '钉钉机器人Webhook地址（加密存储）',
    template_content TEXT NOT NULL COMMENT '消息模板内容（Jinja2格式）',
    schedule_config JSON NOT NULL COMMENT '调度配置（JSON格式）',
    data_source_config JSON COMMENT '数据源配置（SQL查询等）',
    enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用：1-启用，0-禁用',
    description TEXT COMMENT '配置描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_enabled (enabled),
    INDEX idx_category (category),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送配置表';

-- 3. 创建执行历史表
CREATE TABLE IF NOT EXISTS dingtalk_push_history (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '历史记录ID',
    config_id INT NOT NULL COMMENT '关联的配置ID',
    trigger_type VARCHAR(20) NOT NULL COMMENT '触发类型：manual/scheduled/api',
    status VARCHAR(20) NOT NULL COMMENT '执行状态：success/failed/pending',
    message_content TEXT COMMENT '实际发送的消息内容',
    execution_duration_ms INT COMMENT '执行耗时（毫秒）',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    error_message TEXT COMMENT '错误信息',
    triggered_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '触发时间',
    completed_at DATETIME COMMENT '完成时间',
    operator VARCHAR(50) COMMENT '操作人（手动触发时）',
    INDEX idx_config_id (config_id),
    INDEX idx_status (status),
    INDEX idx_triggered_at (triggered_at),
    FOREIGN KEY (config_id) REFERENCES dingtalk_push_config(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送执行历史表';

-- 4. 创建推送日志表
CREATE TABLE IF NOT EXISTS dingtalk_push_log (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    history_id INT NOT NULL COMMENT '关联的历史记录ID',
    step VARCHAR(50) NOT NULL COMMENT '步骤名称',
    status VARCHAR(20) NOT NULL COMMENT '步骤状态：success/failed',
    details TEXT COMMENT '详细信息',
    duration_ms INT COMMENT '步骤耗时（毫秒）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_history_id (history_id),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (history_id) REFERENCES dingtalk_push_history(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送详细日志表';

-- 5. 插入示例配置（可选）
INSERT INTO dingtalk_push_config 
(name, category, webhook_url, template_content, schedule_config, enabled, description)
VALUES 
('测试推送配置', 'test', 
 '***encrypted_webhook***',
 '## 📢 测试消息\n\n当前时间：{{ now }}\n\n这是一条测试消息。',
 '{"type": "cron", "expression": "0 9 * * *"}',
 1,
 '用于测试钉钉推送功能的示例配置');
