#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
排班配置管理路由
"""
from flask import Blueprint, render_template, request, jsonify
from routes.排班.paiBanNew_v2 import DB_CONFIG, RosterDB
from datetime import datetime, date, timedelta
from typing import List, Dict
import csv
import io
import requests
import json
import os
from cryptography.fernet import Fernet

schedule_config_bp = Blueprint('schedule_config_bp', __name__, url_prefix='/schedule-config')

# ========== Webhook 加密/解密配置 ==========
ENCRYPTION_KEY = os.environ.get('WEBHOOK_ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    os.environ['WEBHOOK_ENCRYPTION_KEY'] = ENCRYPTION_KEY  # 存入环境变量供推送服务使用
    print(f"[WARNING] WEBHOOK_ENCRYPTION_KEY 未设置，使用自动生成密钥")

fernet = Fernet(ENCRYPTION_KEY if isinstance(ENCRYPTION_KEY, bytes) else ENCRYPTION_KEY.encode())

def encrypt_webhook(webhook_url):
    """加密 Webhook URL"""
    if not webhook_url:
        return None
    encrypted = fernet.encrypt(webhook_url.encode())
    return encrypted.decode()

def decrypt_webhook(encrypted_webhook):
    """解密 Webhook URL（兼容明文和密文）"""
    if not encrypted_webhook:
        return None
    try:
        decrypted = fernet.decrypt(encrypted_webhook.encode())
        result = decrypted.decode()
        print(f"[DEBUG] Webhook 解密成功: {result[:50]}...")
        return result
    except Exception as e:
        # 解密失败，可能是明文数据，直接返回原值
        print(f"[WARNING] Webhook 解密失败，尝试作为明文使用: {str(e)[:100]}")
        return encrypted_webhook



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

# @schedule_config_bp.route('/')
# def schedule_config_page():
#     """排班配置页面（已废弃，使用 Vue 页面）"""
#     return render_template('schedule/schedule_config.html')

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
    """生成排班表 API"""
    from routes.排班.paiBanNew_v2 import RosterGenerator

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
        return jsonify({"success": False, "msg": "生成排班表失败：" + str(e)})

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
            return jsonify({"success": False, "msg": "获取排班记录失败：" + str(e)})


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


@schedule_config_bp.route('/api/import-schedule', methods=['POST'])
def import_schedule():
    """从 CSV 文件导入排班数据 API"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({"success": False, "msg": "未找到上传文件"})
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"success": False, "msg": "未选择文件"})
        
        if not file.filename.endswith('.csv'):
            return jsonify({"success": False, "msg": "请上传 CSV 格式的文件"})
        
        # 读取 CSV 文件内容
        content = file.read().decode('utf-8-sig')  # utf-8-sig 可以处理 BOM 头
        csv_file = io.StringIO(content)
        
        # 解析 CSV
        reader = csv.DictReader(csv_file)
        
        # 验证 CSV 列名
        required_columns = ['日期', '星期', '时段', '人员']
        if not all(col in reader.fieldnames for col in required_columns):
            return jsonify({"success": False, "msg": f"CSV 文件格式不正确，需要包含以下列：{', '.join(required_columns)}"})
        
        # 解析数据并按日期和时段分组
        schedule_data = {}
        for row in reader:
            date_str = row['日期'].strip()
            time_slot = row['时段'].strip()
            staff_str = row['人员'].strip()
            # 如果 CSV 有备注列则读取，否则使用空字符串
            remark = row.get('备注', '').strip() if '备注' in reader.fieldnames else ''
            
            # 解析日期 (支持多种格式)
            try:
                # 尝试 YYYY/M/D 格式 (如 2026/2/24)
                if '/' in date_str:
                    parsed_date = datetime.strptime(date_str, '%Y/%m/%d').date()
                else:
                    # 尝试 YYYY-MM-DD 格式
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"success": False, "msg": f"日期格式错误：{date_str}，请使用 YYYY-MM-DD 或 YYYY/MM/DD 格式"})
            
            date_key = parsed_date.strftime('%Y-%m-%d')
            
            if date_key not in schedule_data:
                schedule_data[date_key] = {}
            
            if time_slot not in schedule_data[date_key]:
                schedule_data[date_key][time_slot] = {'staffs': [], 'remark': remark}
            
            # 分割多个人员 (使用顿号、逗号等分隔符)
            staff_list = [s.strip() for s in staff_str.replace(',', ',').split('、')]
            schedule_data[date_key][time_slot]['staffs'].extend(staff_list)
        
        # 获取需要导入的日期范围
        if not schedule_data:
            return jsonify({"success": False, "msg": "CSV 文件中没有有效的排班数据"})
        
        dates = sorted(schedule_data.keys())
        start_date = dates[0]
        end_date = dates[-1]
        
        # 返回导入预览信息
        total_records = sum(
            len(slot_data['staffs']) 
            for date_data in schedule_data.values() 
            for slot_data in date_data.values()
        )
        
        # 将数据暂存在 session 或其他地方，等待用户确认
        # 这里简单起见，直接返回预览信息
        return jsonify({
            "success": True,
            "msg": f"解析成功，共 {total_records} 条记录",
            "data": {
                "start_date": start_date,
                "end_date": end_date,
                "total_days": len(dates),
                "total_records": total_records,
                "schedule_data": schedule_data
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "msg": "导入失败：" + str(e)})


@schedule_config_bp.route('/api/confirm-import-schedule', methods=['POST'])
def confirm_import_schedule():
    """确认导入排班数据 API"""
    try:
        data = request.get_json()
        schedule_data = data.get('schedule_data')
        
        if not schedule_data:
            return jsonify({"success": False, "msg": "未提供排班数据"})
        
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})
        
        # 获取日期范围
        dates = sorted(schedule_data.keys())
        start_date = dates[0]
        end_date = dates[-1]
        
        # 先删除已有数据
        delete_sql = "DELETE FROM roster WHERE date BETWEEN %s AND %s"
        db.execute(delete_sql, (start_date, end_date))
        
        # 插入新数据
        insert_sql = """
        INSERT INTO roster (date, time_slot, staff_name, is_main, remark)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        inserted_count = 0
        for date_str in sorted(schedule_data.keys()):
            date_data = schedule_data[date_str]
            
            for time_slot, slot_data in date_data.items():
                staff_list = slot_data['staffs']
                remark = slot_data.get('remark', '')
                
                # 如果是多人，第一个作为主班，其他为辅班
                for idx, staff_name in enumerate(staff_list):
                    is_main = (idx == 0)  # 第一个人员为主班
                    db.execute(insert_sql, (
                        date_str, 
                        time_slot, 
                        staff_name, 
                        is_main, 
                        remark if remark else None
                    ))
                    inserted_count += 1
        
        db.close()
        
        return jsonify({
            "success": True, 
            "msg": f"导入成功！共导入 {inserted_count} 条排班记录，日期范围：{start_date} 至 {end_date}"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "msg": "确认导入失败：" + str(e)})


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


# ==================== Vue 前端兼容 API ====================

@schedule_config_bp.route('/api/list', methods=['GET'])
def schedule_list_api():
    """排班列表API - Vue前端使用"""
    try:
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})
        
        # 获取总数
        count_sql = "SELECT COUNT(DISTINCT date) as total FROM roster"
        count_result = db.query(count_sql)
        total = count_result[0]['total'] if count_result else 0
        
        # 分页查询
        offset = (page - 1) * size
        sql = """
        SELECT DISTINCT r.date,
               MIN(r.staff_name) as name,
               '运维部' as department,
               MIN(r.date) as startDate,
               MAX(r.date) as endDate,
               CASE WHEN MAX(r.date) >= CURDATE() THEN 'active' ELSE 'ended' END as status
        FROM roster r
        GROUP BY r.date
        ORDER BY r.date DESC
        LIMIT %s OFFSET %s
        """
        
        results = db.query(sql, (size, offset))
        db.close()
        
        # 处理结果
        processed_results = []
        for idx, row in enumerate(results):
            processed_results.append({
                'id': idx + 1,
                'name': f"{row['date']} 排班",
                'department': row['department'],
                'startDate': row['startDate'].strftime('%Y-%m-%d') if hasattr(row['startDate'], 'strftime') else str(row['startDate']),
                'endDate': row['endDate'].strftime('%Y-%m-%d') if hasattr(row['endDate'], 'strftime') else str(row['endDate']),
                'status': row['status']
            })
        
        return jsonify({
            "success": True,
            "data": processed_results,
            "total": total
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "msg": "获取排班列表失败: " + str(e)})


@schedule_config_bp.route('/api/create', methods=['POST'])
def create_schedule_api():
    """创建排班API - Vue前端使用"""
    # TODO: 实现创建排班逻辑
    return jsonify({"success": True, "msg": "创建成功"})


@schedule_config_bp.route('/api/<int:schedule_id>', methods=['PUT'])
def update_schedule_api(schedule_id):
    """更新排班API - Vue前端使用"""
    # TODO: 实现更新排班逻辑
    return jsonify({"success": True, "msg": "更新成功"})


@schedule_config_bp.route('/api/send-dingtalk-message', methods=['POST'])
def send_dingtalk_message():
    """发送钉钉消息API - 推送排班信息给群和人员"""
    try:
        data = request.get_json()
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        time_slots = data.get('time_slots', [])  # 要推送的时段列表
        dingtalk_webhook = data.get('dingtalk_webhook')  # 钉钉机器人 webhook URL
        
        if not start_date or not end_date:
            return jsonify({"success": False, "msg": "开始日期和结束日期不能为空"})
        
        if not dingtalk_webhook:
            return jsonify({"success": False, "msg": "钉钉 Webhook 地址不能为空"})
        
        # 解密 Webhook URL（兼容明文和密文）
        webhook_url = decrypt_webhook(dingtalk_webhook)
        if not webhook_url or not webhook_url.startswith('http'):
            return jsonify({"success": False, "msg": "Webhook 地址格式不正确，请检查配置"})
        
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})
        
        # 查询指定日期范围的排班数据
        sql = """
        SELECT r.*
        FROM roster r
        WHERE r.date BETWEEN %s AND %s
        ORDER BY r.date, r.time_slot, r.is_main DESC
        """
        
        results = db.query(sql, (start_date, end_date))
        db.close()
        
        if not results:
            return jsonify({"success": False, "msg": "没有找到排班数据"})
        
        # 按日期和时段分组
        grouped_data = {}
        for record in results:
            date_key = record['date'].strftime('%Y-%m-%d') if hasattr(record['date'], 'strftime') else str(record['date'])
            time_slot = record['time_slot']
            
            # 如果指定了时段过滤，则只推送指定的时段
            if time_slots and time_slot not in time_slots:
                continue
            
            if date_key not in grouped_data:
                grouped_data[date_key] = {}
            
            if time_slot not in grouped_data[date_key]:
                grouped_data[date_key][time_slot] = []
            
            grouped_data[date_key][time_slot].append(record)
        
        # 构建钉钉消息内容（优化后的Markdown格式）
        today = datetime.now().date()
        msg_content = "# 📅 排班信息推送\n\n"
        
        # 按日期排序
        sorted_dates = sorted(grouped_data.keys())
        
        for date_str in sorted_dates:
            day_data = grouped_data[date_str]
            
            # 计算星期和相对日期描述
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
            
            # 判断是今天、明天还是其他日期
            delta = (date_obj - today).days
            if delta == 0:
                date_label = f"**今天** {date_str} ({weekday})"
            elif delta == 1:
                date_label = f"**明天** {date_str} ({weekday})"
            elif delta == -1:
                date_label = f"**昨天** {date_str} ({weekday})"
            else:
                date_label = f"**{date_str}** ({weekday})"
            
            msg_content += f"### {date_label}\n\n"
            
            # 按时段排序（按时间顺序）
            time_slot_order = [
                '8:00～9:00',
                '8:00～12:00',
                '9:00～12:00',
                '13:30～17:30',
                '13:30～18:00',
                '17:30～21:30',
                '18:00～21:00'
            ]
            
            sorted_slots = sorted(day_data.keys(), 
                                key=lambda x: time_slot_order.index(x) if x in time_slot_order else 999)
            
            for time_slot in sorted_slots:
                staff_records = day_data[time_slot]
                
                # 提取主班和辅班
                main_staff = [r['staff_name'] for r in staff_records if r['is_main']]
                backup_staff = [r['staff_name'] for r in staff_records if not r['is_main']]
                
                staff_display = '、'.join(main_staff + backup_staff) if (main_staff + backup_staff) else '空闲'
                
                msg_content += f"- **{time_slot}**: {staff_display}\n"
            
            msg_content += "\n---\n\n"
        
        # 添加查看详情链接（Markdown格式，钉钉会自动渲染为按钮）
        schedule_view_url = "https://alidocs.dingtalk.com/i/nodes/20eMKjyp81LOavDgf46AORZwJxAZB1Gv?utm_scene=person_space&iframeQuery=viewId%3Drm8nwl6hqzo0v1952seh4%26sheetId%3Dhe1d5bovtjfxcies7i3fi"
        msg_content += f"[查看完整排班]({schedule_view_url})\n"
        
        # 发送钉钉消息（使用 actionCard 类型）
        dingtalk_data = {
            "msgtype": "actionCard",
            "actionCard": {
                "title": "排班信息推送",
                "text": msg_content,
                "btnOrientation": "0"
            }
        }
        
        response = requests.post(
            webhook_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(dingtalk_data),
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('errcode') == 0:
                return jsonify({
                    "success": True,
                    "msg": "钉钉消息推送成功",
                    "data": {
                        "total_dates": len(sorted_dates),
                        "time_slots": len(time_slots) if time_slots else '全部时段'
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "msg": f"钉钉推送失败: {result.get('errmsg', '未知错误')}"
                })
        else:
            return jsonify({
                "success": False,
                "msg": f"钉钉推送失败，HTTP状态码: {response.status_code}"
            })
            
    except requests.exceptions.RequestException as e:
        # 网络请求异常，提供更友好的错误提示
        error_msg = str(e)
        if 'Connection refused' in error_msg:
            friendly_msg = "无法连接到钉钉服务器，请检查网络连接"
        elif 'timeout' in error_msg.lower():
            friendly_msg = "连接钉钉服务器超时，请稍后重试"
        elif 'Invalid URL' in error_msg:
            friendly_msg = "Webhook 地址格式不正确，请重新配置"
        else:
            friendly_msg = f"网络请求失败: {error_msg}"
        return jsonify({"success": False, "msg": friendly_msg})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "msg": f"推送失败: {str(e)}"})


@schedule_config_bp.route('/api/dingtalk-schedule-config', methods=['GET', 'POST'])
def dingtalk_schedule_config():
    """钉钉定时推送配置API"""
    if request.method == 'GET':
        # 获取当前定时推送配置
        try:
            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})
            
            sql = "SELECT * FROM dingtalk_schedule_config ORDER BY id"
            results = db.query(sql)
            db.close()
            
            # 处理时间字段（不解密 Webhook，保持加密状态）
            processed_results = serialize_datetime_objects(results)
            
            return jsonify({
                "success": True,
                "data": processed_results
            })
        except Exception as e:
            return jsonify({"success": False, "msg": "获取配置失败: " + str(e)})
    
    elif request.method == 'POST':
        # 保存或更新定时推送配置
        try:
            data = request.get_json()
            config_id = data.get('id')
            webhook_url = data.get('webhook_url')
            time_slots = data.get('time_slots', [])  # 推送时段列表
            schedule_times = data.get('schedule_times', [])  # 推送时间点，如 ["08:00", "09:00", "18:00"]
            enabled = data.get('enabled', True)
            description = data.get('description', '')
            
            if not webhook_url:
                return jsonify({"success": False, "msg": "Webhook地址不能为空"})
            
            if not schedule_times:
                return jsonify({"success": False, "msg": "至少需要配置一个推送时间"})
            
            db = RosterDB(DB_CONFIG)
            if not db.connect():
                return jsonify({"success": False, "msg": "数据库连接失败"})
            
            # 将时间列表转换为JSON字符串存储
            import json as json_module
            time_slots_json = json_module.dumps(time_slots, ensure_ascii=False)
            schedule_times_json = json_module.dumps(schedule_times, ensure_ascii=False)
            
            # 加密 Webhook URL
            encrypted_webhook = encrypt_webhook(webhook_url)
            
            if config_id:
                # 更新现有配置
                update_sql = """
                UPDATE dingtalk_schedule_config 
                SET webhook_url = %s, time_slots = %s, schedule_times = %s, 
                    enabled = %s, description = %s, updated_at = NOW()
                WHERE id = %s
                """
                db.execute(update_sql, (encrypted_webhook, time_slots_json, schedule_times_json, 
                                       enabled, description, config_id))
                msg = "配置更新成功"
            else:
                # 新增配置
                insert_sql = """
                INSERT INTO dingtalk_schedule_config 
                (webhook_url, time_slots, schedule_times, enabled, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                """
                db.execute(insert_sql, (encrypted_webhook, time_slots_json, schedule_times_json, 
                                       enabled, description))
                msg = "配置添加成功"
            
            db.close()
            
            # 重新加载定时任务
            try:
                from flask import current_app
                pusher = current_app.dingtalk_pusher
                if pusher:
                    pusher.load_and_schedule_tasks()
                    # 获取当前任务列表并输出日志
                    jobs = pusher.scheduler.get_jobs()
                    dingtalk_jobs = [job for job in jobs if job.id.startswith('dingtalk_push_')]
                    print(f"\n[INFO] 当前共有 {len(dingtalk_jobs)} 个定时任务:")
                    for job in dingtalk_jobs:
                        next_run = job.next_run_time
                        if next_run:
                            print(f"  - {job.name}: 下次执行时间 {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            except Exception as reload_error:
                import traceback
                traceback.print_exc()
            
            return jsonify({"success": True, "msg": msg})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "msg": "保存配置失败: " + str(e)})


@schedule_config_bp.route('/api/dingtalk-schedule-config/<int:config_id>', methods=['DELETE'])
def delete_dingtalk_schedule_config(config_id):
    """删除定时推送配置"""
    try:
        db = RosterDB(DB_CONFIG)
        if not db.connect():
            return jsonify({"success": False, "msg": "数据库连接失败"})
        
        delete_sql = "DELETE FROM dingtalk_schedule_config WHERE id = %s"
        db.execute(delete_sql, (config_id,))
        db.close()
        
        # 重新加载定时任务
        try:
            from flask import current_app
            pusher = current_app.dingtalk_pusher
            if pusher:
                pusher.load_and_schedule_tasks()
                # 获取当前任务列表并输出日志
                jobs = pusher.scheduler.get_jobs()
                dingtalk_jobs = [job for job in jobs if job.id.startswith('dingtalk_push_')]
                print(f"\n[INFO] 当前共有 {len(dingtalk_jobs)} 个定时任务:")
                for job in dingtalk_jobs:
                    next_run = job.next_run_time
                    if next_run:
                        print(f"  - {job.name}: 下次执行时间 {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as reload_error:
            import traceback
            traceback.print_exc()
        
        return jsonify({"success": True, "msg": "配置删除成功"})
    except Exception as e:
        return jsonify({"success": False, "msg": "删除配置失败: " + str(e)})
