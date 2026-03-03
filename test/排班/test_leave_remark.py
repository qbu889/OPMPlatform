#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试排班备注功能 - 验证请假人员是否被正确添加到备注中
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.排班.paiBanNew_v2 import RosterGenerator
from datetime import date

def test_leave_remark():
    """测试请假备注功能"""
    
    print("=" * 60)
    print("测试排班备注功能")
    print("=" * 60)
    
    # 创建排班生成器实例
    generator = RosterGenerator()
    
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
        return True
    else:
        print("✗ 测试失败：备注不符合预期")
        return False


if __name__ == "__main__":
    success = test_leave_remark()
    sys.exit(0 if success else 1)
