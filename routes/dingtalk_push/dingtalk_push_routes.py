"""
钉钉智能推送系统 - 后端路由
"""
import os
import json
import time
import logging
import requests
from datetime import datetime, timedelta
from functools import wraps
from cryptography.fernet import Fernet
from flask import Blueprint, request, jsonify, current_app
from jinja2 import Template, Environment, BaseLoader, sandbox

logger = logging.getLogger(__name__)

dingtalk_push_bp = Blueprint('dingtalk_push', __name__, url_prefix='/dingtalk-push')

# ==================== 工具函数 ====================

def get_fernet():
    """获取 Fernet 加密实例"""
    key = os.environ.get('WEBHOOK_ENCRYPTION_KEY')
    if not key:
        # 开发环境使用默认密钥（生产环境必须设置环境变量）
        key = 'dGVzdF9rZXlfZm9yX2Rldl9vbmx5XzEyMzQ1Njc4OTA='
    return Fernet(key.encode())

def encrypt_webhook(webhook_url):
    """加密 Webhook URL"""
    if not webhook_url:
        return None
    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(webhook_url.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Webhook 加密失败: {e}")
        raise

def decrypt_webhook(encrypted_webhook):
    """解密 Webhook URL"""
    if not encrypted_webhook:
        return None
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(encrypted_webhook.encode())
        return decrypted.decode()
    except Exception as e:
        # 兼容明文数据（迁移场景）
        logger.warning(f"Webhook 解密失败，尝试作为明文处理: {e}")
        return encrypted_webhook

def get_db_connection():
    """获取数据库连接"""
    from config import Config
    import mysql.connector
    
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.DINGTALK_PUSH_DB,
        charset='utf8mb4'
    )
    return conn

