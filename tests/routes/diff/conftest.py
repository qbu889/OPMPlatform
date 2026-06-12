"""Pytest 配置文件 - 处理 Python 路径问题"""

import sys
import os

# 添加项目根目录到 Python 路径
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

print(f"Python path updated. Root directory: {root_dir}")
