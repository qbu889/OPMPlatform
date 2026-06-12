#!/usr/bin/env python3
"""
数据一致性验证脚本：验证 kafka_field_dict 表的数据完整性
"""

import pymysql
from typing import Dict, Set, Tuple

MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12345678",
    "database": "schedule",
    "charset": "utf8mb4"
}


def get_kafka_field_dict_data(conn) -> Dict[str, Set[Tuple[str, str]]]:
    """获取 kafka_field_dict 表中所有数据"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT kafka_field, dict_key, dict_value 
        FROM kafka_field_dict 
        WHERE is_enabled = 1
        ORDER BY kafka_field, dict_key
    """)
    result = {}
    for row in cursor.fetchall():
        kafka_field = str(row[0])
        dict_key = str(row[1])
        dict_value = str(row[2])
        if kafka_field not in result:
            result[kafka_field] = set()
        result[kafka_field].add((dict_key, dict_value))
    return result


def main():
    conn = pymysql.connect(**MYSQL_CONFIG)
    print(f"成功连接数据库: {MYSQL_CONFIG['database']}\n")
    
    # 获取所有数据
    field_data = get_kafka_field_dict_data(conn)
    
    # 统计信息
    total_records = sum(len(rows) for rows in field_data.values())
    total_fields = len(field_data)
    
    print("=" * 60)
    print("              kafka_field_dict 表数据完整性报告")
    print("=" * 60)
    print(f"总字段数: {total_fields}")
    print(f"总记录数: {total_records}")
    print("-" * 60)
    print(f"{'字段名':<30} {'记录数':>10} {'状态':<10}")
    print("-" * 60)
    
    for field_name, records in sorted(field_data.items()):
        count = len(records)
        if count > 0:
            status = "✅ 正常"
        else:
            status = "⚠️  空"
        print(f"{field_name:<30} {count:>10} {status:<10}")
    
    print("-" * 60)
    
    # 验证特定字段 NETWORK_TYPE_TOP
    print("\n验证 NETWORK_TYPE_TOP 字段数据:")
    network_type_top_data = field_data.get("NETWORK_TYPE_TOP", set())
    print(f"  记录数: {len(network_type_top_data)}")
    if network_type_top_data:
        print("  数据示例:")
        for item in sorted(list(network_type_top_data))[:5]:
            print(f"    - {item[0]}: {item[1]}")
        if len(network_type_top_data) > 5:
            print(f"    ... 还有 {len(network_type_top_data) - 5} 条")
    
    conn.close()
    
    # 测试 API 调用
    print("\n" + "=" * 60)
    print("                    API 接口测试")
    print("=" * 60)
    try:
        import requests
        
        # 测试 field-options 接口
        url = "http://localhost:5004/kafka-generator/field-options?kafka_field=NETWORK_TYPE_TOP"
        response = requests.get(url)
        
        print(f"\n测试接口: {url}")
        print(f"HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应格式: {'JSON' if isinstance(data, dict) else '其他'}")
            if data.get("success"):
                rows = data.get("data", {}).get("rows", [])
                print(f"返回记录数: {len(rows)}")
                print("返回数据示例:")
                for row in rows[:3]:
                    print(f"  - {row}")
                if len(rows) > 3:
                    print(f"  ... 还有 {len(rows) - 3} 条")
            else:
                print(f"错误信息: {data.get('message')}")
        else:
            print(f"请求失败: {response.text}")
            
    except ImportError:
        print("⚠️  requests 库未安装，跳过 API 测试")
    except Exception as e:
        print(f"⚠️  API 测试失败: {e}")


if __name__ == "__main__":
    main()