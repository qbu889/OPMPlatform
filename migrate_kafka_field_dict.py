#!/usr/bin/env python3
"""
数据迁移脚本：将 /sql/kafka_field/ 目录下的 CSV 文件迁移到 schedule.kafka_field_dict 表

CSV 文件命名规则：{kafka_field_name}_{date}.csv
CSV 格式支持两种：
1. 简单格式：ID,TXT 两列
2. 复杂格式：多列（专业ID,专业名称,备注等）

目标表结构：kafka_field_dict
- id: 主键
- kafka_field: 字段名（分类）
- dict_key: 字典键
- dict_value: 字典值
- sort_order: 排序
- is_enabled: 是否启用
- remark: 备注
- created_at: 创建时间
- updated_at: 更新时间
"""

import os
import csv
import re
import pymysql
from datetime import datetime
from typing import Dict, List, Tuple

# 配置
CSV_DIR = "/Users/linziwang/PycharmProjects/wordToWord/sql/kafka_field"
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12345678",
    "database": "schedule",
    "charset": "utf8mb4"
}

# 字段映射配置 - 复杂格式CSV的字段映射
FIELD_MAPPING = {
    "NETWORK_TYPE_TOP": {
        "key_column": "专业ID",
        "value_column": "专业名称",
        "remark_column": "备注"
    }
}


def get_kafka_field_name(filename: str) -> str:
    """从文件名提取 kafka_field 名称"""
    # 匹配模式：{name}_{date}.csv
    match = re.match(r"^([a-zA-Z_]+)_(\d{8})\.csv$", filename)
    if match:
        return match.group(1).upper()
    return filename.replace(".csv", "").upper()


def parse_csv_file(filepath: str) -> List[Dict]:
    """解析 CSV 文件，返回数据列表"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"解析文件失败 {filepath}: {e}")
    return data


def transform_simple_format(kafka_field: str, rows: List[Dict]) -> List[Tuple]:
    """转换简单格式 (ID, TXT)"""
    records = []
    for idx, row in enumerate(rows):
        dict_key = row.get('ID', row.get('id', '')).strip()
        dict_value = row.get('TXT', row.get('txt', row.get('value', ''))).strip()
        
        if not dict_key or not dict_value:
            continue
        
        # 截断过长的字段值（MySQL VARCHAR 默认最大 255）
        dict_key = dict_key[:255]
        dict_value = dict_value[:255]
            
        records.append({
            'kafka_field': kafka_field,
            'dict_key': dict_key,
            'dict_value': dict_value,
            'sort_order': idx + 1,
            'is_enabled': 1,
            'remark': ''
        })
    return records


def transform_complex_format(kafka_field: str, rows: List[Dict]) -> List[Tuple]:
    """转换复杂格式"""
    records = []
    mapping = FIELD_MAPPING.get(kafka_field, {})
    
    key_col = mapping.get('key_column', '专业ID')
    value_col = mapping.get('value_column', '专业名称')
    remark_col = mapping.get('remark_column', '备注')
    
    for idx, row in enumerate(rows):
        dict_key = row.get(key_col, row.get('ID', '')).strip()
        dict_value = row.get(value_col, row.get('专业名称', row.get('name', ''))).strip()
        remark = row.get(remark_col, '').strip()
        
        if not dict_key or not dict_value:
            continue
            
        records.append({
            'kafka_field': kafka_field,
            'dict_key': dict_key,
            'dict_value': dict_value,
            'sort_order': idx + 1,
            'is_enabled': 1,
            'remark': remark[:255] if remark else ''
        })
    return records


def detect_csv_format(rows: List[Dict]) -> str:
    """检测 CSV 格式"""
    if not rows:
        return 'unknown'
    
    first_row = rows[0]
    keys = set(first_row.keys())
    
    # 简单格式特征
    simple_keys = {'ID', 'TXT'}
    simple_keys_lower = {'id', 'txt', 'key', 'value'}
    
    if keys == simple_keys or keys.issubset(simple_keys_lower):
        return 'simple'
    
    # 复杂格式特征
    complex_keys = {'专业ID', '专业名称', '备注'}
    if keys & complex_keys:
        return 'complex'
    
    return 'simple'  # 默认按简单格式处理


def get_existing_keys(conn, kafka_field: str) -> set:
    """获取已存在的字典键"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT dict_key FROM kafka_field_dict WHERE kafka_field = %s",
        (kafka_field,)
    )
    return {row[0] for row in cursor.fetchall()}


def backup_table(conn, backup_file: str):
    """备份当前表数据"""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM kafka_field_dict")
    rows = cursor.fetchall()
    
    with open(backup_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([desc[0] for desc in cursor.description])
        writer.writerows(rows)
    
    print(f"已备份 {len(rows)} 条记录到 {backup_file}")


def migrate_data(conn, csv_files: List[str], backup: bool = True):
    """执行数据迁移"""
    # 备份
    if backup:
        backup_file = f"kafka_field_dict_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        backup_table(conn, backup_file)
    
    total_imported = 0
    total_skipped = 0
    
    for csv_file in csv_files:
        filepath = os.path.join(CSV_DIR, csv_file)
        kafka_field = get_kafka_field_name(csv_file)
        
        print(f"\n处理文件: {csv_file}")
        print(f"  -> Kafka字段: {kafka_field}")
        
        # 解析 CSV
        rows = parse_csv_file(filepath)
        if not rows:
            print(f"  -> 跳过：文件为空或解析失败")
            continue
        
        # 检测格式并转换
        fmt = detect_csv_format(rows)
        print(f"  -> 格式: {fmt}")
        
        if fmt == 'simple':
            records = transform_simple_format(kafka_field, rows)
        else:
            records = transform_complex_format(kafka_field, rows)
        
        # 获取已存在的键
        existing_keys = get_existing_keys(conn, kafka_field)
        
        # 插入数据
        cursor = conn.cursor()
        imported = 0
        skipped = 0
        
        for record in records:
            if record['dict_key'] in existing_keys:
                skipped += 1
                continue
            
            cursor.execute("""
                INSERT INTO kafka_field_dict 
                (kafka_field, dict_key, dict_value, sort_order, is_enabled, remark, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                record['kafka_field'],
                record['dict_key'],
                record['dict_value'],
                record['sort_order'],
                record['is_enabled'],
                record['remark'],
                datetime.now(),
                datetime.now()
            ))
            imported += 1
        
        conn.commit()
        print(f"  -> 导入: {imported} 条, 跳过(已存在): {skipped} 条")
        
        total_imported += imported
        total_skipped += skipped
    
    print(f"\n=== 迁移完成 ===")
    print(f"总计导入: {total_imported} 条")
    print(f"总计跳过: {total_skipped} 条")


def main():
    # 获取所有 CSV 文件
    csv_files = sorted([f for f in os.listdir(CSV_DIR) if f.endswith('.csv')])
    
    if not csv_files:
        print("错误：未找到 CSV 文件")
        return
    
    print(f"找到 {len(csv_files)} 个 CSV 文件:")
    for f in csv_files:
        print(f"  - {f}")
    
    # 连接数据库
    try:
        conn = pymysql.connect(**MYSQL_CONFIG)
        print(f"\n成功连接数据库: {MYSQL_CONFIG['database']}")
        
        # 执行迁移
        migrate_data(conn, csv_files)
        
        conn.close()
        print("\n数据库连接已关闭")
        
    except Exception as e:
        print(f"数据库连接失败: {e}")
        raise


if __name__ == "__main__":
    main()