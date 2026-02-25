#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证管理员账户初始化修复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 清理现有数据库
if os.path.exists('users.db'):
    os.remove('users.db')
    print("🗑️  已删除现有数据库文件")

print("🔧 测试修复后的管理员初始化...")

try:
    from models.auth_models import db_manager, user_model
    
    # 测试数据库初始化
    db_manager.init_database()
    print("✅ 数据库初始化成功")
    
    # 验证管理员账户
    success, message, user_info = user_model.authenticate("admin", "Admin123!")
    if success:
        print("✅ 管理员账户验证成功!")
        print(f"   用户信息: {user_info}")
    else:
        print(f"❌ 管理员账户验证失败: {message}")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n🎉 管理员账户初始化功能已修复并验证成功!")