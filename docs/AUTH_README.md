# OPM系统单点登录认证功能说明

## 功能概述

本系统实现了完整的用户认证和授权功能，包括：
- 用户注册和登录
- 安全问题设置和验证
- 密码修改和重置
- 基于角色的访问控制
- 会话管理

## 技术架构

### 后端技术栈
- Python 3.10.8
- Flask 2.2.5
- SQLite3（内置数据库）
- PBKDF2密码哈希算法

### 前端技术栈
- Bootstrap 5
- JavaScript ES6+
- Font Awesome 图标库

## 功能详情

### 1. 用户注册
**路径**: `/register`

**功能特点**:
- 用户名验证（3-20位，支持中文）
- 邮箱格式验证
- 密码强度检查（至少8位，包含字母和数字）
- 安全问题设置（预设问题或自定义）
- 防重复注册检查

### 2. 用户登录
**路径**: `/login`

**功能特点**:
- 用户名/邮箱登录
- 密码显示/隐藏切换
- 登录失败次数限制（5次后锁定30分钟）
- 会话保持（24小时有效期）
- 记住我功能

### 3. 忘记密码
**路径**: `/forgot-password`

**三步验证流程**:
1. 输入用户名验证身份
2. 回答安全问题
3. 设置新密码

### 4. 密码修改
**功能位置**: 用户菜单中的"修改密码"

**功能特点**:
- 需要验证原密码
- 新密码强度验证
- 实时确认密码匹配

### 5. 权限控制
**角色类型**:
- `admin`: 管理员角色，拥有所有权限
- `user`: 普通用户角色，基础使用权限

**权限装饰器**:
```python
@login_required    # 需要登录
@admin_required    # 需要管理员权限
```

## API接口说明

### 认证相关接口

#### POST `/api/register`
用户注册接口
```json
{
    "username": "用户名",
    "email": "邮箱",
    "password": "密码",
    "confirm_password": "确认密码",
    "security_question": "安全问题",
    "security_answer": "安全答案"
}
```

#### POST `/api/login`
用户登录接口
```json
{
    "username": "用户名或邮箱",
    "password": "密码"
}
```

#### POST `/api/logout`
用户登出接口

#### POST `/api/change-password`
修改密码接口
```json
{
    "old_password": "原密码",
    "new_password": "新密码",
    "confirm_password": "确认新密码"
}
```

#### POST `/api/get-security-question`
获取安全问题
```json
{
    "username": "用户名"
}
```

#### POST `/api/verify-security-answer`
验证安全问题答案
```json
{
    "username": "用户名",
    "answer": "答案"
}
```

#### POST `/api/reset-password`
重置密码
```json
{
    "username": "用户名",
    "new_password": "新密码",
    "confirm_password": "确认新密码"
}
```

## 数据库结构

### users表
存储用户基本信息
- id: 用户ID（主键）
- username: 用户名（唯一）
- email: 邮箱（唯一）
- password_hash: 密码哈希值
- salt: 密码盐值
- role: 用户角色（user/admin）
- is_active: 账户状态
- created_at: 创建时间
- last_login: 最后登录时间
- failed_login_attempts: 登录失败次数
- locked_until: 账户锁定时间

### security_questions表
存储用户安全问题
- id: 问题ID（主键）
- user_id: 用户ID（外键）
- question: 安全问题
- answer_hash: 答案哈希值
- answer_salt: 答案盐值
- created_at: 创建时间

### sessions表
存储用户会话信息
- id: 会话ID（主键）
- user_id: 用户ID（外键）
- session_token: 会话令牌（唯一）
- created_at: 创建时间
- expires_at: 过期时间
- ip_address: IP地址
- user_agent: 用户代理
- is_active: 会话状态

## 安全特性

### 密码安全
- 使用PBKDF2算法进行密码哈希
- 100,000次迭代增强安全性
- 随机盐值防止彩虹表攻击
- 密码强度验证

### 会话安全
- JWT风格的会话令牌
- 24小时自动过期
- IP地址和User-Agent绑定
- 会话失效机制

### 防暴力破解
- 登录失败5次后锁定30分钟
- 安全问题答案大小写不敏感
- 请求频率限制

## 使用指南

### 管理员账户初始化
首次使用时需要手动创建管理员账户：
```python
# 在Python终端中执行
from models.auth_models import user_model
user_model.create_user("admin", "admin@example.com", "Admin123", "admin")
```

### 日常使用流程
1. **新用户**: 访问 `/register` 进行注册
2. **已注册用户**: 访问 `/login` 进行登录
3. **忘记密码**: 访问 `/forgot-password` 进行密码重置
4. **修改密码**: 登录后在用户菜单中选择"修改密码"

### 管理员功能
管理员用户可以在用户菜单中看到额外的管理选项：
- 用户管理
- 系统设置

## 部署注意事项

### 环境要求
- Python 3.8+
- Flask及相关依赖包
- 可写的文件系统权限（用于SQLite数据库）

### 生产环境建议
1. 启用HTTPS
2. 配置适当的SECRET_KEY
3. 定期备份数据库文件
4. 监控登录失败日志
5. 设置合理的会话超时时间

## 故障排除

### 常见问题

**Q: 登录时报"账户已被锁定"**
A: 等待30分钟后重试，或联系管理员解锁

**Q: 安全问题答案验证失败**
A: 答案不区分大小写，确保输入正确

**Q: 会话经常过期**
A: 检查客户端时间是否正确，会话有效期为24小时

**Q: 注册时提示"用户名已存在"**
A: 选择其他用户名，或使用"忘记密码"功能

## 开发扩展

### 添加新角色
在 `auth_routes.py` 中修改角色检查逻辑：
```python
# 添加新的角色装饰器
def manager_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') not in ['admin', 'manager']:
            return jsonify({'error': '需要管理员或经理权限'}), 403
        return f(*args, **kwargs)
    return decorated_function
```

### 自定义安全问题
修改 `register.html` 中的安全问题选项列表。

### 集成第三方认证
可以扩展 `auth_routes.py` 添加OAuth或其他认证方式。