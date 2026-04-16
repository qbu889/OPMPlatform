"""
事件数据清洗路由
用于处理 ES 查询结果，提取 EVENT_FP 并生成推送消息
"""
import os
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

clean_event_bp = Blueprint('clean_event', __name__)

UPLOAD_FOLDER = os.path.join('uploads', 'clean_event')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@clean_event_bp.route('/api/clean-event/process', methods=['POST'])
def process_es_data():
    """
    处理 ES 查询结果，提取 EVENT_FP 并生成推送消息
    
    请求体格式：
    {
        "hits": {
            "hits": [
                {"_source": {"EVENT_FP": "xxx", "EVENT_TIME": "xxx"}},
                ...
            ]
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': '未提供数据'}), 400
        
        # 兼容两种数据格式：
        # 1. 前端 Vue 发送的格式：{"data": [{"EVENT_FP": "...", "EVENT_TIME": "..."}], "custom_event_time": "..."}
        # 2. 原始 ES 格式：{"hits": {"hits": [{"_source": {...}}]}}
        
        # 获取自定义事件时间（如果有）
        custom_event_time = data.get('custom_event_time')
        
        # 检测前端 Vue 发送的 data 字段
        if 'data' in data:
            # 前端格式：data 是数组
            hits_data = data.get('data', [])
            if not isinstance(hits_data, list):
                return jsonify({'success': False, 'message': 'data 字段必须是数组'}), 400
            
            # 直接遍历数组提取 EVENT_FP
            event_fp_map = {}
            for item in hits_data:
                event_fp = item.get('EVENT_FP')
                event_time = item.get('EVENT_TIME')
                
                # 如果指定了自定义事件时间，则覆盖
                if custom_event_time:
                    event_time = custom_event_time
                
                if event_fp and event_fp not in event_fp_map:
                    event_fp_map[event_fp] = event_time
            
            # 用于日志记录
            hits_count = len(hits_data)
        else:
            # 原始 ES 格式：从 hits.hits 中提取
            hits = data.get('hits', {}).get('hits', [])
            
            if not hits:
                return jsonify({'success': False, 'message': '未找到 hits 数据'}), 400
            
            # 提取 EVENT_FP 并去重
            event_fp_map = {}  # 使用字典保持顺序，key=EVENT_FP, value=EVENT_TIME
            
            for hit in hits:
                source = hit.get('_source', {})
                event_fp = source.get('EVENT_FP')
                event_time = source.get('EVENT_TIME')
                
                # 如果指定了自定义事件时间，则覆盖
                if custom_event_time:
                    event_time = custom_event_time
                
                if event_fp and event_fp not in event_fp_map:
                    event_fp_map[event_fp] = event_time
            
            # 用于日志记录
            hits_count = len(hits)
        
        # 生成推送消息
        push_messages = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for event_fp, event_time in event_fp_map.items():
            message = {
                "ACTIVE_STATUS": "3",
                "CFP0_CFP1_CFP2_CFP3": event_fp,
                "EVENT_TIME": event_time or current_time,
                "FP0_FP1_FP2_FP3": event_fp
            }
            push_messages.append(message)
        
        logger.info(f'成功处理 {hits_count} 条数据，生成 {len(push_messages)} 条推送消息')
        
        return jsonify({
            'success': True,
            'message': f'处理成功，共生成 {len(push_messages)} 条推送消息',
            'data': push_messages,
            'count': len(push_messages)
        })
    
    except Exception as e:
        logger.error(f'处理 ES 数据失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'处理失败: {str(e)}'}), 500


@clean_event_bp.route('/api/clean-event/upload', methods=['POST'])
def upload_json_file():
    """
    上传 JSON 文件并处理
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '未提供文件'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '仅支持 JSON 文件'}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        timestamp = int(datetime.now().timestamp())
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        logger.info(f'文件已保存: {filepath}')
        
        # 读取并解析 JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 删除临时文件
        os.remove(filepath)
        logger.info(f'临时文件已删除: {filepath}')
        
        # 处理数据
        hits = data.get('hits', {}).get('hits', [])
        
        if not hits:
            return jsonify({'success': False, 'message': 'JSON 文件中未找到 hits 数据'}), 400
        
        # 提取 EVENT_FP 并去重
        event_fp_map = {}
        
        for hit in hits:
            source = hit.get('_source', {})
            event_fp = source.get('EVENT_FP')
            event_time = source.get('EVENT_TIME')
            
            if event_fp and event_fp not in event_fp_map:
                event_fp_map[event_fp] = event_time
        
        # 生成推送消息
        push_messages = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for event_fp, event_time in event_fp_map.items():
            message = {
                "ACTIVE_STATUS": "3",
                "CFP0_CFP1_CFP2_CFP3": event_fp,
                "EVENT_TIME": event_time or current_time,
                "FP0_FP1_FP2_FP3": event_fp
            }
            push_messages.append(message)
        
        logger.info(f'成功处理上传文件，生成 {len(push_messages)} 条推送消息')
        
        return jsonify({
            'success': True,
            'message': f'上传并处理成功，共生成 {len(push_messages)} 条推送消息',
            'data': push_messages,
            'count': len(push_messages),
            'filename': filename
        })
    
    except json.JSONDecodeError as e:
        logger.error(f'JSON 解析失败: {str(e)}')
        return jsonify({'success': False, 'message': f'JSON 格式错误: {str(e)}'}), 400
    
    except Exception as e:
        logger.error(f'上传文件处理失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'处理失败: {str(e)}'}), 500

