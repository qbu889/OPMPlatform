#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.8.10 排班程序
实现规则：
1. 日常/节假日时段划分与人员轮换
2. 请假人员过滤（全天/时段）
3. 节假日早班避开前一日同时段人员
4. 排班数据写入MySQL数据库
"""
from logging import debug

import pymysql
from datetime import datetime, date, timedelta
from typing import List, Dict, Set
from dotenv import load_dotenv
import os

# 加载环境变量（建议将数据库配置放在.env文件，避免硬编码）
load_dotenv()

# ===================== 核心配置 =====================
# 人员配置
CORE_STAFF = "郑晨昊"  # 核心主班人员
TEST_STAFFS = ["林子旺", "曾婷婷", "陈伟强", "吴绍烨"]  # 4名测试人员
ALL_STAFFS = TEST_STAFFS + [CORE_STAFF]

# 时段配置
TIME_SLOTS = {
    "日常": [
        "8:00～9:00",
        "9:00～12:00",
        "13:30～18:00",
        "18:00～21:00"
    ],
    "节假日": [
        "8:00～12:00",
        "13:30～17:30",
        "17:30～21:30"
    ]
}

# 数据库配置（从.env读取，或直接填写）
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "12345678"),
    "database": os.getenv("DB_NAME", "schedule"),
    "charset": "utf8mb4"
}


# ===================== 数据库工具类 =====================
class RosterDB:
    def __init__(self, config: Dict):
        self.config = config
        self.conn = None
        self.cursor = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.conn = pymysql.connect(**self.config)
            self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def query(self, sql: str, params: tuple = ()) -> List[Dict]:
        """执行查询"""
        try:
            self.cursor.execute(sql, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"查询失败: {sql} | {params} | {e}")
            return []

    def execute(self, sql: str, params: tuple = ()) -> bool:
        """执行增删改"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"执行失败: {sql} | {params} | {e}")
            return False


