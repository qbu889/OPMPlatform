# auth_manual_test.py
"""手动测试认证系统"""

print("=== 手动测试认证系统 ===")

# 测试数据库初始化
try:
    from models.auth_models import db_manager, user_model, security_question_model, session_manager
    print("✓ 数据库模型导入成功")
except Exception as e:
    print(f"✗ 数据库模型导入失败: {e}")

# 测试用户注册
try:
    success, message = user_model.create_user(
        username="admin",
        email="admin@example.com",
        password="Admin123",
        role="admin"
    )
    print(f"✓ 管理员注册: {success} - {message}")
except Exception as e:
    print(f"✗ 管理员注册失败: {e}")

try:
    success, message = user_model.create_user(
        username="normaluser",
        email="user@example.com",
        password="User123",
        role="user"
    )
    print(f"✓ 普通用户注册: {success} - {message}")
except Exception as e:
    print(f"✗ 普通用户注册失败: {e}")

# 测试用户认证
try:
    success, message, user_info = user_model.authenticate("admin", "Admin123")
    if success:
        print(f"✓ 管理员认证成功: {user_info}")
        admin_id = user_info['id']
    else:
        print(f"✗ 管理员认证失败: {message}")
except Exception as e:
    print(f"✗ 管理员认证异常: {e}")

try:
    success, message, user_info = user_model.authenticate("normaluser", "User123")
    if success:
        print(f"✓ 普通用户认证成功: {user_info}")
        user_id = user_info['id']
    else:
        print(f"✗ 普通用户认证失败: {message}")
except Exception as e:
    print(f"✗ 普通用户认证异常: {e}")

# 测试安全问题
try:
    if 'admin_id' in locals():
        success = security_question_model.set_security_question(
            admin_id, "您的出生地是？", "北京"
        )
        print(f"✓ 管理员安全问题设置: {success}")
        
        success = security_question_model.verify_answer(admin_id, "北京")
        print(f"✓ 管理员安全问题验证: {success}")
        
        question = security_question_model.get_security_question(admin_id)
        print(f"✓ 获取管理员安全问题: {question}")
except Exception as e:
    print(f"✗ 安全问题测试失败: {e}")

# 测试会话管理
try:
    if 'admin_id' in locals():
        session_token = session_manager.create_session(admin_id, "127.0.0.1", "Test Browser")
        print(f"✓ 会话创建: {session_token[:20]}...")
        
        session_info = session_manager.validate_session(session_token)
        print(f"✓ 会话验证: {session_info is not None}")
        
        success = session_manager.invalidate_session(session_token)
        print(f"✓ 会话失效: {success}")
except Exception as e:
    print(f"✗ 会话管理测试失败: {e}")

print("\n=== 测试完成 ===")