-- 关键词修改历史记录表
CREATE TABLE IF NOT EXISTS keyword_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword_type TEXT NOT NULL,  -- 'person_keywords' 或 'system_keywords'
    keyword TEXT NOT NULL,       -- 关键词内容
    action TEXT NOT NULL,        -- 'add', 'edit', 'delete', 'snapshot'
    original_keyword TEXT,       -- 原关键词（编辑时）
    operator TEXT DEFAULT 'system',  -- 操作者
    remark TEXT,                 -- 备注
    version_snapshot TEXT,       -- 版本快照（JSON 格式，保存当时所有关键词）
    is_snapshot BOOLEAN DEFAULT 0,  -- 是否为完整版本快照
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 操作时间
);

-- 创建索引提高查询效率
CREATE INDEX IF NOT EXISTS idx_keyword_type ON keyword_history(keyword_type);
CREATE INDEX IF NOT EXISTS idx_created_at ON keyword_history(created_at);
CREATE INDEX IF NOT EXISTS idx_is_snapshot ON keyword_history(is_snapshot);
