#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""初始化钉钉定时推送配置表"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "12345678"),
    "database": os.getenv("SCHEDULE_DB", "schedule_system")
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    sql = """
    CREATE TABLE IF NOT EXISTS dingtalk_schedule_config (
        id INT AUTO_INCREMENT PRIMARY KEY COMMENT '配置ID',
        webhook_url VARCHAR(500) NOT NULL COMMENT '钉钉机器人Webhook地址',
        time_slots TEXT COMMENT '推送时段列表（JSON格式）',
        schedule_times TEXT NOT NULL COMMENT '推送时间点列表（JSON格式）',
        enabled TINYINT(1) DEFAULT 1 COMMENT '是否启用',
        description VARCHAR(200) COMMENT '配置描述',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        INDEX idx_enabled (enabled),
        INDEX idx_created_at (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    cursor.execute(sql)
    conn.commit()
    print("✅ 数据库表创建成功")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ 错误: {e}")
