#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FPA 异步任务管理
封装 Celery 异步任务处理
"""
import threading
import time
import logging
from typing import Dict, Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class AsyncTaskManager:
    """异步任务管理器（基于线程）"""
    
    def __init__(self):
        self.tasks: Dict[str, dict] = {}  # task_id -> task_info
        self.lock = threading.Lock()
    
    def create_task(self, task_id: str, task_func: Callable, *args, **kwargs) -> str:
        """
        创建并启动异步任务
        
        Args:
            task_id: 任务 ID
            task_func: 任务函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            task_id
        """
        from flask import current_app
        
        # 在主线程中获取 Flask 应用实例
        try:
            app = current_app._get_current_object()
        except RuntimeError:
            # 如果不在应用上下文中，尝试从 gunicorn 或其他方式获取
            import sys
            app = None
            # 尝试从 sys.modules 中获取
            if 'flask' in sys.modules:
                from flask import Flask
                # 查找已注册的 Flask 应用
                for obj in sys.modules.values():
                    if hasattr(obj, 'app') and isinstance(obj.app, Flask):
                        app = obj.app
                        break
        
        with self.lock:
            self.tasks[task_id] = {
                'id': task_id,
                'status': 'PENDING',
                'progress': 0,
                'message': '任务已创建',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'result': None,
                'error': None,
                'logs': []  # 任务日志
            }
        
        # 启动线程执行任务
        thread = threading.Thread(
            target=self._execute_task,
            args=(task_id, task_func, app, *args),
            kwargs=kwargs,
            daemon=True
        )
        thread.start()
        
        logger.info(f"[TASK] 创建任务：{task_id}")
        return task_id
    
    def _execute_task(self, task_id: str, task_func: Callable, app, *args, **kwargs):
        """执行任务（在线程中）"""
        try:
            # 更新状态为进行中
            self._update_task_status(task_id, '运行中', 0, '任务开始执行')
            
            # 如果传入了 Flask 应用实例，使用它创建应用上下文
            if app:
                with app.app_context():
                    # 执行任务
                    result = task_func(*args, task_id=task_id, progress_callback=self._update_progress, **kwargs)
                        
                    # 更新状态为完成
                    self._update_task_status(task_id, 'COMPLETED', 100, '任务执行完成', result=result)
                    logger.info(f"[TASK] 任务完成：{task_id}")
            else:
                # 没有应用实例，直接执行（可能无法访问 current_app）
                result = task_func(*args, task_id=task_id, progress_callback=self._update_progress, **kwargs)
                self._update_task_status(task_id, 'COMPLETED', 100, '任务执行完成', result=result)
                logger.info(f"[TASK] 任务完成：{task_id}")
                
        except Exception as e:
            logger.error(f"[TASK] 任务失败：{task_id}, 错误：{e}", exc_info=True)
            self._update_task_status(task_id, 'FAILED', 0, f'任务失败：{str(e)}', error=str(e))
    
    def _update_task_status(self, task_id: str, status: str, progress: int, 
                           message: str, result=None, error=None, log_entry=None):
        """更新任务状态"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].update({
                    'status': status,
                    'progress': progress,
                    'message': message,
                    'updated_at': datetime.now().isoformat(),
                })
                if result is not None:
                    self.tasks[task_id]['result'] = result
                if error is not None:
                    self.tasks[task_id]['error'] = error
                if log_entry:
                    self.tasks[task_id]['logs'].append({
                        'timestamp': datetime.now().isoformat(),
                        'message': log_entry
                    })
    
    def _update_progress(self, task_id: str, progress: int, message: str, log_entry: str = None):
        """
        更新任务进度（供任务函数调用）
        
        Args:
            task_id: 任务 ID
            progress: 进度百分比 (0-100)
            message: 进度消息
            log_entry: 日志条目
        """
        self._update_task_status(task_id, '运行中', progress, message, log_entry=log_entry)
        logger.info(f"[TASK:{task_id}] {progress}% - {message}")
    
    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        with self.lock:
            if task_id in self.tasks:
                return self.tasks[task_id].copy()
            return None
    
    def get_task_result(self, task_id: str) -> Optional[dict]:
        """获取任务结果"""
        with self.lock:
            if task_id in self.tasks and self.tasks[task_id]['status'] == 'COMPLETED':
                return self.tasks[task_id]['result']
            return None
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """清理旧任务"""
        now = datetime.now()
        with self.lock:
            to_delete = []
            for task_id, task_info in self.tasks.items():
                created_at = datetime.fromisoformat(task_info['created_at'])
                age = (now - created_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_delete.append(task_id)
            
            for task_id in to_delete:
                del self.tasks[task_id]
                logger.info(f"[TASK] 清理旧任务：{task_id}")


# 全局任务管理器实例
task_manager = AsyncTaskManager()


def get_task_manager() -> AsyncTaskManager:
    """获取任务管理器单例"""
    return task_manager
