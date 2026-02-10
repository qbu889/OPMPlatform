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
            ("日常18-21", ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"]),
            ("节假日", ["郑晨昊", "林子旺", "曾婷婷", "陈伟强", "吴绍烨"])
        ]
        
        for config_type, default_order in required_configs:
            if config_type not in config:
                # 初始化轮换配置（确保所有5人参与轮换）
                sql_insert = "INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) VALUES (%s, %s, %s)"
                self.db.execute(sql_insert, (config_type, ",".join(default_order), 0))
                config[config_type] = {
                    "order": default_order,
                    "index": 0
                }
        
        return config

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
        sql = """
        SELECT is_working_day 
        FROM holiday_config 
        WHERE holiday_date = %s
        """
        result = self.db.query(sql, (target_date,))
        if result and not result[0]["is_working_day"]:
            return "节假日"
        return "日常"

    def _get_leave_staffs(self, target_date: date, time_slot: str = None) -> Set[str]:
        """获取指定日期/时段的请假人员
        :param target_date: 请假日期
        :param time_slot: 时段（格式如"8:00～9:00"），None则查全天请假
        :return: 请假人员集合
        """
        leave_staffs = set()
        # 1. 全天请假人员
        sql_all = """
        SELECT staff_name 
        FROM leave_record 
        WHERE leave_date = %s AND is_full_day = TRUE
        """
        all_leave = self.db.query(sql_all, (target_date,))
        leave_staffs.update([item["staff_name"] for item in all_leave])

        # 2. 时段请假人员（仅当指定时段时查询）
        if not time_slot:
            return leave_staffs
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

    def _get_prev_holiday_morning_staff(self, target_date: date) -> str:
        """获取前一日节假日8:00～12:00的排班人员（用于节假日早班过滤）"""
        prev_date = target_date - timedelta(days=1)
        sql = """
        SELECT staff_name 
        FROM roster 
        WHERE date = %s AND time_slot = '8:00～12:00'
        """
        result = self.db.query(sql, (prev_date,))
        if result:
            return result[0]["staff_name"]
        return ""

    def _get_daily_roster(self, target_date: date) -> List[Dict]:
        """生成日常排班数据"""
        roster_list = []
        # 1. 8:00～9:00 轮换（所有人员轮流，不分主辅）
        slot_8_9 = "8:00～9:00"
        leave_8_9 = self._get_leave_staffs(target_date, slot_8_9)
        # 筛选可用人员（所有人员，包括核心和测试人员）
        rotation_8_9 = self.rotation_config["日常8-9"]
        # 获取所有可用人员：核心人员 + 测试人员
        all_staffs = [CORE_STAFF] + TEST_STAFFS  # 修复：TEST_STAFFS 而不是 TEST_STAFF
        available = [s for s in all_staffs if s not in leave_8_9]
        if available:
            # 使用轮换索引获取人员
            staff_index = rotation_8_9["index"] % len(available)
            staff_8_9 = available[staff_index]
            roster_list.append({
                "date": target_date,
                "time_slot": slot_8_9,
                "staff_name": staff_8_9,
                "is_main": False  # 不区分主辅，统一为False
            })
            self._update_rotation_index("日常8-9")

        # 2. 9:00～12:00 和 13:30～18:00（主班+辅助）
        middle_slots = ["9:00～12:00", "13:30～18:00"]
        for slot in middle_slots:
            leave_middle = self._get_leave_staffs(target_date, slot)
            # 主班：优先郑晨昊，请假则取第一个未请假的测试人员
            main_staff = CORE_STAFF if CORE_STAFF not in leave_middle else None
            if not main_staff:
                main_staff = next((s for s in TEST_STAFFS if s not in leave_middle), None)
            if not main_staff:
                print(f"警告：{target_date} {slot} 无可用主班人员！")
                continue
            # 辅助人员：3名测试人员（排除请假+主班）
            aux_candidates = [s for s in TEST_STAFFS if s not in leave_middle and s != main_staff]
            # 不足3人则取所有可用
            aux_staffs = aux_candidates[:3]
            # 主班记录
            roster_list.append({
                "date": target_date,
                "time_slot": slot,
                "staff_name": main_staff,
                "is_main": True
            })
            # 辅助人员记录
            for aux in aux_staffs:
                roster_list.append({
                    "date": target_date,
                    "time_slot": slot,
                    "staff_name": aux,
                    "is_main": False
                })

        # 3. 18:00～21:00 轮换（所有人员轮流，不分主辅）
        slot_18_21 = "18:00～21:00"
        leave_18_21 = self._get_leave_staffs(target_date, slot_18_21)
        rotation_18_21 = self.rotation_config["日常18-21"]
        # 获取所有可用人员：核心人员 + 测试人员  
        all_staffs_18_21 = [CORE_STAFF] + TEST_STAFFS  # 修复：TEST_STAFFS 而不是 TEST_STAFF
        available = [s for s in all_staffs_18_21 if s not in leave_18_21]
        if available:
            # 使用轮换索引获取人员
            staff_index = rotation_18_21["index"] % len(available)
            staff_18_21 = available[staff_index]
            roster_list.append({
                "date": target_date,
                "time_slot": slot_18_21,
                "staff_name": staff_18_21,
                "is_main": False  # 不区分主辅
            })
            self._update_rotation_index("日常18-21")

        return roster_list

    def _get_holiday_roster(self, target_date: date) -> List[Dict]:
        """生成节假日排班数据"""
        roster_list = []
        rotation_holiday = self.rotation_config["节假日"]
        # 遍历节假日时段
        for slot in TIME_SLOTS["节假日"]:
            leave = self._get_leave_staffs(target_date, slot)
            available = [s for s in rotation_holiday["order"] if s not in leave]
            if not available:
                print(f"警告：{target_date} {slot} 无可用人员！")
                continue

            # 特殊处理：8:00～12:00 排除前一日该时段人员
            selected = None
            if slot == "8:00～12:00":
                prev_staff = self._get_prev_holiday_morning_staff(target_date)
                # 过滤前一日人员（首日prev_staff为空，无需过滤）
                if prev_staff:
                    available_filtered = [s for s in available if s != prev_staff]
                    selected = available_filtered[0] if available_filtered else available[0]
            # 其他时段直接选轮换首位
            if not selected:
                selected = available[0]

            roster_list.append({
                "date": target_date,
                "time_slot": slot,
                "staff_name": selected,
                "is_main": False
            })
            self._update_rotation_index("节假日")

        return roster_list

    def generate_roster(self, start_date: date, end_date: date):
        """生成指定日期范围的排班数据并入库
        :param start_date: 开始日期（date对象）
        :param end_date: 结束日期（date对象）
        """
        # 强制重置轮换索引为0（首次生成时）
        # 检查是否有轮换配置，如果没有则初始化
        if not self.rotation_config:
            # 初始化轮换配置
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
        
        # 确保轮换索引正确（重置为0用于测试）
        # 实际生产环境应保留原有索引，这里为了快速验证问题
        # self._reset_rotation_indices()  # 可选：重置所有索引为0

        current_date = start_date
        while current_date <= end_date:
            # 1. 判断日期类型
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
                # 轮换索引取当前配置的index
                rot_index = 0
                if date_type == "日常":
                    if item["time_slot"] == "8:00～9:00":
                        rot_index = self.rotation_config["日常8-9"]["index"]
                    elif item["time_slot"] == "18:00～21:00":
                        rot_index = self.rotation_config["日常18-21"]["index"]
                else:
                    rot_index = self.rotation_config["节假日"]["index"]
                # 执行插入
                self.db.execute(sql, (
                    item["date"], item["time_slot"], item["staff_name"],
                    item["is_main"], rot_index
                ))
            # 4. 日期+1
            current_date += timedelta(days=1)
        print(f"排班生成完成：{start_date} 至 {end_date}")

# ===================== 主程序 =====================
if __name__ == "__main__":
    # 1. 初始化数据库连接
    db = RosterDB(DB_CONFIG)
    if not db.connect():
        exit(1)

    # 2. 初始化排班生成器
    generator = RosterGenerator(db)

    # 3. 生成指定日期范围的排班（示例：2026-02-10 至 2026-02-13）
    start = date(2026, 2, 14)
    end = date(2026, 2, 28)
    generator.generate_roster(start, end)

    # 4. 关闭连接
    db.close()