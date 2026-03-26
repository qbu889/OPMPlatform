-- 为 faq_preview_cache 表添加进度跟踪字段
-- 用于智能客服文档上传进度显示

USE knowledge_base;

-- 添加进度跟踪字段（如果不存在则添加）
-- 注意：MySQL 不支持 IF NOT EXISTS，需要手动检查

-- 添加 total_sections 字段
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'knowledge_base' 
  AND TABLE_NAME = 'faq_preview_cache' 
  AND COLUMN_NAME = 'total_sections';

SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE faq_preview_cache ADD COLUMN total_sections INT DEFAULT 0 COMMENT \'总功能点数量\'', 
    'SELECT \'Column total_sections already exists\' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 processed_sections 字段
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'knowledge_base' 
  AND TABLE_NAME = 'faq_preview_cache' 
  AND COLUMN_NAME = 'processed_sections';

SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE faq_preview_cache ADD COLUMN processed_sections INT DEFAULT 0 COMMENT \'已处理的功能点数量\'', 
    'SELECT \'Column processed_sections already exists\' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 添加 faqs_extracted 字段
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'knowledge_base' 
  AND TABLE_NAME = 'faq_preview_cache' 
  AND COLUMN_NAME = 'faqs_extracted';

SET @sql = IF(@col_exists = 0, 
    'ALTER TABLE faq_preview_cache ADD COLUMN faqs_extracted INT DEFAULT 0 COMMENT \'已提取的 FAQ 数量\'', 
    'SELECT \'Column faqs_extracted already exists\' AS message');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 显示表结构验证
DESCRIBE faq_preview_cache;
