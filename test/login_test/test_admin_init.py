#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理员账户初始化功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.auth_models import db_manager, user_model
import sqlite3

def test_admin_initialization():
    """测试管理员账户初始化"""
    print("🔍 测试管理员账户初始化...")
    
    try:
        # 重新初始化数据库（这会触发管理员账户创建）
        db_manager.init_database()
        print("✅ 数据库初始化完成")
        
        # 验证管理员账户是否存在
        conn = sqlite3.connect('../../users.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, role, is_active FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            user_id, username, email, role, is_active = admin_user
            print(f"✅ 管理员账户存在:")
            print(f"   ID: {user_id}")
            print(f"   用户名: {username}")
            print(f"   邮箱: {email}")
            print(f"   角色: {role}")
            print(f"   状态: {'激活' if is_active else '未激活'}")
            
            # 验证安全问题
            cursor.execute("SELECT question FROM security_questions WHERE user_id = ?", (user_id,))
            security_question = cursor.fetchone()
            if security_question:
                print(f"✅ 安全问题已设置: {security_question[0]}")
            else:
                print("❌ 安全问题未设置")
        else:
            print("❌ 管理员账户未创建")
        
        # 测试管理员登录
        print("\n🔐 测试管理员登录...")
        success, message, user_info = user_model.authenticate("admin", "Admin123!")
        if success:
            print(f"✅ 管理员登录成功: {message}")
            print(f"   用户信息: {user_info}")
        else:
            print(f"❌ 管理员登录失败: {message}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

def list_all_users():
    """列出所有用户"""
    print("\n👥 当前所有用户:")
    try:
        conn = sqlite3.connect('../../users.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.id, u.username, u.email, u.role, u.is_active, u.created_at,
                   sq.question as security_question
            FROM users u
            LEFT JOIN security_questions sq ON u.id = sq.user_id
            ORDER BY u.id
        """)
        
        users = cursor.fetchall()
        if users:
            for user in users:
                user_id, username, email, role, is_active, created_at, security_question = user
                status = "🟢 激活" if is_active else "🔴 未激活"
                print(f"   [{user_id}] {username} ({email}) - {role} - {status}")
                print(f"       创建时间: {created_at}")
                if security_question:
                    print(f"       安全问题: {security_question}")
                print()
        else:
            print("   暂无用户")
            
        conn.close()
    except Exception as e:
        print(f"❌ 查询用户列表失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("管理员账户初始化测试")
    print("=" * 50)
    
    test_admin_initialization()
    list_all_users()
    
    print("\n📝 使用说明:")
    print("   默认管理员账户:")
    print("   - 用户名: admin")
    print("   - 密码: Admin123!")
    print("   - 邮箱: admin@example.com")
    print("   - 角色: admin")
    print("\n   ⚠️  请务必在首次登录后修改默认密码!")