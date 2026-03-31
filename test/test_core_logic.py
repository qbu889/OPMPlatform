"""
test_core_logic.py - 核心业务逻辑单元测试

测试项目的核心业务逻辑，包括：
1. FPA 功能点解析与计算
2. Kafka 消息格式转换
3. 文档解析与生成
4. 工作量计算
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.fpa.fpa_generator_routes import parse_requirement_document, clean_function_point_name
from utils.format_matcher import FormatMatcher


class TestFPAParsing:
    """FPA 功能点解析测试"""
    
    def test_parse_empty_content(self):
        """测试解析空内容"""
        result = parse_requirement_document('')
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_parse_no_function_requirements(self):
        """测试解析没有功能需求章节的内容"""
        content = "# 项目介绍\n这是一个测试项目"
        result = parse_requirement_document(content)
        assert isinstance(result, list)
    
    def test_clean_function_point_name_with_slash(self):
        """测试清理功能点名称中的斜杠"""
        name = "查询/统计功能"
        cleaned = clean_function_point_name(name)
        assert "/" not in cleaned
        assert "和" in cleaned
    
    def test_clean_function_point_name_with_parentheses(self):
        """测试清理功能点名称中的括号"""
        name = "用户管理（增删改查）"
        cleaned = clean_function_point_name(name)
        assert "（" not in cleaned
        assert "(" not in cleaned
    
    def test_clean_function_point_name_with_quotes(self):
        """测试清理功能点名称中的引号"""
        name = '数据"同步"功能'
        cleaned = clean_function_point_name(name)
        assert '"' not in cleaned


class TestFormatMatcher:
    """格式匹配器测试"""
    
    def test_init(self):
        """测试初始化"""
        matcher = FormatMatcher()
        assert matcher is not None
    
    def test_match_empty(self):
        """测试空数据匹配"""
        matcher = FormatMatcher()
        result = matcher.match_format('', '')
        assert result is not None


class TestWorkloadCalculation:
    """工作量计算测试"""
    
    def test_calculation_parameters_exist(self):
        """测试工作量计算参数存在"""
        from routes.fpa.fpa_generator_routes import WORK_PARAMS
        
        assert '规模变更调整因子' in WORK_PARAMS
        assert '基准生产率' in WORK_PARAMS
        assert '调整因子' in WORK_PARAMS
        
        # 验证参数值范围合理
        assert WORK_PARAMS['规模变更调整因子'] > 0
        assert WORK_PARAMS['基准生产率'] > 0
    
    def test_fpa_columns_defined(self):
        """测试 FPA 列定义存在"""
        from routes.fpa.fpa_generator_routes import FPA_COLUMNS
        
        expected_columns = ['编号', '一级分类', '二级分类', '三级分类', 
                          '功能点名称', '功能点计数项', '类别', 'UFP', 
                          '重用程度', '修改类型', 'AFP', '备注']
        
        for col in expected_columns:
            assert col in FPA_COLUMNS


class TestRegexPatterns:
    """正则表达式模式测试"""
    
    def test_patterns_compiled(self):
        """测试预编译的正则表达式存在"""
        from routes.fpa.fpa_generator_routes import PATTERNS
        
        # 验证所有必需的模式都已编译
        required_patterns = [
            'level1', 'level2', 'level3', 'level4', 'level5',
            'bold', 'note_zh', 'zero_width', 'special_chars'
        ]
        
        for pattern_name in required_patterns:
            assert pattern_name in PATTERNS
            # 验证是编译的正则对象
            assert hasattr(PATTERNS[pattern_name], 'match') or hasattr(PATTERNS[pattern_name], 'sub')
    
    def test_keyword_patterns(self):
        """测试关键词匹配模式"""
        from routes.fpa.fpa_generator_routes import KEYWORD_PATTERNS
        
        # 验证所有类别的关键词模式
        categories = ['ilf_keywords', 'ei_keywords', 'eo_keywords', 'eq_keywords']
        
        for category in categories:
            assert category in KEYWORD_PATTERNS
            # 验证是编译的正则对象
            assert hasattr(KEYWORD_PATTERNS[category], 'search')


class TestFPAFlowIntegration:
    """FPA 流程集成测试"""
    
    def test_full_parse_flow(self):
        """测试完整的解析流程"""
        # 模拟简单的需求文档
        md_content = """
# 功能需求

## 用户管理

### 基础信息

#### 用户信息维护

##### 用户信息查询

**功能描述**: 查询用户基本信息

**输入**: 用户 ID

**输出**: 用户信息详情

**处理过程**: 根据用户 ID 查询数据库
"""
        
        result = parse_requirement_document(md_content)
        
        # 验证解析结果
        assert isinstance(result, list)
        # 应该至少解析出一个功能点
        assert len(result) > 0
        
        # 验证功能点结构
        if len(result) > 0:
            point = result[0]
            assert 'level5' in point
            assert '功能描述' in point
            assert '输入' in point
            assert '输出' in point
    
    def test_multiple_function_points(self):
        """测试多个功能点的解析"""
        md_content = """
# 功能需求

## 模块一

### 功能一

#### 功能点一

##### 功能点 1.1

**功能描述**: 测试功能 1

## 模块二

### 功能二

#### 功能点二

##### 功能点 2.1

**功能描述**: 测试功能 2
"""
        
        result = parse_requirement_document(md_content)
        
        # 应该解析出多个功能点
        assert len(result) >= 2


class TestErrorHandling:
    """错误处理测试"""
    
    def test_parse_malformed_markdown(self):
        """测试解析格式错误的 Markdown"""
        # 不规范的 Markdown 格式
        md_content = """
# 功能需求
##### 没有父级标题的功能点
**功能描述**: 测试
"""
        
        # 不应该抛出异常
        try:
            result = parse_requirement_document(md_content)
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"解析不应抛出异常：{e}")
    
    def test_parse_special_characters(self):
        """测试包含特殊字符的内容"""
        md_content = """
# 功能需求

## 特殊@#$%字符测试

### 功能<>?测试

#### 功能点&*()测试

##### 功能点名称{}[]

**功能描述**: 测试\|符号
"""
        
        try:
            result = parse_requirement_document(md_content)
            assert isinstance(result, list)
        except Exception as e:
            pytest.fail(f"应能处理特殊字符：{e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
