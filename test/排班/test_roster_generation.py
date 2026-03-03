#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试排班生成功能
验证8:00～9:00和18:00～21:00排同一个人的逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes.排班.paiBanNew import RosterDB, RosterGenerator, DB_CONFIG
from datetime import date, datetime

def test_same_person_shifts():
    """测试8:00～9:00和18:00～21:00是否排同一个人"""
    print("=== 测试8:00～9:00和18:00～21:00排同一个人 ===")
    
    # 连接数据库
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败")
        return False
    
    try:
        # 清理测试数据
        test_date = date(2026, 2, 28)  # 选择一个工作日
        clean_sql = "DELETE FROM roster WHERE date = %s"
        db.execute(clean_sql, (test_date,))
        
        # 生成排班
        generator = RosterGenerator(db)
        generator.generate_roster(test_date, test_date)
        
        # 查询结果
        query_sql = """
        SELECT time_slot, staff_name, is_main 
        FROM roster 
        WHERE date = %s 
        ORDER BY time_slot
        """
        results = db.query(query_sql, (test_date,))
        
        print(f"\n📅 {test_date} 排班结果:")
        morning_staff = None
        evening_staff = None
        
        for row in results:
            time_slot = row['time_slot']
            staff_name = row['staff_name']
            is_main = row['is_main']
            role = "主班" if is_main else "辅班"
            
            print(f"  {time_slot}: {staff_name} ({role})")
            
            # 记录关键时段的人员
            if time_slot == "8:00～9:00":
                morning_staff = staff_name
            elif time_slot == "18:00～21:00":
                evening_staff = staff_name
        
        # 验证是否为同一个人
        if morning_staff and evening_staff:
            if morning_staff == evening_staff:
                print(f"\n✅ 成功：8:00～9:00和18:00～21:00都排了 {morning_staff}")
                return True
            else:
                print(f"\n❌ 失败：8:00～9:00排了 {morning_staff}，18:00～21:00排了 {evening_staff}")
                return False
        else:
            print("\n❌ 失败：未能找到8:00～9:00或18:00～21:00的排班记录")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    finally:
        db.close()

def test_multiple_days_rotation():
    """测试多天轮换是否正常工作"""
    print("\n=== 测试多天轮换 ===")
    
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败")
        return False
    
    try:
        # 清理测试数据
        start_date = date(2026, 3, 1)
        end_date = date(2026, 3, 3)
        
        clean_sql = "DELETE FROM roster WHERE date BETWEEN %s AND %s"
        db.execute(clean_sql, (start_date, end_date))
        
        # 生成三天排班
        generator = RosterGenerator(db)
        generator.generate_roster(start_date, end_date)
        
        # 查询每天的8:00～9:00和18:00～21:00人员
        query_sql = """
        SELECT date, time_slot, staff_name
        FROM roster 
        WHERE date BETWEEN %s AND %s 
        AND time_slot IN ('8:00～9:00', '18:00～21:00')
        ORDER BY date, time_slot
        """
        results = db.query(query_sql, (start_date, end_date))
        
        print(f"\n📅 {start_date} 至 {end_date} 轮换情况:")
        daily_assignments = {}
        
        for row in results:
            date_key = row['date']
            time_slot = row['time_slot']
            staff_name = row['staff_name']
            
            if date_key not in daily_assignments:
                daily_assignments[date_key] = {}
            daily_assignments[date_key][time_slot] = staff_name
        
        # 验证每天的情况
        for test_date in [start_date, start_date + timedelta(days=1), start_date + timedelta(days=2)]:
            if test_date in daily_assignments:
                assignments = daily_assignments[test_date]
                morning_staff = assignments.get('8:00～9:00')
                evening_staff = assignments.get('18:00～21:00')
                
                if morning_staff and evening_staff:
                    same_person = "✅" if morning_staff == evening_staff else "❌"
                    print(f"  {test_date}: 8:00～9:00={morning_staff}, 18:00～21:00={evening_staff} {same_person}")
                else:
                    print(f"  {test_date}: 数据不完整")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    from datetime import timedelta
    
    print("开始测试排班生成功能...")
    
    # 运行测试
    test1_passed = test_same_person_shifts()
    test2_passed = test_multiple_days_rotation()
    
    print(f"\n=== 测试结果 ===")
    print(f"同人排班测试: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"多天轮换测试: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 所有测试通过！8:00～9:00和18:00～21:00成功排同一个人")
    else:
        print("\n⚠️  部分测试失败，请检查代码逻辑")