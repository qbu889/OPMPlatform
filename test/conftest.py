import pytest
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def pytest_configure(config):
    """Pytest 配置钩子"""
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )

def pytest_collection_modifyitems(config, items):
    """修改测试项集合，排除需要外部资源的测试"""
    # 排除这些需要特定文件或外部服务的测试
    skip_files = [
        'test_large_doc_faq.py',
        'test_parallel_faq.py',
        'test_real_upload.py'
    ]
    
    items[:] = [
        item for item in items
        if not any(skip_file in item.nodeid for skip_file in skip_files)
    ]
