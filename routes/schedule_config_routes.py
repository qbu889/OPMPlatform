#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班配置管理路由
"""
from flask import Blueprint, render_template, request, jsonify
from routes.排班.paiBanNew import DB_CONFIG, RosterDB, CORE_STAFF, TEST_STAFFS
from datetime import datetime, date, timedelta
from typing import List, Dict

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
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            is_full_day = data.get('is_full_day', False)
            start_time = data.get('start_time')
            end_time = data.get('end_time')

            if not staff_name or not start_date_str or not end_date_str:
                return jsonify({"success": False, "msg": "人员姓名、开始日期和结束日期不能为空"})

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

            # 检查整个日期范围内的冲突
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # 逐天检查冲突
            current_date = start_date
            while current_date <= end_date:
                conflict_check = db.query(check_sql, (
                    staff_name, current_date.strftime('%Y-%m-%d'),
                    start_time, start_time,
                    end_time, end_time,
                    start_time, start_time
                ))
                if conflict_check:
                    db.close()
                    return jsonify({"success": False, "msg": f"在 {current_date} 存在冲突的请假记录"})
                current_date += timedelta(days=1)

            if conflict_check:
                db.close()
                return jsonify({"success": False, "msg": "存在冲突的请假记录"})

            sql = """
            INSERT INTO leave_record (staff_name, leave_date, is_full_day, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            """

            # 批量插入多天请假记录
            success_count = 0
            current_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            while current_date <= end_date_obj:
                insert_success = db.execute(sql, (
                    staff_name, 
                    current_date.strftime('%Y-%m-%d'), 
                    is_full_day, 
                    start_time, 
                    end_time
                ))
                if insert_success:
                    success_count += 1
                current_date += timedelta(days=1)
            
            success = success_count > 0
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

            # sql = """
            # SELECT r.*, sc.staff_type
            # FROM roster r
            # LEFT JOIN staff_config sc ON r.staff_name = sc.staff_name
            # WHERE r.date BETWEEN %s AND %s
            # ORDER BY r.date, r.time_slot, r.is_main DESC
            # """
            sql = """
            SELECT r.*, sc.staff_type
            FROM roster r
            LEFT JOIN staff_config sc ON r.staff_name = sc.staff_name
            WHERE r.date BETWEEN %s AND %s
            ORDER BY r.date,
                     CASE r.time_slot
                         WHEN '8:00～12:00' THEN 1
                         WHEN '13:30～17:30' THEN 2
                         WHEN '17:30～21:30' THEN 3
                         ELSE 4
                     END,
                     r.is_main DESC
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

@schedule_config_bp.route('/api/conflict-records', methods=['GET'])
def conflict_records():
    """查询避让记录API（新增需求：20260301）"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})

        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})

        # 查询避让记录：找出违反避让规则的排班
        sql = """
        SELECT 
            r1.date as current_date,
            r1.time_slot as current_slot,
            r1.staff_name as current_staff,
            r2.date as prev_date,
            r2.time_slot as prev_slot,
            r2.staff_name as prev_staff
        FROM roster r1
        JOIN roster r2 ON r1.staff_name = r2.staff_name
        WHERE r1.date BETWEEN %s AND %s
        AND r2.date = DATE_SUB(r1.date, INTERVAL 1 DAY)
        AND (
            -- 早班避让规则：前一天8:00～9:00，今天任何时段都不应该安排
            (r2.time_slot = '8:00～9:00') OR
            -- 上午班避让规则：前一天9:00～12:00，今天任何时段都不应该安排
            (r2.time_slot = '9:00～12:00')
        )
        ORDER BY r1.date, r1.time_slot
        """

        results = db.query(sql, (start_date, end_date))
        db.close()
        
        # 处理时间字段
        processed_results = serialize_datetime_objects(results)
        
        return jsonify({
            "success": True,
            "data": processed_results,
            "total": len(processed_results)
        })
    except Exception as e:
        return jsonify({"success": False, "msg": "查询避让记录失败: " + str(e)})


@schedule_config_bp.route('/api/check-conflicts', methods=['POST'])
def check_conflicts():
    """检查指定日期是否存在潜在的避让冲突（新增需求：20260301）"""
    try:
        data = request.get_json()
        check_date_str = data.get('check_date')
        
        if not check_date_str:
            return jsonify({"success": False, "msg": "检查日期不能为空"})
            
        check_date = datetime.strptime(check_date_str, '%Y-%m-%d').date()
        prev_date = check_date - timedelta(days=1)
        
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})

        # 检查前一天的排班情况
        prev_sql = """
        SELECT time_slot, staff_name 
        FROM roster 
        WHERE date = %s AND time_slot IN ('8:00～9:00', '9:00～12:00')
        """
        
        prev_results = db.query(prev_sql, (prev_date,))
        conflicts = []
        
        for prev_record in prev_results:
            prev_slot = prev_record['time_slot']
            prev_staff = prev_record['staff_name']
            
            # 检查今天的排班是否违反了避让规则
            current_sql = """
            SELECT time_slot 
            FROM roster 
            WHERE date = %s AND staff_name = %s
            """
            
            current_results = db.query(current_sql, (check_date, prev_staff))
            
            if current_results:
                conflicts.append({
                    'conflict_date': check_date_str,
                    'prev_date': prev_date.strftime('%Y-%m-%d'),
                    'prev_slot': prev_slot,
                    'staff_name': prev_staff,
                    'current_slots': [r['time_slot'] for r in current_results],
                    'violation_type': '早班避让' if prev_slot == '8:00～9:00' else '上午班避让'
                })
        
        db.close()
        
        return jsonify({
            "success": True,
            "data": conflicts,
            "has_conflicts": len(conflicts) > 0
        })
    except Exception as e:
        return jsonify({"success": False, "msg": "检查避让冲突失败: " + str(e)})


