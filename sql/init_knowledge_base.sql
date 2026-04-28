-- =============================================
-- Knowledge Base 数据库初始化脚本
-- 数据库: knowledge_base
-- 字符集: utf8mb4
-- 创建时间: 2026-04-28
-- =============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `knowledge_base` 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `knowledge_base`;

-- =============================================
-- 1. 文档表 (documents)
-- 用于存储上传的文档信息
-- =============================================
DROP TABLE IF EXISTS `documents`;
CREATE TABLE `documents` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '文档ID',
  `filename` VARCHAR(255) NOT NULL COMMENT '文件名',
  `original_filename` VARCHAR(255) COMMENT '原始文件名',
  `file_type` VARCHAR(50) COMMENT '文件类型',
  `file_size` INT COMMENT '文件大小(字节)',
  `upload_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
  `content_hash` VARCHAR(255) COMMENT '内容哈希值',
  `status` VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/deleted',
  `metadata` TEXT COMMENT '元数据(JSON格式)',
  `created_by` INT COMMENT '创建者ID',
  INDEX `idx_upload_time` (`upload_time`),
  INDEX `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文档管理表';

-- =============================================
-- 2. 专业领域表 (categories)
-- 用于管理FAQ的分类/领域
-- =============================================
DROP TABLE IF EXISTS `categories`;
CREATE TABLE `categories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '领域ID',
  `name` VARCHAR(100) NOT NULL UNIQUE COMMENT '领域名称',
  `description` TEXT COMMENT '领域描述',
  `color` VARCHAR(20) DEFAULT '#1890ff' COMMENT '显示颜色',
  `is_active` TINYINT DEFAULT 1 COMMENT '是否激活: 1-激活, 0-禁用',
  `sort_order` INT DEFAULT 0 COMMENT '排序顺序',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX `idx_name` (`name`),
  INDEX `idx_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业领域分类表';

