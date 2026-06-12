"""
diff_routes.py 接口测试用例
测试模块：JSON 对比和格式化接口
"""

import pytest
import requests
import json
from datetime import datetime


class TestDiffCompareAPI:
    """JSON 对比接口测试类"""
    
    # 测试基础配置
    BASE_URL = "http://localhost:5000/api/diff/compare"  # 根据实际情况修改
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def valid_json_data(self):
        """生成有效的测试 JSON 数据"""
        return {
            "left": json.dumps({
                "name": "张三",
                "age": 25,
                "email": "zhangsan@example.com",
                "address": {
                    "city": "北京",
                    "district": "朝阳区"
                },
                "hobbies": ["阅读", "运动"]
            }, ensure_ascii=False),
            "right": json.dumps({
                "name": "张三",
                "age": 26,
                "email": "zhangsan_new@example.com",
                "address": {
                    "city": "上海",
                    "district": "浦东新区"
                },
                "hobbies": ["阅读", "旅行"]
            }, ensure_ascii=False),
            "options": {
                "strict_mode": False,
                "ignore_case": False,
                "ignore_whitespace": False
            }
        }
    
    # ============ 正常场景测试 ============
    
    def test_compare_success_basic(self, client):
        """[正常] 基础 JSON 对比成功"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"a": 1, "b": 2}),
                "right": json.dumps({"a": 1, "b": 3})
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'stats' in data['data']
    
    def test_compare_success_with_options(self, client):
        """[正常] 带选项的 JSON 对比成功"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"name": "张三", "age": 25}),
                "right": json.dumps({"name": "李四", "age": 25}),
                "options": {"ignore_case": True}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_compare_success_complex_structure(self, client):
        """[正常] 复杂嵌套结构对比成功"""
        left_data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["admin"]},
                {"id": 2, "name": "Bob", "roles": ["user"]}
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        right_data = {
            "users": [
                {"id": 1, "name": "Alice", "roles": ["admin", "editor"]},
                {"id": 2, "name": "Bob", "roles": ["user"]},
                {"id": 3, "name": "Charlie", "roles": ["user"]}
            ],
            "metadata": {
                "version": "1.1",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps(left_data, ensure_ascii=False),
                "right": json.dumps(right_data, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_compare_success_empty_objects(self, client):
        """[正常] 空对象对比"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({}),
                "right": json.dumps({})
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_compare_success_identical_json(self, client):
        """[正常] 相同 JSON 对比"""
        json_str = json.dumps({"test": "value", "number": 123}, ensure_ascii=False)
        
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json_str,
                "right": json_str
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    # ============ 异常场景测试 ============
    
    def test_compare_empty_request_body(self, client):
        """[异常] 请求体为空"""
        response = client.post(
            '/api/diff/compare',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_compare_missing_left_json(self, client):
        """[异常] 缺少左侧 JSON"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "right": json.dumps({"a": 1})
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_compare_missing_right_json(self, client):
        """[异常] 缺少右侧 JSON"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"a": 1})
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_compare_invalid_left_json(self, client):
        """[异常] 左侧 JSON 格式错误"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": "{invalid json}",
                "right": json.dumps({"a": 1})
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_compare_invalid_right_json(self, client):
        """[异常] 右侧 JSON 格式错误"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"a": 1}),
                "right": "{invalid json}"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_compare_invalid_json_format(self, client):
        """[异常] 非 JSON 格式数据"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": "not json at all",
                "right": "also not json"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_compare_special_characters(self, client):
        """[异常] 包含特殊字符的 JSON"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"text": "你好，世界！🎉"}, ensure_ascii=False),
                "right": json.dumps({"text": "Hello, World! 🌍"}, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_compare_unicode_content(self, client):
        """[异常] 中文内容对比"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"姓名": "张三", "年龄": 25}, ensure_ascii=False),
                "right": json.dumps({"姓名": "李四", "年龄": 26}, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    # ============ 边界条件测试 ============
    
    def test_compare_very_large_json(self, client):
        """[边界] 超大 JSON 数据对比"""
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps(large_data, ensure_ascii=False),
                "right": json.dumps(large_data, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_compare_deeply_nested_json(self, client):
        """[边界] 深层嵌套 JSON"""
        nested = {"level1": {"level2": {"level3": {"level4": {"level5": "value"}}}}}
        
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps(nested, ensure_ascii=False),
                "right": json.dumps(nested, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_compare_array_comparison(self, client):
        """[边界] 数组对比"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({"items": [1, 2, 3, 4, 5]}),
                "right": json.dumps({"items": [1, 2, 3, 4, 5, 6]})
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_compare_mixed_types(self, client):
        """[边界] 混合数据类型"""
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps({
                    "string": "text",
                    "number": 123,
                    "float": 45.67,
                    "boolean": True,
                    "null_value": None,
                    "array": [1, 2, 3],
                    "object": {"nested": "value"}
                }),
                "right": json.dumps({
                    "string": "text",
                    "number": 123,
                    "float": 45.67,
                    "boolean": False,
                    "null_value": None,
                    "array": [1, 2, 3],
                    "object": {"nested": "value"}
                })
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    # ============ 性能测试 ============
    
    def test_compare_performance(self, client):
        """[性能] 对比接口响应时间"""
        import time
        
        data = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        start_time = time.time()
        response = client.post(
            '/api/diff/compare',
            data=json.dumps({
                "left": json.dumps(data, ensure_ascii=False),
                "right": json.dumps(data, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 5.0, f"响应时间 {elapsed:.2f}s 超过阈值 5s"


class TestDiffFormatAPI:
    """JSON 格式化接口测试类"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    # ============ 正常场景测试 ============
    
    def test_format_success_basic(self, client):
        """[正常] 基础 JSON 格式化成功"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({
                "json": '{"a":1,"b":2}'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
    
    def test_format_success_chinese(self, client):
        """[正常] 中文内容格式化"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({
                "json": json.dumps({"姓名": "张三", "年龄": 25}, ensure_ascii=False)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_format_success_nested(self, client):
        """[正常] 嵌套 JSON 格式化"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({
                "json": json.dumps({
                    "user": {
                        "name": "Alice",
                        "address": {
                            "city": "Beijing"
                        }
                    }
                })
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    # ============ 异常场景测试 ============
    
    def test_format_empty_json(self, client):
        """[异常] 缺少 JSON 数据"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_format_invalid_json(self, client):
        """[异常] 无效 JSON"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({
                "json": "{invalid json}"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_format_empty_string(self, client):
        """[异常] 空字符串"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({
                "json": ""
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_format_not_json_string(self, client):
        """[异常] 非 JSON 字符串"""
        response = client.post(
            '/api/diff/format',
            data=json.dumps({
                "json": "not a json string"
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
