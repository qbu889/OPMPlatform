-- 在线表格系统数据库初始化脚本
-- 用于创建表格管理系统所需的所有表结构

-- 使用数据库
USE fpa_rules;

-- 1. 表格定义表
CREATE TABLE IF NOT EXISTS `spreadsheet` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '表格 ID',
  `name` VARCHAR(200) NOT NULL COMMENT '表格名称',
  `description` VARCHAR(500) COMMENT '表格描述',
  `created_by` VARCHAR(100) COMMENT '创建人',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_template` BOOLEAN DEFAULT FALSE COMMENT '是否为模板',
  `row_count` INT DEFAULT 0 COMMENT '总行数',
  `col_count` INT DEFAULT 0 COMMENT '总列数',
  PRIMARY KEY (`id`),
  INDEX `idx_spreadsheet_name` (`name`),
  INDEX `idx_spreadsheet_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表格定义表';

-- 2. 表格列定义表
CREATE TABLE IF NOT EXISTS `spreadsheet_column` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '列 ID',
  `spreadsheet_id` INT NOT NULL COMMENT '表格 ID',
  `column_index` INT NOT NULL COMMENT '列索引 (从 0 开始)',
  `column_name` VARCHAR(100) NOT NULL COMMENT '列名',
  `column_type` VARCHAR(50) DEFAULT 'text' COMMENT '列类型：text, number, date, select',
  `width` INT DEFAULT 100 COMMENT '列宽 (像素)',
  `is_required` BOOLEAN DEFAULT FALSE COMMENT '是否必填',
  `default_value` VARCHAR(500) COMMENT '默认值',
  `options` TEXT COMMENT '选项值 (JSON 格式，用于 select 类型)',
  `background_color` VARCHAR(20) COMMENT '背景色',
  `text_color` VARCHAR(20) COMMENT '文字颜色',
  `font_weight` VARCHAR(20) DEFAULT 'normal' COMMENT '字体粗细',
  PRIMARY KEY (`id`),
  INDEX `idx_column_spreadsheet_id` (`spreadsheet_id`),
  INDEX `idx_column_index` (`column_index`),
  CONSTRAINT `fk_column_spreadsheet` FOREIGN KEY (`spreadsheet_id`) 
    REFERENCES `spreadsheet` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表格列定义表';

-- 3. 表格行数据表
CREATE TABLE IF NOT EXISTS `spreadsheet_row` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '行 ID',
  `spreadsheet_id` INT NOT NULL COMMENT '表格 ID',
  `row_index` INT NOT NULL COMMENT '行索引 (从 0 开始)',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  INDEX `idx_row_spreadsheet_id` (`spreadsheet_id`),
  INDEX `idx_row_index` (`row_index`),
  CONSTRAINT `fk_row_spreadsheet` FOREIGN KEY (`spreadsheet_id`) 
    REFERENCES `spreadsheet` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表格行数据表';

-- 4. 单元格数据表
CREATE TABLE IF NOT EXISTS `spreadsheet_cell` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '单元格 ID',
  `row_id` INT NOT NULL COMMENT '行 ID',
  `column_id` INT NOT NULL COMMENT '列 ID',
  `value` TEXT COMMENT '单元格值',
  `background_color` VARCHAR(20) COMMENT '背景色',
  `text_color` VARCHAR(20) COMMENT '文字颜色',
  `font_weight` VARCHAR(20) COMMENT '字体粗细',
  `text_align` VARCHAR(20) DEFAULT 'left' COMMENT '对齐方式',
  `is_validated` BOOLEAN DEFAULT TRUE COMMENT '是否通过验证',
  `validation_message` VARCHAR(500) COMMENT '验证提示信息',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_row_column` (`row_id`, `column_id`),
  INDEX `idx_cell_row_id` (`row_id`),
  INDEX `idx_cell_column_id` (`column_id`),
  CONSTRAINT `fk_cell_row` FOREIGN KEY (`row_id`) 
    REFERENCES `spreadsheet_row` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_cell_column` FOREIGN KEY (`column_id`) 
    REFERENCES `spreadsheet_column` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='单元格数据表';

-- 5. 表格操作历史表
CREATE TABLE IF NOT EXISTS `spreadsheet_history` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '历史记录 ID',
  `spreadsheet_id` INT NOT NULL COMMENT '表格 ID',
  `operation_type` VARCHAR(50) NOT NULL COMMENT '操作类型：add_row, delete_row, update_cell, etc.',
  `operation_data` TEXT COMMENT '操作数据 (JSON 格式)',
  `operated_by` VARCHAR(100) COMMENT '操作人',
  `operated_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  INDEX `idx_history_spreadsheet_id` (`spreadsheet_id`),
  INDEX `idx_history_operated_at` (`operated_at`),
  CONSTRAINT `fk_history_spreadsheet` FOREIGN KEY (`spreadsheet_id`) 
    REFERENCES `spreadsheet` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='表格操作历史表';

-- 插入示例数据 - 创建一个 BUG 跟踪表格
INSERT INTO `spreadsheet` (`name`, `description`, `created_by`, `row_count`, `col_count`) VALUES
('BUG 跟踪表', '用于跟踪和管理项目中的 BUG', 'admin', 0, 0);

-- 获取刚插入的表格 ID
SET @bug_table_id = LAST_INSERT_ID();

-- 插入列定义
INSERT INTO `spreadsheet_column` (`spreadsheet_id`, `column_index`, `column_name`, `column_type`, `width`, `is_required`, `options`) VALUES
(@bug_table_id, 0, '序号', 'number', 80, FALSE, NULL),
(@bug_table_id, 1, '发现时间', 'date', 120, TRUE, NULL),
(@bug_table_id, 2, '问题描述', 'text', 300, TRUE, NULL),
(@bug_table_id, 3, '任务 ID&账号', 'text', 150, FALSE, NULL),
(@bug_table_id, 4, '截图 1', 'text', 100, FALSE, NULL),
(@bug_table_id, 5, '截图 2', 'text', 100, FALSE, NULL),
(@bug_table_id, 6, '发现环境', 'select', 100, TRUE, '["生产环境", "测试环境", "开发环境"]'),
(@bug_table_id, 7, '提出人', 'text', 100, TRUE, NULL),
(@bug_table_id, 8, 'BUG 类型', 'select', 80, TRUE, '["BUG", "优化", "需求"]'),
(@bug_table_id, 9, '优先级', 'select', 80, TRUE, '["最高", "高", "中", "低"]'),
(@bug_table_id, 10, 'BUG 状态', 'select', 80, TRUE, '["待处理", "处理中", "待验证", "已关闭"]'),
(@bug_table_id, 11, '责任人', 'text', 100, TRUE, NULL);

-- 更新表格的列数
UPDATE `spreadsheet` SET `col_count` = 12 WHERE `id` = @bug_table_id;

-- 输出成功信息
SELECT '在线表格数据库初始化完成！' AS message;
SELECT CONCAT('创建了示例表格：', `name`) AS info FROM `spreadsheet` WHERE `id` = @bug_table_id;