-- =============================================
-- 3. FAQ表 (faqs)
-- 知识库核心表，存储问答对
-- =============================================
DROP TABLE IF EXISTS `faqs`;
CREATE TABLE `faqs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'FAQ ID',
  `question` TEXT NOT NULL COMMENT '问题',
  `answer` TEXT NOT NULL COMMENT '答案',
  `document_id` INT COMMENT '关联文档ID',
  `category` VARCHAR(100) COMMENT '分类',
  `domain_id` INT COMMENT '专业领域ID',
  `tags` TEXT COMMENT '标签(逗号分隔)',
  `similarity_score` FLOAT DEFAULT 0.0 COMMENT '相似度分数',
  `view_count` INT DEFAULT 0 COMMENT '浏览次数',
  `is_verified` TINYINT DEFAULT 0 COMMENT '是否已验证: 1-已验证, 0-未验证',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON DELETE SET NULL,
  INDEX `idx_question` (`question`(255)),
  INDEX `idx_category` (`category`),
  INDEX `idx_domain` (`domain_id`),
  INDEX `idx_tags` (`tags`(255)),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='FAQ知识库表';

-- =============================================
-- 4. 对话历史表 (conversation_history)
-- 存储用户与AI客服的对话记录
-- =============================================
DROP TABLE IF EXISTS `conversation_history`;
CREATE TABLE `conversation_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
  `session_id` VARCHAR(100) NOT NULL COMMENT '会话ID',
  `user_id` INT COMMENT '用户ID',
  `message_role` VARCHAR(20) NOT NULL COMMENT '消息角色: user/assistant/system',
  `message_content` TEXT NOT NULL COMMENT '消息内容',
  `related_faq_ids` TEXT COMMENT '相关FAQ IDs(JSON数组)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
  INDEX `idx_session` (`session_id`),
  INDEX `idx_user` (`user_id`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话历史记录表';

-- =============================================
-- 初始化数据 - 专业领域
-- =============================================
INSERT INTO `categories` (`name`, `description`, `color`, `is_active`, `sort_order`) VALUES
('系统使用', '关于系统功能和使用方法的常见问题', '#1890ff', 1, 1),
('账户管理', '账户注册、登录、权限等相关问题', '#52c41a', 1, 2),
('数据处理', '数据导入、导出、转换等问题', '#faad14', 1, 3),
('API接口', 'API调用、集成相关问题', '#722ed1', 1, 4),
('故障排查', '常见错误和解决方案', '#f5222d', 1, 5);

-- =============================================
-- 初始化数据 - 示例FAQ
-- =============================================
INSERT INTO `faqs` (`question`, `answer`, `category`, `domain_id`, `tags`, `is_verified`) VALUES
('如何上传文档？', '在系统首页点击"上传文档"按钮，选择您要上传的文件（支持Word、Excel、PDF等格式），然后点击"确定"即可。上传成功后，您可以在"我的文档"中查看和管理已上传的文档。', '系统使用', 1, '上传,文档,操作', 1),
('忘记密码怎么办？', '您可以通过以下方式重置密码：\n1. 在登录页面点击"忘记密码"\n2. 输入您的注册邮箱\n3. 系统会发送重置链接到您的邮箱\n4. 点击链接设置新密码\n\n如果收不到邮件，请检查垃圾邮件箱或联系管理员。', '账户管理', 2, '密码,重置,登录', 1),
('如何将Excel转换为Word？', '使用系统的Excel转Word功能：\n1. 进入"工具中心" -> "Excel转Word"\n2. 上传Excel文件\n3. 选择转换模板\n4. 点击"开始转换"\n5. 下载生成的Word文档\n\n系统会自动保持原有的格式和样式。', '数据处理', 3, 'Excel,Word,转换', 1),
('API认证方式是什么？', '本系统采用JWT Token认证方式：\n1. 调用 /api/auth/login 接口获取token\n2. 在后续请求的Header中添加: Authorization: Bearer {token}\n3. Token有效期为24小时\n4. 过期后需要重新登录获取新token', 'API接口', 4, 'API,认证,Token', 1),
('系统支持哪些文件格式？', '系统支持以下文件格式：\n- 文档类: .doc, .docx, .pdf, .txt, .md\n- 表格类: .xls, .xlsx, .csv\n- 其他: .json, .xml\n\n单个文件大小限制为50MB。', '系统使用', 1, '格式,支持,文件', 1),
('如何批量导入FAQ？', '批量导入FAQ步骤：\n1. 下载FAQ导入模板（Excel格式）\n2. 按照模板格式填写问题和答案\n3. 进入"知识库管理" -> "批量导入"\n4. 上传填好的Excel文件\n5. 系统会自动解析并导入\n\n注意：确保Excel编码为UTF-8。', '数据处理', 3, 'FAQ,批量,导入', 1),
('对话历史保存多久？', '对话历史默认保存30天。超过30天的记录会被自动清理。如需长期保存，可以：\n1. 手动导出对话记录\n2. 联系管理员调整保留期限\n3. 将重要对话收藏到知识库', '系统使用', 1, '对话,历史,保存', 1),
('如何提高搜索准确度？', '提高搜索准确度的建议：\n1. 使用更具体的关键词\n2. 添加标签进行分类\n3. 完善FAQ的问题描述\n4. 定期更新和维护知识库\n5. 使用专业领域过滤\n\n系统会使用智能匹配算法，综合考虑关键词、相似度和浏览次数。', '系统使用', 1, '搜索,准确度,优化', 1),
('遇到系统错误怎么办？', '遇到系统错误时：\n1. 记录错误信息和截图\n2. 刷新页面重试\n3. 清除浏览器缓存\n4. 检查网络连接\n5. 查看系统日志\n6. 联系技术支持并提供错误详情\n\n大部分临时错误可以通过刷新解决。', '故障排查', 5, '错误,故障,解决', 1),
('如何修改个人信息？', '修改个人信息的步骤：\n1. 登录后点击右上角头像\n2. 选择"个人中心"\n3. 点击"编辑资料"\n4. 修改需要更新的信息\n5. 点击"保存"\n\n注意：用户名和邮箱修改可能需要重新验证。', '账户管理', 2, '个人信息,修改,资料', 1);

-- =============================================
-- 初始化数据 - 示例文档记录
-- =============================================
INSERT INTO `documents` (`filename`, `original_filename`, `file_type`, `file_size`, `content_hash`, `status`, `metadata`) VALUES
('user_manual_v1.pdf', '用户手册v1.pdf', 'application/pdf', 2048576, 'a1b2c3d4e5f6', 'active', '{"pages": 50, "author": "技术团队"}'),
('api_guide.docx', 'API开发指南.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 1024000, 'f6e5d4c3b2a1', 'active', '{"version": "2.0", "language": "zh-CN"}'),
('faq_template.xlsx', 'FAQ导入模板.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 51200, '123456abcdef', 'active', '{"sheets": 2, "rows": 100}');

-- =============================================
-- 完成提示
-- =============================================
SELECT '✓ knowledge_base 数据库初始化完成！' AS status;
SELECT COUNT(*) AS categories_count FROM categories;
SELECT COUNT(*) AS faqs_count FROM faqs;
SELECT COUNT(*) AS documents_count FROM documents;
