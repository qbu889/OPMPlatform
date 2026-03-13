-- ============================================
-- 清除 fpa_adjustment_factor 表中的重复数据
-- 保留每个唯一记录的第一条 (id 最小),删除其他重复记录
-- ============================================

-- 步骤 1: 查看清理前的重复数据
SELECT 
    factor_name,
    factor_category,
    option_name,
    score_value,
    COUNT(*) as count
FROM fpa_adjustment_factor
GROUP BY factor_name, factor_category, option_name, score_value
HAVING COUNT(*) > 1;

-- 步骤 2: 查看清理前总记录数
SELECT COUNT(*) as total_before FROM fpa_adjustment_factor;

-- 步骤 3: 删除重复数据 (核心操作)
DELETE t1 FROM fpa_adjustment_factor t1
INNER JOIN fpa_adjustment_factor t2 
WHERE 
    t1.id > t2.id AND 
    t1.factor_name = t2.factor_name AND
    t1.factor_category = t2.factor_category AND
    t1.option_name = t2.option_name AND
    t1.score_value = t2.score_value;

-- 步骤 4: 验证是否还有重复数据
SELECT 
    factor_name,
    factor_category,
    option_name,
    score_value,
    COUNT(*) as count
FROM fpa_adjustment_factor
GROUP BY factor_name, factor_category, option_name, score_value
HAVING COUNT(*) > 1;

-- 步骤 5: 查看清理后总记录数
SELECT COUNT(*) as total_after FROM fpa_adjustment_factor;

-- 步骤 6: 按类别统计清理后的数据分布
SELECT 
    factor_category,
    COUNT(*) as total_records
FROM fpa_adjustment_factor
GROUP BY factor_category
ORDER BY factor_category;

-- 步骤 7: 显示清理结果摘要
SELECT 
    '清理完成' as status,
    (SELECT COUNT(*) FROM fpa_adjustment_factor) as final_total,
    '请对比清理前后的总数' as note;