def dict_factory(cursor, row):
    """将查询结果转换为字典"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# ==================== 配置管理 API ====================

@dingtalk_push_bp.route('/configs', methods=['GET'])
def get_configs():
    """获取配置列表"""
    try:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 10, type=int)
        category = request.args.get('category')
        enabled = request.args.get('enabled')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询条件
        conditions = []
        params = []
        
        if category:
            conditions.append("category = %s")
            params.append(category)
        
        if enabled is not None:
            conditions.append("enabled = %s")
            params.append(enabled == 'true')
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM dingtalk_push_config WHERE {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 分页查询
        query = f"SELECT * FROM dingtalk_push_config WHERE {where_clause} ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([size, (page - 1) * size])
        cursor.execute(query, params)
        configs = cursor.fetchall()
        
        # 处理敏感信息
        for config in configs:
            config['webhook_url'] = '***'  # 隐藏 Webhook
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'list': configs,
                'total': total,
                'page': page,
                'size': size
            }
        })
    
    except Exception as e:
        logger.error(f"获取配置列表失败: {e}", exc_info=True)
        return jsonify({'success': False, 'msg': str(e)}), 500

@dingtalk_push_bp.route('/configs/<int:config_id>', methods=['GET'])
def get_config(config_id):
    """获取配置详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM dingtalk_push_config WHERE id = %s", (config_id,))
        config = cursor.fetchone()
        
        if not config:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '配置不存在'}), 404
        
        # 获取统计数据
        cursor.execute("""
            SELECT 
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count
            FROM dingtalk_push_history 
            WHERE config_id = %s
        """, (config_id,))
        stats = cursor.fetchone()
        
        # 计算成功率
        if stats['total_runs'] > 0:
            stats['success_rate'] = round(
                (stats['success_count'] / stats['total_runs']) * 100, 2
            )
        else:
            stats['success_rate'] = 0
        
        config['statistics'] = stats
        
        # 显示部分 Webhook URL
        if config['webhook_url']:
            decrypted = decrypt_webhook(config['webhook_url'])
            config['webhook_url_decrypted'] = decrypted or ''
            if decrypted and len(decrypted) > 20:
                config['webhook_url_display'] = decrypted[:30] + '***'
            else:
                config['webhook_url_display'] = '***'
        else:
            config['webhook_url_decrypted'] = ''
            config['webhook_url_display'] = ''
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': config})
    
    except Exception as e:
        logger.error(f"获取配置详情失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

@dingtalk_push_bp.route('/configs', methods=['POST'])
def create_config():
    """创建配置"""
    try:
        data = request.json
        
        # 验证必填字段
        required_fields = ['name', 'webhook_url', 'template_content', 'schedule_config']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'msg': f'缺少必填字段: {field}'}), 400
        
        # 加密 Webhook URL
        encrypted_webhook = encrypt_webhook(data['webhook_url'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO dingtalk_push_config 
            (name, description, webhook_url, at_mobiles, at_all, 
             message_type, template_content, data_source_config, schedule_config, 
             timezone, enabled, category, priority, max_retries, timeout_seconds)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            data['name'],
            data.get('description'),
            encrypted_webhook,
            json.dumps(data.get('at_mobiles', [])),
            data.get('at_all', False),
            data.get('message_type', 'markdown'),
            data['template_content'],
            json.dumps(data.get('data_source_config', {})),
            json.dumps(data['schedule_config']),
            data.get('timezone', 'Asia/Shanghai'),
            data.get('enabled', True),
            data.get('category', 'general'),
            data.get('priority', 0),
            data.get('max_retries', 3),
            data.get('timeout_seconds', 10)
        )
        
        cursor.execute(query, values)
        config_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"创建推送配置成功: ID={config_id}, Name={data['name']}")
        
        # 如果启用，注册定时任务
        if data.get('enabled', True):
            try:
                from flask import current_app
                scheduler = current_app.push_scheduler
                scheduler.register_job(config_id, data['schedule_config'])
            except Exception as e:
                logger.warning(f"注册定时任务失败: {e}")
        
        return jsonify({
            'success': True,
            'msg': '配置创建成功',
            'data': {'id': config_id}
        }), 201
    
    except Exception as e:
        logger.error(f"创建配置失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

@dingtalk_push_bp.route('/configs/<int:config_id>', methods=['PUT'])
def update_config(config_id):
    """更新配置"""
    try:
        data = request.json
        logger.info(f"收到更新请求 - ID={config_id}, 数据: {data}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查配置是否存在
        cursor.execute("SELECT id FROM dingtalk_push_config WHERE id = %s", (config_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '配置不存在'}), 404
        
        # 构建更新语句
        update_fields = []
        values = []
        
        for field in ['name', 'description', 
                      'message_type', 'template_content', 'timezone', 
                      'category', 'max_retries', 'timeout_seconds']:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])
                logger.debug(f"添加字段: {field} = {data[field]}")
        
        # 特殊处理布尔值和 JSON 字段
        if 'enabled' in data:
            enabled_value = 1 if data['enabled'] else 0
            update_fields.append("enabled = %s")
            values.append(enabled_value)
            logger.info(f"处理 enabled 字段: 原始值={data['enabled']}, 转换后={enabled_value}")
        
        if 'at_mobiles' in data:
            update_fields.append("at_mobiles = %s")
            values.append(json.dumps(data['at_mobiles']))
        
        if 'at_all' in data:
            at_all_value = 1 if data['at_all'] else 0
            update_fields.append("at_all = %s")
            values.append(at_all_value)
            logger.debug(f"处理 at_all 字段: 原始值={data['at_all']}, 转换后={at_all_value}")
        
        if 'data_source_config' in data:
            update_fields.append("data_source_config = %s")
            values.append(json.dumps(data['data_source_config']))
        
        if 'schedule_config' in data:
            update_fields.append("schedule_config = %s")
            values.append(json.dumps(data['schedule_config']))
        
        # 如果更新了 webhook_url，需要加密
        if 'webhook_url' in data:
            update_fields.append("webhook_url = %s")
            values.append(encrypt_webhook(data['webhook_url']))
            logger.debug(f"Webhook URL 已加密")
        
        if not update_fields:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '没有要更新的字段'}), 400
        
        values.append(config_id)
        query = f"UPDATE dingtalk_push_config SET {', '.join(update_fields)} WHERE id = %s"
        logger.info(f"执行 SQL: {query}")
        logger.info(f"SQL 参数: {values}")
        
        cursor.execute(query, values)
        conn.commit()
        
        logger.info(f"影响行数: {cursor.rowcount}")
        
        # 验证更新结果
        cursor.execute("SELECT enabled FROM dingtalk_push_config WHERE id = %s", (config_id,))
        result = cursor.fetchone()
        if result:
            logger.info(f"更新后数据库中的 enabled 值: {result[0]}")
        
        cursor.close()
        conn.close()
        
        logger.info(f"更新推送配置成功: ID={config_id}")
        
        # 如果更新了调度配置或启用状态，重新加载任务
        if 'schedule_config' in data or 'enabled' in data:
            try:
                from flask import current_app
                scheduler = current_app.push_scheduler
                scheduler.reload_config(config_id)
            except Exception as e:
                logger.warning(f"重新加载定时任务失败: {e}")
        
        return jsonify({'success': True, 'msg': '配置更新成功'})
    
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

