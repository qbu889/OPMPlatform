
-- ============================================================================
-- CityColor 颜色提取系统 - MySQL 数据库初始化脚本
-- 用途：创建颜色方案表、关键词-颜色映射表、城市色彩库表
-- 执行方式：mysql -u root -p < city_color_init.sql
-- ============================================================================

-- 切换到 knowledge_base 数据库（或修改为你实际使用的数据库名）
USE knowledge_base;

-- ============================================================================
-- 表1：颜色方案表（存储用户保存的颜色方案）
-- ============================================================================
CREATE TABLE IF NOT EXISTS city_color_schemes (
    id VARCHAR(50) PRIMARY KEY COMMENT '方案唯一标识',
    title VARCHAR(255) NOT NULL DEFAULT '' COMMENT '方案名称',
    colors TEXT NOT NULL COMMENT '颜色数据(JSON数组)',
    gradient VARCHAR(500) DEFAULT '' COMMENT '渐变CSS字符串',
    palette_type VARCHAR(50) DEFAULT 'custom' COMMENT '配色类型',
    source_text VARCHAR(1000) DEFAULT '' COMMENT '原始输入内容',
    extract_mode VARCHAR(20) DEFAULT 'auto' COMMENT '提取模式: auto/city/brand/random',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at),
    INDEX idx_palette_type (palette_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CityColor-颜色方案表';

-- ============================================================================
-- 表2：关键词-颜色映射配置表（可管理扩展的颜色映射规则）
-- ============================================================================
CREATE TABLE IF NOT EXISTS city_color_keyword_mappings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL COMMENT '关键词',
    hex_color VARCHAR(20) NOT NULL COMMENT 'HEX颜色值',
    color_name VARCHAR(100) DEFAULT '' COMMENT '颜色中文名称',
    category VARCHAR(50) DEFAULT '' COMMENT '分类: nature/city/emotion/brand',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1=启用，0=禁用',
    sort_order INT DEFAULT 0 COMMENT '排序权重',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CityColor-关键词颜色映射配置表';

-- 插入默认关键词-颜色映射数据
INSERT INTO city_color_keyword_mappings 
    (keyword, hex_color, color_name, category, sort_order) VALUES
('天空', '#87CEEB', '天蓝', 'nature', 1),
('蓝天', '#4A90D9', '天空蓝', 'nature', 2),
('海洋', '#1E90FF', '宝蓝', 'nature', 3),
('大海', '#006994', '深海蓝', 'nature', 4),
('水', '#5DADE2', '浅天蓝', 'nature', 5),
('河流', '#85C1E9', '浅蓝灰', 'nature', 6),
('森林', '#27AE60', '森林绿', 'nature', 7),
('绿色', '#2ECC71', '翠绿', 'nature', 8),
('草地', '#82E0AA', '薄荷绿', 'nature', 9),
('树叶', '#52BE80', '绿叶', 'nature', 10),
('树木', '#1ABC9C', '青绿', 'nature', 11),
('太阳', '#F39C12', '金色', 'nature', 12),
('阳光', '#F1C40F', '亮黄', 'nature', 13),
('金色', '#D4AC0D', '暗金', 'nature', 14),
('火焰', '#E74C3C', '珊瑚红', 'nature', 15),
('红色', '#C0392B', '深红', 'nature', 16),
('火', '#E67E22', '橙色', 'nature', 17),
('玫瑰', '#E91E63', '玫红', 'nature', 18),
('花', '#FF69B4', '粉色', 'nature', 19),
('樱花', '#FFB7C5', '樱花粉', 'nature', 20),
('紫色', '#8E44AD', '紫色', 'nature', 21),
('紫', '#9B59B6', '浅紫', 'nature', 22),
('白色', '#ECF0F1', '白色', 'nature', 23),
('雪', '#D5F5E3', '雪白', 'nature', 24),
('云', '#BDC3C7', '灰色', 'nature', 25),
('月亮', '#F9E79F', '月光黄', 'nature', 26),
('星星', '#F4D03F', '星黄', 'nature', 27),
('城市', '#7F8C8D', '石板灰', 'city', 28),
('建筑', '#95A5A6', '建筑灰', 'city', 29),
('钢铁', '#607D8B', '钢灰', 'city', 30),
('霓虹', '#FF00FF', '霓虹紫', 'city', 31),
('灯光', '#F39C12', '暖光黄', 'city', 32),
('夜景', '#2C3E50', '深蓝灰', 'city', 33),
('日落', '#E74C3C', '日落红', 'city', 34),
('黄昏', '#D35400', '深橙', 'city', 35),
('日出', '#F39C12', '日出金', 'city', 36),
('温暖', '#E67E22', '暖橙', 'emotion', 37),
('冷静', '#3498DB', '冷静蓝', 'emotion', 38),
('活力', '#E74C3C', '活力红', 'emotion', 39),
('宁静', '#AED6F1', '宁静蓝', 'emotion', 40),
('神秘', '#6C3483', '神秘紫', 'emotion', 41),
('浪漫', '#FD79A8', '浪漫粉', 'emotion', 42),
('复古', '#B8860B', '复古金', 'emotion', 43),
('未来', '#00CED1', '未来青', 'emotion', 44);

-- ============================================================================
-- 表3：城市色彩库表（可管理扩展的城市标志性色彩）
-- ============================================================================
CREATE TABLE IF NOT EXISTS city_color_city_db (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL UNIQUE COMMENT '城市名称',
    colors TEXT NOT NULL COMMENT '颜色列表(JSON数组)',
    description VARCHAR(500) DEFAULT '' COMMENT '城市色彩描述',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1=启用，0=禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_city_name (city_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CityColor-城市色彩库表';

-- 插入默认城市色彩数据
INSERT INTO city_color_city_db 
    (city_name, colors, description) VALUES
('巴黎', '["#8E44AD", "#F5B7B1", "#2C3E50", "#FDEBD0", "#FFFFFF"]', '紫/粉/灰——浪漫之都'),
('东京', '["#E74C3C", "#FFFFFF", "#2C3E50", "#F1C40F", "#27AE60"]', '红/白/黑——传统与现代'),
('纽约', '["#1A5276", "#F39C12", "#7F8C8D", "#ECF0F1", "#2C3E50"]', '蓝/金/灰——不夜城'),
('伦敦', '["#2C3E50", "#C0392B", "#FDEBD0", "#7D3C98", "#FFFFFF"]', '黑/红/米——古典英伦'),
('罗马', '["#E67E22", "#C0392B", "#F5B7B1", "#D4AC0D", "#ECF0F1"]', '橙/红/金——永恒之城'),
('北京', '["#C0392B", "#F1C40F", "#27AE60", "#ECF0F1", "#7D3C98"]', '红/金/绿——皇城色彩'),
('迪拜', '["#F1C40F", "#2C3E50", "#FFFFFF", "#E67E22", "#1ABC9C"]', '金/黑/白——沙漠明珠'),
('悉尼', '["#1E90FF", "#FFFFFF", "#27AE60", "#F39C12", "#ECF0F1"]', '蓝/白/绿——海港城市');

-- ============================================================================
-- 验证：查看创建的表
-- ============================================================================
SHOW TABLES LIKE 'city_color%';

DESCRIBE city_color_schemes;
DESCRIBE city_color_keyword_mappings;
DESCRIBE city_color_city_db;
