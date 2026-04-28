-- ==========================================
-- 排班系统数据库备份文件
-- 生成时间: 2026-04-27
-- 数据库: schedule_system
-- ==========================================

-- 1. 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `schedule`
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 使用数据库
USE `schedule_system`;

-- 3. 创建数据表

-- 人员表
CREATE TABLE IF NOT EXISTS staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '员工姓名',
    employee_id VARCHAR(20) UNIQUE COMMENT '员工编号',
    department VARCHAR(50) COMMENT '部门',
    position VARCHAR(50) COMMENT '职位',
    is_active TINYINT DEFAULT 1 COMMENT '是否在职 (1=在职, 0=离职)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_employee_id (employee_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='员工信息表';

-- 排班表
CREATE TABLE IF NOT EXISTS roster (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL COMMENT '员工ID',
    shift_date DATE NOT NULL COMMENT '排班日期',
    shift_type VARCHAR(20) COMMENT '班次类型 (早班/中班/晚班等)',
    shift_start TIME COMMENT '班次开始时间',
    shift_end TIME COMMENT '班次结束时间',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    UNIQUE KEY uk_staff_date (staff_id, shift_date),
    INDEX idx_date (shift_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='排班信息表';

-- 请假表
CREATE TABLE IF NOT EXISTS leave_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_id INT NOT NULL COMMENT '员工ID',
    leave_type VARCHAR(20) COMMENT '请假类型 (年假/病假/事假等)',
    start_date DATE NOT NULL COMMENT '请假开始日期',
    end_date DATE NOT NULL COMMENT '请假结束日期',
    reason TEXT COMMENT '请假原因',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态 (pending/approved/rejected)',
    approved_by INT COMMENT '审批人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (staff_id) REFERENCES staff(id),
    INDEX idx_staff (staff_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='请假申请表';

-- 节假日配置表
CREATE TABLE IF NOT EXISTS holiday_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    holiday_date DATE NOT NULL COMMENT '节假日日期',
    is_working_day BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为工作日',
    description VARCHAR(100) COMMENT '节假日描述',
    wage INT DEFAULT 1 COMMENT '薪资倍数',
    after BOOLEAN DEFAULT FALSE COMMENT '是否为补班日',
    target VARCHAR(100) COMMENT '关联的节假日名称',
    rest INT COMMENT '距离下一个假期的天数'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='存储法定节假日配置';

-- 请假记录表
CREATE TABLE IF NOT EXISTS leave_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    staff_name VARCHAR(50) NOT NULL COMMENT '员工姓名',
    leave_date DATE NOT NULL COMMENT '请假日期',
    start_time TIME COMMENT '请假开始时间',
    end_time TIME COMMENT '请假结束时间',
    is_full_day BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为全天请假'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='记录人员请假信息';

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

-- 钉钉推送配置表
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

-- 钉钉推送历史表
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

-- 钉钉推送日志表
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

-- ==========================================
-- 备份完成
-- ==========================================