@dingtalk_push_bp.route('/configs/<int:config_id>', methods=['DELETE'])
def delete_config(config_id):
    """删除配置"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM dingtalk_push_config WHERE id = %s", (config_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '配置不存在'}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"删除推送配置成功: ID={config_id}")
        
        return jsonify({'success': True, 'msg': '配置删除成功'})
    
    except Exception as e:
        logger.error(f"删除配置失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

@dingtalk_push_bp.route('/configs/<int:config_id>/toggle', methods=['PATCH'])
def toggle_config(config_id):
    """启用/禁用配置"""
    try:
        data = request.json
        enabled = data.get('enabled')
        
        if enabled is None:
            return jsonify({'success': False, 'msg': '请指定 enabled 值'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查配置是否存在
        cursor.execute("SELECT id, enabled FROM dingtalk_push_config WHERE id = %s", (config_id,))
        existing = cursor.fetchone()
        
        if not existing:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '配置不存在'}), 404
        
        # 执行更新
        cursor.execute(
            "UPDATE dingtalk_push_config SET enabled = %s WHERE id = %s",
            (enabled, config_id)
        )
        conn.commit()
        
        status = '启用' if enabled else '禁用'
        logger.info(f"{status}推送配置: ID={config_id}")
        
        # 根据启用状态注册或移除定时任务
        try:
            from flask import current_app
            scheduler = current_app.push_scheduler
            
            if enabled:
                # 重新加载并注册任务
                scheduler.reload_config(config_id)
            else:
                # 移除任务
                scheduler.remove_job(config_id)
        except Exception as e:
            logger.warning(f"更新定时任务失败: {e}")
        
        return jsonify({'success': True, 'msg': f'配置已{status}'})
    
    except Exception as e:
        logger.error(f"切换配置状态失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

# ==================== Webhook 测试 API ====================

@dingtalk_push_bp.route('/test-webhook', methods=['POST'])
def test_webhook():
    """测试 Webhook 连接"""
    try:
        data = request.json
        webhook_url = data.get('webhook_url')
        secret_key = data.get('secret_key')
        
        if not webhook_url:
            return jsonify({'success': False, 'msg': '请提供 Webhook URL'}), 400
        
        # 发送测试消息
        test_message = {
            "msgtype": "text",
            "text": {
                "content": "🔔 钉钉推送系统 - Webhook 连接测试成功！"
            }
        }
        
        start_time = time.time()
        response = requests.post(
            webhook_url,
            json=test_message,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        result = response.json()
        
        if result.get('errcode') == 0:
            return jsonify({
                'success': True,
                'msg': 'Webhook 连接测试成功',
                'data': {
                    'response_time_ms': elapsed_ms,
                    'test_message_sent': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'msg': f"钉钉 API 返回错误: {result.get('errmsg')}",
                'data': {
                    'response_time_ms': elapsed_ms,
                    'error_code': result.get('errcode')
                }
            }), 400
    
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'msg': '请求超时'}), 408
    except Exception as e:
        logger.error(f"Webhook 测试失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

# ==================== 模板预览 API ====================

@dingtalk_push_bp.route('/preview', methods=['POST'])
def preview_template():
    """预览消息效果"""
    try:
        data = request.json
        message_type = data.get('message_type', 'markdown')
        template_content = data.get('template_content', '')
        sample_data = data.get('sample_data', {})
        
        # 渲染模板
        env = sandbox.SandboxedEnvironment(loader=BaseLoader())
        template = env.from_string(template_content)
        rendered_content = template.render(**sample_data)
        
        # 构建消息 JSON
        message_json = build_dingtalk_message(
            message_type=message_type,
            content=rendered_content,
            at_mobiles=data.get('at_mobiles', []),
            at_all=data.get('at_all', False)
        )
        
        # 提取使用的变量
        import re
        variables_used = re.findall(r'\{\{\s*(\w+)\s*\}\}', template_content)
        
        return jsonify({
            'success': True,
            'data': {
                'rendered_content': rendered_content,
                'message_json': message_json,
                'variables_used': list(set(variables_used)),
                'warnings': []
            }
        })
    
    except Exception as e:
        logger.error(f"模板预览失败: {e}")
        return jsonify({'success': False, 'msg': f'模板渲染失败: {str(e)}'}), 400

# ==================== 手动推送 API ====================

@dingtalk_push_bp.route('/configs/<int:config_id>/execute', methods=['POST'])
def execute_push(config_id):
    """立即执行推送"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取配置
        cursor.execute("SELECT * FROM dingtalk_push_config WHERE id = %s", (config_id,))
        config = cursor.fetchone()
        
        if not config:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '配置不存在'}), 404
        
        if not config['enabled']:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '配置已禁用'}), 400
        
        cursor.close()
        conn.close()
        
        # 异步执行推送
        import threading
        thread = threading.Thread(target=execute_push_task, args=(config,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'msg': '推送任务已提交',
            'data': {
                'estimated_time': '即将执行'
            }
        })
    
    except Exception as e:
        logger.error(f"提交推送任务失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

def execute_push_task(config):
    """执行推送任务（后台线程）"""
    try:
        config_id = config['id']
        trigger_time = datetime.now()
        
        # 创建历史记录
        history_id = create_push_history(config_id, trigger_time)
        
        # 记录开始日志
        add_push_log(config_id, history_id, 'INFO', '开始执行推送')
        
        start_time = time.time()
        
        # 获取数据源
        data = fetch_data_source(config)
        
        # 渲染模板
        rendered_content = render_template(config['template_content'], data)
        
        # 构建消息
        at_mobiles = json.loads(config['at_mobiles']) if config['at_mobiles'] else []
        message_json = build_dingtalk_message(
            message_type=config['message_type'],
            content=rendered_content,
            at_mobiles=at_mobiles,
            at_all=config['at_all']
        )
        
        # 发送消息
        webhook_url = decrypt_webhook(config['webhook_url'])
        timeout = config['timeout_seconds'] or 10
        max_retries = config['max_retries'] or 3
        
        success = False
        error_msg = None
        retry_count = 0
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    add_push_log(config_id, history_id, 'WARNING', f'第 {attempt} 次重试')
                    retry_count = attempt
                
                response = requests.post(
                    webhook_url,
                    json=message_json,
                    headers={'Content-Type': 'application/json'},
                    timeout=timeout
                )
                
                result = response.json()
                
                if result.get('errcode') == 0:
                    success = True
                    add_push_log(config_id, history_id, 'INFO', f'推送成功: {result}')
                    break
                else:
                    error_msg = result.get('errmsg', '未知错误')
                    add_push_log(config_id, history_id, 'ERROR', f'推送失败: {error_msg}')
            
            except Exception as e:
                error_msg = str(e)
                add_push_log(config_id, history_id, 'ERROR', f'请求异常: {error_msg}')
                
                if attempt < max_retries:
                    delay = min(1 * (2 ** attempt), 60)  # 指数退避
                    time.sleep(delay)
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 更新历史记录
        update_push_history(
            history_id,
            status='success' if success else 'failed',
            response_data=result if success else None,
            error_message=error_msg,
            retry_count=retry_count,
            execution_duration_ms=elapsed_ms,
            message_snapshot=message_json
        )
        
        status = '成功' if success else '失败'
        add_push_log(config_id, history_id, 'INFO' if success else 'ERROR', 
                    f'推送任务完成: 耗时 {elapsed_ms}ms, 状态: {status}')
        
    except Exception as e:
        logger.error(f"执行推送任务失败: {e}")
        if 'history_id' in locals():
            update_push_history(history_id, status='failed', error_message=str(e))
            add_push_log(config_id, history_id, 'ERROR', f'任务执行异常: {str(e)}')

# ==================== 历史记录 API ====================

@dingtalk_push_bp.route('/history', methods=['GET'])
def get_push_history():
    """获取推送历史"""
    try:
        config_id = request.args.get('config_id', type=int)
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 20, type=int)
        status = request.args.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = "SELECT * FROM dingtalk_push_history WHERE 1=1"
        params = []
        
        if config_id:
            query += " AND config_id = %s"
            params.append(config_id)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as t"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # 分页查询
        query += " ORDER BY triggered_at DESC LIMIT %s OFFSET %s"
        params.extend([size, (page - 1) * size])
        cursor.execute(query, params)
        history_list = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'list': history_list,
                'total': total,
                'page': page,
                'size': size
            }
        })
    
    except Exception as e:
        logger.error(f"获取推送历史失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

@dingtalk_push_bp.route('/history/<int:history_id>', methods=['GET'])
def get_push_history_detail(history_id):
    """获取推送详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 获取历史记录
        cursor.execute("SELECT * FROM dingtalk_push_history WHERE id = %s", (history_id,))
        history = cursor.fetchone()
        
        if not history:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'msg': '历史记录不存在'}), 404
        
        # 获取关联日志
        cursor.execute(
            "SELECT * FROM dingtalk_push_log WHERE history_id = %s ORDER BY created_at ASC",
            (history_id,)
        )
        logs = cursor.fetchall()
        
        history['logs'] = logs
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': history})
    
    except Exception as e:
        logger.error(f"获取推送详情失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

# ==================== 统计分析 API ====================

@dingtalk_push_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        config_id = request.args.get('config_id', type=int)
        period = request.args.get('period', '7d')
        
        # 计算时间范围
        days_map = {'7d': 7, '30d': 30, '90d': 90}
        days = days_map.get(period, 7)
        start_date = datetime.now() - timedelta(days=days)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 基础统计
        query = """
            SELECT 
                COUNT(*) as total_runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
                AVG(execution_duration_ms) as avg_execution_time_ms
            FROM dingtalk_push_history 
            WHERE triggered_at >= %s
        """
        params = [start_date]
        
        if config_id:
            query += " AND config_id = %s"
            params.append(config_id)
        
        cursor.execute(query, params)
        stats = cursor.fetchone()
        
        # 计算成功率
        if stats['total_runs'] > 0:
            stats['success_rate'] = round(
                (stats['success_count'] / stats['total_runs']) * 100, 2
            )
        else:
            stats['success_rate'] = 0
        
        # 趋势数据
        trend_query = """
            SELECT 
                DATE(triggered_at) as date,
                COUNT(*) as runs,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success
            FROM dingtalk_push_history 
            WHERE triggered_at >= %s
        """
        trend_params = [start_date]
        
        if config_id:
            trend_query += " AND config_id = %s"
            trend_params.append(config_id)
        
        trend_query += " GROUP BY DATE(triggered_at) ORDER BY date ASC"
        
        cursor.execute(trend_query, trend_params)
        trend = cursor.fetchall()
        
        stats['trend'] = trend
        stats['period'] = period
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': stats})
    
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500

# ==================== 辅助函数 ====================

def create_push_history(config_id, trigger_time, trigger_type='manual'):
    """创建推送历史记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO dingtalk_push_history 
           (config_id, triggered_at, trigger_type, status) 
           VALUES (%s, %s, %s, 'pending')""",
        (config_id, trigger_time, trigger_type)
    )
    
    history_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    
    return history_id

def update_push_history(history_id, **kwargs):
    """更新推送历史记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 字段映射：代码字段名 -> 数据库实际字段名
    field_mapping = {
        'response_data': 'message_content',
        'message_snapshot': 'message_content',
        'execution_duration_ms': 'execution_duration_ms',
        'error_message': 'error_message',
        'retry_count': 'retry_count',
        'status': 'status',
        'completed_at': 'completed_at'
    }
    
    fields = []
    values = []
    
    for key, value in kwargs.items():
        db_field = field_mapping.get(key, key)
        # JSON 字段需要序列化
        if key in ['response_data', 'message_snapshot']:
            fields.append(f"{db_field} = %s")
            values.append(json.dumps(value) if value else None)
        else:
            fields.append(f"{db_field} = %s")
            values.append(value)
    
    values.append(history_id)
    query = f"UPDATE dingtalk_push_history SET {', '.join(fields)} WHERE id = %s"
    
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def add_push_log(config_id, history_id, log_level, message, context_data=None):
    """添加推送日志"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO dingtalk_push_log 
               (history_id, step, status, details, duration_ms) 
               VALUES (%s, %s, %s, %s, %s)""",
            (history_id, log_level, 'success', message, None)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"添加推送日志失败: {e}")

