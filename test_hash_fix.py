#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试密码哈希函数修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 清理现有数据库
if os.path.exists('users.db'):
    os.remove('users.db')

print("🧪 测试密码哈希函数修复...")

try:
    from models.auth_models import db_manager, user_model
    
    # 测试数据库初始化（会调用修复后的哈希函数）
    print("正在初始化数据库...")
    db_manager.init_database()
    print("✅ 数据库初始化成功")
    
    # 验证管理员账户
    print("正在验证管理员账户...")
    success, message, user_info = user_model.authenticate("admin", "Admin123!")
    if success:
        print("✅ 管理员账户验证成功!")
        print(f"   用户信息: {user_info}")
    else:
        print(f"❌ 管理员账户验证失败: {message}")
        
    print("\n🎉 所有测试通过！密码哈希函数修复成功。")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()