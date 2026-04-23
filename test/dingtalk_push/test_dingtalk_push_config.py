#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉推送系统 - 配置管理 API 测试
测试配置的 CRUD、启用/禁用、筛选等核心功能
"""
import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app


class TestDingTalkPushConfig(unittest.TestCase):
    """配置管理测试类"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        cls.test_config = {
            'name': '测试排班推送',
            'description': '用于测试的排班推送任务',
            'webhook_url': 'https://oapi.dingtalk.com/robot/send?access_token=test_token_123456',
            'secret_key': 'SECtest123',
            'at_mobiles': ['13800138000', '13900139000'],
            'at_all': False,
            'message_type': 'markdown',
            'template_content': '# 📅 排班推送\n\n**今天**: {{ today }}\n{% for slot in schedule %}\n- {{ slot.time }}: {{ slot.staff }}\n{% endfor %}',
            'data_source_config': {
                'type': 'static',
                'config': {
                    'data': {
                        'today': '2026-04-21',
                        'schedule': [
                            {'time': '8:00-9:00', 'staff': '张三'},
                            {'time': '9:00-12:00', 'staff': '李四'}
                        ]
                    }
                }
            },
            'schedule_config': {
                'type': 'daily',
                'config': {
                    'times': ['08:00', '18:00'],
                    'weekdays': [1, 2, 3, 4, 5],
                    'exclude_holidays': True
                }
            },
            'timezone': 'Asia/Shanghai',
            'enabled': True,
            'category': 'roster',
            'priority': 5,
            'max_retries': 3,
            'timeout_seconds': 10
        }
        
        cls.created_config_id = None
    
    @classmethod
    def tearDownClass(cls):
        if cls.created_config_id:
            try:
                cls.client.delete(f'/api/dingtalk-push/configs/{cls.created_config_id}')
            except:
                pass
        cls.app_context.pop()
    
    def test_01_create_config(self):
        """测试创建配置"""
        print("\n📝 测试: 创建推送配置")
        
        response = self.client.post(
            '/api/dingtalk-push/configs',
            data=json.dumps(self.test_config),
            content_type='application/json'
        )
        
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result['success'])
        self.assertIn('id', result['data'])
        
        TestDingTalkPushConfig.created_config_id = result['data']['id']
        print(f"✅ 配置创建成功，ID: {result['data']['id']}")
    
    def test_02_get_config_list(self):
        """测试获取配置列表"""
        print("\n📋 测试: 获取配置列表")
        
        response = self.client.get('/api/dingtalk-push/configs?page=1&size=10')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        self.assertIn('list', result['data'])
        self.assertIn('total', result['data'])
        
        print(f"✅ 获取到 {len(result['data']['list'])} 条配置")
    
    def test_03_get_config_detail(self):
        """测试获取配置详情"""
        print("\n🔍 测试: 获取配置详情")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        response = self.client.get(f'/api/dingtalk-push/configs/{self.created_config_id}')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        config = result['data']
        self.assertEqual(config['name'], self.test_config['name'])
        self.assertEqual(config['category'], self.test_config['category'])
        
        print(f"✅ 配置详情获取成功: {config['name']}")
    
    def test_04_update_config(self):
        """测试更新配置"""
        print("\n✏️  测试: 更新配置")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        update_data = {
            'name': '更新后的测试排班推送',
            'description': '已更新的描述',
            'priority': 8
        }
        
        response = self.client.put(
            f'/api/dingtalk-push/configs/{self.created_config_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        
        print("✅ 配置更新成功")
    
    def test_05_toggle_config(self):
        """测试启用/禁用配置"""
        print("\n🔄 测试: 切换配置状态")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        # 禁用
        response = self.client.patch(
            f'/api/dingtalk-push/configs/{self.created_config_id}/toggle',
            data=json.dumps({'enabled': False}),
            content_type='application/json'
        )
        
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        print("✅ 配置已禁用")
        
        # 重新启用
        response = self.client.patch(
            f'/api/dingtalk-push/configs/{self.created_config_id}/toggle',
            data=json.dumps({'enabled': True}),
            content_type='application/json'
        )
        
        result = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        print("✅ 配置已重新启用")
    
    def test_06_filter_configs(self):
        """测试筛选配置"""
        print("\n🔎 测试: 筛选配置")
        
        # 按分类筛选
        response = self.client.get('/api/dingtalk-push/configs?category=roster')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        print(f"✅ 按分类筛选成功")
        
        # 按状态筛选
        response = self.client.get('/api/dingtalk-push/configs?enabled=true')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        print(f"✅ 按状态筛选成功")
    
    def test_07_delete_config(self):
        """测试删除配置"""
        print("\n🗑️  测试: 删除配置")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        response = self.client.delete(f'/api/dingtalk-push/configs/{self.created_config_id}')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        
        print("✅ 配置删除成功")
        TestDingTalkPushConfig.created_config_id = None


if __name__ == '__main__':
    unittest.main(verbosity=2)
