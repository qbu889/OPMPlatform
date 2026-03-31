"""
更新关键词历史记录表结构，添加 version_snapshot 和 is_snapshot 字段
"""
import sqlite3
import os

DATABASE = 'models/keywords.db'

def update_table():
    """更新表结构"""
    if not os.path.exists(DATABASE):
        print(f"数据库文件不存在：{DATABASE}")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='keyword_history'")
        if not cursor.fetchone():
            print("表 keyword_history 不存在，请先创建表")
            return
        
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(keyword_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 添加 version_snapshot 字段
        if 'version_snapshot' not in columns:
            cursor.execute('ALTER TABLE keyword_history ADD COLUMN version_snapshot TEXT')
            print("添加 version_snapshot 字段成功")
        else:
            print("version_snapshot 字段已存在")
        
        # 添加 is_snapshot 字段
        if 'is_snapshot' not in columns:
            cursor.execute('ALTER TABLE keyword_history ADD COLUMN is_snapshot BOOLEAN DEFAULT 0')
            print("添加 is_snapshot 字段成功")
        else:
            print("is_snapshot 字段已存在")
        
        conn.commit()
        print("表结构更新完成")
        
    except Exception as e:
        print(f"更新失败：{e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_table()