# ===================== 排班核心逻辑 =====================
class RosterGenerator:
    def __init__(self, db: RosterDB):
        self.db = db
        # 初始化轮换队列（从数据库读取）
        self.rotation_config = self._load_rotation_config()

    def _load_rotation_config(self) -> Dict:
        """加载轮换配置"""
        sql = "SELECT time_slot_type, rotation_order, current_index FROM rotation_config"
        result = self.db.query(sql)
        config = {}
        for item in result:
            config[item["time_slot_type"]] = {
                "order": item["rotation_order"].split(","),
                "index": item["current_index"]
            }

        # 确保必要的轮换配置存在（包含所有5名人员）
        required_configs = [
            ("日常8-9", ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"]),
            ("节假日", ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"])
        ]

        for config_type, default_order in required_configs:
            if config_type not in config:
                sql_insert = "INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) VALUES (%s, %s, %s)"
                self.db.execute(sql_insert, (config_type, ",".join(default_order), 0))
                config[config_type] = {
                    "order": default_order,
                    "index": 0
                }

        return config


    def is_holiday(self, date_obj):
        """通过查询holiday_config表判断是否为节假日"""
        date_str = date_obj.strftime('%Y-%m-%d')

        # 查询holiday_config表
        sql = """
        SELECT id FROM holiday_config 
        WHERE holiday_date = %s AND is_working_day = '0'
        """
        result = self.db.query(sql, (date_str,))
        return len(result) > 0

    def get_time_slots_for_date(self, date_obj):
        """根据日期是否为节假日返回对应的时段列表"""
        if self.is_holiday(date_obj):
            # 节假日时段：8:00～12:00, 13:30～17:30, 17:30～21:30
            return [
                ('8:00～12:00', 'MORNING'),
                ('13:30～17:30', 'AFTERNOON'),
                ('17:30～21:30', 'EVENING')
            ]
        else:
            # 正常工作日时段
            return [
                ('8:00～9:00', 'EARLY'),
                ('9:00～12:00', 'MORNING'),
                ('13:30～18:00', 'AFTERNOON'),
                ('18:00～21:00', 'EVENING')
            ]

    def _update_rotation_index(self, slot_type: str):
        """更新轮换索引（索引+1，超出人数重置为0）"""
        if slot_type not in self.rotation_config:
            return
        current = self.rotation_config[slot_type]
        new_index = (current["index"] + 1) % len(current["order"])
        # 更新内存
        self.rotation_config[slot_type]["index"] = new_index
        # 更新数据库
        sql = "UPDATE rotation_config SET current_index = %s WHERE time_slot_type = %s"
        self.db.execute(sql, (new_index, slot_type))

    def _get_date_type(self, target_date: date) -> str:
        """判断日期类型：日常/节假日"""
        # 先查询 holiday_config 表（使用标准日期格式）
        sql = """
        SELECT is_working_day 
        FROM holiday_config 
        WHERE holiday_date = %s
        """
        # 使用标准日期格式查询
        result = self.db.query(sql, (target_date.strftime('%Y-%m-%d'),))

        # 如果在 holiday_config 中有记录
        if result:
            is_working = result[0]["is_working_day"]
            return "日常" if is_working == 1 else "节假日"

        # 如果不在 holiday_config 中，判断是否为周末
        weekday = target_date.weekday()
        return "节假日" if weekday == 5 or weekday == 6 else "日常"

    def _get_leave_staffs(self, target_date: date, time_slot: str = None) -> Set[str]:
        """获取指定日期/时段的请假人员"""
        leave_staffs = set()

        # 1. 全天请假人员
        sql_all = """
        SELECT staff_name 
        FROM leave_record 
        WHERE leave_date = %s AND is_full_day = TRUE
        """
        all_leave = self.db.query(sql_all, (target_date,))
        leave_staffs.update([item["staff_name"] for item in all_leave])

        # 2. 时段请假人员（当time_slot为None时，查询所有时段请假）
        if time_slot is None:
            # 查询该日期所有时段请假人员
            sql_all_slots = """
            SELECT staff_name 
            FROM leave_record 
            WHERE leave_date = %s AND is_full_day = FALSE
            """
            slot_leave = self.db.query(sql_all_slots, (target_date,))
            leave_staffs.update([item["staff_name"] for item in slot_leave])
        elif time_slot:
            # 解析时段
            start_str, end_str = time_slot.split("～")
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()
            sql_slot = """
            SELECT staff_name 
            FROM leave_record 
            WHERE leave_date = %s 
            AND is_full_day = FALSE 
            AND start_time <= %s 
            AND end_time >= %s
            """
            slot_leave = self.db.query(sql_slot, (target_date, start, end))
            leave_staffs.update([item["staff_name"] for item in slot_leave])

        return leave_staffs


    def _get_prev_shift_staff(self, target_date: date, time_slot: str) -> str:
        """获取前一天指定时段的排班人员（用于避让机制）"""
        prev_date = target_date - timedelta(days=1)
        sql = """
        SELECT staff_name 
        FROM roster 
        WHERE date = %s AND time_slot = %s
        """
        result = self.db.query(sql, (prev_date, time_slot))
        if result:
            return result[0]["staff_name"]
        return ""

    def _filter_conflict_staffs(self, available_staffs: List[str],
                                target_date: date, time_slot: str) -> List[str]:
        """过滤存在冲突的人员（实现避让机制）"""
        prev_day_early_staffs = self._get_prev_day_early_staffs(target_date)

        # 对于第二天的8:00～9:00和8:00～12:00时段，避让前一天8:00～12:00排班人员
        if time_slot in ['8:00～9:00', '8:00～12:00']:
            filtered_staffs = [staff for staff in available_staffs if staff not in prev_day_early_staffs]
            # 如果过滤后没有可用人员，避免无人可用，返回原列表
            return filtered_staffs if filtered_staffs else available_staffs

        # 对于其他时段（如9:00～12:00、13:30～18:00），不避让
        return available_staffs

    def _get_prev_day_early_staffs(self, target_date: date) -> set:
        """获取前一天8:00～12:00时段排班人员集合"""
        prev_date = target_date - timedelta(days=1)
        sql = """
              SELECT DISTINCT staff_name
              FROM roster
              WHERE date = %s AND time_slot IN ('8:00～9:00', '9:00～12:00', '8:00～12:00') \
              """
        results = self.db.query(sql, (prev_date,))
        return set(item['staff_name'] for item in results)

    def _get_daily_roster(self, target_date: date) -> List[Dict]:
        """生成日常排班数据（8:00～9:00和18:00～21:00排同一个人）"""
        roster_list = []

        # 获取当天请假人员
        all_leave_staffs = self._get_leave_staffs(target_date)

        # 固定人员列表（5人）
        fixed_staffs = [CORE_STAFF] + TEST_STAFFS  # ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"]

        # 过滤请假人员
        available_fixed_staffs = [s for s in fixed_staffs if s not in all_leave_staffs]

        # 1. 8:00～9:00 和 18:00～21:00 轮换（同一个人）
        slot_8_9 = "8:00～9:00"
        slot_18_21 = "18:00～21:00"
        leave_8_9 = self._get_leave_staffs(target_date, slot_8_9)
        rotation_8_9 = self.rotation_config["日常8-9"]
        available_8_9 = [s for s in rotation_8_9["order"] if s not in leave_8_9]

        # 应用避让机制：过滤前一天8:00～9:00排班的人员
        available_8_9 = self._filter_conflict_staffs(available_8_9, target_date, '8:00～9:00')

        if available_8_9:
            # 修复轮换索引逻辑：确保按完整轮换顺序进行
            original_order = rotation_8_9["order"]
            current_index = rotation_8_9["index"] % len(original_order)

            # 找到当前索引位置对应的人员（跳过请假和避让人员）
            selected_staff = None
            for i in range(len(original_order)):
                candidate = original_order[(current_index + i) % len(original_order)]
                if candidate in available_8_9:
                    selected_staff = candidate
                    break

            if not selected_staff:
                # 如果没有可用人员，使用第一个可用人员
                selected_staff = available_8_9[0]

            # 为两个时段安排同一个人
            roster_list.append({
                "date": target_date,
                "time_slot": slot_8_9,
                "staff_name": selected_staff,
                "is_main": False
            })
            roster_list.append({
                "date": target_date,
                "time_slot": slot_18_21,
                "staff_name": selected_staff,
                "is_main": False
            })
            
            # 更新轮换索引
            self._update_rotation_index("日常8-9")

        # 2. 9:00～12:00（保持原有主辅逻辑，但应用避让机制）
        slot_9_12 = "9:00～12:00"
        leave_9_12 = self._get_leave_staffs(target_date, slot_9_12)
        
        # 获取可用的主班人员（核心人员优先）
        main_candidates = [CORE_STAFF] + [s for s in TEST_STAFFS if s not in leave_9_12]
        # 应用避让机制：过滤前一天9:00～12:00排班的人员
        main_candidates = self._filter_conflict_staffs(main_candidates, target_date, slot_9_12)
        
        main_staff = None
        if main_candidates:
            # 优先选择核心人员，如果没有则选择第一个可用的测试人员
            main_staff = next((s for s in main_candidates if s == CORE_STAFF), 
                            next((s for s in main_candidates if s in TEST_STAFFS), None))
        if main_staff:
            roster_list.append({
                "date": target_date,
                "time_slot": slot_9_12,
                "staff_name": main_staff,
                "is_main": True
            })
            aux_candidates = [s for s in TEST_STAFFS if s not in leave_9_12 and s != main_staff]
            for aux in aux_candidates[:3]:
                roster_list.append({
                    "date": target_date,
                    "time_slot": slot_9_12,
                    "staff_name": aux,
                    "is_main": False
                })

        # 3. 13:30～18:00（固定5人，但需要应用避让机制）
        slot_13_18 = "13:30～18:00"
        # 对于下午班，需要考虑两种避让情况：
        # 1. 避让前一天8:00～9:00的人员
        # 2. 避让前一天9:00～12:00的人员
        afternoon_available = available_fixed_staffs.copy()
        
        # 获取前一天两个时段的排班人员
        prev_early_staff = self._get_prev_shift_staff(target_date, "8:00～9:00")
        prev_morning_staff = self._get_prev_shift_staff(target_date, "9:00～12:00")
        
        # 过滤掉前一天这两个时段的人员
        afternoon_available = [staff for staff in afternoon_available 
                             if staff != prev_early_staff and staff != prev_morning_staff]
        
        # 如果过滤后没有可用人员，恢复原始列表（避免无人可用）
        if not afternoon_available:
            afternoon_available = available_fixed_staffs
        
        for staff in afternoon_available:
            roster_list.append({
                "date": target_date,
                "time_slot": slot_13_18,
                "staff_name": staff,
                "is_main": False
            })

        return roster_list



    def _get_holiday_roster(self, target_date: date) -> List[Dict]:
        """生成节假日排班数据（一天一人轮流）"""
        roster_list = []
        rotation_holiday = self.rotation_config["节假日"]

        # 获取当天请假人员
        all_leave_staffs = self._get_leave_staffs(target_date)

        # 可用人员：轮换队列中未请假的人员
        available_staffs = [s for s in rotation_holiday["order"] if s not in all_leave_staffs]
        
        # 应用避让机制：过滤前一天9:00～12:00排班的人员
        # 注意：节假日使用9:00～12:00时段作为避让参考
        available_staffs = self._filter_conflict_staffs(available_staffs, target_date, '8:00～12:00')

        # 如果没有可用人员，默认郑晨昊
        if not available_staffs:
            selected_staff = CORE_STAFF
        else:
            staff_index = rotation_holiday["index"] % len(available_staffs)
            selected_staff = available_staffs[staff_index]

        # 为所有节假日时段安排同一个人
        holiday_slots = ["8:00～12:00", "13:30～17:30", "17:30～21:30"]
        for slot in holiday_slots:
            roster_list.append({
                "date": target_date,
                "time_slot": slot,
                "staff_name": selected_staff,
                "is_main": False
            })

        # 更新轮换索引
        self._update_rotation_index("节假日")

        return roster_list


    def generate_roster(self, start_date: date, end_date: date):
        """生成指定日期范围的排班数据并入库"""
        # 初始化轮换配置（如果为空）
        if not self.rotation_config:
            default_rotation = {
                "日常8-9": ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"],
                "日常18-21": ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"],
                "节假日": ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"]
            }
            for config_type, order in default_rotation.items():
                sql_check = "SELECT COUNT(*) as count FROM rotation_config WHERE time_slot_type = %s"
                result = self.db.query(sql_check, (config_type,))
                if result[0]['count'] == 0:
                    sql_insert = "INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) VALUES (%s, %s, %s)"
                    self.db.execute(sql_insert, (config_type, ",".join(order), 0))

        current_date = start_date
        while current_date <= end_date:
            # 1. 判断日期类型（通过查询 holiday_config 表)
            date_type = self._get_date_type(current_date)

            # 2. 生成排班数据
            if date_type == "日常":
                roster_data = self._get_daily_roster(current_date)
            else:
                roster_data = self._get_holiday_roster(current_date)

            # 3. 写入数据库
            for item in roster_data:
                sql = """
                INSERT INTO roster (date, time_slot, staff_name, is_main, rotation_index)
                VALUES (%s, %s, %s, %s, %s)
                """
                # 获取对应轮换索引
                rot_index = 0
                if date_type == "日常":
                    if item["time_slot"] == "8:00～9:00":
                        rot_index = self.rotation_config["日常8-9"]["index"]
                    elif item["time_slot"] == "18:00～21:00":
                        rot_index = self.rotation_config["日常18-21"]["index"]
                else:
                    rot_index = self.rotation_config["节假日"]["index"]

                self.db.execute(sql, (
                    item["date"], item["time_slot"], item["staff_name"],
                    item["is_main"], rot_index
                ))

            # 4. 日期+1
            current_date += timedelta(days=1)

        debug(f"排班生成完成：{start_date} 至 {end_date}")

    # ===================== 主程序 =====================


if __name__ == "__main__":
    # 1. 初始化数据库连接
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        exit(1)

    # 2. 初始化排班生成器
    generator = RosterGenerator(db)

    # 3. 生成指定日期范围的排班（示例：2026-02-10 至 2026-02-13）
    start = date(2026, 2, 28)
    end = date(2026, 3, 1)
    generator.generate_roster(start, end)

    # 4. 关闭连接
    db.close()
