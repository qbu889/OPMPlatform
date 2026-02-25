#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试管理员初始化
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 删除现有的数据库文件以便重新初始化
if os.path.exists('users.db'):
    os.remove('users.db')
    print("🗑️  已删除现有数据库文件")

# 导入并初始化
from models.auth_models import db_manager

print("🚀 初始化数据库...")
db_manager.init_database()

print("✅ 管理员账户初始化完成!")
print("\n📝 默认管理员账户信息:")
print("   用户名: admin")
print("   密码: Admin123!")
print("   邮箱: admin@example.com")
print("   角色: admin")
print("\n⚠️  请及时登录并修改默认密码!")