#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试排班轮换逻辑 - 追踪为什么 2026-02-05 又排了林子旺
"""

import sys
import os
from dotenv import load_dotenv
from datetime import date, timedelta

load_dotenv()

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import pymysql
from routes.排班.paiBanNew_v2 import RosterGenerator, RosterDB

def debug_rotation():
    """调试轮换逻辑"""
    
    print("=" * 80)
    print("调试排班轮换逻辑")
    print("=" * 80)
    
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
        return
    
    # 手动检查 2026-02-03 到 2026-02-06 的排班和轮换索引
    test_dates = [
        date(2026, 2, 3),
        date(2026, 2, 4),
        date(2026, 2, 5),
        date(2026, 2, 6)
    ]
    
    for test_date in test_dates:
        print(f"\n{'='*80}")
        print(f"日期：{test_date}")
        print(f"{'='*80}")
        
        # 查询当天的排班记录
        sql = """
        SELECT time_slot, staff_name, rotation_index 
        FROM roster 
        WHERE date = %s 
        ORDER BY 
            CASE time_slot
                WHEN '8:00～9:00' THEN 1
                WHEN '9:00～12:00' THEN 2
                WHEN '13:30～18:00' THEN 3
                WHEN '18:00～21:00' THEN 4
                ELSE 5
            END
        """
        results = db.query(sql, (test_date,))
        
        print(f"\n当天排班:")
        for row in results:
            print(f"  {row['time_slot']:20s} - {row['staff_name']:5s} (索引:{row['rotation_index']})")
        
        # 查询轮换配置的当前索引
        sql_config = "SELECT time_slot_type, current_index FROM rotation_config WHERE time_slot_type = '日常 8-9'"
        config_result = db.query(sql_config)
        if config_result:
            print(f"\n轮换配置 '日常 8-9' 的当前索引：{config_result[0]['current_index']}")
        
        # 查询请假人员
        sql_leave = """
        SELECT staff_name, is_full_day, start_time, end_time
        FROM leave_record 
        WHERE leave_date = %s
        """
        leave_results = db.query(sql_leave, (test_date,))
        if leave_results:
            print(f"\n请假人员:")
            for row in leave_results:
                if row['is_full_day']:
                    print(f"  {row['staff_name']:5s} - 全天")
                else:
                    print(f"  {row['staff_name']:5s} - {row['start_time']}~{row['end_time']}")
        
        # 查询前一天晚班人员
        prev_date = test_date - timedelta(days=1)
        sql_prev_evening = """
        SELECT staff_name 
        FROM roster 
        WHERE date = %s AND time_slot LIKE '%%18:00%%'
        """
        prev_evening_results = db.query(sql_prev_evening, (str(prev_date),))
        if prev_evening_results:
            prev_evening_staffs = [row['staff_name'] for row in prev_evening_results]
            print(f"\n前一天 ({prev_date}) 晚班人员：{', '.join(prev_evening_staffs)}")

if __name__ == "__main__":
    debug_rotation()
