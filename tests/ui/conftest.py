"""
pytest 配置文件 - UI 自动化测试
"""

import pytest
from selenium import webdriver


@pytest.fixture(scope='session')
def browser_type():
    """获取浏览器类型"""
    return "chrome"


@pytest.fixture(scope='function')
def chrome_options():
    """配置 Chrome 浏览器选项"""
    options = webdriver.ChromeOptions()
    
    # 无头模式
    options.add_argument('--headless')
    
    # 其他配置
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    return options


@pytest.fixture(scope='function')
def driver(chrome_options):
    """创建浏览器实例"""
    from selenium import webdriver
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    
    yield driver
    
    driver.quit()
