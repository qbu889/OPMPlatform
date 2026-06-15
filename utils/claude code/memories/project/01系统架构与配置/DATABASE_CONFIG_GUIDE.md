# 多数据库配置指南

## 📊 系统数据库架构

本项目使用**多数据库分离**架构，不同业务模块使用独立数据库：

```
├── knowledge_base (知识库数据库)
│   ├── users          - 用户表
│   ├── documents      - 文档表
│   ├── faqs          - FAQ 表
│   └── conversation_history - 对话历史表
│
├── auth_system (认证系统数据库)
│   ├── users          - 用户表
│   ├── user_tokens    - 用户令牌表
│   └── login_logs     - 登录日志表
│
└── schedule_system (排班系统数据库)
    ├── staff          - 人员表
    ├── roster         - 排班表
    └── leave_requests - 请假表
```

## ⚙️ 配置方式

### 方案 A: SQLite 模式（默认，适合开发）

**优点：**
- 无需安装 MySQL
- 配置简单
- 单文件存储

**配置：**
```bash
# .env 文件
USE_MYSQL=false
```

**数据库文件位置：**
- `knowledge_base.db` - 知识库数据
- `auth.db` - 认证数据（如有）

### 方案 B: MySQL 模式（生产环境推荐）

**优点：**
- 高性能
- 支持并发
- 数据安全性高
- 易于备份和扩展

**配置步骤：**

#### 1. 编辑 .env 文件

```bash
# 启用 MySQL
USE_MYSQL=true

# MySQL 全局配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=12345678
MYSQL_CHARSET=utf8mb4

# 各业务数据库名称（可选，使用默认值即可）
KNOWLEDGE_BASE_DB=knowledge_base
AUTH_DB=auth_system
SCHEDULE_DB=schedule_system
```

#### 2. 初始化数据库

**方式 1: 一键初始化所有数据库（推荐）**

```bash
mysql -u root -p < sql/init_all_databases.sql
```

**方式 2: 单独初始化各个数据库**

```bash
# 初始化知识库数据库
mysql -u root -p < sql/init_knowledge_base.sql

# 初始化认证数据库
mysql -u root -p auth_system < sql/init_auth_system.sql

# 初始化排班数据库
mysql -u root -p schedule_system < sql/init_schedule_system.sql
```

#### 3. 启动应用

```bash
python app.py
```

## 📝 详细配置说明

### 环境变量说明

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| USE_MYSQL | 是否启用 MySQL | false | 否 |
| MYSQL_HOST | MySQL 主机地址 | localhost | 否 |
| MYSQL_PORT | MySQL 端口 | 3306 | 否 |
| MYSQL_USER | MySQL 用户名 | root | 否 |
| MYSQL_PASSWORD | MySQL 密码 | 123456 | 否 |
| MYSQL_CHARSET | 字符集 | utf8mb4 | 否 |
| KNOWLEDGE_BASE_DB | 知识库数据库名 | knowledge_base | 否 |
| AUTH_DB | 认证数据库名 | auth_system | 否 |
| SCHEDULE_DB | 排班数据库名 | schedule_system | 否 |

### 数据库连接池配置（可选）

如需配置连接池，可在 `config.py` 中添加：

```python
# 数据库连接池配置
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 20
DB_POOL_TIMEOUT = 30
```

## 🔄 数据迁移

### 从 SQLite 迁移到 MySQL

```python
# scripts/migrate_all_to_mysql.py
import sqlite3
import pymysql

def migrate_database(sqlite_db, mysql_config, mysql_db):
    """迁移单个数据库"""
    # SQLite 连接
    sqlite_conn = sqlite3.connect(sqlite_db)
    sqlite_cursor = sqlite_conn.cursor()
    
    # MySQL 连接
    mysql_conn = pymysql.connect(**mysql_config, database=mysql_db)
    mysql_cursor = mysql_conn.cursor()
    
    # 获取所有表
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = sqlite_cursor.fetchall()
    
    # 迁移每个表
    for table in tables:
        table_name = table[0]
        print(f"迁移表：{table_name}")
        
        # 获取表结构
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if rows:
            # 插入数据（需要根据表结构调整）
            # ... 具体实现略
    
    mysql_conn.commit()
    mysql_conn.close()
    sqlite_conn.close()

# 使用示例
if __name__ == '__main__':
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'charset': 'utf8mb4'
    }
    
    # 迁移知识库数据库
    migrate_database('knowledge_base.db', mysql_config, 'knowledge_base')
    
    # 迁移认证数据库
    migrate_database('auth.db', mysql_config, 'auth_system')
    
    print("迁移完成！")
```

## 🎯 最佳实践

### 1. 开发环境
```bash
USE_MYSQL=false  # 使用 SQLite，方便调试
```

### 2. 测试环境
```bash
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_PASSWORD=test_password
```

### 3. 生产环境
```bash
USE_MYSQL=true
MYSQL_HOST=192.168.1.100  # 独立数据库服务器
MYSQL_USER=app_user
MYSQL_PASSWORD=strong_password_here
```

## 🚨 常见问题

### Q1: 如何查看当前使用的数据库？

查看应用日志：
```
INFO: 初始化 Ollama 客户端：URL=..., Model=...
```

或在代码中添加调试输出：
```python
print(f"使用数据库：{'MySQL' if self.use_mysql else 'SQLite'}")
```

### Q2: 如何切换数据库？

1. 修改 `.env` 中的 `USE_MYSQL`
2. 重启 Flask 应用

### Q3: 数据库密码忘记了怎么办？

```bash
# MySQL 重置 root 密码
mysql -u root --skip-grant-tables
UPDATE mysql.user SET authentication_string=PASSWORD('新密码') WHERE User='root';
FLUSH PRIVILEGES;
```

### Q4: 如何备份数据库？

```bash
# 备份所有数据库
mysqldump -u root -p --all-databases > backup.sql

# 备份单个数据库
mysqldump -u root -p knowledge_base > knowledge_base_backup.sql

# 恢复数据库
mysql -u root -p < backup.sql
```

## 📊 数据库监控

### 查看数据库大小

```sql
SELECT 
    TABLE_SCHEMA as '数据库',
    TABLE_NAME as '表名',
    TABLE_ROWS as '行数',
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) as '大小 (MB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA IN ('knowledge_base', 'auth_system', 'schedule_system')
ORDER BY TABLE_SCHEMA, TABLE_NAME;
```

### 查看连接数

```sql
SHOW STATUS LIKE 'Threads_connected';
```

## ✅ 配置检查清单

- [ ] 安装 pymysql: `pip install pymysql`
- [ ] 配置 .env 文件
- [ ] 执行数据库初始化脚本
- [ ] 启动应用测试
- [ ] 验证数据写入
- [ ] 配置备份策略

## 📚 相关文档

- [MySQL 官方文档](https://dev.mysql.com/doc/)
- [PyMySQL 文档](https://pymysql.readthedocs.io/)
- [SQLite 文档](https://www.sqlite.org/docs.html)
