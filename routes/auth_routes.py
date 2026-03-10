# routes/auth_routes.py
"""用户认证相关路由"""

import re
import json
import logging
from datetime import datetime
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for
from models.auth_models import user_model, security_question_model, session_manager
from functools import wraps

# 配置日志 - 使用统一格式
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """登录装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查会话中的用户信息
        if 'user_id' not in session:
            # 检查cookie中的会话令牌
            session_token = request.cookies.get('session_token')
            if session_token:
                user_info = session_manager.validate_session(session_token)
                if user_info:
                    session['user_id'] = user_info['user_id']
                    session['username'] = user_info['username']
                    session['role'] = user_info['role']
                else:
                    return jsonify({'error': '会话已过期，请重新登录'}), 401
            else:
                return jsonify({'error': '请先登录'}), 401
        
        # 检查用户是否激活
        if not session.get('is_active', True):
            return jsonify({'error': '账户已被禁用'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False, "密码长度至少8位"
    if not re.search(r'[A-Za-z]', password):
        return False, "密码必须包含字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含数字"
    return True, "密码符合要求"

@auth_bp.route('/login')
def login_page():
    """登录页面"""
    # 如果已经登录，重定向到首页
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register_page():
    """注册页面"""
    # 如果已经登录，重定向到首页
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('auth/register.html')

@auth_bp.route('/forgot-password')
def forgot_password_page():
    """忘记密码页面"""
    return render_template('auth/forgot_password.html')

@auth_bp.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['username', 'email', 'password', 'confirm_password', 'security_question', 'security_answer']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field}不能为空'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        confirm_password = data['confirm_password']
        security_question = data['security_question'].strip()
        security_answer = data['security_answer'].strip()
        
        # 验证用户名格式
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度应在3-20位之间'}), 400
        
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            return jsonify({'success': False, 'message': '用户名只能包含字母、数字、下划线和中文'}), 400
        
        # 验证邮箱
        if not validate_email(email):
            return jsonify({'success': False, 'message': '邮箱格式不正确'}), 400
        
        # 验证密码
        is_valid, msg = validate_password(password)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400
        
        # 确认密码
        if password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400
        
        # 验证安全问题
        if len(security_question) < 5:
            return jsonify({'success': False, 'message': '安全问题至少5个字符'}), 400
        
        if len(security_answer) < 2:
            return jsonify({'success': False, 'message': '安全答案至少2个字符'}), 400
        
        # 创建用户
        success, message = user_model.create_user(username, email, password)
        if not success:
            return jsonify({'success': False, 'message': message}), 400
        
        # 获取刚创建的用户ID
        user_info = user_model.authenticate(username, password)
        if user_info[0]:  # 登录成功
            _, _, user_data = user_info
            user_id = user_data['id']
            
            # 设置安全问题
            if not security_question_model.set_security_question(user_id, security_question, security_answer):
                return jsonify({'success': False, 'message': '设置安全问题失败'}), 500
            
            return jsonify({'success': True, 'message': '注册成功，请登录'})
        else:
            return jsonify({'success': False, 'message': '注册后自动登录失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('username') or not data.get('password'):
            logger.warning("登录失败：用户名或密码为空")
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # 记录登录尝试
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        logger.info(f"[LOGIN_ATTEMPT] User: {username} | IP: {client_ip} | UA: {user_agent}")
        
        # 用户认证
        success, message, user_info = user_model.authenticate(username, password)
        
        if success:
            # 登录成功日志
            logger.info(f"[LOGIN_SUCCESS] UserID: {user_info['id']} | Username: {user_info['username']} | IP: {client_ip}")
            
            # 创建会话
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            session_token = session_manager.create_session(user_info['id'], ip_address, user_agent)
            
            if session_token:
                # 设置session
                session['user_id'] = user_info['id']
                session['username'] = user_info['username']
                session['email'] = user_info['email']
                session['role'] = user_info['role']
                session['is_active'] = user_info['is_active']
                
                # 返回详细的成功信息
                response_data = {
                    'success': True, 
                    'message': message,
                    'user': {
                        'id': user_info['id'],
                        'username': user_info['username'],
                        'email': user_info['email'],
                        'role': user_info['role'],
                        'is_active': user_info['is_active']
                    },
                    'session_info': {
                        'created_at': session_manager.get_session_info(session_token).get('created_at') if session_manager.get_session_info(session_token) else None,
                        'expires_at': session_manager.get_session_info(session_token).get('expires_at') if session_manager.get_session_info(session_token) else None
                    }
                }
                
                response = jsonify(response_data)
                
                # 设置会话cookie
                response.set_cookie('session_token', session_token, max_age=24*60*60, httponly=True, secure=False)
                logger.info(f"[SESSION_CREATED] Token: {session_token[:10]}... | UserID: {user_info['id']}")
                return response
            else:
                logger.error(f"[SESSION_CREATE_FAILED] UserID: {user_info['id']} | Username: {user_info['username']}")
                return jsonify({'success': False, 'message': '创建会话失败'}), 500
        else:
            # 登录失败日志
            logger.warning(f"[LOGIN_FAILED] User: {username} | IP: {client_ip} | Reason: {message}")
            return jsonify({
                'success': False, 
                'message': message,
                'error_details': {
                    'username': username,
                    'attempt_time': str(datetime.now()),
                    'ip_address': client_ip,
                    'reason': message
                }
            }), 401
            
    except Exception as e:
        logger.error(f"[LOGIN_EXCEPTION] Error: {str(e)} | IP: {request.remote_addr}", exc_info=True)
        return jsonify({
            'success': False, 
            'message': f'登录失败: {str(e)}',
            'error_details': {
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': str(datetime.now())
            }
        }), 500

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    try:
        # 使会话失效
        session_token = request.cookies.get('session_token')
        if session_token:
            session_manager.invalidate_session(session_token)
        
        # 清除session
        session.clear()
        
        response = jsonify({'success': True, 'message': '登出成功'})
        response.set_cookie('session_token', '', expires=0)
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登出失败: {str(e)}'}), 500

@auth_bp.route('/api/get-security-question', methods=['POST'])
def get_security_question():
    """获取用户安全问题"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        # 根据用户名获取用户ID
        user_info = user_model.get_user_by_id(1)  # 这里需要实际查询用户ID
        # 临时解决方案：遍历所有用户查找匹配的用户名
        conn = user_model.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        user_id = result[0]
        question = security_question_model.get_security_question(user_id)
        
        if question:
            return jsonify({'success': True, 'question': question})
        else:
            return jsonify({'success': False, 'message': '该用户未设置安全问题'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取安全问题失败: {str(e)}'}), 500

@auth_bp.route('/api/verify-security-answer', methods=['POST'])
def verify_security_answer():
    """验证安全问题答案"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        answer = data.get('answer', '').strip()
        
        if not username or not answer:
            return jsonify({'success': False, 'message': '用户名和答案不能为空'}), 400
        
        # 获取用户ID
        conn = user_model.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        user_id = result[0]
        
        # 验证答案
        if security_question_model.verify_answer(user_id, answer):
            return jsonify({'success': True, 'message': '答案正确'})
        else:
            return jsonify({'success': False, 'message': '答案错误'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证答案失败: {str(e)}'}), 500

@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not username or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': '所有字段都不能为空'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400
        
        # 验证密码强度
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400
        
        # 获取用户ID
        conn = user_model.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        user_id = result[0]
        
        # 更新密码
        if user_model.update_password(user_id, new_password):
            return jsonify({'success': True, 'message': '密码重置成功'})
        else:
            return jsonify({'success': False, 'message': '密码重置失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'重置密码失败: {str(e)}'}), 500

@auth_bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码（已登录状态下）"""
    try:
        data = request.get_json()
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not old_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': '所有字段都不能为空'}), 400
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': '两次输入的密码不一致'}), 400
        
        # 验证新密码强度
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400
        
        user_id = session['user_id']
        
        # 验证旧密码
        user_info = user_model.get_user_by_id(user_id)
        if not user_info:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 重新认证旧密码
        auth_success, _, _ = user_model.authenticate(user_info['username'], old_password)
        if not auth_success:
            return jsonify({'success': False, 'message': '原密码错误'}), 400
        
        # 更新密码
        if user_model.update_password(user_id, new_password):
            return jsonify({'success': True, 'message': '密码修改成功'})
        else:
            return jsonify({'success': False, 'message': '密码修改失败'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'修改密码失败: {str(e)}'}), 500

@auth_bp.route('/api/current-user')
def current_user():
    """获取当前用户信息"""
    if 'user_id' in session:
        user_info = {
            'id': session['user_id'],
            'username': session['username'],
            'email': session.get('email', ''),
            'role': session.get('role', 'user'),
            'is_active': session.get('is_active', True)
        }
        return jsonify({'success': True, 'user': user_info})
    else:
        return jsonify({'success': False, 'message': '未登录'}), 401

@auth_bp.route('/api/check-auth')
def check_auth():
    """检查认证状态"""
    is_authenticated = 'user_id' in session
    user_role = session.get('role', 'user') if is_authenticated else None
    
    return jsonify({
        'authenticated': is_authenticated,
        'role': user_role
    })