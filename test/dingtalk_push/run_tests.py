#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉推送系统 - 测试运行脚本
运行所有测试用例并生成报告
"""
import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


def run_tests():
    """运行所有测试"""
    print("=" * 80)
    print("钉钉推送系统 - 自动化测试")
    print("=" * 80)
    
    # 发现测试用例
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # 添加测试模块
    from test.dingtalk_push import (
        test_dingtalk_push_config,
        test_dingtalk_push_integration
    )
    
    test_suite.addTests(test_loader.loadTestsFromModule(test_dingtalk_push_config))
    test_suite.addTests(test_loader.loadTestsFromModule(test_dingtalk_push_integration))
    
    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 输出总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 80)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
