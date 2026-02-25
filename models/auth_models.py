# models/auth_models.py
"""用户认证相关数据模型"""

import hashlib
import secrets
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


def _hash_password(password: str, salt: str = None) -> tuple:
    """密码哈希处理（全局工具函数）"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    
    return password_hash, salt

def _hash_answer(answer: str, salt: str = None) -> tuple:
    """答案哈希处理（全局工具函数）"""
    if salt is None:
        salt = secrets.token_hex(32)
    
    answer_hash = hashlib.pbkdf2_hmac(
        'sha256',
        answer.lower().encode('utf-8'),  # 转小写以提高容错性
        salt.encode('utf-8'),
        50000
    ).hex()
    
    return answer_hash, salt


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = 'users.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP
            )
        ''')
        
        # 安全问题表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer_hash TEXT NOT NULL,
                answer_salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 登录会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)')
        
        conn.commit()
        
        # 初始化默认管理员账户
        self._init_default_admin(cursor)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def _init_default_admin(self, cursor):
        """初始化默认管理员账户"""
        try:
            # 检查是否已存在管理员账户
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if cursor.fetchone():
                return  # 管理员已存在
            
            # 创建默认管理员账户
            admin_username = "admin"
            admin_email = "admin@example.com"
            admin_password = "Admin123!"  # 默认密码，建议用户首次登录后修改
            
            # 哈希密码（使用全局工具函数）
            password_hash, salt = _hash_password(admin_password)
            
            # 插入管理员账户
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (admin_username, admin_email, password_hash, salt, 'admin', 1))
            
            user_id = cursor.lastrowid
            
            # 为管理员设置安全问题
            security_question = "系统默认管理员账户"
            security_answer = "admin"
            answer_hash, answer_salt = _hash_answer(security_answer)
            
            cursor.execute('''
                INSERT INTO security_questions (user_id, question, answer_hash, answer_salt)
                VALUES (?, ?, ?, ?)
            ''', (user_id, security_question, answer_hash, answer_salt))
            
            print(f"✅ 默认管理员账户创建成功!")
            print(f"   用户名: {admin_username}")
            print(f"   邮箱: {admin_email}")
            print(f"   默认密码: {admin_password}")
            print("   ⚠️  请及时登录并修改默认密码!")
            
        except Exception as e:
            print(f"⚠️  创建默认管理员账户失败: {e}")


class User:
    """用户模型"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    @staticmethod
    def _hash_password(password: str, salt: str = None) -> tuple:
        """密码哈希处理"""
        return _hash_password(password, salt)
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> bool:
        """创建新用户"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 检查用户名和邮箱是否已存在
            cursor.execute(
                'SELECT id FROM users WHERE username = ? OR email = ?',
                (username, email)
            )
            if cursor.fetchone():
                conn.close()
                return False, "用户名或邮箱已存在"
            
            # 哈希密码
            password_hash, salt = self._hash_password(password)
            
            # 插入用户
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, role))
            
            conn.commit()
            conn.close()
            return True, "用户创建成功"
            
        except Exception as e:
            return False, f"创建用户失败: {str(e)}"
    
    def authenticate(self, username: str, password: str) -> tuple:
        """用户认证"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 获取用户信息
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, is_active, 
                       failed_login_attempts, locked_until
                FROM users 
                WHERE username = ? OR email = ?
            ''', (username, username))
            
            user_data = cursor.fetchone()
            if not user_data:
                conn.close()
                return False, "用户不存在", None
            
            user_id, username, email, stored_hash, salt, role, is_active, failed_attempts, locked_until = user_data
            
            # 检查账户是否被锁定
            if locked_until:
                lock_time = datetime.fromisoformat(locked_until)
                if datetime.now() < lock_time:
                    conn.close()
                    return False, "账户已被锁定，请稍后再试", None
            
            # 验证密码
            password_hash, _ = self._hash_password(password, salt)
            
            if password_hash != stored_hash:
                # 增加失败尝试次数
                failed_attempts += 1
                if failed_attempts >= 5:  # 5次失败后锁定账户30分钟
                    lock_time = datetime.now().replace(microsecond=0)
                    lock_until = lock_time.replace(minute=lock_time.minute + 30)
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = ?, locked_until = ?
                        WHERE id = ?
                    ''', (failed_attempts, lock_until.isoformat(), user_id))
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET failed_login_attempts = ?
                        WHERE id = ?
                    ''', (failed_attempts, user_id))
                
                conn.commit()
                conn.close()
                return False, "用户名或密码错误", None
            
            # 登录成功，重置失败次数
            cursor.execute('''
                UPDATE users 
                SET failed_login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            user_info = {
                'id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'is_active': is_active
            }
            
            return True, "登录成功", user_info
            
        except Exception as e:
            return False, f"认证失败: {str(e)}", None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, role, is_active, created_at, last_login
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return {
                    'id': user_data[0],
                    'username': user_data[1],
                    'email': user_data[2],
                    'role': user_data[3],
                    'is_active': user_data[4],
                    'created_at': user_data[5],
                    'last_login': user_data[6]
                }
            return None
            
        except Exception:
            return None
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """更新用户密码"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            password_hash, salt = self._hash_password(new_password)
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, salt = ?
                WHERE id = ?
            ''', (password_hash, salt, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception:
            return False


class SecurityQuestion:
    """安全问题模型"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    @staticmethod
    def _hash_answer(answer: str, salt: str = None) -> tuple:
        """答案哈希处理"""
        return _hash_answer(answer, salt)
    
    def set_security_question(self, user_id: int, question: str, answer: str) -> bool:
        """设置安全问题"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 删除已有的安全问题
            cursor.execute('DELETE FROM security_questions WHERE user_id = ?', (user_id,))
            
            # 哈希答案
            answer_hash, answer_salt = self._hash_answer(answer)
            
            # 插入新的安全问题
            cursor.execute('''
                INSERT INTO security_questions (user_id, question, answer_hash, answer_salt)
                VALUES (?, ?, ?, ?)
            ''', (user_id, question, answer_hash, answer_salt))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception:
            return False
    
    def verify_answer(self, user_id: int, answer: str) -> bool:
        """验证安全问题答案"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT answer_hash, answer_salt
                FROM security_questions 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            stored_hash, salt = result
            answer_hash, _ = self._hash_answer(answer, salt)
            
            return answer_hash == stored_hash
            
        except Exception:
            return False
    
    def get_security_question(self, user_id: int) -> Optional[str]:
        """获取用户的安全问题（不返回答案）"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT question
                FROM security_questions 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception:
            return None


class SessionManager:
    """会话管理器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_session(self, user_id: int, ip_address: str = None, user_agent: str = None) -> str:
        """创建用户会话"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # 生成会话令牌
            session_token = secrets.token_urlsafe(32)
            
            # 设置过期时间（24小时）
            expires_at = datetime.now().replace(microsecond=0)
            expires_at = expires_at.replace(day=expires_at.day + 1)
            
            cursor.execute('''
                INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, session_token, expires_at.isoformat(), ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
            return session_token
            
        except Exception:
            return None
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """验证会话有效性"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.username, u.email, u.role, u.is_active
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_token = ? AND s.is_active = 1
            ''', (session_token,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return None
            
            user_id, expires_at, username, email, role, is_active = result
            
            # 检查是否过期
            if datetime.now() > datetime.fromisoformat(expires_at):
                self.invalidate_session(session_token)
                return None
            
            return {
                'user_id': user_id,
                'username': username,
                'email': email,
                'role': role,
                'is_active': is_active
            }
            
        except Exception:
            return None
    
    def invalidate_session(self, session_token: str) -> bool:
        """使会话失效"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET is_active = 0 
                WHERE session_token = ?
            ''', (session_token,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception:
            return False
    
    def cleanup_expired_sessions(self):
        """清理过期会话"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions 
                SET is_active = 0 
                WHERE expires_at < CURRENT_TIMESTAMP
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception:
            pass


# 全局数据库管理器实例
db_manager = DatabaseManager()
user_model = User(db_manager)
security_question_model = SecurityQuestion(db_manager)
session_manager = SessionManager(db_manager)