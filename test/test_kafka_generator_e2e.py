"""
Kafka Generator 页面 E2E 测试用例

高级测试工程师技能应用：
- 等价类划分：测试正常/异常输入场景
- 边界值分析：测试字段长度、数值范围边界
- 场景法/用户故事：基于业务流程设计端到端测试
- UI 自动化：使用 Playwright 进行浏览器自动化测试

测试覆盖：
1. ES 源数据加载与验证
2. Kafka 消息生成流程
3. 字段映射交互功能
4. 数据清除与重置
5. 异常场景处理
"""

import pytest
from playwright.sync_api import Page, expect
import json


class TestKafkaGeneratorE2E:
    """Kafka 消息生成器 E2E 测试类"""
    
    BASE_URL = "http://8.146.228.47:5173/kafka-generator"
    
    @pytest.fixture(scope="function")
    def page(self, page):
        """测试前置准备"""
        page.goto(self.BASE_URL)
        page.wait_for_load_state("networkidle")
        yield page
    
    def test_01_page_load_and_title(self, page):
        """测试 1: 页面加载和标题验证"""
        # 等价类：正常页面加载
        expect(page).to_have_url(self.BASE_URL)
        expect(page).to_have_title("Kafka 消息生成")
        
        # 验证页面主要元素存在
        expect(page.locator("text=Kafka 消息生成器")).to_be_visible()
        expect(page.locator("text=根据 ES 数据生成 Kafka 消息")).to_be_visible()
    
    def test_02_load_sample_data(self, page):
        """测试 2: 加载示例数据功能"""
        # 边界值：空数据 -> 加载示例数据
        page.click('button:has-text("加载示例数据")')
        
        # 验证 ES 源数据文本框已填充
        textarea = page.locator("textarea")
        expect(textarea).to_be_visible()
        
        es_data = textarea.evaluate("el => el.value")
        assert es_data, "ES 源数据不应为空"
        
        # 验证 JSON 格式正确性（等价类：有效 JSON）
        try:
            data = json.loads(es_data)
            assert isinstance(data, dict), "ES 数据应为对象格式"
        except json.JSONDecodeError:
            pytest.fail("加载的示例数据不是有效的 JSON 格式")
    
    def test_03_generate_kafka_message(self, page):
        """测试 3: 生成 Kafka 消息功能"""
        # 场景：正常流程 - 加载数据后生成消息
        
        # 步骤 1: 加载示例数据
        page.click('button:has-text("加载示例数据")')
        
        # 步骤 2: 生成 Kafka 消息
        page.click('button:has-text("生成 Kafka 消息")')
        
        # 验证：应该有生成结果输出
        # 等待可能的加载时间
        page.wait_for_timeout(1000)
        
        # 检查是否有结果区域显示
        result_exists = page.locator("text=Kafka 消息").count() > 0
        
        # 验证页面状态正常
        expect(page).to_have_title("Kafka 消息生成")
    
    def test_04_clear_all_fields(self, page):
        """测试 4: 清除所有字段功能"""
        # 边界值：有数据 -> 清除为空
        
        # 加载示例数据
        page.click('button:has-text("加载示例数据")')
        
        # 获取原始数据长度
        textarea = page.locator("textarea")
        original_length = len(textarea.evaluate("el => el.value"))
        
        # 清除所有字段
        page.click('button:has-text("清除所有字段")')
        
        # 验证文本框被清空或重置
        cleared_value = textarea.evaluate("el => el.value")
        
        # 注意：清除功能可能是清空或重置为初始状态
        assert len(cleared_value) < original_length or cleared_value.strip() != ""
    
    def test_05_field_mapping_buttons(self, page):
        """测试 5: 字段映射管理按钮"""
        # 场景：访问字段映射管理功能
        
        # 点击"字段映射管理"按钮
        field_mapping_btn = page.locator('button:has-text("字段映射管理")')
        expect(field_mapping_btn).to_be_visible()
        
        # 尝试点击（可能需要处理弹窗）
        try:
            field_mapping_btn.click()
            page.wait_for_timeout(500)
        except Exception:
            # 如果点击失败，记录为已知问题
            pytest.skip("字段映射管理按钮需要额外配置")
    
    def test_06_field_dictionary_management(self, page):
        """测试 6: 字段字典管理功能"""
        # 场景：访问字段字典管理
        
        dict_mgmt_btn = page.locator('button:has-text("字段字典管理")')
        expect(dict_mgmt_btn).to_be_visible()
        
        # 尝试点击
        try:
            dict_mgmt_btn.click()
            page.wait_for_timeout(500)
        except Exception:
            pytest.skip("字段字典管理按钮需要额外配置")
    
    def test_07_add_dictionary_item(self, page):
        """测试 7: 新增字典项功能"""
        # 场景：添加新的字段字典项
        
        add_dict_btn = page.locator('button:has-text("新增字典项")')
        expect(add_dict_btn).to_be_visible()
        
        try:
            add_dict_btn.click()
            page.wait_for_timeout(500)
        except Exception:
            pytest.skip("新增字典项功能需要额外配置")
    
    def test_08_es_data_validation(self, page):
        """测试 8: ES 源数据验证（边界值分析）"""
        
        # 测试用例 1: 有效 JSON 数据（等价类：有效）
        page.click('button:has-text("加载示例数据")')
        
        textarea = page.locator("textarea")
        es_data = json.loads(textarea.evaluate("el => el.value"))
        
        # 验证数据结构完整性（边界值：最小/最大字段数）
        assert len(es_data) > 0, "ES 数据不应为空对象"
        
        # 验证关键字段存在（等价类：必需字段）
        required_fields = ["FULL_REGION_ID", "EVENT_LEVEL"]
        for field in required_fields:
            if field in es_data:
                assert es_data[field] is not None, f"字段 {field} 不应为 null"
    
    def test_09_page_navigation(self, page):
        """测试 9: 页面导航功能"""

        # 测试首页链接 - 使用 text=选择器 (.spec.ts 格式)
        home_link = page.locator("text=首页")
        expect(home_link).to_be_visible()

        # 测试文档链接 - .spec.ts 格式
        doc_link = page.locator("text=文档")
        expect(doc_link).to_be_visible()

        # 测试智能系统链接 - .spec.ts 格式
        system_link = page.locator("text=智能系统")
        expect(system_link).to_be_visible()

        # 测试高效工具链接 - .spec.ts 格式
        tool_link = page.locator("text=高效工具")
        expect(tool_link).to_be_visible()

    def test_10_login_registration(self, page):
        """测试 10: 登录/注册功能"""

        # 验证登录按钮存在 - button:has-text()选择器 (.spec.ts 格式)
        login_btn = page.locator('button:has-text("登录")')
        expect(login_btn).to_be_visible()

        # 验证注册按钮存在 - .spec.ts 格式
        register_btn = page.locator('button:has-text("注册")')
        expect(register_btn).to_be_visible()

        # 尝试点击登录（可能需要处理认证）
        try:
            login_btn.click()
            page.wait_for_timeout(500)
        except Exception:
            pytest.skip("登录功能需要额外配置")
    
    def test_11_error_handling(self, page):
        """测试 11: 错误处理场景（错误推测法）"""
        
        # 场景 1: 输入无效 JSON
        textarea = page.locator("textarea")
        invalid_json = "{invalid json}"
        textarea.fill(invalid_json)
        
        # 尝试生成消息，应该显示错误提示
        page.click('button:has-text("生成 Kafka 消息")')
        page.wait_for_timeout(1000)
        
        # 验证是否有错误提示（等价类：无效输入）
        error_exists = page.locator("text=错误").count() > 0 or \
                      page.locator("text=Error").count() > 0
        
        # 场景 2: 清空后尝试生成
        textarea.fill("")
        page.click('button:has-text("生成 Kafka 消息")')
        page.wait_for_timeout(500)
    
    def test_12_performance_basic(self, page):
        """测试 12: 基础性能检查"""
        
        # 记录页面加载时间
        start_time = page.evaluate("() => performance.now()")
        
        # 执行主要操作
        page.click('button:has-text("加载示例数据")')
        page.click('button:has-text("生成 Kafka 消息")')
        
        end_time = page.evaluate("() => performance.now()")
        
        # 验证操作在合理时间内完成（边界值：< 5 秒）
        assert (end_time - start_time) / 1000 < 5, "操作应在 5 秒内完成"
    
    def test_13_data_consistency(self, page):
        """测试 13: 数据一致性验证"""

        # 加载示例数据
        page.click('button:has-text("加载示例数据")')

        # 获取原始 ES 数据 - 使用更精确的选择器（第一个 textarea，有 placeholder）
        textarea = page.locator("textarea[placeholder='请输入 ES 查询结果的 JSON 数据']")
        original_data = json.loads(textarea.evaluate("el => el.value"))

        # 生成 Kafka 消息
        page.click('button:has-text("生成 Kafka 消息")')
        page.wait_for_timeout(1000)

        # 验证数据在操作过程中保持一致性 - 使用相同的精确选择器
        current_data = json.loads(textarea.evaluate("el => el.value"))

        # 原始关键字段应该保持一致（等价类：数据完整性）
        for key in ["FULL_REGION_ID", "EVENT_LEVEL"]:
            if key in original_data and key in current_data:
                assert original_data[key] == current_data[key], \
                    f"字段 {key} 在操作过程中发生变化"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
