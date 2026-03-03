#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班系统测试脚本
验证改进后的排班逻辑是否正确
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from routes.排班.paiBanNew_v2 import RosterDB, RosterGenerator, DB_CONFIG
from datetime import date

def test_roster_generation():
    """测试排班生成"""
    print("=" * 60)
    print("排班系统测试")
    print("=" * 60)
    
    # 1. 初始化数据库连接
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        print("数据库连接失败!")
        return
    
    print("\n1. 清除旧数据...")
    start_clean = date(2026, 2, 1)
    end_clean = date(2026, 3, 1)
    sql = "DELETE FROM roster WHERE date BETWEEN %s AND %s"
    db.execute(sql, (start_clean.strftime('%Y-%m-%d'), end_clean.strftime('%Y-%m-%d')))
    print(f"   已清除 {start_clean} 至 {end_clean} 的数据")
    
    # 重置轮换索引
    print("\n2. 重置轮换索引...")
    sql_reset = "UPDATE rotation_config SET current_index = 0 WHERE time_slot_type IN ('日常 8-9', '节假日')"
    db.execute(sql_reset)
    print("   轮换索引已重置")
    
    # 2. 生成排班
    print("\n3. 生成排班...")
    generator = RosterGenerator(db)
    start_date = date(2026, 2, 1)
    end_date = date(2026, 2, 23)
    generator.generate_roster(start_date, end_date)
    print(f"   已生成 {start_date} 至 {end_date} 的排班")
    
    # 3. 查询并显示结果
    print("\n4. 查询排班结果:")
    print("-" * 60)
    
    # 查询日常排班 (工作日)
    sql_daily = """
    SELECT date, time_slot, staff_name, is_main, rotation_index 
    FROM roster 
    WHERE date BETWEEN %s AND %s 
    AND time_slot IN ('8:00～9:00', '18:00～21:00')
    ORDER BY date, time_slot
    """
    
    results = db.query(sql_daily, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    print("\n日常早班和晚班排班 (8:00-9:00 和 18:00-21:00):")
    print(f"{'日期':<12} {'时段':<15} {'人员':<10} {'主班':<6} {'索引':<6}")
    print("-" * 60)
    
    current_date = None
    for row in results:
        row_date = str(row['date'])
        if row_date != str(current_date):
            if current_date is not None:
                print()
            current_date = row_date
        is_main_str = "是" if row['is_main'] else "否"
        print(f"{row_date:<12} {row['time_slot']:<15} {row['staff_name']:<10} {is_main_str:<6} {row['rotation_index']:<6}")
    
    # 查询节假日排班
    sql_holiday = """
    SELECT r.date, r.time_slot, r.staff_name, r.is_main, r.rotation_index
    FROM roster r
    INNER JOIN holiday_config h ON r.date = h.holiday_date
    WHERE r.date BETWEEN %s AND %s 
    AND h.is_working_day = 0
    ORDER BY r.date, r.time_slot
    """
    
    holiday_results = db.query(sql_holiday, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    if holiday_results:
        print("\n\n节假日排班:")
        print(f"{'日期':<12} {'时段':<15} {'人员':<10} {'主班':<6} {'索引':<6}")
        print("-" * 60)
        
        current_date = None
        for row in holiday_results:
            row_date = str(row['date'])
            if row_date != str(current_date):
                if current_date is not None:
                    print()
                current_date = row_date
            is_main_str = "是" if row['is_main'] else "否"
            print(f"{row_date:<12} {row['time_slot']:<15} {row['staff_name']:<10} {is_main_str:<6} {row['rotation_index']:<6}")
    
    # 检查轮换索引
    print("\n\n当前轮换索引状态:")
    sql_index = "SELECT time_slot_type, rotation_order, current_index FROM rotation_config"
    index_results = db.query(sql_index)
    
    for row in index_results:
        order = row['rotation_order'].split(',')
        index = row['current_index']
        next_person = order[index] if index < len(order) else "N/A"
        print(f"  {row['time_slot_type']}: 索引={index}, 下一人={next_person}")
    
    # 验证问题点
    print("\n" + "=" * 60)
    print("问题验证:")
    print("=" * 60)
    
    # 验证 1: 2026-02-02 到 2026-02-06 的日常排班
    verify_dates = [
        (date(2026, 2, 2), "吴绍烨"),
        (date(2026, 2, 3), "郑晨昊"),
        (date(2026, 2, 4), "林子旺"),
        (date(2026, 2, 5), "曾婷婷"),
        (date(2026, 2, 6), "陈伟强"),
    ]
    
    print("\n日常排班轮换验证 (8:00-9:00 时段):")
    for check_date, expected in verify_dates:
        sql_check = """
        SELECT staff_name FROM roster 
        WHERE date = %s AND time_slot = '8:00～9:00'
        """
        result = db.query(sql_check, (check_date.strftime('%Y-%m-%d'),))
        actual = result[0]['staff_name'] if result else "无排班"
        status = "✓" if actual == expected else "✗"
        print(f"  {check_date}: {actual} (期望：{expected}) {status}")
    
    # 验证 2: 节假日排班
    holiday_checks = [
        (date(2026, 2, 7), "陈伟强"),
        (date(2026, 2, 8), "郑晨昊"),
        (date(2026, 2, 15), "林子旺"),  # 应该轮到下一个人
    ]
    
    print("\n节假日排班轮换验证 (8:00-12:00 时段):")
    for check_date, expected in holiday_checks:
        sql_check = """
        SELECT staff_name FROM roster 
        WHERE date = %s AND time_slot = '8:00～12:00'
        """
        result = db.query(sql_check, (check_date.strftime('%Y-%m-%d'),))
        actual = result[0]['staff_name'] if result else "无排班"
        status = "✓" if actual == expected else "✗"
        print(f"  {check_date}: {actual} (期望：{expected}) {status}")
    
    db.close()
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_roster_generation()
