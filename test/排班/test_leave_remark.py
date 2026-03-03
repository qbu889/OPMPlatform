#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试排班备注功能 - 验证请假人员是否被正确添加到备注中
"""

import sys
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pymysql
from routes.排班.paiBanNew_v2 import RosterGenerator, RosterDB

def test_leave_remark():
    """测试请假备注功能"""
    
    print("=" * 60)
    print("测试排班备注功能")
    print("=" * 60)
    
    # 创建数据库连接配置
    db_config = {
        'host': os.getenv("DB_HOST", "localhost"),
        'port': int(os.getenv("DB_PORT", 3306)),
        'user': os.getenv("DB_USER", "root"),
        'password': os.getenv("DB_PASSWORD", "12345678"),
        'database': os.getenv("DB_NAME", "schedule"),
        'charset': 'utf8mb4'
    }
    
    # 创建 RosterDB 实例
    db = RosterDB(db_config)
    if not db.connect():
        print("数据库连接失败，退出测试")
        return False
    
    # 创建排班生成器实例
    generator = RosterGenerator(db)
    
    # 测试日期：2026-02-05（有请假人员）
    test_date = date(2026, 2, 5)
    
    print(f"\n测试日期：{test_date}")
    print("-" * 60)
    
    # 获取当天请假人员
    all_leave_staffs = generator._get_leave_staffs(test_date)
    print(f"请假人员：{all_leave_staffs}")
    
    # 生成日常排班
    daily_roster = generator._get_daily_roster(test_date)
    
    print(f"\n生成的排班记录数：{len(daily_roster)}")
    print("\n排班详情:")
    print("-" * 60)
    
    # 检查备注
    remarks_found = set()
    for record in daily_roster:
        remark = record.get('remark')
        if remark:
            remarks_found.add(remark)
        print(f"{record['time_slot']:20s} - {record['staff_name']:5s} - 备注：{remark or '无'}")
    
    print("\n" + "=" * 60)
    print(f"找到的备注类型：{len(remarks_found)} 种")
    for remark in sorted(remarks_found):
        print(f"  - {remark}")
    print("=" * 60)
    
    # 验证期望结果
    expected_remark = f"因请假调整（{', '.join(all_leave_staffs)}）"
    print(f"\n期望备注：{expected_remark}")
    
    if expected_remark in remarks_found:
        print("✓ 测试通过：备注格式正确，包含所有请假人员")
        success1 = True
    else:
        print("✗ 测试失败：备注不符合预期")
        success1 = False
    
    # 测试第二个日期：2026-02-06（多人请假）
    print("\n\n" + "=" * 60)
    print("测试第二组：2026-02-06（多人请假）")
    print("=" * 60)
    
    test_date2 = date(2026, 2, 6)
    print(f"\n测试日期：{test_date2}")
    print("-" * 60)
    
    all_leave_staffs2 = generator._get_leave_staffs(test_date2)
    print(f"请假人员：{all_leave_staffs2}")
    
    daily_roster2 = generator._get_daily_roster(test_date2)
    
    print(f"\n生成的排班记录数：{len(daily_roster2)}")
    print("\n排班详情:")
    print("-" * 60)
    
    remarks_found2 = set()
    for record in daily_roster2:
        remark = record.get('remark')
        if remark:
            remarks_found2.add(remark)
        print(f"{record['time_slot']:20s} - {record['staff_name']:5s} - 备注：{remark or '无'}")
    
    print("\n" + "=" * 60)
    print(f"找到的备注类型：{len(remarks_found2)} 种")
    for remark in sorted(remarks_found2):
        print(f"  - {remark}")
    print("=" * 60)
    
    expected_remark2 = f"因请假调整（{', '.join(all_leave_staffs2)}）"
    print(f"\n期望备注：{expected_remark2}")
    
    if expected_remark2 in remarks_found2:
        print("✓ 测试通过：备注格式正确，包含所有请假人员")
        success2 = True
    else:
        print("✗ 测试失败：备注不符合预期")
        success2 = False
    
    return success1 and success2


if __name__ == "__main__":
    success = test_leave_remark()
    sys.exit(0 if success else 1)
