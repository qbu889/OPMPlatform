 # AI 辅助的功能点智能拆分（带自动去重、多线程优化）
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import threading

logger = logging.getLogger(__name__)

# 线程安全的计数器
class ThreadSafeCounter:
    def __init__(self, initial=0):
        self._value = initial
        self._lock = threading.Lock()
    
    def increment(self):
        with self._lock:
            self._value += 1
            return self._value
    
    def get_value(self):
        with self._lock:
            return self._value

def ai_assisted_expand_function_points(original_points: list, expand_count: int, 
                                       progress_callback=None, task_id: str = None) -> list:
    """
    AI 辅助的功能点智能拆分（带自动去重和进度回调，多线程优化版）
    
    Args:
        original_points: 原始功能点列表
        expand_count: 需要扩展的数量
        progress_callback: 进度回调函数 (task_id, progress, message, log_entry)
        task_id: 任务 ID
        
    Returns:
        新生成的功能点列表（已去重）
    """
    from utils.ollama_client import OllamaClient
    ollama = OllamaClient()
    
    expanded_points = []
    existing_names = set(p.get('功能点计数项', '').strip() for p in original_points)
    names_lock = threading.Lock()  # 保护 existing_names 的锁
    
    # 选择有代表性的功能点进行拆分（优先选择复杂的、描述详细的功能点）
    sorted_points = sorted(
        original_points,
        key=lambda p: len(p.get('功能描述', '')) + len(p.get('处理过程', '')),
        reverse=True
    )
    
    # 根据需要的扩展数量，动态决定选择多少个功能点进行拆分
    # 每个功能点平均拆分出 2-3 个子功能点
    points_needed = max(1, expand_count // 2)  # 至少选择 1 个
    points_to_split = sorted_points[:min(points_needed, len(sorted_points), 50)]  # 最多选择 50 个
    
    logger.info(f"[AI_EXPAND] 开始 AI 辅助扩展，需要扩展 {expand_count} 个功能点")
    logger.info(f"[AI_EXPAND] 选择了 {len(points_to_split)} 个复杂功能点进行拆分（目标：{points_needed}个）")
    logger.info(f"[AI_EXPAND] 使用多线程模式，最大并发数：8")
    
    if progress_callback and task_id:
        progress_callback(task_id, 40, f'开始 AI 拆分，目标扩展{expand_count}个功能点',
                         f'选择了{len(points_to_split)}个功能点进行 AI 拆分（多线程模式）')
    
    # 使用线程池并行处理
    # 根据 CPU 负载动态调整并发数，避免过热降频
    # M3 Max 建议：4 线程平衡性能和温度，8 线程性能最强但温度高
    import os
    cpu_cores = os.cpu_count() or 8
    
    # 智能选择并发数：使用 4 线程平衡性能和稳定性
    max_workers = 4  # 4 线程并发，提高处理速度
    temp_estimate = "65-75°C"
    cpu_estimate = "35-45%"
    
    # 确保不超过待处理数量
    max_workers = min(max_workers, len(points_to_split))
    
    logger.info(f"[AI_EXPAND] 启动线程池，工作线程数：{max_workers} (CPU 核心数：{cpu_cores})")
    logger.info(f"[AI_EXPAND] 预计 CPU 使用率：{cpu_estimate}，温度：{temp_estimate}")
    logger.info(f"[AI_EXPAND] 处理 {len(points_to_split)} 个功能点，预计耗时：{len(points_to_split) * 8 / max_workers:.1f}秒（4 线程并发）")
    
    processed_count = ThreadSafeCounter(0)
    stop_flag = threading.Event()
    ai_failures = {'count': 0}  # 使用字典包装，避免作用域问题
    max_ai_failures = 3  # 最多允许 3 次 AI 失败
    
    def process_single_point(args: Tuple[int, dict]) -> Tuple[int, List[dict], set]:
        """处理单个功能点的函数（在线程中执行）"""
        i, point = args
        
        if stop_flag.is_set():
            return i, [], set()
        
        # 添加延迟避免瞬间高负载（单线程模式下增加间隔）
        import time
        if i > 0:  # 第一个请求不延迟
            time.sleep(50.0)  # 50 秒间隔，单线程模式下更稳定
        
        # 构造 AI 提示词（针对 qwen:1.8b 强制 JSON 格式 + 基于实际需求）
        prompt = f"""
你是一个专业的软件需求分析师。只返回 JSON，不要任何其他文字。

任务：根据需求文档的实际内容，将功能点拆分成**3 个**具体的子功能点（优先），如果确实无法拆分成 3 个，则拆分成 2 个

原始功能点：**{point.get('功能点计数项', '')}**
功能描述：{point.get('功能描述', '')}
输入：{point.get('输入', '')}
输出：{point.get('输出', '')}
处理过程：{point.get('处理过程', '')}

必须返回的 JSON 格式（**优先返回 3 个子功能点**）：
[
  {{"name": "实际功能名称 1", "description": "详细描述 1", "input": "输入 1", "output": "输出 1", "process": "处理过程 1"}},
  {{"name": "实际功能名称 2", "description": "详细描述 2", "input": "输入 2", "output": "输出 2", "process": "处理过程 2"}},
  {{"name": "实际功能名称 3", "description": "详细描述 3", "input": "输入 3", "output": "输出 3", "process": "处理过程 3"}}
]

重要要求：
1. **优先拆分成 3 个子功能点**，从不同维度进行拆分，例如：
   - 查询类功能：可以拆分为"条件筛选查询"、"结果列表排序"、"详情下钻查看"
   - 配置类功能：可以拆分为"参数配置编辑"、"规则有效性校验"、"配置保存生效"
   - 处理类功能：可以拆分为"数据预处理"、"核心逻辑运算"、"结果持久化存储"
   - 界面类功能：可以拆分为"界面元素渲染"、"用户交互响应"、"数据实时更新"
   - 采集类功能：可以拆分为"数据源连接"、"实时数据采集"、"采集结果存储"
   - 告警类功能：可以拆分为"阈值监测判断"、"告警信息生成"、"通知发送处理"

2. 如果确实无法拆分成 3 个有实际意义的子功能，再拆分成 2 个

3. **name 字段命名规范**（非常重要！）：
   - 必须是有实际意义的功能名称，要从需求上下文推断具体功能
   - **推荐使用后缀方式**：原始功能点名称_操作类型，例如：
     * "时段规则参数配置_查询"、"时段规则参数配置_保存"、"时段规则参数配置_校验"
     * "工单流转管理_新增"、"工单流转管理_修改"、"工单流转管理_删除"
     * "业务影响分析_数据采集"、"业务影响分析_数据处理"、"业务影响分析_结果显示"
   - 或者使用简短的业务术语，例如："条件筛选"、"结果排序"、"详情查看"
   - **绝对不要用**："子功能 1"、"功能点 A"、"具体子功能名称"等无意义占位符

4. **绝对不能使用**"子功能名称 1"、"功能点 1"、"具体子功能名称"等任何占位符

5. name 不能与"{point.get('功能点计数项', '')}"重复

6. description、input、output、process 都要根据原始功能点的实际内容生成，要具体、明确

7. 必须是合法的 JSON 数组

8. 只返回 JSON，不要任何其他文字

9. 不要用 markdown 标记

现在直接返回 JSON：
"""
        
        try:
            # 调用本地 AI 模型
            response = ollama.generate(
                prompt=prompt,
                stream=False
            )
            
            # 重置失败计数（成功一次后清零）
            if ai_failures['count'] > 0:
                ai_failures['count'] = 0
            
            # 解析 AI 响应
            import re
            import json
            
            # 记录完整响应以便调试（重要！）
            logger.info(f"[AI_EXPAND] 功能点 {i+1} 的完整响应：{response}")
            
            # 尝试多种模式提取 JSON
            sub_points_data = None
                        
            # 模式 1: 提取 ```json 包裹的内容
            json_match = re.search(r'```json\s*(.+?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    sub_points_data = json.loads(json_match.group(1))
                    logger.info(f"[AI_EXPAND] 功能点 {i+1}: 从 markdown json 块中解析成功")
                except json.JSONDecodeError as e:
                    logger.warning(f"[AI_EXPAND] 功能点 {i+1}: markdown json 解析失败 - {e}")
                        
            # 模式 2: 直接查找 JSON 数组（没有 markdown 标记）
            if not sub_points_data:
                json_array_match = re.search(r'\[\s*\{.*?\}\s*\]', response, re.DOTALL)
                if json_array_match:
                    try:
                        sub_points_data = json.loads(json_array_match.group(0))
                        logger.info(f"[AI_EXPAND] 功能点 {i+1}: 从纯 JSON 数组中解析成功")
                    except json.JSONDecodeError as e:
                        logger.warning(f"[AI_EXPAND] 功能点 {i+1}: 纯 JSON 解析失败 - {e}")
                        # 记录失败时的原始内容片段
                        logger.warning(f"[AI_EXPAND] 功能点 {i+1}: 失败内容片段：{json_array_match.group(0)[:200]}")
                        
            # 模式 3: 尝试修复常见的 JSON 格式问题
            if not sub_points_data:
                # 移除可能的中文冒号，替换为英文冒号
                fixed_response = response.replace(',', ',').replace(':', ':')
                json_array_match = re.search(r'\[\s*\{.*?\}\s*\]', fixed_response, re.DOTALL)
                if json_array_match:
                    try:
                        sub_points_data = json.loads(json_array_match.group(0))
                        logger.info(f"[AI_EXPAND] 功能点 {i+1}: 从修复后的 JSON 中解析成功")
                    except json.JSONDecodeError as e:
                        logger.warning(f"[AI_EXPAND] 功能点 {i+1}: 修复后 JSON 仍失败 - {e}")
                        logger.warning(f"[AI_EXPAND] 功能点 {i+1}: 原始响应片段：{response[:300]}")
                        
            # 模式 4: 如果还是失败，尝试直接使用 eval（仅在内网环境，安全性可控）
            if not sub_points_data:
                try:
                    # 清理响应，只保留 JSON 部分
                    json_start = response.find('[')
                    json_end = response.rfind(']') + 1
                    if json_start >= 0 and json_end > json_start:
                        json_str = response[json_start:json_end]
                        # 替换中文标点
                        json_str = json_str.replace(',', ',').replace(':', ':')
                        sub_points_data = eval(json_str)
                        logger.info(f"[AI_EXPAND] 功能点 {i+1}: 使用 eval 解析成功（不推荐）")
                except Exception as e:
                    logger.warning(f"[AI_EXPAND] 功能点 {i+1}: eval 也失败了 - {e}")
            
            if sub_points_data and isinstance(sub_points_data, list) and len(sub_points_data) > 0:
                logger.info(f"[AI_EXPAND] 功能点 {i+1}: 解析到 {len(sub_points_data)} 个子功能点")
                
                # 创建新的功能点
                new_points = []
                new_names = set()
                
                # 每个原始功能点最多拆分出 3 个子功能点
                for idx, sub_point in enumerate(sub_points_data[:3]):
                    # 生成唯一的名称
                    base_name = sub_point.get('name', '').strip()
                    
                    # 检查名称是否为空或是占位符
                    if not base_name or any(placeholder in base_name for placeholder in ['子功能名称', '功能点', '具体子功能', '子功能', '名称']):
                        # 如果是占位符或空值，根据功能描述生成有意义的名称
                        desc = sub_point.get('description', '')
                        process = sub_point.get('process', '')
                        input_data = sub_point.get('input', '')
                        output_data = sub_point.get('output', '')
                        
                        # 从描述和过程中提取关键字生成名称（优先级顺序）
                        if '查询' in desc or '搜索' in process or '检索' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_查询"
                        elif '配置' in desc or '设置' in process or '参数' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_配置"
                        elif '保存' in desc or '存储' in process or '持久化' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_保存"
                        elif '校验' in desc or '验证' in process or '审核' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_校验"
                        elif '显示' in desc or '呈现' in process or '展示' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_显示"
                        elif '新增' in desc or '创建' in process or '添加' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_新增"
                        elif '修改' in desc or '更新' in process or '编辑' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_修改"
                        elif '删除' in desc or '移除' in process or '注销' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_删除"
                        elif '导入' in desc or '导出' in process or '转换' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_数据交换"
                        elif '统计' in desc or '分析' in process or '报表' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_统计分析"
                        elif '告警' in desc or '通知' in process or '提醒' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_告警通知"
                        elif '采集' in desc or '收集' in process or '获取' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_数据采集"
                        elif '处理' in desc or '计算' in process or '运算' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_数据处理"
                        elif '同步' in desc or '异步' in process or '消息' in desc:
                            base_name = f"{point.get('功能点计数项', '')}_同步通信"
                        else:
                            # 默认使用序号区分，使用短横线连接
                            base_name = f"{point.get('功能点计数项', '')}-{idx + 1}"
                    
                    # 线程安全地检查和添加名称
                    with names_lock:
                        if base_name in existing_names:
                            # 如果重复，生成唯一名称（使用短横线 + 序号）
                            counter = 1
                            while f"{base_name}-{counter}" in existing_names and counter < 100:
                                counter += 1
                            unique_name = f"{base_name}-{counter}"
                            existing_names.add(unique_name)
                        else:
                            unique_name = base_name
                            existing_names.add(unique_name)
                    
                    new_point = {
                        'level1': point.get('level1', ''),
                        'level2': point.get('level2', ''),
                        'level3': point.get('level3', ''),
                        'level4': point.get('level4', ''),
                        'level5': unique_name,
                        '功能点计数项': unique_name,
                        '功能描述': sub_point.get('description', point.get('功能描述', '')),
                        '系统界面': point.get('系统界面', ''),
                        '输入': sub_point.get('input', point.get('输入', '')),
                        '输出': sub_point.get('output', point.get('输出', '')),
                        '处理过程': sub_point.get('process', point.get('处理过程', '')),
                        '内部逻辑文件数': 0,
                        '外部逻辑文件数': 0,
                        '新增/变更内部逻辑文件': '',
                        '原有未修改内部逻辑文件': '',
                        '新增/变更外部逻辑文件': '无',
                        '原有未修改外部逻辑文件': '',
                        '类别': 'EO',
                        'UFP': 5,
                        '重用程度': '高',
                        '修改类型': '新增',
                        'AFP': 0,
                        '备注': f'AI 拆分自：{point.get("功能点计数项", "")}',
                        '_parent_index': i
                    }
                    new_points.append(new_point)
                    new_names.add(unique_name)
                
                return i, new_points, new_names
            else:
                logger.warning(f"[AI_EXPAND] 功能点 {i+1}: AI 响应格式错误")
                return i, [], set()
                
        except Exception as e:
            logger.warning(f"[AI_EXPAND] 功能点 {i+1} 处理失败：{e}")
            
            # 记录 AI 失败次数
            ai_failures['count'] += 1
            failures = ai_failures['count']
            logger.error(f"[AI_EXPAND] AI 服务失败次数：{failures}/{max_ai_failures}")
            
            # 如果连续失败超过阈值，停止所有任务
            if failures >= max_ai_failures:
                logger.error(f"[AI_EXPAND] AI 服务连续失败{max_ai_failures}次，停止所有后续任务！")
                logger.error(f"[AI_EXPAND] 请检查 Ollama 服务是否运行：http://localhost:11434")
                stop_flag.set()  # 设置停止标志
            
            return i, [], set()
    
    # 提交任务到线程池
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        futures = {executor.submit(process_single_point, (i, point)): i 
                   for i, point in enumerate(points_to_split)}
        
        # 收集结果
        all_results = []
        total_processed = 0
        
        for future in as_completed(futures):
            try:
                i, new_points, new_names = future.result(timeout=120)  # 每个任务最多 2 分钟
                all_results.append((i, new_points, new_names))
                
                # 更新进度
                total_processed = processed_count.increment()
                current_progress = 40 + int((total_processed / len(points_to_split)) * 30)
                
                if progress_callback and task_id:
                    progress_callback(task_id, current_progress,
                                    f'正在拆分功能点 {total_processed}/{len(points_to_split)}',
                                    f'已处理：{points_to_split[i].get("功能点计数项", "")}')
                
                logger.info(f"[AI_EXPAND] 完成 {total_processed}/{len(points_to_split)} 个功能点拆分")
                
                # 检查是否需要停止
                if stop_flag.is_set():
                    logger.error("[AI_EXPAND] 检测到停止标志，取消剩余任务")
                    break
                
            except Exception as e:
                logger.error(f"[AI_EXPAND] 任务执行失败：{e}")
    
    # 按原始顺序合并结果
    all_results.sort(key=lambda x: x[0])  # 按索引排序
    
    for i, new_points, new_names in all_results:
        expanded_points.extend(new_points)
        if len(expanded_points) >= expand_count:
            expanded_points = expanded_points[:expand_count]
            break
    
    logger.info(f"[AI_EXPAND] AI 扩展完成，共扩展 {len(expanded_points)} 个功能点")
    logger.info(f"[AI_EXPAND] 实际处理：{len(all_results)} 个功能点，平均每个拆分：{len(expanded_points)/max(len(all_results),1):.2f}个")
    
    # 如果是因为 AI 服务失败而停止，给出明确提示并抛出异常
    if stop_flag.is_set():
        logger.error(f"[AI_EXPAND] ⚠️  警告：AI 服务不可用，任务已提前终止")
        logger.error(f"[AI_EXPAND] ⚠️  请启动 Ollama 服务：ollama serve")
        logger.error(f"[AI_EXPAND] ⚠️  然后确保模型已下载：ollama pull qwen3:4b")
        if progress_callback and task_id:
            progress_callback(task_id, 40, 'AI 服务不可用，任务已停止',
                            f'AI 服务连续失败{max_ai_failures}次，请检查服务状态')
        # 抛出异常，让上层捕获并更新数据库状态为 FAILED
        raise Exception(f"AI 服务不可用，连续失败{max_ai_failures}次。请检查 Ollama 服务是否运行。")
    else:
        if progress_callback and task_id:
            progress_callback(task_id, 70, f'AI 扩展完成，新增{len(expanded_points)}个功能点',
                             f'成功扩展 {len(expanded_points)} 个功能点（多线程加速）')
    
    return expanded_points


def ensure_unique_name(base_name: str, existing_names: set) -> str:
    """
    确保功能点名称唯一，如果重复则添加描述性后缀
    
    Args:
        base_name: 基础名称
        existing_names: 已存在的名称集合
        
    Returns:
        唯一的名称
    """
    if base_name not in existing_names:
        return base_name
    
    # 如果名称已存在，尝试添加描述性后缀
    counter = 1
    while True:
        # 尝试不同的后缀模式
        suffixes = [
            f"的子功能{counter}",
            f"-{counter}",
            f"（{counter}）",
        ]
        
        for suffix in suffixes:
            candidate = f"{base_name}{suffix}"
            if candidate not in existing_names:
                return candidate
        
        counter += 1
        
        # 防止无限循环
        if counter > 100:
            import uuid
            return f"{base_name}_{uuid.uuid4().hex[:6]}"
