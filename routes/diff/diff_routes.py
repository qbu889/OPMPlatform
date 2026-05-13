from flask import Blueprint, jsonify, request
import json
import logging

diff_bp = Blueprint('diff_bp', __name__, url_prefix='/api/diff')

# 获取logger
logger = logging.getLogger(__name__)

# 延迟导入，避免循环依赖
def get_compare_function():
    from utils.json_diff_utils import compare_json_data
    return compare_json_data


@diff_bp.route('/compare', methods=['POST'])
def compare_json():
    """
    JSON对比接口
    
    请求体:
    {
        "left": "JSON字符串1",
        "right": "JSON字符串2",
        "options": {
            "strict_mode": false,
            "ignore_case": false,
            "ignore_whitespace": false
        }
    }
    
    返回:
    {
        "success": true,
        "data": {
            "left_tree": {...},
            "right_tree": {...},
            "stats": {...}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求体不能为空'
            }), 400
        
        left_json = data.get('left', '')
        right_json = data.get('right', '')
        options = data.get('options', {})
        
        if not left_json or not right_json:
            return jsonify({
                'success': False,
                'message': '请提供左右两侧的JSON数据'
            }), 400
        
        # 解析JSON
        try:
            left_data = json.loads(left_json)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'message': f'左侧JSON格式错误: {str(e)}'
            }), 400
        
        try:
            right_data = json.loads(right_json)
        except json.JSONDecodeError as e:
            return jsonify({
                'success': False,
                'message': f'右侧JSON格式错误: {str(e)}'
            }), 400
        
        # 执行对比
        compare_func = get_compare_function()
        result = compare_func(left_data, right_data, options)
        
        logger.info(f'JSON对比成功: 相同={result["stats"]["same"]}, 不同={result["stats"]["different"]}')
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f'JSON对比失败: {e}')
        return jsonify({
            'success': False,
            'message': f'对比失败: {str(e)}'
        }), 500


@diff_bp.route('/format', methods=['POST'])
def format_json():
    """JSON格式化接口"""
    try:
        data = request.get_json()
        json_text = data.get('json', '')
        
        if not json_text:
            return jsonify({
                'success': False,
                'message': '请提供JSON数据'
            }), 400
        
        # 解析并格式化
        parsed = json.loads(json_text)
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'data': formatted
        })
        
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'message': f'JSON格式错误: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f'JSON格式化失败: {e}')
        return jsonify({
            'success': False,
            'message': f'格式化失败: {str(e)}'
        }), 500
