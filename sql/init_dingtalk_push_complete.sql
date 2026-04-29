-- ==========================================
-- 钉钉推送系统数据库初始化脚本
-- ==========================================
-- 用于创建 dingtalk_push 数据库及相关表结构
-- 支持 MySQL/MariaDB
-- ==========================================

-- 1. 创建数据库
CREATE DATABASE IF NOT EXISTS dingtalk_push 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE dingtalk_push;

-- ==========================================
-- 2. 创建核心表
-- ==========================================

-- 2.1 推送配置表
CREATE TABLE IF NOT EXISTS dingtalk_push_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
    name VARCHAR(100) NOT NULL COMMENT '任务名称',
    description TEXT COMMENT '任务描述',
    
    -- Webhook 配置
    webhook_url TEXT NOT NULL COMMENT '钉钉机器人Webhook地址（加密存储）',
    secret_key VARCHAR(255) COMMENT '加签密钥（可选）',
    
    -- 推送对象配置
    at_mobiles JSON COMMENT '@指定手机号列表，JSON格式: ["13800138000"]',
    at_all TINYINT(1) DEFAULT 0 COMMENT '是否@所有人: 1-是, 0-否',
    
    -- 消息配置
    message_type VARCHAR(20) DEFAULT 'markdown' COMMENT '消息类型: markdown/actionCard/text',
    template_content TEXT NOT NULL COMMENT '消息模板内容（Jinja2格式）',
    
    -- 数据源配置
    data_source_config JSON COMMENT '数据源配置（JSON格式），支持 static/api/sql',
    
    -- 调度配置
    schedule_config JSON NOT NULL COMMENT '调度配置（JSON格式），如 {"type": "daily", "time": "08:00"}',
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai' COMMENT '时区',
    
    -- 状态与分类
    enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用: 1-启用, 0-禁用',
    category VARCHAR(50) DEFAULT 'general' COMMENT '任务分类: roster/alert/report/general',
    priority INT DEFAULT 0 COMMENT '优先级（数字越大优先级越高）',
    
    -- 执行配置
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

-- 2.2 推送历史表
CREATE TABLE IF NOT EXISTS dingtalk_push_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '历史记录ID',
    config_id INT NOT NULL COMMENT '配置ID',
    
    -- 触发信息
    trigger_type VARCHAR(20) DEFAULT 'manual' COMMENT '触发类型: manual/scheduled/api',
    triggered_at DATETIME NOT NULL COMMENT '触发时间',
    
    -- 执行信息
    start_time DATETIME COMMENT '开始执行时间',
    end_time DATETIME COMMENT '结束执行时间',
    execution_duration_ms INT COMMENT '执行耗时（毫秒）',
    
    -- 执行结果
    status VARCHAR(20) NOT NULL COMMENT '状态: success/failed/pending/retrying',
    message_content TEXT COMMENT '实际发送的消息内容',
    error_message TEXT COMMENT '错误信息',
    retry_count INT DEFAULT 0 COMMENT '重试次数',
    
    -- 操作人
    operator VARCHAR(50) COMMENT '操作人（手动触发时）',
    completed_at DATETIME COMMENT '完成时间',
    
    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    
    FOREIGN KEY (config_id) REFERENCES dingtalk_push_config(id) ON DELETE CASCADE,
    INDEX idx_config_id (config_id),
    INDEX idx_triggered_at (triggered_at),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送历史表';

-- 2.3 推送日志表
CREATE TABLE IF NOT EXISTS dingtalk_push_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    history_id BIGINT NOT NULL COMMENT '关联的历史记录ID',
    
    -- 日志信息
    step VARCHAR(50) NOT NULL COMMENT '步骤名称/日志级别: INFO/WARNING/ERROR',
    status VARCHAR(20) NOT NULL COMMENT '步骤状态: success/failed',
    details TEXT NOT NULL COMMENT '详细信息',
    duration_ms INT COMMENT '步骤耗时（毫秒）',
    
    -- 审计字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '日志时间',
    
    FOREIGN KEY (history_id) REFERENCES dingtalk_push_history(id) ON DELETE CASCADE,
    INDEX idx_history_id (history_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='钉钉推送日志表';

-- ==========================================
-- 3. 插入示例数据（可选）
-- ==========================================

-- 3.1 示例配置：每日早班提醒
INSERT INTO dingtalk_push_config (
    name, 
    description,
    webhook_url, 
    at_mobiles,
    at_all,
    message_type, 
    template_content,
    data_source_config,
    schedule_config,
    timezone,
    enabled,
    category,
    priority,
    max_retries,
    timeout_seconds,
    created_by
) VALUES
(
    '每日早班提醒',
    '每天早上8点推送当日早班人员信息',
    'ENCRYPTED_WEBHOOK_URL_HERE',
    '["13800138000"]',
    FALSE,
    'markdown',
    '# 📅 早班提醒\n\n**日期**: {{ now }}\n**早班人员**: {{ staff_name }}\n\n请准时到岗！',
    '{"type": "static", "data": {"staff_name": "张三"}}',
    '{"type": "daily", "time": "08:00"}',
    'Asia/Shanghai',
    TRUE,
    'roster',
    5,
    3,
    10,
    'admin'
);

-- 3.2 示例配置：打卡提醒
INSERT INTO dingtalk_push_config (
    name, 
    description,
    webhook_url, 
    at_mobiles,
    at_all,
    message_type, 
    template_content,
    data_source_config,
    schedule_config,
    timezone,
    enabled,
    category,
    priority,
    max_retries,
    timeout_seconds,
    created_by
) VALUES
(
    '上班打卡提醒',
    '工作日上午9点前提醒打卡',
    'ENCRYPTED_WEBHOOK_URL_HERE',
    '["13800138000"]',
    FALSE,
    'text',
    '【打卡提醒】\n\n当前时间：{{ now }}\n\n请记得及时打卡！\n\n温馨提示：\n- 上班打卡时间：09:00 前\n- 下班打卡时间：18:00 后',
    '{"type": "static", "data": {}}',
    '{"type": "cron", "expression": "0 8 * * 1-5"}',
    'Asia/Shanghai',
    TRUE,
    'alert',
    8,
    3,
    10,
    'admin'
);

-- ==========================================
-- 4. 验证创建结果
-- ==========================================

-- 查看创建的表
SHOW TABLES;

-- 查看配置表示例数据
SELECT id, name, category, enabled, created_at FROM dingtalk_push_config;

-- ==========================================
-- 初始化完成
-- ==========================================
