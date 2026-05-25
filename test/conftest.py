"""
Pytest 配置文件 - 启用有头模式
"""

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def playwright():
    """创建 Playwright 实例"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright):
    """创建浏览器实例（有头模式）"""
    browser = playwright.chromium.launch(
        headless=False,
        slow_mo=600  # 放慢操作以便观察
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """创建页面实例"""
    page = browser.new_page()
    yield page
    page.close()