def fetch_data_source(config):
    """获取数据源"""
    data_source_config = json.loads(config['data_source_config']) if config['data_source_config'] else {}
    source_type = data_source_config.get('type', 'static')
    
    if source_type == 'static':
        return data_source_config.get('data', {})
    
    elif source_type == 'api':
        api_config = data_source_config.get('config', {})
        url = api_config.get('url')
        method = api_config.get('method', 'GET')
        params = api_config.get('params', {})
        headers = api_config.get('headers', {})
        timeout = api_config.get('timeout', 5)
        
        response = requests.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        
        transform_func = api_config.get('transform')
        data = response.json()
        
        if transform_func:
            # TODO: 实现数据转换逻辑
            pass
        
        return data
    
    elif source_type == 'sql':
        sql_config = data_source_config.get('config', {})
        query = sql_config.get('query')
        params = sql_config.get('params', {})
        database = sql_config.get('database', 'schedule_db')
        
        if not query:
            raise ValueError("SQL 查询不能为空")
        
        try:
            from config import Config
            import mysql.connector
            
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=database,
                charset='utf8mb4'
            )
            
            cursor = conn.cursor(dictionary=True)
            
            # 参数化查询（防止 SQL 注入）
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {'results': results, 'count': len(results)}
        
        except Exception as e:
            logger.error(f"SQL 查询失败: {e}")
            raise ValueError(f"SQL 查询执行失败: {str(e)}")
    
    return {}

