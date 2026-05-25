#!/usr/bin/env python3
"""
Kafka Generator 可视化测试脚本
在浏览器中显示操作过程
"""

from playwright.sync_api import sync_playwright
import time


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Kafka Generator 可视化测试")
    print("=" * 60)
    
    BASE_URL = "http://8.146.228.47:5173/kafka-generator"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=600
        )
        
        page = browser.new_page()
        
        try:
            print(f"\n📱 导航到: {BASE_URL}")
            page.goto(BASE_URL)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            print("✅ 页面加载成功！")
            
            print("\n🔍 点击 '加载示例数据'")
            sample_btn = page.locator('button:has-text("加载示例数据")')
            if sample_btn.count() > 0:
                sample_btn.click()
                time.sleep(2.5)
                print("✅ 点击成功！")
            
            print("\n🔍 点击 '生成 Kafka 消息'")
            generate_btn = page.locator('button:has-text("生成 Kafka 消息")')
            if generate_btn.count() > 0:
                generate_btn.click()
                time.sleep(3)
                print("✅ 点击成功！")
            
            print("\n" + "=" * 60)
            print("🎉 可视化演示完成！")
            print("=" * 60)
            print("\n💡 浏览器将保持打开，您可以继续操作查看。")
            print("按 Enter 键关闭浏览器...")
            
            input()
            
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            print("\n按 Enter 键关闭浏览器...")
            input()
            
        finally:
            print("\n🔒 关闭浏览器...")
            page.close()
            browser.close()


if __name__ == "__main__":
    main()
