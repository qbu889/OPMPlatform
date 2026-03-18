-- 创建访问日志表
-- 用于记录所有用户的访问行为，支持系统统计和审计功能

CREATE TABLE IF NOT EXISTS visit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address VARCHAR(50) NOT NULL,
    user_id INTEGER,
    username VARCHAR(100),
    endpoint VARCHAR(200),
    user_agent VARCHAR(500),
    response_time FLOAT,
    status_code INTEGER,
    visit_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提升查询性能
CREATE INDEX IF NOT EXISTS idx_visit_log_ip_address ON visit_log(ip_address);
CREATE INDEX IF NOT EXISTS idx_visit_log_user_id ON visit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_visit_log_visit_time ON visit_log(visit_time);

-- 添加表注释
COMMENT ON TABLE visit_log IS '访问日志表，记录所有用户的访问行为';

-- 添加字段注释
COMMENT ON COLUMN visit_log.id IS '主键 ID';
COMMENT ON COLUMN visit_log.ip_address IS 'IP 地址';
COMMENT ON COLUMN visit_log.user_id IS '用户 ID（如果已登录）';
COMMENT ON COLUMN visit_log.username IS '用户名';
COMMENT ON COLUMN visit_log.endpoint IS '访问的接口路径';
COMMENT ON COLUMN visit_log.user_agent IS '用户代理';
COMMENT ON COLUMN visit_log.response_time IS '响应时间（秒）';
COMMENT ON COLUMN visit_log.status_code IS 'HTTP 状态码';
COMMENT ON COLUMN visit_log.visit_time IS '访问时间';
