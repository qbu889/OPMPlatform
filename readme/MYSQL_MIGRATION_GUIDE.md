# MySQL 数据库迁移指南

## 📋 迁移步骤

### 1️⃣ 安装依赖

```bash
pip install pymysql
```

### 2️⃣ 配置 MySQL 数据库

#### 方案 A: 使用环境变量（推荐）

编辑 `.env` 文件：

```bash
# 启用 MySQL
USE_MYSQL=true

# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=knowledge_base
```

#### 方案 B: 使用系统环境变量

```bash
export USE_MYSQL=true
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=knowledge_base
```

### 3️⃣ 初始化 MySQL 数据库

```bash
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source /Users/linziwang/PycharmProjects/wordToWord/sql/init_knowledge_base.sql
```

或者使用命令行一键执行：

```bash
mysql -u root -p < sql/init_knowledge_base.sql
```

### 4️⃣ 启动应用

```bash
python app.py
```

## 🔄 从 SQLite 迁移数据（可选）

如果需要将现有 SQLite 数据迁移到 MySQL：

```python
# scripts/migrate_sqlite_to_mysql.py
import sqlite3
import pymysql
import json

# SQLite 连接
sqlite_conn = sqlite3.connect('knowledge_base.db')
sqlite_cursor = sqlite_conn.cursor()

# MySQL 连接
mysql_conn = pymysql.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='knowledge_base',
    charset='utf8mb4'
)
mysql_cursor = mysql_conn.cursor()

# 迁移文档
sqlite_cursor.execute('SELECT * FROM documents')
documents = sqlite_cursor.fetchall()

for doc in documents:
    mysql_cursor.execute('''
        INSERT INTO documents (id, filename, original_filename, file_type, file_size, 
                              upload_time, content_hash, status, metadata, created_by)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', doc)

# 迁移 FAQ
sqlite_cursor.execute('SELECT * FROM faqs')
faqs = sqlite_cursor.fetchall()

for faq in faqs:
    mysql_cursor.execute('''
        INSERT INTO faqs (id, question, answer, document_id, category, tags, 
                         similarity_score, view_count, is_verified, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', faq)

mysql_conn.commit()
mysql_conn.close()
sqlite_conn.close()

print("迁移完成！")
```

执行迁移：

```bash
python scripts/migrate_sqlite_to_mysql.py
```

## 🎯 验证迁移

访问智能客服系统：
```
http://localhost:5001/chatbot/
```

上传文档测试，查看日志确认数据已写入 MySQL。

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| USE_MYSQL | 是否使用 MySQL | false |
| MYSQL_HOST | MySQL 主机地址 | localhost |
| MYSQL_PORT | MySQL 端口 | 3306 |
| MYSQL_USER | MySQL 用户名 | root |
| MYSQL_PASSWORD | MySQL 密码 | '' |
| MYSQL_DATABASE | 数据库名称 | knowledge_base |

## 📝 注意事项

1. **字符集**: 使用 utf8mb4 支持中文和 emoji
2. **引擎**: 使用 InnoDB 支持事务和外键
3. **密码安全**: 生产环境请修改默认密码
4. **备份**: 迁移前务必备份 SQLite 数据

## 🚨 常见问题

### Q: 提示 `pymysql` 未找到
```bash
pip install pymysql
```

### Q: 数据库连接失败
检查 MySQL 服务是否启动：
```bash
# macOS
brew services list | grep mysql

# Linux
systemctl status mysql
```

### Q: 外键约束错误
确保 `users` 表已创建，或暂时禁用外键检查：
```sql
SET FOREIGN_KEY_CHECKS=0;
-- 执行迁移
SET FOREIGN_KEY_CHECKS=1;
```

## 📊 SQLite vs MySQL 对比

| 特性 | SQLite | MySQL |
|------|--------|-------|
| 并发性能 | 低 | 高 |
| 数据量 | <10GB | 不限 |
| 多用户 | 不支持 | 支持 |
| 网络访问 | 不支持 | 支持 |
| 备份恢复 | 文件复制 | 在线备份 |
| 适用场景 | 开发测试 | 生产环境 |

## ✅ 完成标志

- [ ] 安装 pymysql
- [ ] 配置 .env 文件
- [ ] 执行初始化脚本
- [ ] 启动应用测试
- [ ] 验证数据写入 MySQL
