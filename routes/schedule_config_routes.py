#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班配置管理路由
"""
from flask import Blueprint, render_template, request, jsonify
from routes.排班.paiBanNew import DB_CONFIG, RosterDB
from datetime import datetime, date, timedelta
schedule_config_bp = Blueprint('schedule_config_bp', __name__, url_prefix='/schedule-config')



def serialize_datetime_objects(obj):
    """
    将包含datetime、date、timedelta对象的数据结构转换为可JSON序列化的格式
    """
    if isinstance(obj, dict):
        return {key: serialize_datetime_objects(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_objects(item) for item in obj]
    elif isinstance(obj, timedelta):
        total_seconds = int(obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    elif isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    else:
        return obj

@schedule_config_bp.route('/')
def schedule_config_page():
    """排班配置页面"""
    return render_template('schedule_config.html')

@schedule_config_bp.route('/api/staff-config', methods=['GET', 'POST'])
def staff_config():
    """人员配置API"""
    if request.method == 'GET':
        # 获取当前人员配置
        try:
            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})

            # 获取核心人员
            core_sql = "SELECT staff_name FROM staff_config WHERE staff_type = 'CORE'"
            core_result = db.query(core_sql)
            core_staff = core_result[0]['staff_name'] if core_result else ""

            # 获取测试人员
            test_sql = "SELECT staff_name FROM staff_config WHERE staff_type = 'TEST'"
            test_results = db.query(test_sql)
            test_staffs = [item['staff_name'] for item in test_results]

            db.close()

            return jsonify({
                "success": True,
                "data": {
                    "core_staff": core_staff,
                    "test_staffs": test_staffs
                }
            })
        except Exception as e:
            return jsonify({"success": False, "msg": "获取人员配置失败: " + str(e)})

    elif request.method == 'POST':
        # 更新人员配置
        try:
            data = request.get_json()
            core_staff = data.get('core_staff', '')
            test_staffs = data.get('test_staffs', [])

            if not core_staff:
                return jsonify({"success": False, "msg": "核心人员不能为空"})

            if not test_staffs or len(test_staffs) < 1:
                return jsonify({"success": False, "msg": "至少需要一名测试人员"})

            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})

            # 清空现有配置
            clear_sql = "DELETE FROM staff_config"
            db.execute(clear_sql)

            # 插入新的核心人员
            insert_core_sql = "INSERT INTO staff_config (staff_name, staff_type) VALUES (%s, 'CORE')"
            db.execute(insert_core_sql, (core_staff,))

            # 插入测试人员
            for staff in test_staffs:
                insert_test_sql = "INSERT INTO staff_config (staff_name, staff_type) VALUES (%s, 'TEST')"
                db.execute(insert_test_sql, (staff,))

            db.close()

            return jsonify({"success": True, "msg": "人员配置更新成功"})
        except Exception as e:
            return jsonify({"success": False, "msg": "更新人员配置失败: " + str(e)})


@schedule_config_bp.route('/api/leave-records', methods=['GET', 'POST', 'DELETE'])
def leave_records():
    """请假记录API"""
    if request.method == 'GET':
        # 获取请假记录
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            if not start_date or not end_date:
                return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})

            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})

            sql = """
            SELECT lr.*, sc.staff_type
            FROM leave_record lr
            LEFT JOIN staff_config sc ON lr.staff_name = sc.staff_name
            WHERE lr.leave_date BETWEEN %s AND %s
            ORDER BY lr.leave_date, lr.start_time
            """

            results = db.query(sql, (start_date, end_date))
            db.close()
            # 使用辅助函数处理时间字段，将timedelta等不可序列化对象转换为字符串
            processed_results = serialize_datetime_objects(results)
            return jsonify({
                "success": True,
                "data": processed_results
            })
        except Exception as e:
            return jsonify({"success": False, "msg": "获取请假记录失败: " + str(e)})

    elif request.method == 'POST':
        # 添加请假记录
        try:
            data = request.get_json()
            staff_name = data.get('staff_name')
            leave_date = data.get('leave_date')
            is_full_day = data.get('is_full_day', False)
            start_time = data.get('start_time')
            end_time = data.get('end_time')

            if not staff_name or not leave_date:
                return jsonify({"success": False, "msg": "人员姓名和请假日期不能为空"})

            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})

            # 如果是全天请假，设置时间段为00:00-23:59
            if is_full_day:
                start_time = "00:00"
                end_time = "23:59"
            elif not start_time or not end_time:
                return jsonify({"success": False, "msg": "时段请假需提供开始时间和结束时间"})

            # 检查是否有冲突的请假记录
            check_sql = """
            SELECT id FROM leave_record 
            WHERE staff_name = %s AND leave_date = %s
            AND (
                (is_full_day = TRUE) OR 
                (is_full_day = FALSE AND 
                 ((%s <= start_time AND %s >= start_time) OR 
                  (%s <= end_time AND %s >= end_time) OR 
                  (%s >= start_time AND %s <= end_time)))
            )
            """

            conflict_check = db.query(check_sql, (
                staff_name, leave_date,
                start_time, start_time,
                end_time, end_time,
                start_time, start_time
            ))

            if conflict_check:
                db.close()
                return jsonify({"success": False, "msg": "存在冲突的请假记录"})

            sql = """
            INSERT INTO leave_record (staff_name, leave_date, is_full_day, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            """

            success = db.execute(sql, (staff_name, leave_date, is_full_day, start_time, end_time))
            db.close()

            if success:
                return jsonify({"success": True, "msg": "请假记录添加成功"})
            else:
                return jsonify({"success": False, "msg": "请假记录添加失败"})
        except Exception as e:
            return jsonify({"success": False, "msg": "添加请假记录失败: " + str(e)})

    elif request.method == 'DELETE':
        # 删除请假记录
        try:
            data = request.get_json()
            record_id = data.get('id')

            if not record_id:
                return jsonify({"success": False, "msg": "记录ID不能为空"})

            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})

            sql = "DELETE FROM leave_record WHERE id = %s"
            success = db.execute(sql, (record_id,))
            db.close()

            if success:
                return jsonify({"success": True, "msg": "请假记录删除成功"})
            else:
                return jsonify({"success": False, "msg": "请假记录删除失败"})
        except Exception as e:
            return jsonify({"success": False, "msg": "删除请假记录失败: " + str(e)})

@schedule_config_bp.route('/api/generate-schedule', methods=['POST'])
def generate_schedule():
    """生成排班表API"""
    from routes.排班.paiBanNew import RosterGenerator

    try:
        data = request.get_json()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')

        if not start_date_str or not end_date_str:
            return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

        if start_date > end_date:
            return jsonify({"success": False, "msg": "开始日期不能晚于结束日期"})

        # 初始化数据库连接和排班生成器
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})

        generator = RosterGenerator(db)
        generator.generate_roster(start_date, end_date)

        db.close()

        return jsonify({"success": True, "msg": f"排班表生成成功：{start_date_str} 至 {end_date_str}"})
    except Exception as e:
        return jsonify({"success": False, "msg": "生成排班表失败: " + str(e)})

@schedule_config_bp.route('/api/schedule-records', methods=['GET'])
def schedule_records():
    """排班记录查询API"""
    if request.method == 'GET':
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            if not start_date or not end_date:
                return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})

            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})

            sql = """
            SELECT r.*, sc.staff_type
            FROM roster r
            LEFT JOIN staff_config sc ON r.staff_name = sc.staff_name
            WHERE r.date BETWEEN %s AND %s
            ORDER BY r.date, r.time_slot, r.is_main DESC
            """

            results = db.query(sql, (start_date, end_date))
            db.close()

            # 使用辅助函数处理时间字段，将timedelta等不可序列化对象转换为字符串
            processed_results = serialize_datetime_objects(results)

            return jsonify({
                "success": True,
                "data": processed_results
            })
        except Exception as e:
            return jsonify({"success": False, "msg": "获取排班记录失败: " + str(e)})

@schedule_config_bp.route('/api/check-existing-roster', methods=['GET'])
def check_existing_roster():
    """检查指定日期范围内是否存在排班记录"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})

        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})

        # 查询指定日期范围内的排班记录
        sql = "SELECT COUNT(*) as count FROM roster WHERE date BETWEEN %s AND %s"
        result = db.query(sql, (start_date, end_date))
        
        count = result[0]['count'] if result else 0
        
        # 如果有记录，返回详细信息
        if count > 0:
            detail_sql = "SELECT DISTINCT date, time_slot FROM roster WHERE date BETWEEN %s AND %s ORDER BY date, time_slot"
            details = db.query(detail_sql, (start_date, end_date))
            
            db.close()
            
            return jsonify({
                "success": True,
                "data": details,
                "total": count
            })
        else:
            db.close()
            return jsonify({
                "success": True,
                "data": [],
                "total": 0
            })
    except Exception as e:
        return jsonify({"success": False, "msg": "检查现有排班失败: " + str(e)})


@schedule_config_bp.route('/api/delete-existing-roster', methods=['POST'])
def delete_existing_roster():
    """删除指定日期范围内的排班记录"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not start_date or not end_date:
            return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})

        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})

        # 删除指定日期范围内的排班记录
        sql = "DELETE FROM roster WHERE date BETWEEN %s AND %s"
        success = db.execute(sql, (start_date, end_date))
        
        db.close()
        
        if success:
            return jsonify({"success": True, "msg": "现有排班记录已清除"})
        else:
            return jsonify({"success": False, "msg": "清除排班记录失败"})
    except Exception as e:
        return jsonify({"success": False, "msg": "清除排班记录失败: " + str(e)})
