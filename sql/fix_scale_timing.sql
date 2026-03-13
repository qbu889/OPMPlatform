-- 修复规模计数时机的 score_value 值
-- 根据 Excel 公式更新为正确的值

-- 估算早期 (D36) - 概算、预算阶段
UPDATE fpa_adjustment_factor 
SET score_value = '1.39'
WHERE factor_category = '规模变更调整系数' 
AND option_name = '估算早期';

-- 估算中期 (D37) - 投标、项目计划阶段
UPDATE fpa_adjustment_factor 
SET score_value = '1.21'
WHERE factor_category = '规模变更调整系数' 
AND option_name = '估算中期';

-- 估算晚期 (D38) - 需求分析阶段
UPDATE fpa_adjustment_factor 
SET score_value = '1.10'
WHERE factor_category = '规模变更调整系数' 
AND option_name = '估算晚期';

-- 项目完成 (D39) - 项目交付后及运维阶段
UPDATE fpa_adjustment_factor 
SET score_value = '1.00'
WHERE factor_category = '规模变更调整系数' 
AND option_name = '项目完成';

-- 验证更新结果
SELECT id, option_name, score_value 
FROM fpa_adjustment_factor
WHERE factor_category = '规模变更调整系数'
ORDER BY id;
