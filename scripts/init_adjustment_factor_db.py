#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化调整因子数据库表
"""
import sqlite3
import mysql.connector
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ 已加载 .env 文件：{env_path}")
else:
    print(f"⚠ 未找到 .env 文件，使用默认配置")

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config

def create_adjustment_factor_tables():
    """创建调整因子相关的数据库表"""
    
    # 使用 MySQL 数据库
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        charset=Config.MYSQL_CHARSET,
        database=Config.KNOWLEDGE_BASE_DB  # 使用知识库数据库
    )
    cursor = conn.cursor()
    
    try:
        # 1. 调整因子主表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fpa_adjustment_factor (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增 ID',
                factor_name VARCHAR(255) NOT NULL COMMENT '因子名称',
                factor_category VARCHAR(100) COMMENT '因子分类（如：应用类型、质量特性等）',
                option_name TEXT COMMENT '选项名称',
                score_value DECIMAL(5,2) COMMENT '分值',
                formula TEXT COMMENT '计算公式',
                display_order INT DEFAULT 0 COMMENT '显示顺序',
                parent_id INT DEFAULT NULL COMMENT '父级 ID（用于层级关系）',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_category (factor_category),
                INDEX idx_parent (parent_id),
                INDEX idx_order (display_order)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='FPA 调整因子表'
        ''')
        
        # 2. 调整因子配置表（存储整体配置）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fpa_adjustment_config (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '自增 ID',
                config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
                config_value TEXT COMMENT '配置值',
                config_type VARCHAR(50) COMMENT '配置类型（scale_timing: 规模计数时机，application_type: 应用类型等）',
                description VARCHAR(500) COMMENT '配置描述',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_key (config_key),
                INDEX idx_type (config_type)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
            COMMENT='FPA 调整因子配置表'
        ''')
        
        # 插入默认配置数据
        default_configs = [
            ('scale_timing', '估算中期', 'scale_timing', '规模计数时机'),
            ('application_type_default', '业务处理', 'application_type', '默认应用类型'),
        ]
        
        cursor.executemany('''
            INSERT INTO fpa_adjustment_config (config_key, config_value, config_type, description)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE config_value = VALUES(config_value)
        ''', default_configs)
        
        conn.commit()
        
        print("✓ 调整因子数据库表创建成功！")
        print(f"  - fpa_adjustment_factor: 调整因子主表")
        print(f"  - fpa_adjustment_config: 调整因子配置表")
        
    except Exception as e:
        print(f"✗ 创建数据库表失败：{e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    create_adjustment_factor_tables()
