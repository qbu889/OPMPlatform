-- ============================================================================
-- 内容转Excel模块 - MySQL 数据库初始化脚本
-- 用途：创建软件-IP映射表和初始版本号表
-- 执行方式：mysql -u root -p < content_to_excel_init.sql
-- ============================================================================

-- 切换到 knowledge_base 数据库（或修改为你实际使用的数据库名）
USE knowledge_base;

-- ============================================================================
-- 表1：软件-IP映射表
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_to_excel_software_ip (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_name VARCHAR(255) NOT NULL UNIQUE COMMENT '软件名称',
    target_ip VARCHAR(255) DEFAULT '' COMMENT '目标IP',
    operator VARCHAR(100) DEFAULT '' COMMENT '操作员',
    verifier VARCHAR(100) DEFAULT '' COMMENT '验证员',
    initial_version VARCHAR(100) DEFAULT '' COMMENT '初始版本号',
    is_builtin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否内置软件：1=内置不可删除，0=外部配置可删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_software_name (software_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容转Excel-软件IP映射表';

-- ============================================================================
-- 表2：初始版本号表
-- ============================================================================
CREATE TABLE IF NOT EXISTS content_to_excel_initial_version (
    id INT AUTO_INCREMENT PRIMARY KEY,
    software_name VARCHAR(255) NOT NULL UNIQUE COMMENT '软件名称',
    initial_version VARCHAR(100) DEFAULT '' COMMENT '初始版本号',
    is_builtin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否内置软件：1=内置不可删除，0=外部配置可删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_software_name (software_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容转Excel-初始版本号表';

-- ============================================================================
-- 验证：查看创建的表
-- ============================================================================
SHOW TABLES LIKE 'content_to_excel%';

DESCRIBE content_to_excel_software_ip;
DESCRIBE content_to_excel_initial_version;
