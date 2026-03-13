# 异步任务相关路由（追加到 fpa_generator_routes.py 末尾）
import os
import time
import uuid
from pathlib import Path
from datetime import datetime
from flask import jsonify, current_app, request

from routes.fpa_generator_routes import fpa_generator_bp, parse_requirement_document, generate_fpa_excel
from utils.task_manager import get_task_manager
import logging

logger = logging.getLogger(__name__)


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
        
        # 保存临时文件
        timestamp = int(time.time() * 1000)
        upload_dir = Path(current_app.config['UPLOAD_FOLDER']) / "fpa_input"
        os.makedirs(upload_dir, exist_ok=True)
        
        filename = Path(file.filename).stem
        temp_md_path = upload_dir / f"{filename}_{timestamp}.md"
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
        return jsonify({
            'success': False,
            'message': '任务不存在'
        }), 404
    
    return jsonify({
        'success': True,
        'data': task_info
    })


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
    try:
        # 【第一步】先从数据库读取目标 UFP 值
        if progress_callback:
            progress_callback(task_id, 5, '正在读取评估结果...', '从数据库加载目标 UFP 值')
        
        # 从数据库读取评估结果（使用 afp 作为目标 UFP）
        from routes.fpa_generator_routes import get_db_connection
        from decimal import Decimal
        
        target_ufp = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            # 注意：表中没有 target_ufp 字段，使用 afp 代替
            cursor.execute("SELECT afp FROM fpa_evaluation_result ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result.get('afp'):
                target_ufp = float(result['afp']) if isinstance(result['afp'], Decimal) else result['afp']
                logger.info(f"[步骤 1] 从数据库读取目标 UFP (使用 AFP): {target_ufp}")
        except Exception as e:
            logger.warning(f"读取评估结果失败：{e}")
        
        # 【第二步】读取并解析需求文档
        if progress_callback:
            progress_callback(task_id, 10, '正在读取需求文档...', '开始解析 Markdown 文件')
        
        with open(temp_md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        if progress_callback:
            progress_callback(task_id, 15, '正在解析功能点...', '从文档中提取功能点信息')
        
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
            
            if progress_callback:
                progress_callback(task_id, 25, f'AFP 对比分析', 
                                f'当前:{current_afp:.2f}, 目标:{target_ufp:.2f}')
            
            need_ai_expansion = current_afp < target_ufp
            
            logger.info(f"[步骤 3] 判断结果：need_ai_expansion = {need_ai_expansion} ({current_afp:.2f} < {target_ufp:.2f})")
            
            if need_ai_expansion:
                # 需要扩展
                # 计算需要扩展多少个功能点：(目标 AFP - 当前 AFP) / 平均每功能点 AFP
                avg_afp_per_point = 1.65  # UFP=5 × 0.33（高重用新增）
                expand_count = int((target_ufp - current_afp) / avg_afp_per_point + 0.5)
                logger.info(f"[步骤 4] 需要扩展约 {expand_count} 个功能点 (AFP 差距：{target_ufp - current_afp:.2f})")
                
                if progress_callback:
                    progress_callback(task_id, 30, f'开始 AI 扩展 (需要{expand_count}个)', 
                                    '正在进行 AI 辅助功能点拆分')
                
                # 调用 AI 扩展函数
                from routes.fpa_ai_expander import ai_assisted_expand_function_points
                new_points = ai_assisted_expand_function_points(
                    function_points, 
                    expand_count,
                    progress_callback=progress_callback,
                    task_id=task_id
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
                        
                        # 跳过 ILF 表（已经在 parse_requirement_document 中处理）
                        if point.get('类别') == 'ILF' and item_text.endswith('表'):
                            # ILF 已经正确设置
                            pass
                        else:
                            # 根据功能点名称重新识别类别
                            # ILF: 结尾有"表"字，并且是系统内部维护的数据表
                            if item_text.endswith('表') or any(keyword in item_text for keyword in ['数据表', '配置表', '结果表', '详单表']):
                                point['类别'] = 'ILF'
                                point['UFP'] = 7
                            # EI: 包含"赋值/新增/修改/删除"等关键字
                            elif any(keyword in item_text for keyword in ['赋值', '新增', '修改', '删除', '增', '删', '改', '同步', '导入', '配置', '管理', '添加', '设置', '保存', '提交', '派发', '移交', '回单']):
                                point['类别'] = 'EI'
                                point['UFP'] = 4
                            # EQ: 包含"列表呈现/列表/快速查询/查询/搜索/查看/浏览"等
                            elif any(keyword in item_text for keyword in ['列表呈现', '列表', '快速查询', '查询', '搜索', '查看', '浏览', '筛选', '详情', '展示', '显示', '获取', '读取']):
                                point['类别'] = 'EQ'
                                point['UFP'] = 4
                            # EO: 查询统计及逻辑计算
                            elif any(keyword in item_text for keyword in ['判定', '分析', '计算', '处理', '识别', '匹配', '切换', '呈现', '导出', '上报', '调度', '推送', '验证', '检测', '剔除', '运算', '渲染', '生成', '跳转', '控制', '监听', '播报', '触发']):
                                point['类别'] = 'EO'
                                point['UFP'] = 5
                            # EIF: 外部系统表
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
                if progress_callback:
                    progress_callback(task_id, 30, f'无需 AI 扩展', 
                                    f'当前 AFP 已满足要求')
        else:
            logger.warning(f"[步骤 3] 未获取到目标 UFP 值，跳过 UFP 对比")
            if progress_callback:
                progress_callback(task_id, 25, '未获取到目标 UFP', 
                                '将使用默认 UFP 值')
        
        if progress_callback:
            progress_callback(task_id, 70, '正在生成 Excel 文件...', '开始创建 FPA 预估表')
        
        # 生成 Excel 文件（文件名使用可读的时间戳格式：YYYYMMDD_HHMMSS）
        output_dir = Path(current_app.config['UPLOAD_FOLDER']) / "fpa_output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 将毫秒时间戳转换为秒（如果是毫秒级）
        if timestamp > 1e12:  # 大于 2001-09-09 的毫秒时间戳
            timestamp_seconds = timestamp / 1000
        else:
            timestamp_seconds = timestamp
        
        timestamp_str = datetime.fromtimestamp(timestamp_seconds).strftime('%Y%m%d_%H%M%S')
        output_filename = f"{filename}_FPA_Estimation_{timestamp_str}.xlsx"
        output_path = output_dir / output_filename
        
        generate_fpa_excel(function_points, str(output_path))
        
        if progress_callback:
            progress_callback(task_id, 90, '正在清理临时文件...', '删除临时 Markdown 文件')
        
        # 清理临时文件
        try:
            os.remove(temp_md_path)
        except Exception as e:
            logger.warning(f"临时文件删除失败：{e}")
        
        if progress_callback:
            progress_callback(task_id, 95, '任务即将完成', f'生成的文件：{output_filename}')
        
        logger.info(f"FPA Excel 生成成功：{output_path}")
        
        # 返回结果
        result = {
            'output_filename': output_filename,
            'output_path': str(output_path),
            'function_point_count': len(function_points),
            'download_url': f'/fpa-generator/download/{output_filename}'
        }
        
        if progress_callback:
            progress_callback(task_id, 100, '任务完成！', 
                            f'FPA 预估表生成成功，共 {len(function_points)} 个功能点')
        
        return result
        
    except Exception as e:
        logger.error(f"FPA 生成任务失败：{e}", exc_info=True)
        raise
