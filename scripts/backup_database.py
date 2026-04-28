#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库备份脚本 - 导出表结构和数据为SQL文件
"""
import mysql.connector
from mysql.connector import Error
import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_connection(database=None):
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=database or Config.KNOWLEDGE_BASE_DB,
            charset=Config.MYSQL_CHARSET
        )
        return connection
    except Error as e:
        print(f"连接数据库时出错: {e}")
        return None

def get_all_tables(cursor):
    """获取所有表名"""
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def get_table_structure(cursor, table_name):
    """获取表结构（CREATE TABLE语句）"""
    cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
    result = cursor.fetchone()
    if result:
        return result[1]
    return None

def get_table_data(cursor, table_name):
    """获取表数据并生成INSERT语句"""
    cursor.execute(f"SELECT * FROM `{table_name}`")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    insert_statements = []
    for row in rows:
        values = []
        for value in row:
            if value is None:
                values.append('NULL')
            elif isinstance(value, str):
                # 转义特殊字符
                escaped = value.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '\\r')
                values.append(f"'{escaped}'")
            elif isinstance(value, bytes):
                values.append(f"_binary'{value.hex()}'")
            elif isinstance(value, datetime):
                values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
            else:
                values.append(str(value))
        
        values_str = ', '.join(values)
        columns_str = ', '.join([f'`{col}`' for col in columns])
        insert_stmt = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({values_str});"
        insert_statements.append(insert_stmt)
    
    return insert_statements

def backup_database(output_file):
    """备份整个数据库"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 获取所有表
        tables = get_all_tables(cursor)
        print(f"找到 {len(tables)} 个表: {', '.join(tables)}")
        
        # 打开输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write("-- ==========================================\n")
            f.write(f"-- 数据库备份文件\n")
            f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- 数据库: {Config.KNOWLEDGE_BASE_DB}\n")
            f.write("-- ==========================================\n\n")
            
            # 创建数据库语句
            f.write("-- 1. 创建数据库（如果不存在）\n")
            f.write(f"CREATE DATABASE IF NOT EXISTS `{Config.KNOWLEDGE_BASE_DB}` \n")
            f.write("    DEFAULT CHARACTER SET utf8mb4 \n")
            f.write("    DEFAULT COLLATE utf8mb4_unicode_ci;\n\n")
            
            # 使用数据库
            f.write("-- 2. 使用数据库\n")
            f.write(f"USE `{Config.KNOWLEDGE_BASE_DB}`;\n\n")
            
            # 处理每个表
            f.write("-- 3. 创建数据表\n")
            for table_name in tables:
                print(f"\n处理表: {table_name}")
                
                # 获取表结构
                create_stmt = get_table_structure(cursor, table_name)
                if create_stmt:
                    f.write(f"{create_stmt};\n\n")
                    print(f"  ✓ 导出表结构")
                
                # 获取表数据
                insert_stmts = get_table_data(cursor, table_name)
                if insert_stmts:
                    f.write(f"-- 表 {table_name} 的数据\n")
                    for stmt in insert_stmts:
                        f.write(f"{stmt}\n")
                    f.write("\n")
                    print(f"  ✓ 导出 {len(insert_stmts)} 条数据")
                else:
                    print(f"  - 表为空，跳过数据导出")
        
        print(f"\n✓ 备份完成！文件已保存到: {output_file}")
        return True
        
    except Error as e:
        print(f"备份过程中出错: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    # 设置输出文件路径
    output_dir = '/Users/linziwang/PycharmProjects/wordToWord/sql/run'
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'backup_{timestamp}.sql')
    
    print("=" * 60)
    print("开始备份数据库...")
    print(f"数据库: {Config.KNOWLEDGE_BASE_DB}")
    print(f"输出文件: {output_file}")
    print("=" * 60)
    
    success = backup_database(output_file)
    
    if success:
        print("\n备份成功！")
    else:
        print("\n备份失败！")
