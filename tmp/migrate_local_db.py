import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db
import mysql.connector
from config import Config

# 获取数据库配置
config = Config()

# 直接连接 dingtalk_push 数据库
conn = mysql.connector.connect(
    host=config.MYSQL_HOST,
    port=config.MYSQL_PORT,
    user=config.MYSQL_USER,
    password=config.MYSQL_PASSWORD,
    database=config.DINGTALK_PUSH_DB,
    charset=config.MYSQL_CHARSET
)
cursor = conn.cursor()

fields_to_add = [
    ("is_deleted", "ALTER TABLE dingtalk_push_config ADD COLUMN is_deleted TINYINT(1) DEFAULT 0 COMMENT '是否已删除' AFTER enabled"),
    ("deleted_at", "ALTER TABLE dingtalk_push_config ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间' AFTER is_deleted"),
    ("deleted_by", "ALTER TABLE dingtalk_push_config ADD COLUMN deleted_by VARCHAR(50) NULL DEFAULT NULL COMMENT '删除人' AFTER deleted_at")
]

for field_name, sql in fields_to_add:
    try:
        cursor.execute(sql)
        conn.commit()
        print(f"✅ 成功添加 {field_name} 字段")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print(f"⚠️  {field_name} 字段已存在")
        else:
            print(f"❌ 添加 {field_name} 失败: {e}")

cursor.close()
conn.close()
print("🎉 数据库迁移完成，请刷新页面测试。")
