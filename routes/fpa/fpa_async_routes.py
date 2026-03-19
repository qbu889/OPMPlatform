# 异步任务相关路由（追加到 fpa_generator_routes.py 末尾）
import os
import time
import uuid
from pathlib import Path
from datetime import datetime
from flask import jsonify, current_app, request
import mysql.connector
from utils.task_manager import get_task_manager
import logging

# 注意：这里可以安全地导入 fpa_generator_bp，因为是在 app.py 中统一导入
# 不会导致循环依赖
from .fpa_generator_routes import fpa_generator_bp

logger = logging.getLogger(__name__)


def get_db_connection():
    """获取数据库连接"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '12345678'),
        database=os.getenv('DB_NAME', 'knowledge_base')
    )


def init_export_history_table():
    """初始化导出历史表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fpa_export_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                task_id VARCHAR(50) UNIQUE NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                output_filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT,
                function_point_count INT,
                status ENUM('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
                progress INT DEFAULT 0,
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                INDEX idx_task_id (task_id),
                INDEX idx_created_at (created_at),
                INDEX idx_status (status)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("[EXPORT_HISTORY] 导出历史表初始化成功")
    except Exception as e:
        logger.error(f"[EXPORT_HISTORY] 初始化导出历史表失败：{e}")


@fpa_generator_bp.route('/api/generate-async', methods=['POST'])
def generate_fpa_async():
    """
    异步生成 FPA 预估表
    不阻塞请求，返回 task_id，前端轮询查询进度
    """
    try:
        if 'requirement_file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未选择上传文件'
            }), 400
        
        file = request.files['requirement_file']
        if file.filename == '' or not file.filename.endswith('.md'):
            return jsonify({
                'success': False,
                'message': '请上传有效的 Markdown 文件'
            }), 400
        
        # 生成任务 ID
        task_id = f"fpa_{uuid.uuid4().hex[:12]}"
        
        # 保存临时文件（使用 task_id 确保唯一性）
        timestamp = int(time.time() * 1000)
        upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / "fpa_input"
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = Path(file.filename).stem
        # 使用 task_id + 时间戳确保文件名绝对唯一
        temp_md_path = upload_dir / f"{filename}_{task_id}_{timestamp}.md"
        file.save(temp_md_path)
        
        # 创建异步任务
        task_manager = get_task_manager()
        task_manager.create_task(
            task_id,
            generate_fpa_task,
            str(temp_md_path),
            filename,
            timestamp
        )
        
        # 记录到导出历史表
        init_export_history_table()
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO fpa_export_history 
                (task_id, original_filename, output_filename, file_path, status, progress, message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (task_id, file.filename, '', str(temp_md_path), 'PENDING', 0, '任务已创建'))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.warning(f"记录导出历史失败：{e}")
        
        logger.info(f"[ASYNC] 创建 FPA 生成任务：{task_id}")
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '任务已创建，正在后台处理'
        })
        
    except Exception as e:
        logger.error(f"创建异步任务失败：{e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@fpa_generator_bp.route('/api/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """
    查询任务状态和进度
    """
    task_manager = get_task_manager()
    task_info = task_manager.get_task_status(task_id)
    
    if not task_info:
        # 尝试从数据库查询历史任务
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute('''
                SELECT * FROM fpa_export_history 
                WHERE task_id = %s 
                ORDER BY created_at DESC LIMIT 1
            ''', (task_id,))
            history = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if history:
                return jsonify({
                    'success': True,
                    'data': {
                        'id': history['task_id'],
                        'status': history['status'],
                        'progress': history['progress'],
                        'message': history['message'],
                        'created_at': str(history['created_at']),
                        'completed_at': str(history['completed_at']) if history['completed_at'] else None,
                        'output_filename': history['output_filename'],
                        'file_size': history['file_size'],
                        'function_point_count': history['function_point_count'],
                        'is_history': True
                    }
                })
        except Exception as e:
            logger.error(f"查询历史任务失败：{e}")
        
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': task_info
    })


@fpa_generator_bp.route('/api/task-cancel/<task_id>', methods=['POST'])
def cancel_task(task_id):
    """
    取消/停止任务
    """
    try:
        task_manager = get_task_manager()
        task_info = task_manager.get_task_status(task_id)
        
        if not task_info:
            # 任务不存在，可能是已经完成或被删除
            # 检查数据库中是否存在
            conn = None
            cursor = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT status FROM fpa_export_history WHERE task_id = %s', (task_id,))
                db_record = cursor.fetchone()
                
                if db_record:
                    # 数据库中存在，但不是 RUNNING 状态
                    if db_record[0] != 'RUNNING':
                        cursor.close()
                        conn.close()
                        return jsonify({
                            'success': False,
                            'message': f'任务已结束，当前状态：{db_record[0]}'
                        }), 400
                    
                    # 数据库中存在且是 RUNNING 状态，但任务管理器中没有
                    # 说明任务可能异常退出，将状态更新为 FAILED
                    cursor.execute('''
                        UPDATE fpa_export_history 
                        SET status = 'FAILED',
                            message = '任务异常终止（任务管理器中不存在）',
                            completed_at = NOW()
                        WHERE task_id = %s
                    ''', (task_id,))
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    logger.warning(f"[TASK_CANCEL] 任务 {task_id} 在任务管理器中不存在，已标记为 FAILED")
                    
                    return jsonify({
                        'success': True,
                        'message': '任务已停止（任务异常终止）'
                    })
                else:
                    # 数据库中也不存在
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()
                    return jsonify({
                        'success': False,
                        'message': '任务不存在'
                    }), 404
            except Exception as e:
                logger.error(f"查询数据库失败：{e}", exc_info=True)
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                raise
        
        if task_info['status'] in ['COMPLETED', 'FAILED', 'CANCELLED']:
            return jsonify({
                'success': False,
                'message': f'任务已结束，当前状态：{task_info["status"]}'
            }), 400
        
        # 更新任务状态为 CANCELLED
        task_manager._update_task_status(task_id, 'CANCELLED', 0, '任务已被用户取消')
        
        # 更新导出历史表
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE fpa_export_history 
                SET status = 'CANCELLED',
                    message = '任务被用户取消',
                    completed_at = NOW()
                WHERE task_id = %s
            ''', (task_id,))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.warning(f"更新导出历史失败：{e}")
        
        logger.info(f"[TASK_CANCEL] 任务已取消：{task_id}")
        
        return jsonify({
            'success': True,
            'message': '任务已停止'
        })
        
    except Exception as e:
        logger.error(f"取消任务失败：{e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'服务器内部错误：{str(e)}'
        }), 500


@fpa_generator_bp.route('/api/export-history', methods=['GET'])
def get_export_history():
    """
    查询导出历史记录
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 查询总数
        cursor.execute('SELECT COUNT(*) as total FROM fpa_export_history')
        total = cursor.fetchone()['total']
        
        # 分页查询
        cursor.execute('''
            SELECT * FROM fpa_export_history 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        ''', (page_size, offset))
        
        history_list = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'list': history_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
        
    except Exception as e:
        logger.error(f"查询导出历史失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def update_task_progress(task_id, progress, message):
    """
    更新任务进度到数据库
    
    Args:
        task_id: 任务 ID
        progress: 进度百分比 (0-100)
        message: 进度消息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先查询当前状态
        cursor.execute('SELECT status FROM fpa_export_history WHERE task_id = %s', (task_id,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return
        
        current_status = result[0]
        
        # 如果任务已经结束（COMPLETED/FAILED/CANCELLED），不再更新状态
        if current_status in ['COMPLETED', 'FAILED', 'CANCELLED']:
            cursor.close()
            conn.close()
            return
        
        # 只在进度小于 100 时设置为 RUNNING
        new_status = 'RUNNING' if progress < 100 else current_status
        
        cursor.execute('''
            UPDATE fpa_export_history 
            SET progress = %s,
                message = %s,
                status = %s
            WHERE task_id = %s
        ''', (progress, message, new_status, task_id))
        conn.commit()
        cursor.close()
        conn.close()
        logger.debug(f"[UPDATE_PROGRESS] task_id={task_id}, progress={progress}, message={message}, status={new_status}")
    except Exception as e:
        logger.error(f"更新任务进度失败：{e}")


@fpa_generator_bp.route('/api/export-history/<task_id>', methods=['DELETE'])
def delete_export_history(task_id):
    """
    删除导出历史记录
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先查询记录是否存在
        cursor.execute('SELECT id, status FROM fpa_export_history WHERE task_id = %s', (task_id,))
        record = cursor.fetchone()
        
        if not record:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '记录不存在'
            }), 404
        
        # 运行中的任务不允许删除
        if record[1] == 'RUNNING':
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '运行中的任务无法删除'
            }), 400
        
        # 删除记录
        cursor.execute('DELETE FROM fpa_export_history WHERE task_id = %s', (task_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info(f"[DELETE_HISTORY] 删除导出历史记录：{task_id}")
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除导出历史失败：{e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def generate_fpa_task(temp_md_path: str, filename: str, timestamp: int, 
                     task_id: str = None, progress_callback=None, **kwargs):
    """
    FPA 生成任务（异步执行）
    
    Args:
        temp_md_path: 临时 Markdown 文件路径
        filename: 文件名
        timestamp: 时间戳
        task_id: 任务 ID
        progress_callback: 进度回调函数 (task_id, progress, message, log_entry)
    """
    # 包装进度回调函数，使其同时更新到数据库
    def wrapped_progress_callback(task_id, progress, message, log_entry):
        # 调用原始回调（用于前端实时显示）
        if progress_callback:
            progress_callback(task_id, progress, message, log_entry)
        # 同时更新到数据库（用于持久化存储）
        update_task_progress(task_id, progress, message)
    
    try:
        # 【第一步】从数据库读取目标 UFP 值（优化：复用连接）
        if progress_callback:
            progress_callback(task_id, 5, '正在读取评估结果...', '从数据库加载目标 UFP 值')
        
        # 优化：使用连接池，减少连接开销
        from routes.fpa.fpa_generator_routes import get_db_connection
        from decimal import Decimal
        
        target_ufp = None
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT afp FROM fpa_evaluation_result ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            cursor.close()
            
            if result and result.get('afp'):
                target_ufp = float(result['afp']) if isinstance(result['afp'], Decimal) else result['afp']
                logger.info(f"[步骤 1] 从数据库读取目标 UFP (使用 AFP): {target_ufp}")
        except Exception as e:
            logger.warning(f"读取评估结果失败：{e}")
        finally:
            if conn:
                conn.close()
        
        # 【第二步】读取并解析需求文档
        if progress_callback:
            progress_callback(task_id, 10, '正在读取需求文档...', '开始解析 Markdown 文件')
        
        with open(temp_md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        if progress_callback:
            progress_callback(task_id, 15, '正在解析功能点...', '从文档中提取功能点信息')
        
        # 延迟导入，避免循环依赖
        from routes.fpa.fpa_generator_routes import parse_requirement_document
        function_points = parse_requirement_document(md_content)
        
        if not function_points:
            raise Exception("未能从文档中提取到功能点信息")
        
        logger.info(f"[步骤 2] 解析完成，共提取 {len(function_points)} 个功能点")
        
        if progress_callback:
            progress_callback(task_id, 20, f'已解析 {len(function_points)} 个功能点', 
                            f'成功提取 {len(function_points)} 个功能点')
        
        # 【第三步】对比当前 AFP 和目标 AFP，判断是否需要 AI 扩展
        if target_ufp:  # target_ufp 实际是从数据库读取的 AFP 值
            current_afp = sum(p.get('AFP', 0) for p in function_points)
            
            # 统计各类别的数量分布
            from collections import Counter
            category_dist = Counter(p.get('类别', '未知') for p in function_points)
            afp_by_category = {}
            for category, count in category_dist.items():
                # 计算每个类别的 AFP：UFP × 0.33 (高重用新增)
                ufp_value = 7 if category=='ILF' else 5 if category in ['EO','EIF'] else 4
                afp_by_category[category] = count * ufp_value * 0.33
            
            logger.info(f"[步骤 3] AFP 对比分析 - 当前 AFP: {current_afp:.2f}, 目标 AFP: {target_ufp:.2f}")
            logger.info(f"[步骤 3] 功能点类别分布详情:")
            for category, count in sorted(category_dist.items()):
                ufp_value = 7 if category=='ILF' else 5 if category in ['EO','EIF'] else 4
                afp_value = count * ufp_value * 0.33
                logger.info(f"    - {category}: {count}个 × {ufp_value} × 0.33 = {afp_value:.2f} AFP")
            logger.info(f"[步骤 3] AFP 计算验证：Σ(各类别 AFP) = {sum(afp_by_category.values()):.2f} = {current_afp:.2f}")
            
            if wrapped_progress_callback:
                wrapped_progress_callback(task_id, 25, f'AFP 对比分析', 
                                f'当前:{current_afp:.2f}, 目标:{target_ufp:.2f}')
            
            need_ai_expansion = current_afp < target_ufp
            
            logger.info(f"[步骤 3] 判断结果：need_ai_expansion = {need_ai_expansion} ({current_afp:.2f} < {target_ufp:.2f})")
            
            if need_ai_expansion:
                # 需要扩展
                # 计算需要扩展多少个功能点：(目标 AFP - 当前 AFP) / 平均每功能点 AFP
                avg_afp_per_point = 1.65  # UFP=5 × 0.33（高重用新增）
                expand_count = int((target_ufp - current_afp) / avg_afp_per_point + 0.5)
                logger.info(f"[步骤 4] 需要扩展约 {expand_count} 个功能点 (AFP 差距：{target_ufp - current_afp:.2f})")
                
                if wrapped_progress_callback:
                    wrapped_progress_callback(task_id, 30, f'开始 AI 扩展 (需要{expand_count}个)', 
                                    '正在进行 AI 辅助功能点拆分')
                
                # 配置项：是否使用 OMLX 模型（Qwen3.5-4B-OptiQ-4bit）
                # True = 使用 OMLX 在线模型，False = 使用本地 Ollama 模型
                USE_OMLX = True  # 修改这里来切换模型：True=OMLX, False=本地 Ollama
                
                if USE_OMLX:
                    logger.info("[AI_EXPAND] 🌐 使用 OMLX 模型：Qwen3.5-4B-OptiQ-4bit")
                else:
                    logger.info("[AI_EXPAND] 💻 使用本地 Ollama 模型：qwen3:4b")
                
                # 调用 AI 扩展函数
                from routes.fpa.fpa_ai_expander import ai_assisted_expand_function_points
                new_points = ai_assisted_expand_function_points(
                    function_points, 
                    expand_count,
                    progress_callback=wrapped_progress_callback,
                    task_id=task_id,
                    use_omlx=USE_OMLX  # 传递模型选择参数
                )
                
                # 将 AI 扩展的功能点插入到对应的父功能点之后（保持文档顺序）
                # 而不是简单地添加到末尾
                logger.info(f"开始按文档顺序插入 {len(new_points)} 个 AI 扩展功能点")
                
                # 按照_parent_index 分组
                from collections import defaultdict
                points_by_parent = defaultdict(list)
                for point in new_points:
                    parent_idx = point.pop('_parent_index', None)  # 移除辅助字段
                    if parent_idx is not None:
                        points_by_parent[parent_idx].append(point)
                
                # 从后往前插入，避免索引偏移
                for parent_idx in sorted(points_by_parent.keys(), reverse=True):
                    child_points = points_by_parent[parent_idx]
                    # 插入到父功能点之后
                    insert_pos = parent_idx + 1
                    for i, child_point in enumerate(child_points):
                        function_points.insert(insert_pos + i, child_point)
                
                logger.info(f"AI 扩展完成，新增 {len(new_points)} 个功能点，已按文档顺序插入")
                
                # AI 扩展后，需要重新识别所有功能点的类别和计算 UFP、AFP
                if new_points:
                    logger.info(f"开始重新识别 {len(function_points)} 个功能点的类别和计算 AFP")
                    
                    for point in function_points:
                        item_text = point.get('功能点计数项', '')
                        
                        # 使用数据库中的规则判断类别（与 fpa_generator_routes.py 保持一致）
                        try:
                            from models.fpa_category_rules import FPACategoryRule
                            category, ufp = FPACategoryRule.apply_rules(item_text)
                            point['类别'] = category
                            point['UFP'] = ufp
                            logger.info(f"功能点 '{item_text}' -> 类别={category}, UFP={ufp}")
                        except Exception as e:
                            logger.error(f"应用类别规则失败：{e}，使用默认规则")
                            # 降级到硬编码规则（如果数据库不可用）
                            if item_text.endswith('表') or any(keyword in item_text for keyword in ['数据表', '配置表', '结果表', '详单表']):
                                point['类别'] = 'ILF'
                                point['UFP'] = 7
                            elif any(keyword in item_text for keyword in ['赋值', '新增', '修改', '删除', '增', '删', '改', '同步', '导入', '配置', '管理', '添加', '设置', '保存', '提交', '派发', '移交', '回单']):
                                point['类别'] = 'EI'
                                point['UFP'] = 4
                            elif any(keyword in item_text for keyword in ['列表呈现', '列表', '快速查询', '查询', '搜索', '查看', '浏览', '筛选', '详情', '展示', '显示', '获取', '读取']):
                                point['类别'] = 'EQ'
                                point['UFP'] = 4
                            elif any(keyword in item_text for keyword in ['判定', '分析', '计算', '处理', '识别', '匹配', '切换', '呈现', '导出', '上报', '调度', '推送', '验证', '检测', '剔除', '运算', '渲染', '生成', '跳转', '控制', '监听', '播报', '触发']):
                                point['类别'] = 'EO'
                                point['UFP'] = 5
                            elif any(keyword in item_text for keyword in ['引用', '外部', '财务', 'HR', '架构', '同步']):
                                point['类别'] = 'EIF'
                                point['UFP'] = 5
                            else:
                                point['类别'] = 'EO'
                                point['UFP'] = 5
                        
                        # 统一设置重用程度和修改类型
                        point['重用程度'] = '高'
                        point['修改类型'] = '新增'
                        
                        # 计算 AFP
                        ufp = point['UFP']
                        point['AFP'] = round(ufp * 0.33, 2)
                    
                    logger.info(f"功能点类别识别和 AFP 计算完成")
            else:
                # 不需要扩展
                logger.info(f"[步骤 4] ✅ 当前 AFP ({current_afp:.2f}) >= 目标 AFP ({target_ufp:.2f})，无需 AI 扩展")
                if wrapped_progress_callback:
                    wrapped_progress_callback(task_id, 30, f'无需 AI 扩展', 
                                    f'当前 AFP 已满足要求')
        else:
            logger.warning(f"[步骤 3] 未获取到目标 UFP 值，跳过 UFP 对比")
            if wrapped_progress_callback:
                wrapped_progress_callback(task_id, 25, '未获取到目标 UFP', 
                                '将使用默认 UFP 值')
        
        if wrapped_progress_callback:
            wrapped_progress_callback(task_id, 70, '正在生成 Excel 文件...', '开始创建 FPA 预估表')
        
        # 生成 Excel 文件（文件名使用可读的时间戳格式：YYYYMMDD_HHMMSS）
        output_dir = Path(current_app.config['UPLOAD_FOLDER']) / "fpa_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 将毫秒时间戳转换为秒（如果是毫秒级）
        if timestamp > 1e12:  # 大于 2001-09-09 的毫秒时间戳
            timestamp_seconds = timestamp / 1000
        else:
            timestamp_seconds = timestamp
        
        timestamp_str = datetime.fromtimestamp(timestamp_seconds).strftime('%Y%m%d_%H%M%S')
        # 使用 task_id 确保文件名绝对唯一，防止多用户同时生成时重名
        output_filename = f"{filename}_FPA_Estimation_{task_id}_{timestamp_str}.xlsx"
        output_path = output_dir / output_filename
        
        # 延迟导入，避免循环依赖
        from routes.fpa.fpa_generator_routes import generate_fpa_excel
        generate_fpa_excel(function_points, str(output_path))
        
        if wrapped_progress_callback:
            wrapped_progress_callback(task_id, 90, '正在清理临时文件...', '删除临时 Markdown 文件')
        
        # 清理临时文件
        try:
            os.remove(temp_md_path)
        except Exception as e:
            logger.warning(f"临时文件删除失败：{e}")
        
        if wrapped_progress_callback:
            wrapped_progress_callback(task_id, 95, '任务即将完成', f'生成的文件：{output_filename}')
        
        logger.info(f"FPA Excel 生成成功：{output_path}")
        
        # 返回结果
        result = {
            'output_filename': output_filename,
            'output_path': str(output_path),
            'function_point_count': len(function_points),
            'download_url': f'/fpa-generator/download/{output_filename}'
        }
        
        # 更新导出历史表
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 先获取文件大小
            file_size = os.path.getsize(str(output_path))
            
            logger.info(f"[UPDATE_HISTORY] 开始更新导出历史表，task_id={task_id}")
            logger.info(f"[UPDATE_HISTORY] output_filename={output_filename}, file_size={file_size}, function_point_count={len(function_points)}")
            
            sql = '''
                UPDATE knowledge_base.fpa_export_history 
                SET status = 'COMPLETED',
                    progress = 100,
                    message = '任务完成',
                    output_filename = %s,
                    file_path = %s,
                    file_size = %s,
                    function_point_count = %s,
                    completed_at = NOW()
                WHERE task_id = %s
            '''
            params = (output_filename, str(output_path), file_size, len(function_points), task_id)
            
            logger.info(f"[UPDATE_HISTORY] 执行 SQL: {sql}")
            logger.info(f"[UPDATE_HISTORY] 参数：{params}")
            
            cursor.execute(sql, params)
            conn.commit()
            
            # 验证更新结果
            cursor.execute('SELECT output_filename, status, completed_at FROM knowledge_base.fpa_export_history WHERE task_id = %s', (task_id,))
            result = cursor.fetchone()
            logger.info(f"[UPDATE_HISTORY] 验证更新结果：{result}")
            logger.info(f"[UPDATE_HISTORY] completed_at = {result[2] if result and len(result) > 2 else 'N/A'}")
            
            cursor.close()
            conn.close()
            
            logger.info(f"[UPDATE_HISTORY] 导出历史表更新成功")
        except Exception as e:
            logger.error(f"[UPDATE_HISTORY] 更新导出历史失败：{e}", exc_info=True)
            raise
        
        if wrapped_progress_callback:
            wrapped_progress_callback(task_id, 100, '任务完成！', 
                            f'FPA 预估表生成成功，共 {len(function_points)} 个功能点')
        
        return result
        
    except Exception as e:
        logger.error(f"FPA 生成任务失败：{e}", exc_info=True)
        # 更新导出历史表为失败状态
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE fpa_export_history 
                SET status = 'FAILED',
                    message = %s,
                    completed_at = NOW()
                WHERE task_id = %s
            ''', (str(e), task_id))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_error:
            logger.error(f"更新导出历史失败：{db_error}")
        raise
