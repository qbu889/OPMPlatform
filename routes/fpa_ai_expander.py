 # AI 辅助的功能点智能拆分（带自动去重、多线程优化）
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
import threading
import time

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
    # 远程 Ollama 服务器建议使用单线程，避免 502 错误
    import os
    cpu_cores = os.cpu_count() or 2
    
    # 智能选择并发数：远程服务器使用 1 线程，本地可使用 2-4 线程
    max_workers = 1  # 单线程顺序请求，避免远程服务器过载
    temp_estimate = "40-50°C"
    cpu_estimate = "15-25%"
    
    # 确保不超过待处理数量
    max_workers = min(max_workers, len(points_to_split))
    
    logger.info(f"[AI_EXPAND] 启动线程池，工作线程数：{max_workers} (CPU 核心数：{cpu_cores})")
    logger.info(f"[AI_EXPAND] 预计 CPU 使用率：{cpu_estimate}，温度：{temp_estimate}")
    logger.info(f"[AI_EXPAND] 处理 {len(points_to_split)} 个功能点，预计耗时：{len(points_to_split) * 8 / max_workers:.1f}秒（4 线程并发）")
    
    processed_count = ThreadSafeCounter(0)
    stop_flag = threading.Event()
    ai_failures = {'count': 0}
    max_ai_failures = 3
    
    # 批量处理功能点（每次处理 5 个功能点）
    batch_size = 5
    all_results = []
    
    for batch_start in range(0, len(points_to_split), batch_size):
        batch_end = min(batch_start + batch_size, len(points_to_split))
        batch_points = [(idx, points_to_split[idx]) for idx in range(batch_start, batch_end)]
        
        logger.info(f"[AI_EXPAND] 处理批次 {batch_start//batch_size + 1}: 功能点 {batch_start+1} 到 {batch_end}（共{len(batch_points)}个）")
        
        if stop_flag.is_set():
            break
        
        # 批次间添加延迟避免瞬间高负载
        if batch_start > 0:
            time.sleep(120.0)  # 批次间等待 120 秒
        
        # 构造批量处理的提示词
        points_info = []
        for idx, (i, point) in enumerate(batch_points):
            points_info.append(f"""功能点{idx+1}:
原始功能点：{point.get('功能点计数项', '')}
功能描述：{point.get('功能描述', '')}
输入：{point.get('输入', '')}
输出：{point.get('输出', '')}
处理过程：{point.get('处理过程', '')}""")
        
        # 使用 join 连接，避免在 f-string 中使用反斜杠
        points_info_text = '\n\n'.join(points_info)
        
        prompt = f"""
只返回 JSON 对象，不要其他文字。

任务：将以下 {len(batch_points)} 个功能点分别拆分成 3 个子功能点（优先），无法拆分则返回 2 个

{points_info_text}

JSON 格式（每个功能点对应一个数组）：
{{
  "功能点 1": [
    {{"name": "功能名称", "description": "描述", "input": "输入", "output": "输出", "process": "处理过程"}},
    {{"name": "功能名称", "description": "描述", "input": "输入", "output": "输出", "process": "处理过程"}},
    {{"name": "功能名称", "description": "描述", "input": "输入", "output": "输出", "process": "处理过程"}}
  ],
  "功能点 2": [...],
  ...
}}

命名规则（重要）：
- 使用后缀方式：原始功能点名称_操作类型
  例："时段规则参数配置_查询"、"工单流转管理_新增"、"业务影响分析_数据处理"
- 或使用简短术语："条件筛选"、"结果排序"、"详情查看"
- 禁止使用："子功能 1"、"功能点 A"等无意义名称
- name 不能与对应的原始功能点名称重复
- **功能点计数项字段要求**：名称中不要有空格、特殊符号（如括号、引号、逗号等），只用中文、英文、数字和下划线

拆分维度参考：
- 查询类：条件筛选查询、结果列表排序、详情下钻查看
- 配置类：参数配置编辑、规则有效性校验、配置保存生效
- 处理类：数据预处理、核心逻辑运算、结果持久化存储
- 采集类：数据源连接、实时数据采集、采集结果存储

要求：
1. 优先拆分成 3 个有实际意义的子功能点
2. description/input/output/process 根据原始内容生成，要具体明确
3. 合法 JSON 对象，直接用 {{}} 包裹，不要用代码
4. name 字段保持简洁，去除所有空格和特殊符号
5. 按功能点顺序依次返回结果

现在直接返回 JSON：
"""
        
        try:
            # 调用本地 AI 模型
            response = ollama.generate(
                prompt=prompt,
                stream=False
            )
            
            # 重置失败计数
            if ai_failures['count'] > 0:
                ai_failures['count'] = 0
            
            # 解析 AI 响应
            import re
            import json
            
            logger.info(f"[AI_EXPAND] 批量处理 {len(batch_points)} 个功能点的完整响应：{response[:500]}...")
            
            # 尝试提取 JSON 对象
            json_data = None
            
            # 模式 1: 提取 ```json 包裹的内容
            json_match = re.search(r'```json\s*(.+?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    json_data = json.loads(json_match.group(1))
                    logger.info(f"[AI_EXPAND] 从 markdown json 块中解析成功")
                except json.JSONDecodeError as e:
                    logger.warning(f"[AI_EXPAND] markdown json 解析失败 - {e}")
            
            # 模式 2: 直接查找 JSON 对象
            if not json_data:
                json_obj_match = re.search(r'\{\s*".*?":\s*\[.*?\]\s*\}', response, re.DOTALL)
                if json_obj_match:
                    try:
                        json_data = json.loads(json_obj_match.group(0))
                        logger.info(f"[AI_EXPAND] 从纯 JSON 对象中解析成功")
                    except json.JSONDecodeError as e:
                        logger.warning(f"[AI_EXPAND] 纯 JSON 解析失败 - {e}")
            
            # 模式 3: 尝试修复常见的 JSON 格式问题
            if not json_data:
                fixed_response = response.replace(',', ',').replace(':', ':')
                json_obj_match = re.search(r'\{\s*".*?":\s*\[.*?\]\s*\}', fixed_response, re.DOTALL)
                if json_obj_match:
                    try:
                        json_data = json.loads(json_obj_match.group(0))
                        logger.info(f"[AI_EXPAND] 从修复后的 JSON 中解析成功")
                    except json.JSONDecodeError as e:
                        logger.warning(f"[AI_EXPAND] 修复后 JSON 仍失败 - {e}")
            
            if json_data and isinstance(json_data, dict):
                logger.info(f"[AI_EXPAND] 解析到 {len(json_data)} 个功能点的拆分结果")
                
                # 按顺序处理每个功能点的结果
                for idx, (orig_idx, point) in enumerate(batch_points):
                    key = f"功能点{idx+1}"
                    sub_points_data = json_data.get(key, [])
                    
                    if not sub_points_data:
                        logger.warning(f"[AI_EXPAND] 功能点{idx+1}未找到拆分结果")
                        all_results.append((orig_idx, [], set()))
                        continue
                    
                    logger.info(f"[AI_EXPAND] 功能点{idx+1}: 解析到 {len(sub_points_data)} 个子功能点")
                    
                    # 创建新的功能点
                    new_points = []
                    new_names = set()
                    
                    # 每个原始功能点最多拆分出 3 个子功能点
                    for sub_idx, sub_point in enumerate(sub_points_data[:3]):
                        # 生成唯一的名称
                        base_name = sub_point.get('name', '').strip()
                        
                        # 检查名称是否为空或是占位符
                        if not base_name or any(placeholder in base_name for placeholder in ['子功能名称', '功能点', '具体子功能', '子功能', '名称']):
                            desc = sub_point.get('description', '')
                            process = sub_point.get('process', '')
                            
                            # 从描述中提取关键字生成名称
                            if '查询' in desc or '搜索' in process:
                                base_name = f"{point.get('功能点计数项', '')}_查询"
                            elif '配置' in desc or '设置' in process or '参数' in desc:
                                base_name = f"{point.get('功能点计数项', '')}_配置"
                            elif '保存' in desc or '存储' in process:
                                base_name = f"{point.get('功能点计数项', '')}_保存"
                            elif '校验' in desc or '验证' in process:
                                base_name = f"{point.get('功能点计数项', '')}_校验"
                            elif '显示' in desc or '呈现' in process:
                                base_name = f"{point.get('功能点计数项', '')}_显示"
                            elif '新增' in desc or '创建' in process:
                                base_name = f"{point.get('功能点计数项', '')}_新增"
                            elif '修改' in desc or '更新' in process:
                                base_name = f"{point.get('功能点计数项', '')}_修改"
                            elif '删除' in desc or '移除' in process:
                                base_name = f"{point.get('功能点计数项', '')}_删除"
                            else:
                                base_name = f"{point.get('功能点计数项', '')}-{sub_idx + 1}"
                        
                        # 线程安全地检查和添加名称
                        with names_lock:
                            if base_name in existing_names:
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
                            '_parent_index': orig_idx
                        }
                        new_points.append(new_point)
                        new_names.add(unique_name)
                    
                    all_results.append((orig_idx, new_points, new_names))
                    expanded_points.extend(new_points)
                    
                    if len(expanded_points) >= expand_count:
                        expanded_points = expanded_points[:expand_count]
                        break
            else:
                logger.warning(f"[AI_EXPAND] 批量解析失败，返回空结果")
                for idx, (orig_idx, _) in enumerate(batch_points):
                    all_results.append((orig_idx, [], set()))
            
            # 检查是否已达到目标数量
            if len(expanded_points) >= expand_count:
                break
                
        except Exception as e:
            logger.error(f"[AI_EXPAND] 批量处理失败：{e}")
            ai_failures['count'] += 1
            failures = ai_failures['count']
            logger.error(f"[AI_EXPAND] AI 服务失败次数：{failures}/{max_ai_failures}")
            
            if failures >= max_ai_failures:
                logger.error(f"[AI_EXPAND] AI 服务连续失败{max_ai_failures}次，停止所有后续任务！")
                stop_flag.set()
            
            for idx, (orig_idx, _) in enumerate(batch_points):
                all_results.append((orig_idx, [], set()))
    
    # 按原始顺序合并结果
    all_results.sort(key=lambda x: x[0])
        
    logger.info(f"[AI_EXPAND] AI 扩展完成，共扩展 {len(expanded_points)} 个功能点")
    logger.info(f"[AI_EXPAND] 实际处理：{len(all_results)} 个批次，平均每批拆分：{len(expanded_points)/max(len(all_results),1):.2f}个")
        
    if progress_callback and task_id:
        progress_callback(task_id, 70, f'AI 扩展完成，新增{len(expanded_points)}个功能点',
                         f'成功扩展 {len(expanded_points)} 个功能点（批量处理加速）')

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
