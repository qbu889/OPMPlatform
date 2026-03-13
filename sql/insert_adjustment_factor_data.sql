-- 调整因子数据插入语句
-- 根据 /Users/linziwang/PycharmProjects/wordToWord/test/fpa/调整因子.xlsx 生成
-- 执行时间：2026-03-11

USE knowledge_base;

-- =============================================
-- 1. 应用类型调整因子 (行 3, 12-19)
-- =============================================
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('应用类型', '应用类型', '业务处理', 1.0, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 1),
('应用类型', '应用类型', '应用集成', 1.2, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 2),
('应用类型', '应用类型', '科技', 1.2, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 3),
('应用类型', '应用类型', '多媒体', 1.5, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 4),
('应用类型', '应用类型', '智能信息', 1.7, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 5),
('应用类型', '应用类型', '基础软件/支撑软件', 1.7, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 6),
('应用类型', '应用类型', '通信控制', 1.9, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 7),
('应用类型', '应用类型', '流程控制', 2.0, '=IF(C3=B12,D12,IF(C3=B13,D13,IF(C3=B14,D14,IF(C3=B15,D15,IF(C3=B16,D16,IF(C3=B17,D17,IF(C3=B18,D18,IF(C3=B19,D19,0))))))))', 8);

-- =============================================
-- 2. 质量特性调整因子 (行 4-7, 22-33)
-- =============================================
-- 2.1 分布式处理
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('分布式处理', '质量特性', '没有明示对分布式处理的需求事项', -1.0, '=IF(C4=C22,D22,IF(C4=C23,D23,IF(C4=C24,D24,-10)))', 1),
('分布式处理', '质量特性', '通过网络进行客户端/服务器及网络基础应用分布处理和传输', 0.0, '=IF(C4=C22,D22,IF(C4=C23,D23,IF(C4=C24,D24,-10)))', 2),
('分布式处理', '质量特性', '在多个服务器及处理器上同时相互执行计算机系统中的处理功能', 1.0, '=IF(C4=C22,D22,IF(C4=C23,D23,IF(C4=C24,D24,-10)))', 3);

-- 2.2 性能
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('性能', '质量特性', '没有明示对性能的特别需求事项或活动，因此提供基本性能', -1.0, '=IF(C5=C25,D25,IF(C5=C26,D26,IF(C5=C27,D27,-10)))', 4),
('性能', '质量特性', '应答时间或处理率对高峰时间或所有业务时间来说都很重要，对连动系统结束处理时间的限制', 0.0, '=IF(C5=C25,D25,IF(C5=C26,D26,IF(C5=C27,D27,-10)))', 5),
('性能', '质量特性', '为满足性能需求事项，要求设计阶段开始进行性能分析，或在设计、开发阶段使用分析工具', 1.0, '=IF(C5=C25,D25,IF(C5=C26,D26,IF(C5=C27,D27,-10)))', 6);

-- 2.3 可靠性
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('可靠性', '质量特性', '没有明示对可靠性的特别需求事项或活动，因此提供基本的可靠性', -1.0, '=IF(C6=C28,D28,IF(C6=C29,D29,IF(C6=C30,D30,-10)))', 7),
('可靠性', '质量特性', '发生故障时可轻易修复，带来一定不便或经济损失', 0.0, '=IF(C6=C28,D28,IF(C6=C29,D29,IF(C6=C30,D30,-10)))', 8),
('可靠性', '质量特性', '发生故障时很难复，发生重大经济损失或有生命危害', 1.0, '=IF(C6=C28,D28,IF(C6=C29,D29,IF(C6=C30,D30,-10)))', 9);

-- 2.4 多重站点
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('多重站点', '质量特性', '在相同用途的硬件或软件环境下运行', -1.0, '=IF(C7=C31,D31,IF(C7=C32,D32,IF(C7=C33,D33,-10)))', 10),
('多重站点', '质量特性', '在用途类似的硬件或软件环境下运行', 0.0, '=IF(C7=C31,D31,IF(C7=C32,D32,IF(C7=C33,D33,-10)))', 11),
('多重站点', '质量特性', '在不同用途的硬件或软件环境下运行', 1.0, '=IF(C7=C31,D31,IF(C7=C32,D32,IF(C7=C33,D33,-10)))', 12);

