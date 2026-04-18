#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉排班消息定时推送服务
使用APScheduler实现基于cron表达式的定时推送
"""
import os
import sys
import json
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import requests

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.排班.paiBanNew_v2 import DB_CONFIG, RosterDB


class DingTalkSchedulePusher:
    """钉钉排班定时推送器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.db_config = DB_CONFIG
    
    def get_schedule_configs(self):
        """获取所有启用的定时推送配置"""
        try:
            db = RosterDB(self.db_config)
            if not db.connect():
                print("[ERROR] 数据库连接失败")
                return []
            
            sql = "SELECT * FROM dingtalk_schedule_config WHERE enabled = 1"
            results = db.query(sql)
            db.close()
            
            return results if results else []
        except Exception as e:
            print(f"[ERROR] 获取配置失败: {e}")
            return []
    
    def build_markdown_message(self, start_date, end_date, time_slots=None):
        """构建Markdown格式的排班消息"""
        try:
            db = RosterDB(self.db_config)
            if not db.connect():
                return None
            
            # 查询指定日期范围的排班数据
            sql = """
            SELECT r.*
            FROM roster r
            WHERE r.date BETWEEN %s AND %s
            ORDER BY r.date, r.time_slot, r.is_main DESC
            """
            
            results = db.query(sql, (start_date, end_date))
            db.close()
            
            if not results:
                return None
            
            # 按日期和时段分组
            grouped_data = {}
            for record in results:
                date_key = record['date'].strftime('%Y-%m-%d') if hasattr(record['date'], 'strftime') else str(record['date'])
                time_slot = record['time_slot']
                
                # 如果指定了时段过滤，则只推送指定的时段
                if time_slots and time_slot not in time_slots:
                    continue
                
                if date_key not in grouped_data:
                    grouped_data[date_key] = {}
                
                if time_slot not in grouped_data[date_key]:
                    grouped_data[date_key][time_slot] = []
                
                grouped_data[date_key][time_slot].append(record)
            
            # 构建钉钉消息内容（优化后的Markdown格式）
            today = datetime.now().date()
            msg_content = "# 📅 排班信息推送\n\n"
            
            # 按日期排序
            sorted_dates = sorted(grouped_data.keys())
            
            for date_str in sorted_dates:
                day_data = grouped_data[date_str]
                
                # 计算星期和相对日期描述
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
                
                # 判断是今天、明天还是其他日期
                delta = (date_obj - today).days
                if delta == 0:
                    date_label = f"**今天** {date_str} ({weekday})"
                elif delta == 1:
                    date_label = f"**明天** {date_str} ({weekday})"
                elif delta == -1:
                    date_label = f"**昨天** {date_str} ({weekday})"
                else:
                    date_label = f"**{date_str}** ({weekday})"
                
                msg_content += f"### {date_label}\n\n"
                
                # 按时段排序（按时间顺序）
                time_slot_order = [
                    '8:00～9:00',
                    '8:00～12:00',
                    '9:00～12:00',
                    '13:30～17:30',
                    '13:30～18:00',
                    '17:30～21:30',
                    '18:00～21:00'
                ]
                
                sorted_slots = sorted(day_data.keys(), 
                                    key=lambda x: time_slot_order.index(x) if x in time_slot_order else 999)
                
                for time_slot in sorted_slots:
                    staff_records = day_data[time_slot]
                    
                    # 提取主班和辅班
                    main_staff = [r['staff_name'] for r in staff_records if r['is_main']]
                    backup_staff = [r['staff_name'] for r in staff_records if not r['is_main']]
                    
                    staff_display = '、'.join(main_staff + backup_staff) if (main_staff + backup_staff) else '空闲'
                    
                    msg_content += f"- **{time_slot}**: {staff_display}\n"
                
                msg_content += "\n---\n\n"
            
            # 添加查看详情链接（Markdown格式）
            schedule_view_url = "https://alidocs.dingtalk.com/i/nodes/20eMKjyp81LOavDgf46AORZwJxAZB1Gv?utm_scene=person_space&iframeQuery=viewId%3Drm8nwl6hqzo0v1952seh4%26sheetId%3Dhe1d5bovtjfxcies7i3fi"
            msg_content += f"[查看完整排班]({schedule_view_url})\n"
            
            return msg_content
            
        except Exception as e:
            print(f"[ERROR] 构建消息失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def send_dingtalk_message(self, webhook_url, msg_content):
        """发送钉钉消息（ActionCard格式）"""
        try:
            # 使用ActionCard格式，钉钉会自动在末尾渲染链接为按钮
            dingtalk_data = {
                "msgtype": "actionCard",
                "actionCard": {
                    "title": "排班信息推送",
                    "text": msg_content,
                    "btnOrientation": "0"
                }
            }
            
            response = requests.post(
                webhook_url,
                headers={'Content-Type': 'application/json'},
                data=json.dumps(dingtalk_data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"[SUCCESS] 钉钉消息推送成功")
                    return True
                else:
                    print(f"[ERROR] 钉钉推送失败: {result.get('errmsg', '未知错误')}")
                    return False
            else:
                print(f"[ERROR] 钉钉推送失败，HTTP状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[ERROR] 发送消息异常: {e}")
            return False
    
    def execute_push(self, config_id):
        """执行推送任务"""
        try:
            print(f"\n[{datetime.now()}] 开始执行推送任务 (配置ID: {config_id})")
            
            # 获取配置
            db = RosterDB(self.db_config)
            if not db.connect():
                print("[ERROR] 数据库连接失败")
                return
            
            sql = "SELECT * FROM dingtalk_schedule_config WHERE id = %s AND enabled = 1"
            results = db.query(sql, (config_id,))
            
            if not results:
                print(f"[WARNING] 未找到配置或配置已禁用 (ID: {config_id})")
                db.close()
                return
            
            config = results[0]
            webhook_url = config['webhook_url']
            time_slots_json = config.get('time_slots')
            
            # 解析时段列表
            time_slots = json.loads(time_slots_json) if time_slots_json else []
            
            db.close()
            
            # 构建消息（推送今天和明天的排班）
            today = date.today()
            tomorrow = today + timedelta(days=1)
            
            start_date = today.strftime('%Y-%m-%d')
            end_date = tomorrow.strftime('%Y-%m-%d')
            
            msg_content = self.build_markdown_message(start_date, end_date, time_slots if time_slots else None)
            
            if not msg_content:
                print("[WARNING] 没有可推送的排班数据")
                return
            
            # 发送消息
            success = self.send_dingtalk_message(webhook_url, msg_content)
            
            if success:
                print(f"[SUCCESS] 推送任务完成 (配置ID: {config_id})")
            else:
                print(f"[ERROR] 推送任务失败 (配置ID: {config_id})")
                
        except Exception as e:
            print(f"[ERROR] 执行推送任务异常: {e}")
            import traceback
            traceback.print_exc()
    
    def schedule_time_to_cron(self, time_str):
        """将时间字符串转换为cron表达式
        例如: "08:00" -> cron(hour=8, minute=0)
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            return CronTrigger(hour=hour, minute=minute)
        except Exception as e:
            print(f"[ERROR] 时间格式转换失败: {time_str}, 错误: {e}")
            return None
    
    def load_and_schedule_tasks(self):
        """重新加载配置并创建定时任务（先清除所有旧任务再重建）"""
        try:
            # 第一步：清除所有现有的钉钉推送任务
            existing_jobs = self.scheduler.get_jobs()
            dingtalk_jobs = [job for job in existing_jobs if job.id.startswith('dingtalk_push_')]
            for job in dingtalk_jobs:
                self.scheduler.remove_job(job.id)
            
            print(f"[INFO] 已清除 {len(dingtalk_jobs)} 个旧的定时任务")
            
            # 第二步：从数据库加载所有启用的配置
            configs = self.get_schedule_configs()
            
            if not configs:
                print("[INFO] 没有启用的定时推送配置")
                return
            
            print(f"[INFO] 重新加载 {len(configs)} 个定时推送配置")
            
            for config in configs:
                config_id = config['id']
                schedule_times_json = config.get('schedule_times')
                description = config.get('description', '')
                
                if not schedule_times_json:
                    print(f"[WARNING] 配置 {config_id} 没有设置推送时间，跳过")
                    continue
                
                try:
                    schedule_times = json.loads(schedule_times_json)
                    
                    if not schedule_times:
                        print(f"[WARNING] 配置 {config_id} 的推送时间为空，跳过")
                        continue
                    
                    for time_str in schedule_times:
                        trigger = self.schedule_time_to_cron(time_str)
                        
                        if trigger:
                            job_id = f"dingtalk_push_{config_id}_{time_str.replace(':', '_')}"
                            
                            # 添加新任务
                            self.scheduler.add_job(
                                func=self.execute_push,
                                trigger=trigger,
                                args=[config_id],
                                id=job_id,
                                name=f"钉钉推送-{description}-{time_str}",
                                replace_existing=True
                            )
                            
                            print(f"[INFO] 已创建定时任务: {job_id} (每天 {time_str} 执行)")
                            
                except json.JSONDecodeError as je:
                    print(f"[ERROR] 配置 {config_id} 的时间解析失败: {je}")
                except Exception as e:
                    print(f"[ERROR] 配置 {config_id} 的任务创建失败: {e}")
            
            # 打印当前任务列表
            current_jobs = self.scheduler.get_jobs()
            dingtalk_jobs = [job for job in current_jobs if job.id.startswith('dingtalk_push_')]
            print(f"\n[INFO] 当前共有 {len(dingtalk_jobs)} 个定时任务:")
            for job in dingtalk_jobs:
                next_run = job.next_run_time
                if next_run:
                    print(f"  - {job.name}: 下次执行时间 {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                    
        except Exception as e:
            print(f"[ERROR] 重新加载定时任务失败: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self):
        """启动调度器"""
        # 加载并创建任务
        self.load_and_schedule_tasks()
        
        # 启动调度器
        self.scheduler.start()
        print("[INFO] 钉钉定时推送服务已启动")
        
        # 打印下次执行时间
        jobs = self.scheduler.get_jobs()
        if jobs:
            print(f"\n[INFO] 当前共有 {len(jobs)} 个定时任务:")
            for job in jobs:
                next_run = job.next_run_time
                if next_run:
                    print(f"  - {job.name}: 下次执行时间 {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def stop(self):
        """停止调度器"""
        self.scheduler.shutdown()
        print("[INFO] 钉钉定时推送服务已停止")


def main():
    """主函数"""
    pusher = DingTalkSchedulePusher()
    
    try:
        pusher.start()
        
        # 保持运行
        import time
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n[INFO] 收到中断信号，正在停止服务...")
        pusher.stop()
    except Exception as e:
        print(f"[ERROR] 服务运行异常: {e}")
        pusher.stop()


if __name__ == "__main__":
    main()