def render_template(template_content, data):
    """渲染 Jinja2 模板"""
    env = sandbox.SandboxedEnvironment(loader=BaseLoader())
    
    # 添加内置函数和变量
    def format_datetime(dt, fmt='%Y-%m-%d %H:%M'):
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.strftime(fmt)
    
    # 预格式化当前时间字符串（用于直接引用 {{ now }}）
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    now_dt = datetime.now()
    
    env.globals['now'] = now_str  # 默认返回格式化字符串
    env.globals['now_datetime'] = now_dt  # 返回 datetime 对象
    env.filters['format_datetime'] = format_datetime
    
    template = env.from_string(template_content)
    return template.render(**data)

def build_dingtalk_message(message_type, content, at_mobiles=None, at_all=False):
    """构建钉钉消息"""
    if at_mobiles is None:
        at_mobiles = []
    
    base_at = {
        "atMobiles": at_mobiles,
        "isAtAll": at_all
    }
    
    if message_type == 'markdown':
        return {
            "msgtype": "markdown",
            "markdown": {
                "title": "推送消息",
                "text": content
            },
            "at": base_at
        }
    
    elif message_type == 'actionCard':
        return {
            "msgtype": "actionCard",
            "actionCard": {
                "title": "推送消息",
                "text": content,
                "btnOrientation": "0",
                "btns": []
            },
            "at": base_at
        }
    
    elif message_type == 'text':
        return {
            "msgtype": "text",
            "text": {
                "content": content
            },
            "at": base_at
        }
    
    else:
        raise ValueError(f"不支持的消息类型: {message_type}")
