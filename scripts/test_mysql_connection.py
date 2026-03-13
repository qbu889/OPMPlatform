#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 MySQL 数据库连接
"""
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ 已加载 .env 文件：{env_path}")

# 从环境变量获取配置
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_CHARSET = os.getenv('MYSQL_CHARSET', 'utf8mb4')
KNOWLEDGE_BASE_DB = os.getenv('KNOWLEDGE_BASE_DB', 'knowledge_base')

print(f"\n📋 数据库配置:")
print(f"  主机：{MYSQL_HOST}:{MYSQL_PORT}")
print(f"  用户：{MYSQL_USER}")
print(f"  密码：{'*' * len(MYSQL_PASSWORD) if MYSQL_PASSWORD else 'None'}")
print(f"  数据库：{KNOWLEDGE_BASE_DB}")
print()

try:
    # 尝试连接
    print("🔌 正在连接 MySQL...")
    conn = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset=MYSQL_CHARSET,
        database=KNOWLEDGE_BASE_DB
    )
    
    print("✅ 连接成功！")
    
    # 测试查询
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE()")
    current_db = cursor.fetchone()[0]
    print(f"📊 当前数据库：{current_db}")
    
    # 检查表是否存在
    cursor.execute("SHOW TABLES LIKE 'fpa_adjustment_%'")
    tables = cursor.fetchall()
    if tables:
        print(f"📋 已存在的调整因子表:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("⚠ 调整因子表不存在，需要执行初始化脚本")
    
    cursor.close()
    conn.close()
    
except mysql.connector.errors.ProgrammingError as e:
    print(f"❌ 连接失败：{e}")
    print("\n💡 可能的原因:")
    print("  1. 密码错误（当前密码：12345678）")
    print("  2. 用户不存在")
    print("  3. 数据库不存在")
    print("\n🔧 解决方案:")
    print("  1. 修改 .env 文件中的 MYSQL_PASSWORD")
    print("  2. 或者修改 MySQL 密码：ALTER USER 'root'@'localhost' IDENTIFIED BY '12345678';")
except Exception as e:
    print(f"❌ 发生错误：{e}")
