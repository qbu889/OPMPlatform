"""
户型设计系统 - 后端路由
========================
提供户型数据的增删改查接口，支持前端动态配置房间信息。
"""
import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

house_design_bp = Blueprint('house_design', __name__, url_prefix='/house-design')

# 数据存储文件路径（默认在项目根目录）
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
DATA_FILE = os.path.join(_DATA_DIR, 'house_design_data.json')


def _ensure_data_file():
    """确保数据文件存在，不存在则创建默认数据"""
    os.makedirs(_DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        default_data = {
            "version": 1,
            "updated_at": datetime.now().isoformat(),
            "cells": [
                {"name": "主卧", "desc": "父亲 & 母亲", "color": "#e0f2fe", "text": "#0369a1"},
                {"name": "次卧", "desc": "正北方位", "color": "#f3f4f6", "text": "#374151"},
                {"name": "客厅", "desc": "东北方位", "color": "#fef9c3", "text": "#a16207"},
                {"name": "书房", "desc": "西中方位", "color": "#e0e7ff", "text": "#3730a3"},
                {"name": "中心", "desc": "核心区域", "color": "#ffffff", "text": "#9ca3af"},
                {"name": "长子房", "desc": "正东方位", "color": "#dcfce7", "text": "#15803d"},
                {"name": "次卧", "desc": "西南方位", "color": "#f3f4f6", "text": "#374151"},
                {"name": "卫生间", "desc": "正南方位", "color": "#fee2e2", "text": "#b91c1c"},
                {"name": "长女房", "desc": "东南方位", "color": "#fce7f3", "text": "#be185d"}
            ]
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)


# ==================== 获取户型数据 ====================

@house_design_bp.route('/data', methods=['GET'])
def get_house_data():
    """获取户型配置数据
    
    返回所有房间的配置信息，供前端渲染使用。
    
    Response:
        {
            "success": true,
            "data": {
                "cells": [...],
                "updated_at": "..."
            }
        }
    """
    try:
        _ensure_data_file()
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        logger.error(f"获取户型数据失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


# ==================== 更新户型数据 ====================

@house_design_bp.route('/data', methods=['PUT'])
def update_house_data():
    """更新户型配置数据
    
    接收前端提交的房间配置，保存到文件。
    
    Request Body:
        {
            "cells": [
                {"name": "主卧", "desc": "...", "color": "#...", "text": "#..."},
                ...
            ]
        }
    
    Response:
        { "success": true, "message": "更新成功" }
    """
    try:
        body = request.get_json()
        if not body or 'cells' not in body:
            return jsonify({'success': False, 'msg': '缺少 cells 数据'}), 400
        
        cells = body['cells']
        if not isinstance(cells, list) or len(cells) != 9:
            return jsonify({'success': False, 'msg': 'cells 必须是包含 9 个元素的数组'}), 400
        
        # 读取现有数据，保留 version
        _ensure_data_file()
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        
        existing['cells'] = cells
        existing['updated_at'] = datetime.now().isoformat()
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        logger.info(f"户型数据已更新，共 {len(cells)} 个房间")
        return jsonify({'success': True, 'message': '更新成功', 'updated_at': existing['updated_at']})
    
    except Exception as e:
        logger.error(f"更新户型数据失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


# ==================== 更新单个房间 ====================

@house_design_bp.route('/data/<int:index>', methods=['PATCH'])
def update_single_cell(index):
    """更新单个房间的配置
    
    只更新指定索引位置的房间信息。
    
    URL: /house-design/data/0
    
    Request Body:
        { "name": "主卧", "desc": "...", "color": "#...", "text": "#" }
    
    Response:
        { "success": true, "message": "更新成功" }
    """
    try:
        if index < 0 or index > 8:
            return jsonify({'success': False, 'msg': '索引必须在 0-8 之间'}), 400
        
        body = request.get_json()
        if not body:
            return jsonify({'success': False, 'msg': '缺少请求体'}), 400
        
        _ensure_data_file()
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 只更新提供的字段
        cell = data['cells'][index]
        for key in ['name', 'desc', 'color', 'text']:
            if key in body:
                cell[key] = body[key]
        
        data['updated_at'] = datetime.now().isoformat()
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '更新成功', 'cell': cell})
    
    except Exception as e:
        logger.error(f"更新单个房间失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


# ==================== 重置为默认数据 ====================

@house_design_bp.route('/data/reset', methods=['POST'])
def reset_house_data():
    """重置户型数据为默认值
    
    Response:
        { "success": true, "message": "已重置为默认数据" }
    """
    try:
        default_data = {
            "version": 1,
            "updated_at": datetime.now().isoformat(),
            "cells": [
                {"name": "主卧", "desc": "父亲 & 母亲", "color": "#e0f2fe", "text": "#0369a1"},
                {"name": "次卧", "desc": "正北方位", "color": "#f3f4f6", "text": "#374151"},
                {"name": "客厅", "desc": "东北方位", "color": "#fef9c3", "text": "#a16207"},
                {"name": "书房", "desc": "西中方位", "color": "#e0e7ff", "text": "#3730a3"},
                {"name": "中心", "desc": "核心区域", "color": "#ffffff", "text": "#9ca3af"},
                {"name": "长子房", "desc": "正东方位", "color": "#dcfce7", "text": "#15803d"},
                {"name": "次卧", "desc": "西南方位", "color": "#f3f4f6", "text": "#374151"},
                {"name": "卫生间", "desc": "正南方位", "color": "#fee2e2", "text": "#b91c1c"},
                {"name": "长女房", "desc": "东南方位", "color": "#fce7f3", "text": "#be185d"}
            ]
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '已重置为默认数据'})
    
    except Exception as e:
        logger.error(f"重置户型数据失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500
