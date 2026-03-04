-- 为 roster 表添加备注字段和更新时间字段
-- 执行此脚本前请确保已备份数据
-- 注意：如果字段已存在会报错，可以忽略错误继续执行
use schedule ;
-- 添加 is_main 字段
ALTER TABLE roster ADD COLUMN is_main BOOLEAN DEFAULT FALSE COMMENT '是否为主班' AFTER staff_name;

-- 添加 rotation_index 字段
ALTER TABLE roster ADD COLUMN rotation_index INT DEFAULT 0 COMMENT '轮换索引' AFTER is_main;

-- 添加 remark 字段
ALTER TABLE roster ADD COLUMN remark VARCHAR(200) COMMENT '备注 (如：因请假调整)' AFTER rotation_index;

-- 添加 created_at 字段
ALTER TABLE roster ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER remark;

-- 显示修改后的表结构
SHOW CREATE TABLE roster;
