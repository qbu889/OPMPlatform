#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉推送系统 - 完整集成测试
测试完整流程：创建配置 -> 预览 -> 手动推送 -> 查看历史
"""
import unittest
import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app


class TestDingTalkPushIntegration(unittest.TestCase):
    """钉钉推送系统集成测试类"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # 测试配置数据
        cls.test_config = {
            'name': '集成测试推送',
            'description': '用于集成测试的推送任务',
            'webhook_url': 'https://oapi.dingtalk.com/robot/send?access_token=test_integration_token',
            'secret_key': 'SECtest123',
            'at_mobiles': ['13800138000'],
            'at_all': False,
            'message_type': 'markdown',
            'template_content': '# 📅 集成测试\n\n**时间**: {{ timestamp }}\n**数据**: {{ data }}',
            'data_source_config': {
                'type': 'static',
                'config': {
                    'data': {
                        'timestamp': '2026-04-21 12:00:00',
                        'data': 'integration test'
                    }
                }
            },
            'schedule_config': {
                'type': 'daily',
                'config': {
                    'times': ['12:00'],
                    'weekdays': [1, 2, 3, 4, 5],
                    'exclude_holidays': False
                }
            },
            'timezone': 'Asia/Shanghai',
            'enabled': True,
            'category': 'general',
            'priority': 5,
            'max_retries': 3,
            'timeout_seconds': 10
        }
        
        cls.created_config_id = None
    
    @classmethod
    def tearDownClass(cls):
        # 清理创建的测试数据
        if cls.created_config_id:
            try:
                cls.client.delete(f'/api/dingtalk-push/configs/{cls.created_config_id}')
            except:
                pass
        cls.app_context.pop()
    
    def test_01_create_config(self):
        """测试创建配置"""
        print("\n📝 测试: 创建配置")
        
        response = self.client.post(
            '/api/dingtalk-push/configs',
            data=json.dumps(self.test_config),
            content_type='application/json'
        )
        
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(result['success'])
        self.assertIn('id', result['data'])
        
        TestDingTalkPushIntegration.created_config_id = result['data']['id']
        print(f"✅ 配置创建成功，ID: {result['data']['id']}")
    
    def test_02_preview_template(self):
        """测试模板预览"""
        print("\n🔍 测试: 模板预览")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        preview_data = {
            'message_type': 'markdown',
            'template_content': self.test_config['template_content'],
            'sample_data': {
                'timestamp': '2026-04-21 12:00:00',
                'data': 'preview test'
            }
        }
        
        response = self.client.post(
            '/api/dingtalk-push/preview',
            data=json.dumps(preview_data),
            content_type='application/json'
        )
        
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        data = result['data']
        self.assertIn('rendered_content', data)
        self.assertIn('message_json', data)
        self.assertIn('variables_used', data)
        
        print("✅ 模板预览成功")
        print(f"   渲染内容长度: {len(data['rendered_content'])} 字符")
        print(f"   使用变量: {data['variables_used']}")
    
    def test_03_execute_push(self):
        """测试手动推送"""
        print("\n🚀 测试: 手动推送")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        response = self.client.post(f'/api/dingtalk-push/configs/{self.created_config_id}/execute')
        result = json.loads(response.data)
        
        # 推送可能会因为Webhook无效而失败，但API应该能正常调用
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        
        print("✅ 推送请求已提交")
    
    def test_04_get_history(self):
        """测试获取历史记录"""
        print("\n📋 测试: 获取推送历史")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        # 等待推送任务执行完成
        time.sleep(1)
        
        response = self.client.get(f'/api/dingtalk-push/history?config_id={self.created_config_id}')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        data = result['data']
        self.assertIn('list', data)
        self.assertIn('total', data)
        
        print(f"✅ 获取到 {len(data['list'])} 条历史记录，总数: {data['total']}")
    
    def test_05_get_history_detail(self):
        """测试获取历史详情"""
        print("\n🔍 测试: 获取历史详情")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        # 获取最新一条历史记录
        response = self.client.get(f'/api/dingtalk-push/history?config_id={self.created_config_id}&page=1&size=1')
        result = json.loads(response.data)
        
        if result['data']['list']:
            history_id = result['data']['list'][0]['id']
            
            response = self.client.get(f'/api/dingtalk-push/history/{history_id}')
            result = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(result['success'])
            self.assertIn('data', result)
            
            detail = result['data']
            self.assertIn('id', detail)
            self.assertIn('logs', detail)
            
            print(f"✅ 历史详情获取成功，ID: {detail['id']}")
        else:
            print("⚠️  没有找到历史记录（可能是Webhook无效导致推送失败）")
    
    def test_06_get_statistics(self):
        """测试获取统计数据"""
        print("\n📊 测试: 获取统计数据")
        
        if not self.created_config_id:
            self.skipTest("没有可用的配置ID")
        
        response = self.client.get(f'/api/dingtalk-push/statistics?config_id={self.created_config_id}&period=7d')
        result = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        
        data = result['data']
        self.assertIn('total_runs', data)
        self.assertIn('success_count', data)
        self.assertIn('failed_count', data)
        self.assertIn('success_rate', data)
        
        print(f"✅ 统计数据获取成功")
        print(f"   总运行: {data['total_runs']}, 成功: {data['success_count']}, 失败: {data['failed_count']}")
        print(f"   成功率: {data['success_rate']}%")


if __name__ == '__main__':
    unittest.main(verbosity=2)