@schedule_config_bp.route('/api/rotation-config', methods=['GET', 'POST'])
def rotation_config():
    """轮换配置管理API（新增需求：20260301）"""
    if request.method == 'GET':
        try:
            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})
            
            # 获取当前轮换配置
            sql = "SELECT time_slot_type, rotation_order, current_index FROM rotation_config"
            results = db.query(sql)
            db.close()
            
            # 处理结果
            config_data = {}
            for item in results:
                config_data[item['time_slot_type']] = {
                    'rotation_order': item['rotation_order'].split(',') if item['rotation_order'] else [],
                    'current_index': item['current_index']
                }
            
            return jsonify({
                "success": True,
                "data": config_data
            })
        except Exception as e:
            return jsonify({"success": False, "msg": "获取轮换配置失败: " + str(e)})
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            config_type = data.get('config_type')  # '日常' 或 '节假日'
            rotation_order = data.get('rotation_order', [])
            current_index = data.get('current_index', 0)
            
            if not config_type or not rotation_order:
                return jsonify({"success": False, "msg": "配置类型和轮换顺序不能为空"})
            
            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})
            
            # 更新或插入轮换配置
            sql = """
            INSERT INTO rotation_config (time_slot_type, rotation_order, current_index) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            rotation_order = VALUES(rotation_order), 
            current_index = VALUES(current_index)
            """
            
            success = db.execute(sql, (config_type, ','.join(rotation_order), current_index))
            db.close()
            
            if success:
                return jsonify({"success": True, "msg": "轮换配置更新成功"})
            else:
                return jsonify({"success": False, "msg": "轮换配置更新失败"})
        except Exception as e:
            return jsonify({"success": False, "msg": "更新轮换配置失败: " + str(e)})


@schedule_config_bp.route('/api/priority-staff', methods=['GET'])
def priority_staff():
    """获取优先安排人员列表（请假归来人员优先）API（新增需求：20260301）"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})
        
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})
        
        # 获取请假记录中的人员及其请假时间
        leave_sql = """
        SELECT staff_name, MIN(leave_date) as first_leave, MAX(leave_date) as last_leave
        FROM leave_record 
        WHERE leave_date BETWEEN %s AND %s
        GROUP BY staff_name
        ORDER BY first_leave
        """
        
        leave_results = db.query(leave_sql, (start_date, end_date))
        
        # 获取当前所有人员
        staff_sql = "SELECT staff_name FROM staff_config"
        staff_results = db.query(staff_sql)
        all_staffs = [item['staff_name'] for item in staff_results]
        
        # 构建优先级列表
        priority_list = []
        
        # 1. 最高优先级：最近请假归来人员
        for leave_record in leave_results:
            staff_name = leave_record['staff_name']
            last_leave = leave_record['last_leave']
            # 检查该人员是否已经在后续日期有排班安排
            check_roster_sql = """
            SELECT COUNT(*) as scheduled_count
            FROM roster 
            WHERE staff_name = %s AND date > %s
            """
            roster_check = db.query(check_roster_sql, (staff_name, last_leave))
            scheduled_count = roster_check[0]['scheduled_count'] if roster_check else 0
            
            if scheduled_count == 0:  # 还没有安排，需要优先
                priority_list.append({
                    'staff_name': staff_name,
                    'priority_level': 1,
                    'reason': f'请假归来优先安排（最后请假日期：{last_leave}）',
                    'last_leave_date': last_leave
                })
        
        # 2. 次优先级：未在近期排班的人员
        recent_days = 7  # 考虑最近7天的排班情况
        recent_start = datetime.strptime(end_date, '%Y-%m-%d').date() - timedelta(days=recent_days)
        
        for staff in all_staffs:
            # 检查是否已在优先列表中
            if any(item['staff_name'] == staff for item in priority_list):
                continue
            
            # 检查近期是否有排班
            recent_roster_sql = """
            SELECT COUNT(*) as recent_count
            FROM roster 
            WHERE staff_name = %s AND date BETWEEN %s AND %s
            """
            recent_check = db.query(recent_roster_sql, (staff, recent_start, end_date))
            recent_count = recent_check[0]['recent_count'] if recent_check else 0
            
            if recent_count == 0:  # 近期无排班，给予次优先级
                priority_list.append({
                    'staff_name': staff,
                    'priority_level': 2,
                    'reason': '近期未排班人员',
                    'last_scheduled': None
                })
        
        # 3. 普通人员按轮换顺序
        remaining_staff = [staff for staff in all_staffs 
                          if not any(item['staff_name'] == staff for item in priority_list)]
        
        for i, staff in enumerate(remaining_staff):
            priority_list.append({
                'staff_name': staff,
                'priority_level': 3,
                'reason': '按轮换顺序安排',
                'rotation_order': i
            })
        
        # 按优先级排序
        priority_list.sort(key=lambda x: (x['priority_level'], 
                                        x.get('last_leave_date', ''), 
                                        x.get('rotation_order', 0)))
        
        db.close()
        
        return jsonify({
            "success": True,
            "data": priority_list,
            "total": len(priority_list)
        })
    except Exception as e:
        return jsonify({"success": False, "msg": "获取优先人员列表失败: " + str(e)})


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
