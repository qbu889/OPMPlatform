# routes/event_routes.py
from flask import Blueprint, request, render_template, jsonify
import re
import json
import logging

event_bp = Blueprint('event', __name__)
logger = logging.getLogger(__name__)

@event_bp.route('/clean-event-page', methods=['GET', 'POST'])
def clean_event_page():
    """事件数据清洗页面"""
    return render_template('fpa/clean_event.html')

@event_bp.route('/api/clean-event', methods=['POST'])
def clean_event():
    """处理事件数据清洗请求"""
    try:
        logger.info('========== 开始处理 /clean-event 请求 ==========')
        
        data = request.get_json()
        logger.info(f'接收到的原始数据: {data}')
        
        if not data:
            logger.error('缺少请求体数据')
            return jsonify({'error': '缺少必需参数'}), 400
            
        fp_value = data.get('fp_value')
        event_time = data.get('event_time')
        
        logger.info(f'fp_value: {fp_value}')
        logger.info(f'event_time: {event_time}')

        if not fp_value or not event_time:
            logger.error(f'缺少参数: fp_value={fp_value}, event_time={event_time}')
            return jsonify({'error': '缺少必需参数'}), 400

        # 修改FP值验证：只要求非空且长度不超过1000
        if not fp_value.strip() or len(fp_value) > 1000:
            logger.error(f'FP值验证失败: 长度={len(fp_value)}, 是否为空={not fp_value.strip()}')
            return jsonify({'error': 'FP值不能为空且长度不能超过1000个字符'}), 400

        # 时间格式验证，支持多种格式
        # 在 event_routes.py 中修改时间格式验证
        time_pattern1 = r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}$'           # YYYY/MM/DD HH:MM
        time_pattern2 = r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}$'            # YYYY-MM-DD HH:MM
        time_pattern3 = r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$'    # YYYY-MM-DD HH:MM:SS
        time_pattern4 = r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$'    # YYYY/MM/DD HH:MM:SS

        time_valid = (re.match(time_pattern1, event_time) or
            re.match(time_pattern2, event_time) or
            re.match(time_pattern3, event_time) or
            re.match(time_pattern4, event_time))
        
        logger.info(f'时间格式验证结果: {time_valid}')
        
        if not time_valid:
            logger.error(f'时间格式不正确: {event_time}')
            return jsonify({'error': '时间格式不正确，支持格式: YYYY/MM/DD HH:MM 或 YYYY-MM-DD HH:MM'}), 400

        logger.info('开始调用 clean_event_data 函数...')
        # 处理数据
        result = clean_event_data(fp_value, event_time)
        logger.info(f'清洗结果: {result}')
        logger.info('========== /clean-event 请求处理成功 ==========')
        return jsonify({'result': result})

    except Exception as e:
        logger.error(f'处理数据时发生错误: {str(e)}', exc_info=True)
        logger.error('========== /clean-event 请求处理失败 ==========')
        return jsonify({'error': f'处理数据时发生错误: {str(e)}'}), 500

@event_bp.route('/api/clean-event/process', methods=['POST'])
def process_es_data():
    """处理 ES 查询结果，提取 EVENT_FP 并生成推送消息"""
    try:
        request_data = request.get_json()
        
        logger.info('='*80)
        logger.info('🔍 [DEBUG] /api/clean-event/process 接口被调用')
        logger.info(f'📥 接收到请求数据: {request_data}')
        logger.info('='*80)
        
        if not request_data:
            logger.error('❌ 请求数据为空')
            return jsonify({'success': False, 'message': '缺少数据'}), 400
        
        # 提取自定义事件时间和实际数据
        custom_event_time = request_data.get('custom_event_time')
        data = request_data.get('data')
        
        logger.info(f'⏰ custom_event_time: {custom_event_time}')
        logger.info(f'📊 data 类型: {type(data).__name__}, 是否为列表: {isinstance(data, list)}')
        
        if not data:
            logger.error('❌ 数据内容为空')
            return jsonify({'success': False, 'message': '缺少数据内容'}), 400
        
        # 提取 EVENT_FP 字段（支持单个对象或数组）
        push_messages = []
        main_count = 0
        sub_count = 0
        
        # 如果是列表，遍历处理每个对象
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

@event_bp.route('/api/clean-event/parse-es', methods=['POST'])
def parse_es_json():
    """解析 ES JSON 数据，识别主单/子单并格式化"""
    try:
        request_data = request.get_json()
        
        if not request_data or 'json_data' not in request_data:
            return jsonify({'success': False, 'message': '缺少 JSON 数据'}), 400
        
        json_str = request_data['json_data']
        es_data = json.loads(json_str)
        
        # 提取 hits
        hits = es_data.get('hits', {}).get('hits', [])
        
        if not hits:
            return jsonify({'success': False, 'message': '未找到事件数据'}), 400
        
        result_list = []
        
        for hit in hits:
            source = hit.get('_source', {})
            dispatch_info = source.get('DISPATCH_INFO', {})
            dispatch_reason = dispatch_info.get('DISPATCH_REASON', '')
            
            # 判断主单还是子单
            is_main_order = (dispatch_reason == '工单派发成功')
            order_type = '主单' if is_main_order else '子单'
            
            # 提取关键字段
            event_data = {
                'order_type': order_type,
                'is_main_order': is_main_order,
                'dispatch_reason': dispatch_reason,
                'event_id': source.get('EVENT_ID'),
                'event_name': source.get('EVENT_NAME'),
                'equipment_name': source.get('EQUIPMENT_NAME'),
                'alarm_name': source.get('ALARM_NAME'),
                'event_time': source.get('EVENT_TIME'),
                'order_id': source.get('ORDER_ID'),
                'full_source': source  # 保留完整数据用于复制
            }
            
            result_list.append(event_data)
        
        return jsonify({
            'success': True,
            'data': result_list,
            'total': len(result_list),
            'main_count': sum(1 for item in result_list if item['is_main_order']),
            'sub_count': sum(1 for item in result_list if not item['is_main_order'])
        })
        
    except json.JSONDecodeError as e:
        logger.error(f'JSON 解析失败: {str(e)}')
        return jsonify({'success': False, 'message': f'JSON 格式错误: {str(e)}'}), 400
    except Exception as e:
        logger.error(f'解析 ES 数据失败: {str(e)}', exc_info=True)
        return jsonify({'success': False, 'message': f'处理失败: {str(e)}'}), 500

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