"""
Pytest 配置文件 - 支持有头/无头模式
"""

import os
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def playwright():
    """创建 Playwright 实例"""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="function")
def browser(playwright):
    """创建浏览器实例（根据环境变量决定有头/无头模式）"""
    # CI环境使用无头模式，本地开发使用有头模式
    is_ci = os.getenv("CI", "false").lower() == "true" or os.getenv("FLASK_ENV", "").lower() == "testing"
    
    browser = playwright.chromium.launch(
        headless=is_ci,
        slow_mo=0 if is_ci else 600,  # CI环境快速执行，本地环境放慢以便观察
        args=["--no-sandbox", "--disable-gpu"] if is_ci else []
    )
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """创建页面实例"""
    page = browser.new_page()
    yield page
    page.close()
