-- 创建 FPA 评估结果表
CREATE TABLE IF NOT EXISTS fpa_evaluation_result (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增 ID',
    requirement_name VARCHAR(500) COMMENT '需求名称',
    requirement_code VARCHAR(100) COMMENT '需求编号',
    afp DECIMAL(10,2) COMMENT '规模估算结果 (功能点)',
    cf DECIMAL(5,2) COMMENT '规模变更调整因子',
    adjusted_scale DECIMAL(10,2) COMMENT '调整后规模 (功能点)',
    base_productivity DECIMAL(10,2) COMMENT '基准生产率 (人时/功能点)',
    unadjusted_effort DECIMAL(10,2) COMMENT '未调整工作量 (人天)',
    factor_application_type DECIMAL(5,2) COMMENT '调整因子 - 应用类型',
    factor_quality DECIMAL(5,2) COMMENT '调整因子 - 质量特性',
    factor_language DECIMAL(5,2) COMMENT '调整因子 - 开发语言',
    factor_team DECIMAL(5,2) COMMENT '调整因子 - 开发团队背景',
    adjusted_effort DECIMAL(10,2) COMMENT '调整后工作量 (人天)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_requirement (requirement_code),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
COMMENT='FPA 评估结果表';

-- 插入示例数据
INSERT INTO fpa_evaluation_result (
    requirement_name, requirement_code, 
    afp, cf, adjusted_scale, base_productivity, unadjusted_effort,
    factor_application_type, factor_quality, factor_language, factor_team,
    adjusted_effort
) VALUES (
    '关于集团事件业务影响分析开发需求', '49900_20250721',
    125.27, 1.21, 151.57, 10.12, 191.74,
    1.00, 0.90, 1.00, 0.80,
    138.05
);
