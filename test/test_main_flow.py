"""
test_main_flow.py - 主流程集成测试

测试项目的主要功能流程，包括：
1. FPA 功能点估算流程
2. Kafka 消息生成流程
3. 文档转换流程
4. 用户认证流程
"""

import pytest
from flask import Flask
from app import create_app
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope='module')
def app():
    """创建测试用的 Flask 应用"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['UPLOAD_FOLDER'] = '/tmp/test_uploads'
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestMainFlow:
    """主流程测试类"""
    
    def test_homepage_access(self, client):
        """测试首页访问"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_fpa_generator_page_access(self, client):
        """测试 FPA 生成器页面访问"""
        response = client.get('/fpa-generator')
        assert response.status_code == 200
    
    def test_kafka_generator_page_access(self, client):
        """测试 Kafka 生成器页面访问"""
        response = client.get('/kafka-generator')
        assert response.status_code == 200
    
    def test_document_convert_page_access(self, client):
        """测试文档转换页面访问"""
        response = client.get('/document-convert')
        assert response.status_code == 200
    
    def test_schedule_config_page_access(self, client):
        """测试排班配置页面访问"""
        response = client.get('/schedule-config')
        assert response.status_code == 200


class TestFPAFlow:
    """FPA 功能点估算流程测试"""
    
    def test_fpa_calculate_api(self, client):
        """测试 FPA 计算接口（空数据）"""
        # 测试空数据情况
        response = client.post('/fpa/calculate', json={})
        # 应该返回错误提示
        assert response.status_code in [200, 400]
    
    def test_fpa_category_rules_api(self, client):
        """测试 FPA 类别规则查询接口"""
        response = client.get('/fpa/category-rules/get-all')
        # 应该返回规则列表或空列表
        assert response.status_code == 200


class TestKafkaFlow:
    """Kafka 消息生成流程测试"""
    
    def test_kafka_generate_empty(self, client):
        """测试 Kafka 生成功能（空数据）"""
        response = client.post('/kafka-generator/generate', json={})
        # 应该返回错误或空结果
        assert response.status_code in [200, 400]
    
    def test_kafka_check_escape_api(self, client):
        """测试 Kafka 转义检查接口"""
        response = client.post('/kafka/check-escape', json={'content': ''})
        # 应该正常响应
        assert response.status_code == 200


class TestDocumentConvertFlow:
    """文档转换流程测试"""
    
    def test_word_to_markdown_empty(self, client):
        """测试 Word 转 Markdown（无文件）"""
        response = client.post('/word-to-md/convert')
        # 应该返回错误提示
        assert response.status_code in [200, 400]
    
    def test_markdown_to_word_empty(self, client):
        """测试 Markdown 转 Word（无文件）"""
        response = client.post('/markdown/upload')
        # 应该返回错误提示
        assert response.status_code in [200, 400]


class TestAuthFlow:
    """用户认证流程测试"""
    
    def test_login_page_access(self, client):
        """测试登录页面访问"""
        response = client.get('/auth/login')
        assert response.status_code == 200
    
    def test_register_page_access(self, client):
        """测试注册页面访问"""
        response = client.get('/auth/register')
        assert response.status_code == 200
    
    def test_login_with_invalid_credentials(self, client):
        """测试使用无效凭据登录"""
        response = client.post('/auth/login', json={
            'username': 'invalid_user',
            'password': 'wrong_password'
        })
        # 应该返回登录失败
        assert response.status_code in [200, 401, 403]
    
    def test_get_current_user_not_logged_in(self, client):
        """测试未登录时获取当前用户信息"""
        response = client.get('/auth/current-user')
        # 应该返回未登录错误
        assert response.status_code in [401, 403]


class TestScheduleFlow:
    """排班管理流程测试"""
    
    def test_schedule_holiday_api(self, client):
        """测试节假日查询接口"""
        response = client.get('/schedule/holidays?year=2026')
        # 应该返回节假日数据或空列表
        assert response.status_code == 200
    
    def test_schedule_roster_api(self, client):
        """测试排班表查询接口"""
        response = client.get('/schedule/roster?month=2026-03')
        # 应该返回排班数据或空列表
        assert response.status_code == 200


class TestAPIHealth:
    """API 健康检查测试"""
    
    def test_api_responds(self, client):
        """测试 API 是否有响应"""
        # 测试任意一个 API 端点
        response = client.get('/favicon.ico')
        # 只要不是 500 错误就说明服务正常
        assert response.status_code != 500


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