-- =============================================
-- 3. 开发语言调整因子 (行 8, 43-45)
-- =============================================
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('开发语言', '开发语言', 'C及其他同级别语言/平台', 1.2, '=IF(C8=B43,D43,IF(C8=B44,D44,IF(C8=B45,D45,0)))', 1),
('开发语言', '开发语言', 'JAVA、C++、C#及其他同级别语言/平台', 1.0, '=IF(C8=B43,D43,IF(C8=B44,D44,IF(C8=B45,D45,0)))', 2),
('开发语言', '开发语言', 'PowerBuilder、ASP及其他同级别语言/平台', 0.8, '=IF(C8=B43,D43,IF(C8=B44,D44,IF(C8=B45,D45,0)))', 3);

-- =============================================
-- 4. 开发团队背景调整因子 (行 9, 48-50)
-- =============================================
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('开发团队背景', '开发团队背景', '为本行业（政府）开发过类似的软件', 0.8, '=IF(C9=B48,D48,IF(C9=B49,D49,IF(C9=B50,D50,0)))', 1),
('开发团队背景', '开发团队背景', '为其他行业开发过类似的软件，或为本行业（政府）开发过不同但相关的软件', 1.0, '=IF(C9=B48,D48,IF(C9=B49,D49,IF(C9=B50,D50,0)))', 2),
('开发团队背景', '开发团队背景', '没有同类软件及本行业（政府）相关软件开发背景', 1.2, '=IF(C9=B48,D48,IF(C9=B49,D49,IF(C9=B50,D50,0)))', 3);

-- =============================================
-- 5. 规模计数时机调整因子 (行 36-39)
-- =============================================
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('规模计数时机', '规模变更调整系数', '估算早期', 1.39, '规模变更调整系数', 1),
('规模计数时机', '规模变更调整系数', '估算中期', 1.21, '规模变更调整系数', 2),
('规模计数时机', '规模变更调整系数', '估算晚期', 1.10, '规模变更调整系数', 3),
('规模计数时机', '规模变更调整系数', '项目完成', 1.00, '规模变更调整系数', 4);

-- =============================================
-- 6. 重用程度调整系数 (行 53-55)
-- =============================================
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('重用程度', '重用程度调整系数', '高', 0.3333, '=1/3', 1),
('重用程度', '重用程度调整系数', '中', 0.6667, '=2/3', 2),
('重用程度', '重用程度调整系数', '低', 1.0000, '=1/1', 3);

-- 说明：重用程度
-- 高：该功能在系统中有一样的功能模块反复出现，代码复用程度高
-- 中：该功能在系统中有一样的功能模块少量重复，代码复用程度中等
-- 低：该功能在系统中没有其它功能模块能够利旧，代码复用程度低

-- =============================================
-- 7. 修改类型调整系数 (行 58-60)
-- =============================================
-- 注意：fpa_adjustment_factor 表没有 description 字段，这里仅插入基本字段
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('修改类型', '修改类型调整系数', '新增', 1.0000, '=1/1', 1),
('修改类型', '修改类型调整系数', '修改', 0.8000, '0.8', 2),
('修改类型', '修改类型调整系数', '删除', 0.2000, '0.2', 3);

-- =============================================
-- 8. 功能点类型基准值 (行 63-67) - 仅供参考
-- =============================================
-- 这些数据是国标基准值，可以作为参考存储在单独的表中
-- 注意：fpa_adjustment_factor 表没有 description 字段
INSERT INTO fpa_adjustment_factor (factor_name, factor_category, option_name, score_value, formula, display_order) VALUES
('ILF', '功能点基准值', 'ILF 为内部逻辑文件数量', 7.0, '国标', 1),
('EIF', '功能点基准值', 'EIF 为外部接口文件数量', 5.0, '国标', 2),
('EI', '功能点基准值', 'EI 为外部输入数量', 4.0, '国标', 3),
('EO', '功能点基准值', 'EO 为外部输出数量', 5.0, '国标', 4),
('EQ', '功能点基准值', 'EQ 为外部查询数量', 4.0, '国标', 5);

-- =============================================
-- 验证插入数据
-- =============================================
SELECT 
    factor_category AS '因子分类',
    COUNT(*) AS '数量',
    GROUP_CONCAT(factor_name ORDER BY display_order SEPARATOR ', ') AS '因子名称列表'
FROM fpa_adjustment_factor
GROUP BY factor_category
ORDER BY MIN(display_order);

-- 查看所有数据
SELECT 
    id,
    factor_category AS '因子分类',
    factor_name AS '因子名称',
    option_name AS '选项名称',
    score_value AS '分值',
    formula AS '公式',
    display_order AS '显示顺序'
FROM fpa_adjustment_factor
ORDER BY factor_category, display_order;
