#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化 roster 表结构"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# 连接数据库
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "12345678"),
    database=os.getenv("DB_NAME", "schedule"),
    charset="utf8mb4"
)

cursor = conn.cursor()

print("=" * 60)
print("初始化 roster 表结构")
print("=" * 60)

# 检查并添加字段
columns_to_add = [
    ("is_main", "BOOLEAN DEFAULT FALSE COMMENT '是否为主班' AFTER staff_name"),
    ("rotation_index", "INT DEFAULT 0 COMMENT '轮换索引' AFTER is_main"),
    ("remark", "VARCHAR(200) COMMENT '备注 (如：因请假调整)' AFTER rotation_index"),
    ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER remark")
]

for column_name, column_def in columns_to_add:
    # 检查字段是否存在
    check_sql = """
    SELECT COUNT(*) 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_SCHEMA = 'schedule' 
    AND TABLE_NAME = 'roster' 
    AND COLUMN_NAME = %s
    """
    cursor.execute(check_sql, (column_name,))
    exists = cursor.fetchone()[0]
    
    if exists == 0:
        # 字段不存在，添加
        add_sql = f"ALTER TABLE roster ADD COLUMN {column_name} {column_def}"
        try:
            cursor.execute(add_sql)
            print(f"✓ 成功添加字段：{column_name}")
        except Exception as e:
            print(f"✗ 添加字段 {column_name} 失败：{e}")
    else:
        print(f"- 字段 {column_name} 已存在，跳过")

conn.commit()

# 显示最终的表结构
print("\n" + "=" * 60)
print("当前 roster 表结构:")
print("=" * 60)
cursor.execute("SHOW CREATE TABLE roster")
result = cursor.fetchone()
print(result[1])

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("表结构初始化完成!")
print("=" * 60)
