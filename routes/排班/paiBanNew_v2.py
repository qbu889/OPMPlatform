#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 3.8.10 排班程序 (改进版)
实现规则:
1. 日常/节假日时段划分与人员轮换
2. 请假人员过滤 (全天/时段)
3. 节假日早班避开前一日同时段人员
4. 排班数据写入 MySQL 数据库
5. 核心人员从数据库动态获取
6. 每次排班后更新可排人员队列
7. 考虑前一天已排班人员的延后处理
"""
from logging import debug

import pymysql
from datetime import datetime, date, timedelta
from typing import List, Dict, Set, Tuple
from dotenv import load_dotenv
import os

# 加载环境变量 (建议将数据库配置放在.env 文件，避免硬编码)
load_dotenv()

# ===================== 核心配置 =====================
# 数据库配置 (从.env 读取，或直接填写)
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
            print(f"数据库连接失败：{e}")
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
            print(f"查询失败：{sql} | {params} | {e}")
            return []

    def execute(self, sql: str, params: tuple = ()) -> bool:
        """执行增删改"""
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"执行失败：{sql} | {params} | {e}")
            return False


# ===================== 排班核心逻辑 =====================
class RosterGenerator:
    def __init__(self, db: RosterDB):
        self.db = db
        # 初始化人员配置
        self.core_staff = self._get_core_staff()
        self.test_staffs = self._get_test_staffs()
        self.all_staffs = self.test_staffs + [self.core_staff]
        
        # 初始化轮换队列 (从数据库读取)
        self.rotation_config = self._load_rotation_config()

    def _get_core_staff(self) -> str:
        """从数据库获取核心人员"""
        sql = "SELECT staff_name FROM staff_config WHERE staff_type = 'CORE'"
        result = self.db.query(sql)
        return result[0]['staff_name'] if result else "郑晨昊"

    def _get_test_staffs(self) -> List[str]:
        """从数据库获取测试人员列表"""
        sql = "SELECT staff_name FROM staff_config WHERE staff_type = 'TEST' ORDER BY id"
        results = self.db.query(sql)
        return [item['staff_name'] for item in results] if results else ["林子旺", "曾婷婷", "陈伟强", "吴绍烨"]

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

        # 确保必要的轮换配置存在 (包含所有人员)
        all_staffs = self.test_staffs + [self.core_staff]
        required_configs = [
            ("日常 8-9", all_staffs),
            ("节假日", all_staffs)
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
        """通过查询 holiday_config 表判断是否为节假日"""
        date_str = date_obj.strftime('%Y-%m-%d')

        # 查询 holiday_config 表
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

    def _update_rotation_index(self, slot_type: str, increment: int = 1):
        """更新轮换索引 (索引+increment，超出人数重置为 0)"""
        if slot_type not in self.rotation_config:
            return
        current = self.rotation_config[slot_type]
        new_index = (current["index"] + increment) % len(current["order"])
        # 更新内存
        self.rotation_config[slot_type]["index"] = new_index
        # 更新数据库
        sql = "UPDATE rotation_config SET current_index = %s WHERE time_slot_type = %s"
        self.db.execute(sql, (new_index, slot_type))

    def _get_date_type(self, target_date: date) -> str:
        """判断日期类型：日常/节假日"""
        # 先查询 holiday_config 表 (使用标准日期格式)
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

        # 2. 时段请假人员 (当 time_slot 为 None 时，查询所有时段请假)
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
            # 解析时段 (注意：使用全角冒号～)
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

    def _get_prev_day_staff(self, target_date: date, time_slot_pattern: str) -> Set[str]:
        """获取前一天某时段或类似时段的排班人员"""
        prev_date = target_date - timedelta(days=1)
        
        # 查询前一天的排班记录
        sql = """
        SELECT staff_name, time_slot 
        FROM roster 
        WHERE date = %s
        """
        results = self.db.query(sql, (prev_date,))
        
        matched_staff = set()
        for row in results:
            slot = row['time_slot']
            # 匹配时段模式
            if time_slot_pattern == "morning" and ("8:00" in slot or "9:00" in slot):
                matched_staff.add(row['staff_name'])
            elif time_slot_pattern == "evening" and "18:00" in slot:
                matched_staff.add(row['staff_name'])
                
        return matched_staff

    def _select_staff_from_queue(self, slot_type: str, available_staffs: List[str], 
                                  exclude_staffs: Set[str] = None) -> Tuple[str, int]:
        """
        从轮换队列中选择人员
        返回：(选中的人员，新的索引)
        """
        if exclude_staffs is None:
            exclude_staffs = set()
            
        rotation = self.rotation_config[slot_type]
        order = rotation["order"]
        current_index = rotation["index"]
        
        # 从当前索引开始，找到第一个未被排除且可用的人员
        n = len(order)
        for i in range(n):
            idx = (current_index + i) % n
            staff = order[idx]
            if staff in available_staffs and staff not in exclude_staffs:
                # 计算新的索引 (选中人员的下一个位置)
                new_index = (idx + 1) % n
                return staff, new_index
        
        # 如果没有找到合适的人员，返回当前索引指向的人员 (如果可用)
        if current_index < len(order) and order[current_index] in available_staffs:
            return order[current_index], (current_index + 1) % n
            
        # 如果都不可用，返回第一个可用人员
        if available_staffs:
            return available_staffs[0], (1 if len(available_staffs) > 1 else 0)
            
        # 无人可用
        return None, current_index

    def _update_rotation_to_index(self, slot_type: str, new_index: int):
        """更新轮换索引到指定位置"""
        if slot_type not in self.rotation_config:
            return
        # 更新内存
        self.rotation_config[slot_type]["index"] = new_index
        # 更新数据库
        sql = "UPDATE rotation_config SET current_index = %s WHERE time_slot_type = %s"
        self.db.execute(sql, (new_index, slot_type))

    def _get_daily_roster(self, target_date: date) -> List[Dict]:
        """生成日常排班数据 (8:00～9:00 和 18:00～21:00 排同一个人)"""
        roster_list = []

        # 获取当天请假人员
        all_leave_staffs = self._get_leave_staffs(target_date)

        # 过滤请假人员后的可用人员
        available_staffs = [s for s in self.all_staffs if s not in all_leave_staffs]
        
        # 记录是否有请假调整
        has_leave_adjustment = len(all_leave_staffs) > 0

        # 1. 8:00～9:00 和 18:00～21:00 轮换 (同一个人)
        slot_8_9 = "8:00～9:00"
        slot_18_21 = "18:00～21:00"
        leave_8_9 = self._get_leave_staffs(target_date, slot_8_9)
        available_8_9 = [s for s in available_staffs if s not in leave_8_9]

        # 获取前一天晚班人员，今天早班要延后
        prev_evening_staff = self._get_prev_day_staff(target_date, "evening")
        
        if available_8_9:
            result = self._select_staff_from_queue(
                "日常 8-9", available_8_9, prev_evening_staff
            )
            debug(f"{target_date} 早班选择结果：{result}")
            selected_staff, new_index = result
            
            if selected_staff:
                # 为两个时段安排同一个人
                remark = "因请假调整" if has_leave_adjustment else None
                roster_list.append({
                    "date": target_date,
                    "time_slot": slot_8_9,
                    "staff_name": selected_staff,
                    "is_main": False,
                    "remark": remark
                })
                roster_list.append({
                    "date": target_date,
                    "time_slot": slot_18_21,
                    "staff_name": selected_staff,
                    "is_main": False,
                    "remark": remark
                })
                
                # 更新轮换索引 (关键：每次排班后必须更新)
                self._update_rotation_to_index("日常 8-9", new_index)
                debug(f"{target_date} 早班更新索引：{new_index}")

        # 2. 9:00～12:00 (主辅班逻辑)
        slot_9_12 = "9:00～12:00"
        leave_9_12 = self._get_leave_staffs(target_date, slot_9_12)
        
        # 主班：优先核心人员
        main_staff = None
        if self.core_staff not in leave_9_12 and self.core_staff in available_staffs:
            main_staff = self.core_staff
        else:
            # 核心人员请假，从测试人员中选
            for staff in self.test_staffs:
                if staff not in leave_9_12 and staff in available_staffs:
                    main_staff = staff
                    break
                    
        if main_staff:
            remark = "因请假调整" if has_leave_adjustment else None
            roster_list.append({
                "date": target_date,
                "time_slot": slot_9_12,
                "staff_name": main_staff,
                "is_main": True,
                "remark": remark
            })
            
            # 辅班：从测试人员中选 3 人 (排除主班)
            aux_candidates = [s for s in self.test_staffs 
                            if s not in leave_9_12 and s in available_staffs and s != main_staff]
            for aux in aux_candidates[:3]:
                roster_list.append({
                    "date": target_date,
                    "time_slot": slot_9_12,
                    "staff_name": aux,
                    "is_main": False,
                    "remark": remark
                })

        # 3. 13:30～18:00 (所有可用人员)
        slot_13_18 = "13:30～18:00"
        leave_13_18 = self._get_leave_staffs(target_date, slot_13_18)
        available_afternoon = [s for s in available_staffs if s not in leave_13_18]
        
        for staff in available_afternoon:
            remark = "因请假调整" if has_leave_adjustment else None
            roster_list.append({
                "date": target_date,
                "time_slot": slot_13_18,
                "staff_name": staff,
                "is_main": False,
                "remark": remark
            })

        return roster_list

    def _get_holiday_roster(self, target_date: date) -> List[Dict]:
        """生成节假日排班数据 (一天一人轮流)"""
        roster_list = []
        rotation_holiday = self.rotation_config["节假日"]

        # 获取当天请假人员
        all_leave_staffs = self._get_leave_staffs(target_date)

        # 可用人员：轮换队列中未请假的人员
        available_staffs = [s for s in rotation_holiday["order"] if s not in all_leave_staffs]
        
        # 记录是否有请假调整
        has_leave_adjustment = len(all_leave_staffs) > 0

        # 获取前一天早班人员 (8:00~12:00),今天应该延后
        prev_morning_staff = self._get_prev_day_staff(target_date, "morning")

        # 选择人员
        if not available_staffs:
            # 无人可用，默认核心人员
            selected_staff = self.core_staff
            new_index = 0
            debug(f"{target_date} 节假日无人可用，默认排核心人员 {self.core_staff}")
        else:
            result = self._select_staff_from_queue(
                "节假日", available_staffs, prev_morning_staff
            )
            debug(f"{target_date} 排班选择结果：{result}")
            selected_staff, new_index = result
            
            if selected_staff:
                # 更新轮换索引 (关键：每次排班后必须更新)
                self._update_rotation_to_index("节假日", new_index)
                debug(f"{target_date} 节假日排班：{selected_staff}, 新索引：{new_index}")
            else:
                selected_staff = self.core_staff
                new_index = 0
                debug(f"{target_date} 节假日选择失败，默认排核心人员 {self.core_staff}")

        # 为所有节假日时段安排同一个人
        holiday_slots = ["8:00～12:00", "13:30～17:30", "17:30～21:30"]
        remark = "因请假调整" if has_leave_adjustment else None
        for slot in holiday_slots:
            roster_list.append({
                "date": target_date,
                "time_slot": slot,
                "staff_name": selected_staff,
                "is_main": False,
                "remark": remark
            })

        return roster_list

    def generate_roster(self, start_date: date, end_date: date):
        """生成指定日期范围的排班数据并入库"""
        # 初始化轮换配置 (如果为空)
        if not self.rotation_config:
            all_staffs = self.test_staffs + [self.core_staff]
            default_rotation = {
                "日常 8-9": all_staffs,
                "节假日": all_staffs
            }
            for config_type, order in default_rotation.items():
                sql_check = "SELECT COUNT(*) as count FROM rotation_config WHERE time_slot_type = %s"
                result = self.db.query(sql_check, (config_type,))
                if result[0]['count'] == 0:
                    sql_insert = "INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) VALUES (%s, %s, %s)"
                    self.db.execute(sql_insert, (config_type, ",".join(order), 0))

        current_date = start_date
        while current_date <= end_date:
            # 1. 判断日期类型 (通过查询 holiday_config 表)
            date_type = self._get_date_type(current_date)

            # 2. 生成排班数据
            if date_type == "日常":
                roster_data = self._get_daily_roster(current_date)
            else:
                roster_data = self._get_holiday_roster(current_date)

            # 3. 写入数据库
            for item in roster_data:
                sql = """
                INSERT INTO roster (date, time_slot, staff_name, is_main, rotation_index, remark)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                # 获取对应轮换索引
                rot_index = 0
                if date_type == "日常":
                    if item["time_slot"] == "8:00～9:00":
                        rot_index = self.rotation_config["日常 8-9"]["index"]
                    elif item["time_slot"] == "18:00～21:00":
                        rot_index = self.rotation_config["日常 8-9"]["index"]
                else:
                    rot_index = self.rotation_config["节假日"]["index"]

                self.db.execute(sql, (
                    item["date"], item["time_slot"], item["staff_name"],
                    item["is_main"], rot_index, item.get("remark")
                ))

            # 4. 日期 +1
            current_date += timedelta(days=1)

        debug(f"排班生成完成:{start_date} 至 {end_date}")

    # ===================== 主程序 =====================


if __name__ == "__main__":
    # 1. 初始化数据库连接
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        exit(1)

    # 2. 清除指定日期范围的旧数据
    start = date(2026, 2, 1)
    end = date(2026, 3, 1)
    print(f"正在清除 {start} 至 {end} 的旧排班数据...")

    sql = "DELETE FROM roster WHERE date BETWEEN %s AND %s"
    success = db.execute(sql, (start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))
    if success:
        print(f"成功清除旧数据")
    else:
        print("清除旧数据失败")

    # 3. 初始化排班生成器
    generator = RosterGenerator(db)

    # 4. 生成指定日期范围的排班
    print(f"正在生成 {start} 至 {end} 的新排班数据...")
    generator.generate_roster(start, end)

    # 5. 关闭连接
    db.close()
    print("排班完成!")
