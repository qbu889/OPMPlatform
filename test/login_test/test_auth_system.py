#!/usr/bin/env python3
# test_auth_system.py
"""测试认证系统功能"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.auth_models import user_model, security_question_model, session_manager
import json

def test_user_registration():
    """测试用户注册功能"""
    print("=== 测试用户注册 ===")
    
    # 测试正常注册
    success, message = user_model.create_user(
        username="testuser",
        email="test@example.com",
        password="Test123456",
        role="user"
    )
    print(f"注册结果: {success} - {message}")
    
    # 测试重复注册
    success, message = user_model.create_user(
        username="testuser",
        email="test2@example.com",
        password="Test123456",
        role="user"
    )
    print(f"重复用户名注册: {success} - {message}")
    
    return "testuser"

def test_authentication(username):
    """测试用户认证"""
    print("\n=== 测试用户认证 ===")
    
    # 测试正确密码
    success, message, user_info = user_model.authenticate(username, "Test123456")
    print(f"正确密码认证: {success} - {message}")
    if user_info:
        print(f"用户信息: {user_info}")
        user_id = user_info['id']
    else:
        return None
    
    # 测试错误密码
    success, message, user_info = user_model.authenticate(username, "WrongPassword")
    print(f"错误密码认证: {success} - {message}")
    
    return user_id

def test_security_questions(user_id):
    """测试安全问题功能"""
    print("\n=== 测试安全问题 ===")
    
    # 设置安全问题
    success = security_question_model.set_security_question(
        user_id=user_id,
        question="您最喜欢的颜色是？",
        answer="蓝色"
    )
    print(f"设置安全问题: {success}")
    
    # 验证正确答案
    success = security_question_model.verify_answer(user_id, "蓝色")
    print(f"验证正确答案: {success}")
    
    # 验证错误答案
    success = security_question_model.verify_answer(user_id, "红色")
    print(f"验证错误答案: {success}")
    
    # 获取安全问题
    question = security_question_model.get_security_question(user_id)
    print(f"获取安全问题: {question}")

def test_session_management(user_id):
    """测试会话管理"""
    print("\n=== 测试会话管理 ===")
    
    # 创建会话
    session_token = session_manager.create_session(
        user_id=user_id,
        ip_address="127.0.0.1",
        user_agent="Test Agent"
    )
    print(f"创建会话令牌: {session_token}")
    
    # 验证会话
    session_info = session_manager.validate_session(session_token)
    print(f"验证会话: {session_info}")
    
    # 使会话失效
    success = session_manager.invalidate_session(session_token)
    print(f"使会话失效: {success}")
    
    # 再次验证应该失败
    session_info = session_manager.validate_session(session_token)
    print(f"失效后验证: {session_info}")

def test_password_update(user_id):
    """测试密码更新"""
    print("\n=== 测试密码更新 ===")
    
    # 更新密码
    success = user_model.update_password(user_id, "NewPass123")
    print(f"更新密码: {success}")
    
    # 验证新密码
    success, message, user_info = user_model.authenticate("testuser", "NewPass123")
    print(f"新密码认证: {success} - {message}")

def main():
    """主测试函数"""
    print("开始测试认证系统...")
    
    try:
        # 测试用户注册
        username = test_user_registration()
        if not username:
            print("用户注册失败，测试终止")
            return
        
        # 测试认证
        user_id = test_authentication(username)
        if not user_id:
            print("用户认证失败，测试终止")
            return
        
        # 测试安全问题
        test_security_questions(user_id)
        
        # 测试会话管理
        test_session_management(user_id)
        
        # 测试密码更新
        test_password_update(user_id)
        
        print("\n=== 所有测试完成 ===")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()