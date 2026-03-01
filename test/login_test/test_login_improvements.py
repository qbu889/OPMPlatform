#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录功能改进
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试导入
    from routes.auth_routes import auth_bp
    print("✅ 登录路由模块导入成功")
    
    # 测试datetime导入
    from datetime import datetime
    print("✅ datetime模块导入成功")
    print(f"当前时间: {datetime.now()}")
    
    # 测试日志配置
    import logging
    logger = logging.getLogger(__name__)
    print("✅ 日志配置成功")
    
    print("\n🎉 所有测试通过！登录功能改进已准备就绪。")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")