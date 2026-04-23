"""
钉钉推送系统 - 定时调度器
使用 APScheduler 管理定时推送任务
"""
import logging
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger

logger = logging.getLogger(__name__)


class DingTalkPushScheduler:
    """钉钉推送定时调度器"""
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = BackgroundScheduler(
            timezone='Asia/Shanghai',
            job_defaults={
                'max_instances': 3,  # 同一任务最多3个实例
                'coalesce': True,     # 错过的任务合并执行
                'misfire_grace_time': 60  # 错过60秒内仍执行
            }
        )
        self._job_map = {}  # config_id -> job_id 映射
    
    def init_app(self, app):
        """初始化应用"""
        self.app = app
        
        # 启动调度器
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ 钉钉推送定时调度器已启动")
        
        # 加载已启用的配置
        self._load_enabled_configs()
    
    def _load_enabled_configs(self):
        """加载所有已启用的配置并注册定时任务"""
        if not self.app:
            return
        
        with self.app.app_context():
            try:
                from routes.dingtalk_push.dingtalk_push_routes import get_db_connection
                
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute(
                    "SELECT id, name, schedule_config FROM dingtalk_push_config WHERE enabled = TRUE"
                )
                configs = cursor.fetchall()
                
                cursor.close()
                conn.close()
                
                for config in configs:
                    try:
                        schedule_config = json.loads(config['schedule_config'])
                        self.register_job(config['id'], schedule_config)
                        logger.info(f"✅ 已加载定时任务: {config['name']} (ID: {config['id']})")
                    except Exception as e:
                        logger.error(f"❌ 加载定时任务失败 [{config['name']}]: {e}")
            
            except Exception as e:
                logger.error(f"❌ 加载启用配置失败: {e}")
    
    def register_job(self, config_id, schedule_config):
        """注册定时任务"""
        try:
            # 移除旧任务（确保彻底清除）
            self.remove_job(config_id)
            
            # 等待一小段时间，确保 APScheduler 完成清理
            import time
            time.sleep(0.1)
            
            schedule_type = schedule_config.get('type')
            config = schedule_config.get('config', {})
            
            if schedule_type == 'once':
                # 单次推送
                execute_at = datetime.fromisoformat(config['execute_at'])
                trigger = DateTrigger(run_date=execute_at)
            
            elif schedule_type == 'daily':
                # 每日推送（支持多时间点）
                times = config.get('times', ['08:00'])
                weekdays = config.get('weekdays', [1, 2, 3, 4, 5])
                
                # 为每个时间点创建任务
                for time_str in times:
                    hour, minute = map(int, time_str.split(':'))
                    
                    trigger = CronTrigger(
                        hour=hour,
                        minute=minute,
                        day_of_week=','.join(map(str, weekdays)),
                        timezone=schedule_config.get('timezone', 'Asia/Shanghai')
                    )
                    
                    job_id = f"{config_id}_{time_str.replace(':', '')}"
                    self.scheduler.add_job(
                        func=self._execute_push_task,
                        trigger=trigger,
                        args=[config_id],
                        id=job_id,
                        name=f"钉钉推送-{config['name']}-{time_str}",
                        replace_existing=True
                    )
                    
                    self._job_map[job_id] = config_id
                
                logger.info(f"✅ 已注册每日推送任务 (ID: {config_id}, 时间: {times})")
                return  # 重要：daily 类型在这里返回，不再执行后面的通用任务注册
            
            elif schedule_type == 'weekly':
                # 每周推送
                day_of_week = config.get('day_of_week', 1)
                time_str = config.get('time', '09:00')
                hour, minute = map(int, time_str.split(':'))
                
                trigger = CronTrigger(
                    hour=hour,
                    minute=minute,
                    day_of_week=str(day_of_week),
                    timezone=schedule_config.get('timezone', 'Asia/Shanghai')
                )
            
            elif schedule_type == 'cron':
                # Cron 表达式（支持多时间点，每个时间点创建独立任务）
                times = config.get('times', [])
                weekdays = config.get('weekdays', [1, 2, 3, 4, 5, 6, 7])
                
                if not times:
                    raise ValueError("推送时间不能为空")
                
                # 为每个时间点创建独立任务
                for time_str in times:
                    try:
                        hour, minute = map(int, time_str.split(':'))
                        
                        trigger = CronTrigger(
                            hour=hour,
                            minute=minute,
                            day_of_week=','.join(map(str, weekdays)),
                            timezone=schedule_config.get('timezone', 'Asia/Shanghai')
                        )
                        
                        # 生成唯一 job_id：config_id_时间
                        job_id = f"{config_id}_{time_str.replace(':', '')}"
                        self.scheduler.add_job(
                            func=self._execute_push_task,
                            trigger=trigger,
                            args=[config_id],
                            id=job_id,
                            name=f"钉钉推送-{config_id}-{time_str}",
                            replace_existing=True
                        )
                        
                        self._job_map[job_id] = config_id
                        logger.debug(f"已注册时间点任务: {job_id} ({time_str})")
                    except Exception as e:
                        logger.error(f"注册时间点 {time_str} 失败: {e}")
                
                logger.info(f"✅ 已注册 Cron 推送任务 (ID: {config_id}, 时间点: {times})")
                return  # 重要：cron 类型在这里返回，不再执行后面的通用任务注册
            
            else:
                raise ValueError(f"不支持的调度类型: {schedule_type}")
            
            # 添加任务
            job_id = str(config_id)
            self.scheduler.add_job(
                func=self._execute_push_task,
                trigger=trigger,
                args=[config_id],
                id=job_id,
                name=f"钉钉推送-{config_id}",
                replace_existing=True
            )
            
            self._job_map[job_id] = config_id
            logger.info(f"✅ 已注册定时任务 (ID: {config_id}, 类型: {schedule_type})")
        
        except Exception as e:
            logger.error(f"❌ 注册定时任务失败 (ID: {config_id}): {e}")
            raise
    
    def remove_job(self, config_id):
        """移除定时任务"""
        try:
            # 查找并移除所有相关任务
            jobs_to_remove = [
                job_id for job_id, cid in self._job_map.items() 
                if cid == config_id or job_id == str(config_id)
            ]
            
            # 同时检查 APScheduler 中是否存在以 config_id 开头的任务
            for job in self.scheduler.get_jobs():
                if job.id.startswith(f"{config_id}_") or job.id == str(config_id):
                    if job.id not in jobs_to_remove:
                        jobs_to_remove.append(job.id)
            
            for job_id in jobs_to_remove:
                try:
                    self.scheduler.remove_job(job_id)
                    if job_id in self._job_map:
                        del self._job_map[job_id]
                    logger.debug(f"已移除任务: {job_id}")
                except Exception as e:
                    logger.warning(f"移除任务失败 {job_id}: {e}")
            
            if jobs_to_remove:
                logger.info(f"✅ 已移除 {len(jobs_to_remove)} 个定时任务 (ID: {config_id})")
        
        except Exception as e:
            logger.error(f"❌ 移除定时任务失败 (ID: {config_id}): {e}")
    
    def _execute_push_task(self, config_id):
        """执行推送任务（由调度器调用）"""
        try:
            logger.info(f"⏰ 触发定时推送任务 (ID: {config_id})")
            
            if not self.app:
                logger.error("应用未初始化")
                return
            
            with self.app.app_context():
                # 导入执行函数
                from routes.dingtalk_push.dingtalk_push_routes import (
                    get_db_connection, execute_push_task
                )
                
                # 获取配置
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute(
                    "SELECT * FROM dingtalk_push_config WHERE id = %s AND enabled = TRUE",
                    (config_id,)
                )
                config = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if not config:
                    logger.warning(f"配置不存在或已禁用 (ID: {config_id})")
                    return
                
                # 检查节假日过滤
                schedule_config = json.loads(config['schedule_config'])
                if self._should_skip_holiday(schedule_config):
                    logger.info(f"⏭️  跳过节假日推送 (ID: {config_id})")
                    return
                
                # 执行推送
                execute_push_task(config)
                
                logger.info(f"✅ 定时推送任务完成 (ID: {config_id})")
        
        except Exception as e:
            logger.error(f"❌ 执行定时推送任务失败 (ID: {config_id}): {e}")
    
    def _should_skip_holiday(self, schedule_config):
        """判断是否应该跳过（节假日过滤）"""
        try:
            config = schedule_config.get('config', {})
            
            if not config.get('exclude_holidays'):
                return False
            
            # TODO: 集成节假日判断逻辑
            # 当前简化实现：周末跳过
            from datetime import datetime
            today = datetime.now()
            
            # 如果配置了工作日过滤，且今天是周末
            if config.get('weekdays'):
                # weekday(): 0=周一, 6=周日
                if today.weekday() >= 5:  # 周六或周日
                    return True
            
            return False
        
        except Exception as e:
            logger.error(f"节假日判断失败: {e}")
            return False
    
    def reload_config(self, config_id):
        """重新加载配置（配置更新后调用）"""
        try:
            if not self.app:
                return
            
            with self.app.app_context():
                from routes.dingtalk_push.dingtalk_push_routes import get_db_connection
                
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute(
                    "SELECT id, schedule_config FROM dingtalk_push_config WHERE id = %s",
                    (config_id,)
                )
                config = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                if config:
                    schedule_config = json.loads(config['schedule_config'])
                    self.register_job(config_id, schedule_config)
                    logger.info(f"✅ 已重新加载配置 (ID: {config_id})")
        
        except Exception as e:
            logger.error(f"❌ 重新加载配置失败 (ID: {config_id}): {e}")
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("🛑 钉钉推送定时调度器已关闭")


# 全局调度器实例
push_scheduler = DingTalkPushScheduler()
