-- 为 fpa_adjustment_factor 表添加 description 字段
-- 执行时间：2026-03-11

USE knowledge_base;

-- 检查字段是否已存在，如果不存在则添加
ALTER TABLE fpa_adjustment_factor 
ADD COLUMN IF NOT EXISTS description TEXT COMMENT '描述说明' 
AFTER display_order;

-- 验证字段添加成功
DESCRIBE fpa_adjustment_factor;

-- 如果有 description 字段，可以更新之前插入的数据
-- UPDATE fpa_adjustment_factor 
-- SET description = '本期项目新增的功能模块'
-- WHERE factor_name = '修改类型' AND option_name = '新增';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '修改往期项目的功能模块'
-- WHERE factor_name = '修改类型' AND option_name = '修改';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '删除往期项目的功能模块'
-- WHERE factor_name = '修改类型' AND option_name = '删除';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '内部逻辑文件 (Internal Logical File)'
-- WHERE factor_name = 'ILF';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '外部接口文件 (External Interface File)'
-- WHERE factor_name = 'EIF';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '外部输入 (External Input)'
-- WHERE factor_name = 'EI';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '外部输出 (External Output)'
-- WHERE factor_name = 'EO';
-- 
-- UPDATE fpa_adjustment_factor 
-- SET description = '外部查询 (External Query)'
-- WHERE factor_name = 'EQ';
