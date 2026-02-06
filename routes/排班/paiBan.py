import datetime
from typing import List, Dict, Tuple

# ===================== 基础配置 =====================
# 核心人员定义
TEST_STAFF = ["林子旺", "曾婷婷", "陈伟强", "吴绍烨"]  # 测试人员（轮流排班）
CORE_STAFF = "郑晨昊"  # 中间时段核心人员

# 请假配置（人员: [开始日期, 结束日期]）
LEAVE_CONFIG = {
    "陈伟强": [datetime.date(2026, 2, 5), datetime.date(2026, 2, 6)],
    "曾婷婷": [datetime.date(2026, 2, 6), datetime.date(2026, 2, 6)]
}

# 时段配置
WORKDAY_TIME_SLOTS = {  # 周一到周五时段
    "早班1": "8:00～9:00",
    "中段1": "9:00～12:00",
    "中段2": "13:30～18:00",
    "晚班1": "18:00～21:00"
}
WEEKEND_TIME_SLOTS = {  # 周末/节假日时段
    "早班": "8:00～12:00",
    "中班": "13:30～17:30",
    "晚班": "17:30～21:30"
}


# ===================== 工具函数 =====================
def is_leave(staff: str, date: datetime.date) -> bool:
    """判断指定人员在指定日期是否请假"""
    if staff not in LEAVE_CONFIG:
        return False
    start, end = LEAVE_CONFIG[staff]
    return start <= date <= end


def get_available_staff(date: datetime.date, exclude: List[str] = None) -> List[str]:
    """获取指定日期可用的测试人员（排除请假+指定排除人员）"""
    available = []
    exclude = exclude or []
    for staff in TEST_STAFF:
        if not is_leave(staff, date) and staff not in exclude:
            available.append(staff)
    return available


def rotate_staff(staff_list: List[str], index: int) -> List[str]:
    """人员轮换（按索引循环）"""
    return staff_list[index % len(staff_list):] + staff_list[:index % len(staff_list)]


# ===================== 排班核心逻辑 =====================
def generate_schedule(start_date: datetime.date, days: int) -> Dict[str, Dict[str, str]]:
    """
    生成排班表
    :param start_date: 开始日期
    :param days: 生成天数
    :return: 排班表 {日期字符串: {时段: 排班人员}}
    """
    schedule = {}
    rotate_index = 0  # 轮换索引（控制四人轮流顺序）
    last_friday_morning_staff = None  # 记录周五早上排班人员（用于周六早上排除）

    for day_offset in range(days):
        current_date = start_date + datetime.timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")
        weekday = current_date.weekday()  # 0=周一, 6=周日
        is_weekend = weekday in [5, 6]  # 周六/周日

        # 初始化当日排班
        schedule[date_str] = {}
        available_staff = get_available_staff(current_date)

        # ---------------- 周末排班逻辑 ----------------
        if is_weekend:
            # 周六早上特殊规则：排除周五早上排班的人
            exclude_staff = []
            if weekday == 5:  # 周六
                if last_friday_morning_staff:
                    exclude_staff = [last_friday_morning_staff]

            # 筛选可用人员（排除请假+周六特殊排除）
            weekend_available = get_available_staff(current_date, exclude_staff)
            rotated = rotate_staff(weekend_available, rotate_index)

            # 分配周末时段
            time_slots = list(WEEKEND_TIME_SLOTS.values())
            for i, slot in enumerate(time_slots):
                schedule[date_str][slot] = rotated[i % len(rotated)]

            rotate_index += 1

        # ---------------- 工作日排班逻辑 ----------------
        else:
            # 1. 早班1（8:00～9:00）：四人轮流，记录周五早上人员
            morning1_staff = rotate_staff(available_staff, rotate_index)[0]
            schedule[date_str][WORKDAY_TIME_SLOTS["早班1"]] = morning1_staff
            if weekday == 4:  # 周五
                last_friday_morning_staff = morning1_staff

            # 2. 中段（9:00～12:00/13:30～18:00）：郑晨昊为主，其他3人为辅
            middle_staff = f"{CORE_STAFF}（主） + {', '.join(available_staff[:3])}（辅）"
            schedule[date_str][WORKDAY_TIME_SLOTS["中段1"]] = middle_staff
            schedule[date_str][WORKDAY_TIME_SLOTS["中段2"]] = middle_staff

            # 3. 晚班1（18:00～21:00）：四人轮流
            evening1_staff = rotate_staff(available_staff, rotate_index + 1)[0]
            schedule[date_str][WORKDAY_TIME_SLOTS["晚班1"]] = evening1_staff

            rotate_index += 2  # 早班+晚班各用一个轮换索引

    return schedule


# ===================== 生成并打印排班表 =====================
if __name__ == "__main__":
    # 生成2026年2月5日开始的7天排班表（覆盖请假日期+周末）
    start_date = datetime.date(2026, 2, 15)
    schedule_result = generate_schedule(start_date, days=7)

    # 打印排班表
    print("=" * 80)
    # print("                测试人员排班表（2026年2月5日-2月11日）")
    # 动态生成排班表标题
    start_date_str = min(schedule_result.keys())
    end_date_str = max(schedule_result.keys())
    print(f"                测试人员排班表（{start_date_str} 至 {end_date_str}）")

    print("=" * 80)
    for date, slots in schedule_result.items():
        # 补充星期信息
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        weekday_map = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        weekday_str = weekday_map[date_obj.weekday()]

        print(f"\n【{date} {weekday_str}】")
        for slot, staff in slots.items():
            print(f"  {slot:<12} 排班人员：{staff}")

    # 打印请假提示
    print("\n" + "=" * 80)
    print("请假提示：")
    for staff, [start, end] in LEAVE_CONFIG.items():
        print(f"  {staff}：{start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')} 请假，不参与排班")
    print("=" * 80)