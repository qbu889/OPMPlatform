# routes/event_routes.py
from flask import Blueprint, request, render_template, jsonify
import re
import logging

event_bp = Blueprint('event', __name__)
logger = logging.getLogger(__name__)

@event_bp.route('/clean-event-page')
def clean_event_page():
    """事件数据清洗页面"""
    return render_template('clean_event.html')

@event_bp.route('/clean-event', methods=['POST'])
def clean_event():
    """处理事件数据清洗请求"""
    try:
        data = request.get_json()
        fp_value = data.get('fp_value')
        event_time = data.get('event_time')

        if not fp_value or not event_time:
            return jsonify({'error': '缺少必需参数'}), 400

        # 修改FP值验证：只要求非空且长度不超过1000
        if not fp_value.strip() or len(fp_value) > 1000:
            return jsonify({'error': 'FP值不能为空且长度不能超过1000个字符'}), 400

        # 时间格式验证，支持多种格式
        # 在 event_routes.py 中修改时间格式验证
        time_pattern1 = r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}$'           # YYYY/MM/DD HH:MM
        time_pattern2 = r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}$'            # YYYY-MM-DD HH:MM
        time_pattern3 = r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$'    # YYYY-MM-DD HH:MM:SS
        time_pattern4 = r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$'    # YYYY/MM/DD HH:MM:SS

        if not (re.match(time_pattern1, event_time) or
            re.match(time_pattern2, event_time) or
            re.match(time_pattern3, event_time) or
            re.match(time_pattern4, event_time)):
            return jsonify({'error': '时间格式不正确，支持格式: YYYY/MM/DD HH:MM 或 YYYY-MM-DD HH:MM'}), 400

        # 处理数据
        result = clean_event_data(fp_value, event_time)
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': f'处理数据时发生错误: {str(e)}'}), 500

# 修改 clean_event_data 函数以支持多种时间格式
def clean_event_data(fp_value, event_time):
    """清洗事件数据"""
    active_status = "3"  # 保持不变

    # 统一处理日期分隔符，将"/"替换为"-"
    cleaned_time = event_time.replace("/", "-")

    # 分割日期和时间部分
    if " " in cleaned_time:
        date_part, time_part = cleaned_time.split(" ", 1)
    else:
        # 如果只有日期部分，默认时间为00:00
        date_part = cleaned_time
        time_part = "00:00:00"

    # 处理日期部分
    if "-" in date_part:
        date_components = date_part.split("-")
        if len(date_components) >= 3:
            year, month, day = date_components[0], date_components[1], date_components[2]
        else:
            raise ValueError("日期格式不正确")
    else:
        raise ValueError("日期格式不正确")

    # 处理时间部分
    if ":" in time_part:
        time_components = time_part.split(":")
        if len(time_components) >= 2:
            hour, minute = time_components[0], time_components[1]
            # 如果有秒部分则保留，否则设为00
            second = time_components[2] if len(time_components) >= 3 else "00"
        else:
            hour, minute, second = time_components[0], "00", "00"
    else:
        hour, minute, second = "00", "00", "00"

    # 确保各部分为两位数
    formatted_hour = hour.zfill(2)
    formatted_minute = minute.zfill(2)
    formatted_second = second.zfill(2)

    # 确保年月日为正确格式
    cleaned_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    cleaned_event_time = f"{cleaned_date} {formatted_hour}:{formatted_minute}:{formatted_second}"

    # 构建目标格式数据
    result = {
        "ACTIVE_STATUS": active_status,
        "EVENT_TIME": cleaned_event_time,
        "FP0_FP1_FP2_FP3": fp_value,
        "CFP0_CFP1_CFP2_CFP3": fp_value
    }

    return result