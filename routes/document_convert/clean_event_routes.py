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
        "data": [
            {"EVENT_FP": "xxx", "EVENT_TIME": "xxx", "DISPATCH_INFO": {...}},
            ...
        ],
        "custom_event_time": "..." (可选)
    }
    """
    try:
        request_data = request.get_json()
        
        logger.info('='*80)
        logger.info('🔍 [DEBUG] /api/clean-event/process 接口被调用')
        logger.info(f'📥 接收到请求数据: {request_data}')
        logger.info('='*80)
        
        if not request_data:
            logger.error('❌ 请求数据为空')
            return jsonify({'success': False, 'message': '未提供数据'}), 400
        
        # 获取自定义事件时间（如果有）
        custom_event_time = request_data.get('custom_event_time')
        data = request_data.get('data')
        
        logger.info(f'⏰ custom_event_time: {custom_event_time}')
        logger.info(f'📊 data 类型: {type(data).__name__}, 是否为列表: {isinstance(data, list)}')
        
        if not data:
            logger.error('❌ 数据内容为空')
            return jsonify({'success': False, 'message': '缺少数据内容'}), 400
        
        # 如果是列表，遍历处理每个对象
        push_messages = []
        main_count = 0
        sub_count = 0
        
        if isinstance(data, list):
            logger.info(f'📋 处理列表，共 {len(data)} 个对象')
            for idx, item in enumerate(data):
                logger.info(f'\n--- 处理第 {idx+1} 条数据 ---')
                logger.info(f'🔑 完整数据键: {list(item.keys())}')
                
                event_fp = item.get('EVENT_FP')
                logger.info(f'🆔 EVENT_FP: {event_fp}')
                
                if event_fp:
                    # 优先使用自定义事件时间，否则使用数据中的 EVENT_TIME
                    if custom_event_time:
                        event_time = custom_event_time
                        logger.info(f'⏱️  使用自定义事件时间: {event_time}')
                    else:
                        event_time = item.get('EVENT_TIME', '')
                        logger.info(f'⏱️  使用数据中的 EVENT_TIME: {event_time}')
                    
                    # 判断主单还是子单
                    dispatch_info = item.get('DISPATCH_INFO', {})
                    logger.info(f'📦 DISPATCH_INFO: {dispatch_info}')
                    
                    dispatch_reason = dispatch_info.get('DISPATCH_REASON', '')
                    logger.info(f'📝 DISPATCH_REASON: "{dispatch_reason}"')
                    
                    is_main_order = (dispatch_reason == '工单派发成功')
                    order_type = '主单' if is_main_order else '子单'
                    
                    logger.info(f'✅ 判断结果: is_main_order={is_main_order}, order_type="{order_type}"')
                    
                    if is_main_order:
                        main_count += 1
                        logger.info(f'📈 主单计数 +1 = {main_count}')
                    else:
                        sub_count += 1
                        logger.info(f'📉 子单计数 +1 = {sub_count}')
                    
                    push_message = {
                        'ACTIVE_STATUS': '3',
                        'CFP0_CFP1_CFP2_CFP3': event_fp,
                        'EVENT_TIME': event_time,
                        'FP0_FP1_FP2_FP3': event_fp,
                        'ORDER_TYPE': order_type,  # 添加订单类型标识
                        'IS_MAIN_ORDER': is_main_order,  # 添加是否主单标识
                        'DISPATCH_REASON': dispatch_reason  # 添加派发原因
                    }
                    logger.info(f'💾 生成的推送消息: {push_message}')
                    push_messages.append(push_message)
                else:
                    logger.warning(f'⚠️  跳过第 {idx+1} 条数据：未找到 EVENT_FP 字段')
        else:
            # 单个对象
            logger.info(f'🔹 处理单个对象')
            logger.info(f'🔑 完整数据键: {list(data.keys())}')
            
            event_fp = data.get('EVENT_FP')
            logger.info(f'🆔 EVENT_FP: {event_fp}')
            
            if not event_fp:
                logger.error('❌ 未找到 EVENT_FP 字段')
                return jsonify({'success': False, 'message': '未找到 EVENT_FP 字段'}), 400
            
            # 优先使用自定义事件时间，否则使用数据中的 EVENT_TIME
            if custom_event_time:
                event_time = custom_event_time
                logger.info(f'⏱️  使用自定义事件时间: {event_time}')
            else:
                event_time = data.get('EVENT_TIME', '')
                logger.info(f'⏱️  使用数据中的 EVENT_TIME: {event_time}')
            
            # 判断主单还是子单
            dispatch_info = data.get('DISPATCH_INFO', {})
            logger.info(f'📦 DISPATCH_INFO: {dispatch_info}')
            
            dispatch_reason = dispatch_info.get('DISPATCH_REASON', '')
            logger.info(f'📝 DISPATCH_REASON: "{dispatch_reason}"')
            
            is_main_order = (dispatch_reason == '工单派发成功')
            order_type = '主单' if is_main_order else '子单'
            
            logger.info(f'✅ 判断结果: is_main_order={is_main_order}, order_type="{order_type}"')
            
            if is_main_order:
                main_count += 1
                logger.info(f'📈 主单计数 +1 = {main_count}')
            else:
                sub_count += 1
                logger.info(f'📉 子单计数 +1 = {sub_count}')
            
            push_message = {
                'ACTIVE_STATUS': '3',
                'CFP0_CFP1_CFP2_CFP3': event_fp,
                'EVENT_TIME': event_time,
                'FP0_FP1_FP2_FP3': event_fp,
                'ORDER_TYPE': order_type,
                'IS_MAIN_ORDER': is_main_order,
                'DISPATCH_REASON': dispatch_reason
            }
            logger.info(f'💾 生成的推送消息: {push_message}')
            push_messages.append(push_message)
        
        if not push_messages:
            logger.error('❌ 未找到有效的 EVENT_FP 字段')
            return jsonify({'success': False, 'message': '未找到有效的 EVENT_FP 字段'}), 400
        
        logger.info('\n' + '='*80)
        logger.info(f'✅ 处理完成！')
        logger.info(f'   - 总消息数: {len(push_messages)}')
        logger.info(f'   - 主单数量: {main_count}')
        logger.info(f'   - 子单数量: {sub_count}')
        logger.info(f'   - 返回数据结构: {list(push_messages[0].keys()) if push_messages else []}')
        logger.info('='*80)
        
        return jsonify({
            'success': True,
            'message': f'处理成功，共生成 {len(push_messages)} 条消息（{main_count} 主单，{sub_count} 子单）',
            'data': push_messages,
            'main_count': main_count,
            'sub_count': sub_count
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

