# routes/sql_routes.py
from flask import Blueprint, request, render_template, jsonify
import logging

sql_bp = Blueprint('sql', __name__)
logger = logging.getLogger(__name__)

@sql_bp.route('/sql-formatter')
def sql_formatter():
    """SQL ID格式化工具页面"""
    return render_template('sql_formatter.html')

@sql_bp.route('/format_ids', methods=['POST'])
def format_ids():
    """处理ID格式化请求"""
    # 获取前端传入的ID文本
    ids_text = request.form.get('ids', '')

    # 按行分割并清理空白字符
    ids_list = [id.strip() for id in ids_text.split('\n') if id.strip()]

    if not ids_list:
        return jsonify({
            'success': False,
            'error': '未输入任何ID'
        })

    # 格式化为SQL格式
    formatted_ids = [f"'{id}'" for id in ids_list]

    if len(ids_list) == 1:
        # 单个ID使用等号
        sql_result = f"'{ids_list[0]}'"
        sql_query = f"WHERE w1.sheet_id = '{ids_list[0]}'"
    else:
        # 多个ID使用IN语句
        sql_result = ',\n'.join(formatted_ids)
        sql_query = f"WHERE w1.sheet_id IN (\n{sql_result}\n)"

    return jsonify({
        'success': True,
        'formatted_ids': sql_result,
        'sql_query': sql_query,
        'count': len(ids_list)
    })
