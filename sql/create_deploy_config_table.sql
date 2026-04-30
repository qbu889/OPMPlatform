-- 部署配置表
CREATE TABLE deploy_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT NOT NULL COMMENT '配置值',
    config_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型: string, number, boolean, json',
    description VARCHAR(500) COMMENT '配置说明',
    category VARCHAR(50) DEFAULT 'general' COMMENT '配置分类: server, deployment, backup, monitor',
    is_sensitive BOOLEAN DEFAULT FALSE COMMENT '是否敏感信息（如密码）',
    updated_by INT COMMENT '最后更新人ID',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_category (category),
    INDEX idx_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部署配置表';

-- 初始化默认配置
INSERT INTO deploy_config (config_key, config_value, config_type, description, category, is_sensitive) VALUES
('remote_host', '8.146.228.47', 'string', '远程服务器IP地址', 'server', FALSE),
('remote_user', 'root', 'string', '远程服务器用户名', 'server', FALSE),
('remote_path', '/project/wordToWord', 'string', '远程项目路径', 'server', FALSE),
('backup_dir', '/project/backups', 'string', '备份文件存储目录', 'backup', FALSE),
('ssh_port', '22', 'number', 'SSH端口号', 'server', FALSE),
('ssh_timeout', '30', 'number', 'SSH连接超时时间（秒）', 'server', FALSE),
('deploy_timeout', '300', 'number', '部署脚本执行超时时间（秒）', 'deployment', FALSE),
('rollback_timeout', '300', 'number', '回滚脚本执行超时时间（秒）', 'deployment', FALSE),
('max_backup_count', '5', 'number', '最大备份保留数量', 'backup', FALSE),
('backup_retention_days', '30', 'number', '备份保留天数', 'backup', FALSE),
('backend_port', '5004', 'number', '后端服务端口', 'server', FALSE),
('frontend_port', '5173', 'number', '前端服务端口', 'server', FALSE),
('git_branch', 'q/dev', 'string', 'Git部署分支', 'deployment', FALSE),
('deploy_password', '', 'string', '部署操作密码（二次验证）', 'deployment', TRUE),
('enable_auto_backup', 'true', 'boolean', '是否启用自动备份', 'deployment', FALSE),
('log_lines_default', '50', 'number', '日志查看默认行数', 'monitor', FALSE),
('health_check_interval', '60', 'number', '健康检查间隔（秒）', 'monitor', FALSE);
