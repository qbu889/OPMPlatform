#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调整因子计算器路由
"""
from flask import Blueprint, render_template, request, jsonify, current_app
import mysql.connector
from decimal import Decimal
import json

adjustment_calc_bp = Blueprint('adjustment_calc', __name__, url_prefix='/adjustment-calc')


def get_db_connection():
    """获取数据库连接"""
    return mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        charset=current_app.config['MYSQL_CHARSET'],
        database=current_app.config['KNOWLEDGE_BASE_DB']
    )


def decimal_to_float(obj):
    """将 Decimal 转换为 float"""
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


@adjustment_calc_bp.route('/page')
def adjustment_calculator_page():
    """调整因子计算器页面"""
    return render_template('adjustment_calculator.html')


@adjustment_calc_bp.route('/api/fix-scale-timing')
def fix_scale_timing():
    """修复规模计数时机的 score_value 值"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Excel 公式对应的正确值
        correct_values = {
            '估算早期': '1.39',  # D36
            '估算中期': '1.21',  # D37
            '估算晚期': '1.10',  # D38
            '项目完成': '1.00',  # D39
        }
        
        updated_count = 0
        for option_name, correct_value in correct_values.items():
            cursor.execute("""
                UPDATE fpa_adjustment_factor
                SET score_value = %s
                WHERE factor_category = '规模变更调整系数' 
                AND option_name = %s
            """, (correct_value, option_name))
            updated_count += cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 条记录',
            'updated_count': updated_count
        })
        
    except Exception as e:
        current_app.logger.error(f"修复数据失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@adjustment_calc_bp.route('/api/calculate-score', methods=['POST'])
def calculate_score():
    """根据描述计算分值（插入或更新）"""
    try:
        data = request.get_json()
        option_name = data.get('option_name')
        description = data.get('description')
        current_score = data.get('current_score')
        
        if not option_name or not description:
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 检查数据库中是否已存在该 option_name 的记录
        cursor.execute("""
            SELECT id, score_value 
            FROM fpa_adjustment_factor
            WHERE option_name = %s AND factor_category = '规模变更调整系数'
        """, (option_name,))
        
        existing_record = cursor.fetchone()
        
        # 根据描述内容计算新的分值
        # 这里可以扩展为：根据描述的关键词、长度等特征计算分值
        # 目前我们使用一个简单的规则：根据描述的长度和关键词匹配
        new_score = calculate_score_from_description(description, current_score)
        
        operation_type = ''
        
        if existing_record:
            # 已存在，更新
            record_id = existing_record['id']
            cursor.execute("""
                UPDATE fpa_adjustment_factor
                SET 
                    score_value = %s,
                    formula = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (str(new_score), description, record_id))
            operation_type = '更新'
            current_app.logger.info(f"更新记录：{record_id}, option_name: {option_name}, score: {new_score}")
        else:
            # 不存在，插入
            # 获取最大的 display_order
            cursor.execute("""
                SELECT MAX(display_order) as max_order 
                FROM fpa_adjustment_factor 
                WHERE factor_category = '规模变更调整系数'
            """)
            max_order_result = cursor.fetchone()
            max_order = max_order_result['max_order'] if max_order_result['max_order'] else 0
            new_order = max_order + 1
            
            cursor.execute("""
                INSERT INTO fpa_adjustment_factor 
                (factor_name, factor_category, option_name, score_value, formula, display_order)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, ('规模变更调整因子', '规模变更调整系数', option_name, str(new_score), description, new_order))
            
            record_id = cursor.lastrowid
            operation_type = '插入'
            current_app.logger.info(f"插入新记录：{record_id}, option_name: {option_name}, score: {new_score}")
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'new_score': new_score,
            'operation_type': operation_type,
            'record_id': record_id,
            'message': f'已{operation_type}记录，新分值为：{new_score:.2f}'
        })
        
    except Exception as e:
        current_app.logger.error(f"计算分值失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def calculate_score_from_description(description, current_score):
    """根据描述内容计算分值
    
    这里可以根据具体的业务规则来实现
    目前使用一个简单的规则：
    - 如果描述包含"早期"、"初期"等词，分值较高
    - 如果描述包含"晚期"、"完成"等词，分值较低
    - 默认使用当前分值
    """
    # 简单规则示例
    if '早期' in description or '初期' in description or '概算' in description:
        return 1.39
    elif '中期' in description or '投标' in description or '计划' in description:
        return 1.21
    elif '晚期' in description or '需求' in description or '分析' in description:
        return 1.10
    elif '完成' in description or '交付' in description or '运维' in description:
        return 1.00
    else:
        # 如果没有匹配的关键词，返回当前分值
        return current_score if current_score else 1.00


def excel_if_formula_c2_b36_d39(selected_value, config_data):
    """将 Excel 公式转化为程序逻辑
    
    原始 Excel 公式：
    =IF('3. 调整因子'!C2='3. 调整因子'!B36,'3. 调整因子'!D36,
      IF('3. 调整因子'!C2='3. 调整因子'!B37,'3. 调整因子'!D37,
        IF('3. 调整因子'!C2='3. 调整因子'!B38,'3. 调整因子'!D38,
          IF('3. 调整因子'!C2='3. 调整因子'!B39,'3. 调整因子'!D39,0))))
    
    参数:
        selected_value: C2 单元格的值（用户选择的值）
        config_data: 配置数据列表，包含 B 列和 D 列的值
                    [{'option_name': '估算早期', 'score_value': 1.39}, ...]
    
    返回:
        对应的分值，如果没有匹配则返回 0
    """
    # 将 Excel 的 IF 嵌套转换为 Python 的循环查找
    for config in config_data:
        if selected_value == config['option_name']:
            return float(config['score_value'])
    
    # 如果没有匹配，返回 0（对应 Excel 公式最后的 0）
    return 0.0


def excel_formula_lookup(selected_value, b_cells, d_cells):
    """通用的 Excel 公式查找函数
    
    模拟 Excel 的 IF 嵌套查找逻辑：
    =IF(C2=B36,D36,IF(C2=B37,D37,IF(C2=B38,D38,IF(C2=B39,D39,0))))
    
    参数:
        selected_value: C2 的值（用户选择）
        b_cells: B 列的值列表 ['估算早期', '估算中期', '估算晚期', '项目完成']
        d_cells: D 列的值列表 [1.39, 1.21, 1.10, 1.00]
    
    返回:
        对应的 D 列分值
    """
    if len(b_cells) != len(d_cells):
        raise ValueError("B 列和 D 列的长度必须相同")
    
    for i in range(len(b_cells)):
        if selected_value == b_cells[i]:
            return float(d_cells[i])
    
    return 0.0


@adjustment_calc_bp.route('/api/scale-timing-config', methods=['GET'])
def get_scale_timing_config():
    """获取规模计数时机配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询规模计数时机的所有配置
        cursor.execute("""
            SELECT 
                id,
                option_name,
                score_value,
                formula as description,
                display_order,
                CONCAT('B', 35 + display_order) as cell_b,
                CONCAT('D', 35 + display_order) as cell_d,
                CONCAT('B', 35 + display_order, '/D', 35 + display_order) as cell_position
            FROM fpa_adjustment_factor
            WHERE factor_category = '规模变更调整系数'
            ORDER BY display_order
        """)
        
        configs = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': configs
        })
        
    except Exception as e:
        current_app.logger.error(f"获取配置失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@adjustment_calc_bp.route('/api/scale-timing-config', methods=['POST'])
def save_scale_timing_config():
    """保存规模计数时机配置"""
    try:
        data = request.get_json()
        configs = data.get('configs', [])
        
        if not configs:
            return jsonify({
                'success': False,
                'message': '没有提供配置数据'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 批量更新配置
        for config in configs:
            cursor.execute("""
                UPDATE fpa_adjustment_factor
                SET 
                    score_value = %s,
                    formula = %s
                WHERE id = %s AND factor_category = '规模变更调整系数'
            """, (
                str(config['score_value']),
                config.get('description', ''),
                config['id']
            ))
        
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功更新 {len(configs)} 条配置'
        })
        
    except Exception as e:
        current_app.logger.error(f"保存配置失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@adjustment_calc_bp.route('/api/calculator-data')
def get_calculator_data():
    """获取计算器所需的所有数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取所有调整因子数据
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            ORDER BY factor_category, display_order, id
        ''')
        
        factors = cursor.fetchall()
        
        # 转换 Decimal 为 float
        for factor in factors:
            if factor.get('score_value'):
                factor['score_value'] = decimal_to_float(factor['score_value'])
        
        cursor.close()
        conn.close()
        
        # 按分类组织数据
        data = {
            'application_types': [],  # 应用类型
            'quality_characteristics': [],  # 质量特性
            'languages': [],  # 开发语言
            'team_backgrounds': [],  # 开发团队背景
            'scale_timing': [],  # 规模计数时机
            'reuse_levels': [],  # 重用程度
            'change_types': [],  # 修改类型
            'function_points': []  # 功能点基准值
        }
        
        for factor in factors:
            category = factor['factor_category']
            
            if category == '应用类型':
                data['application_types'].append(factor)
            elif category == '质量特性':
                data['quality_characteristics'].append(factor)
            elif category == '开发语言':
                data['languages'].append(factor)
            elif category == '开发团队背景':
                data['team_backgrounds'].append(factor)
            elif category == '规模变更调整系数':
                data['scale_timing'].append(factor)
            elif category == '重用程度调整系数':
                data['reuse_levels'].append(factor)
            elif category == '修改类型调整系数':
                data['change_types'].append(factor)
            elif category == '功能点基准值':
                data['function_points'].append(factor)
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        current_app.logger.error(f"获取计算器数据失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@adjustment_calc_bp.route('/api/calculate', methods=['POST'])
def calculate_adjustment():
    """根据用户选择计算调整因子"""
    try:
        data = request.json
        
        # 用户选择
        scale_timing = data.get('scale_timing')  # 估算早期/中期/晚期/项目完成
        application_type = data.get('application_type')  # 业务处理/应用集成等
        distributed_processing = data.get('distributed_processing')  # 分布式处理选项
        performance = data.get('performance')  # 性能选项
        reliability = data.get('reliability')  # 可靠性选项
        multi_site = data.get('multi_site')  # 多重站点选项
        language = data.get('language')  # 开发语言
        team_background = data.get('team_background')  # 开发团队背景
        reuse_level = data.get('reuse_level', '低')  # 重用程度
        change_type = data.get('change_type', '新增')  # 修改类型
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        result = {
            'scale_factor': 0,  # 规模变更调整因子
            'application_factor': 0,  # 应用类型调整因子
            'quality_factor': 0,  # 质量特性调整因子（分布式 + 性能 + 可靠性 + 多重站点）
            'language_factor': 0,  # 开发语言调整因子
            'team_factor': 0,  # 开发团队背景调整因子
            'reuse_factor': 0,  # 重用程度调整因子
            'change_factor': 0,  # 修改类型调整因子
            'total_factor': 0,  # 总调整因子
            'details': {}  # 详细计算过程
        }
        
        # 1. 规模变更调整因子
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_category = '规模变更调整系数' AND option_name = %s
        ''', (scale_timing,))
        scale_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if scale_row:
            result['scale_factor'] = scale_row['score_value']
            result['details']['scale'] = {
                'name': '规模变更调整因子',
                'option': scale_row['option_name'],
                'value': scale_row['score_value']
            }
        
        # 2. 应用类型调整因子
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_category = '应用类型' AND option_name = %s
        ''', (application_type,))
        app_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if app_row:
            result['application_factor'] = app_row['score_value']
            result['details']['application'] = {
                'name': '应用类型调整因子',
                'option': app_row['option_name'],
                'value': app_row['score_value']
            }
        
        # 3. 质量特性调整因子（分布式 + 性能 + 可靠性 + 多重站点）
        quality_total = 0
        quality_details = []
        
        # 分布式处理
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_name = '分布式处理' AND option_name = %s
        ''', (distributed_processing,))
        dp_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if dp_row:
            quality_total += dp_row['score_value']
            quality_details.append({
                'name': '分布式处理',
                'option': dp_row['option_name'],
                'value': dp_row['score_value']
            })
        
        # 性能
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_name = '性能' AND option_name = %s
        ''', (performance,))
        perf_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if perf_row:
            quality_total += perf_row['score_value']
            quality_details.append({
                'name': '性能',
                'option': perf_row['option_name'],
                'value': perf_row['score_value']
            })
        
        # 可靠性
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_name = '可靠性' AND option_name = %s
        ''', (reliability,))
        rel_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if rel_row:
            quality_total += rel_row['score_value']
            quality_details.append({
                'name': '可靠性',
                'option': rel_row['option_name'],
                'value': rel_row['score_value']
            })
        
        # 多重站点
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_name = '多重站点' AND option_name = %s
        ''', (multi_site,))
        ms_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if ms_row:
            quality_total += ms_row['score_value']
            quality_details.append({
                'name': '多重站点',
                'option': ms_row['option_name'],
                'value': ms_row['score_value']
            })
        
        result['quality_factor'] = quality_total
        result['details']['quality'] = {
            'name': '质量特性调整因子',
            'sub_items': quality_details,
            'total': quality_total
        }
        
        # 4. 开发语言调整因子
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_category = '开发语言' AND option_name = %s
        ''', (language,))
        lang_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if lang_row:
            result['language_factor'] = lang_row['score_value']
            result['details']['language'] = {
                'name': '开发语言调整因子',
                'option': lang_row['option_name'],
                'value': lang_row['score_value']
            }
        else:
            result['language_factor'] = 0
            result['details']['language'] = {
                'name': '开发语言调整因子',
                'option': language,
                'value': 0
            }
        
        # 5. 开发团队背景调整因子
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_category = '开发团队背景' AND option_name = %s
        ''', (team_background,))
        team_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if team_row:
            result['team_factor'] = team_row['score_value']
            result['details']['team'] = {
                'name': '开发团队背景调整因子',
                'option': team_row['option_name'],
                'value': team_row['score_value']
            }
        else:
            result['team_factor'] = 0
            result['details']['team'] = {
                'name': '开发团队背景调整因子',
                'option': team_background,
                'value': 0
            }
        
        # 6. 重用程度调整因子
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_category = '重用程度调整系数' AND option_name = %s
        ''', (reuse_level,))
        reuse_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if reuse_row:
            result['reuse_factor'] = reuse_row['score_value']
            result['details']['reuse'] = {
                'name': '重用程度调整因子',
                'option': reuse_row['option_name'],
                'value': reuse_row['score_value']
            }
        else:
            result['reuse_factor'] = 0
            result['details']['reuse'] = {
                'name': '重用程度调整因子',
                'option': reuse_level,
                'value': 0
            }
        
        # 7. 修改类型调整因子
        cursor.execute('''
            SELECT * FROM fpa_adjustment_factor 
            WHERE factor_category = '修改类型调整系数' AND option_name = %s
        ''', (change_type,))
        change_row = cursor.fetchone()
        # 清除未读取的结果
        cursor.fetchall() if cursor.with_rows else None
        if change_row:
            result['change_factor'] = change_row['score_value']
            result['details']['change'] = {
                'name': '修改类型调整因子',
                'option': change_row['option_name'],
                'value': change_row['score_value']
            }
        else:
            result['change_factor'] = 0
            result['details']['change'] = {
                'name': '修改类型调整因子',
                'option': change_type,
                'value': 0
            }
        
        # 计算总调整因子（所有因子的乘积）
        result['total_factor'] = (
            result['scale_factor'] *
            result['application_factor'] *
            result['quality_factor'] *
            result['language_factor'] *
            result['team_factor'] *
            result['reuse_factor'] *
            result['change_factor']
        )
        
        result['details']['total'] = {
            'name': '总调整因子',
            'formula': '规模变更 × 应用类型 × 质量特性 × 开发语言 × 团队背景 × 重用程度 × 修改类型',
            'value': result['total_factor']
        }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"计算调整因子失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
