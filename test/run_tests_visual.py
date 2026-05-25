#!/usr/bin/env python3
"""
运行测试文件并在浏览器中看到操作
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
from test.test_kafka_generator_e2e import TestKafkaGeneratorE2E


def run_tests_visually():
    """可视化运行测试"""
    print("=" * 60)
    print("🚀 Kafka Generator 可视化测试运行")
    print("=" * 60)
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=600
        )
        page = browser.new_page()
        
        test_instance = TestKafkaGeneratorE2E()
        test_instance.BASE_URL = "http://8.146.228.47:5173/kafka-generator"
        
        try:
            # 初始化页面
            print("📱 初始化页面...")
            page.goto(test_instance.BASE_URL)
            page.wait_for_load_state("networkidle")
            print("✅ 页面初始化完成！")
            print()
            
            # 运行测试 1
            print("=" * 60)
            print("🔍 测试 1: 页面加载和标题验证")
            print("=" * 60)
            try:
                test_instance.test_01_page_load_and_title(page)
                print("✅ 测试 1 通过！")
            except Exception as e:
                print(f"❌ 测试 1 失败: {e}")
            print()
            
            # 运行测试 2
            print("=" * 60)
            print("🔍 测试 2: 加载示例数据功能")
            print("=" * 60)
            try:
                test_instance.test_02_load_sample_data(page)
                print("✅ 测试 2 通过！")
            except Exception as e:
                print(f"❌ 测试 2 失败: {e}")
            print()
            
            # 运行测试 3
            print("=" * 60)
            print("🔍 测试 3: 生成 Kafka 消息功能")
            print("=" * 60)
            try:
                test_instance.test_03_generate_kafka_message(page)
                print("✅ 测试 3 通过！")
            except Exception as e:
                print(f"❌ 测试 3 失败: {e}")
            print()
            
            # 运行测试 4
            print("=" * 60)
            print("🔍 测试 4: 清除所有字段功能")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_04_clear_all_fields(page)
                print("✅ 测试 4 通过！")
            except Exception as e:
                print(f"❌ 测试 4 失败: {e}")
            print()
            
            # 运行测试 5
            print("=" * 60)
            print("🔍 测试 5: 字段映射管理按钮")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_05_field_mapping_buttons(page)
                print("✅ 测试 5 通过！")
            except Exception as e:
                print(f"❌ 测试 5 失败: {e}")
            print()
            
            # 运行测试 6
            print("=" * 60)
            print("🔍 测试 6: 字段字典管理功能")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_06_field_dictionary_management(page)
                print("✅ 测试 6 通过！")
            except Exception as e:
                print(f"❌ 测试 6 失败: {e}")
            print()
            
            # 运行测试 7
            print("=" * 60)
            print("🔍 测试 7: 新增字典项功能")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_07_add_dictionary_item(page)
                print("✅ 测试 7 通过！")
            except Exception as e:
                print(f"❌ 测试 7 失败: {e}")
            print()
            
            # 运行测试 8
            print("=" * 60)
            print("🔍 测试 8: ES 源数据验证")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_08_es_data_validation(page)
                print("✅ 测试 8 通过！")
            except Exception as e:
                print(f"❌ 测试 8 失败: {e}")
            print()
            
            # 运行测试 9
            print("=" * 60)
            print("🔍 测试 9: 页面导航功能")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_09_page_navigation(page)
                print("✅ 测试 9 通过！")
            except Exception as e:
                print(f"❌ 测试 9 失败: {e}")
            print()
            
            # 运行测试 10
            print("=" * 60)
            print("🔍 测试 10: 登录/注册功能")
            print("=" * 60)
            try:
                # 重新加载页面
                page.goto(test_instance.BASE_URL)
                page.wait_for_load_state("networkidle")
                
                test_instance.test_10_login_registration(page)
                print("✅ 测试 10 通过！")
            except Exception as e:
                print(f"❌ 测试 10 失败: {e}")
            print()
            
            print("=" * 60)
            print("🎉 可视化测试完成！")
            print("=" * 60)
            print("\n💡 浏览器将保持打开，您可以继续操作查看。")
            print("按 Enter 键关闭浏览器...")
            input()
            
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()
            print("\n按 Enter 键关闭浏览器...")
            input()
            
        finally:
            page.close()
            browser.close()


if __name__ == "__main__":
    run_tests_visually()
