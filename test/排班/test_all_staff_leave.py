#!/usr/bin/env python3
"""测试全体请假时的兜底排班逻辑"""

from dotenv import load_dotenv
import os, sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'routes'))

from 排班.paiBanNew_v2 import RosterDB, RosterGenerator, DB_CONFIG
from datetime import date

def test_all_staff_leave():
    """测试全体请假时的兜底排班"""
    
    # 创建数据库连接
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        print("❌ 数据库连接失败")
        return
    
    # 清除 2026-02-25 的旧数据
    print("清除 2026-02-25 的旧排班数据...")
    sql = "DELETE FROM roster WHERE date = '2026-02-25'"
    db.execute(sql)
    
    # 添加全体请假记录（模拟）
    print("\n添加全体请假记录...")
    all_staffs = ['林子旺', '曾婷婷', '陈伟强', '吴绍烨', '郑晨昊']
    for staff in all_staffs:
        sql = """
        INSERT INTO leave_record (staff_name, leave_date, is_full_day, start_time, end_time)
        VALUES (%s, %s, TRUE, NULL, NULL)
        ON DUPLICATE KEY UPDATE is_full_day = TRUE
        """
        db.execute(sql, (staff, '2026-02-25'))
        print(f"  ✓ {staff} 全天请假")
    
    # 生成排班
    print("\n生成 2026-02-25 的排班...")
    generator = RosterGenerator(db)
    generator.generate_roster(date(2026, 2, 25), date(2026, 2, 25))
    
    # 查询生成的排班
    print("\n查询生成的排班:")
    sql = """
    SELECT time_slot, staff_name, is_main, remark 
    FROM roster 
    WHERE date = '2026-02-25'
    ORDER BY 
        CASE time_slot
            WHEN '8:00～9:00' THEN 1
            WHEN '9:00～12:00' THEN 2
            WHEN '13:30～18:00' THEN 3
            WHEN '18:00～21:00' THEN 4
            ELSE 5
        END
    """
    results = db.query(sql)
    
    if not results:
        print("  ❌ 没有生成排班记录！")
    else:
        print(f"\n  成功生成 {len(results)} 条排班记录:")
        for r in results:
            main_flag = "(主)" if r['is_main'] else ""
            remark = f" [{r['remark']}]" if r['remark'] else ""
            print(f"    {r['time_slot']:20s} - {r['staff_name']:5s}{main_flag:3s}{remark}")
    
    # 验证是否是核心人员
    print("\n验证结果:")
    core_staff_count = sum(1 for r in results if r['staff_name'] == '郑晨昊')
    if core_staff_count > 0:
        print(f"  ✓ 兜底逻辑生效：核心人员（郑晨昊）被安排到 {core_staff_count} 个时段")
    else:
        print(f"  ❌ 兜底逻辑未生效：没有排核心人员")
    
    # 清理测试数据（删除请假记录）
    print("\n清理测试数据...")
    for staff in all_staffs:
        sql = "DELETE FROM leave_record WHERE staff_name = %s AND leave_date = '2026-02-25'"
        db.execute(sql, (staff,))
    print("  ✓ 已删除全体请假记录")
    
    # 重新生成正常排班
    print("\n重新生成 2026-02-25 的正常排班...")
    sql = "DELETE FROM roster WHERE date = '2026-02-25'"
    db.execute(sql)
    generator.generate_roster(date(2026, 2, 25), date(2026, 2, 25))
    print("  ✓ 完成")

if __name__ == "__main__":
    test_all_staff_leave()
