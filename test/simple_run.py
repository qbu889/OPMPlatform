#!/usr/bin/env python3
"""
简单运行测试文件
"""

from playwright.sync_api import sync_playwright
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.test_kafka_generator_e2e import TestKafkaGeneratorE2E
import time


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Kafka Generator 测试运行")
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
            # 初始化
            print("📱 初始化页面...")
            page.goto(test_instance.BASE_URL)
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            print("✅ 页面加载完成！")
            print()
            
            # 测试 1
            print("=" * 60)
            print("🔍 测试 1: 页面加载和标题验证")
            print("=" * 60)
            try:
                test_instance.test_01_page_load_and_title(page)
                print("✅ 测试 1 通过！")
            except Exception as e:
                print(f"❌ 测试 1 失败: {e}")
            print()
            time.sleep(1)
            
            # 测试 2
            print("=" * 60)
            print("🔍 测试 2: 加载示例数据功能")
            print("=" * 60)
            try:
                test_instance.test_02_load_sample_data(page)
                print("✅ 测试 2 通过！")
            except Exception as e:
                print(f"❌ 测试 2 失败: {e}")
            print()
            time.sleep(1)
            
            # 测试 3
            print("=" * 60)
            print("🔍 测试 3: 生成 Kafka 消息功能")
            print("=" * 60)
            try:
                test_instance.test_03_generate_kafka_message(page)
                print("✅ 测试 3 通过！")
            except Exception as e:
                print(f"❌ 测试 3 失败: {e}")
            print()
            time.sleep(1)
            
            print("=" * 60)
            print("🎉 主要测试完成！")
            print("=" * 60)
            print("\n💡 浏览器保持打开中...")
            print("按 Enter 键关闭浏览器")
            input()
            
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            print("\n按 Enter 键关闭浏览器")
            input()
            
        finally:
            page.close()
            browser.close()


if __name__ == "__main__":
    main()
