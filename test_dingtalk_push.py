#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试钉钉推送配置和执行
"""
import os
from dotenv import load_dotenv
load_dotenv()

from utils.dingtalk_schedule_pusher import DingTalkSchedulePusher, decrypt_webhook
from routes.排班.paiBanNew_v2 import DB_CONFIG, RosterDB
from datetime import date, timedelta

# 检查配置
print("=" * 60)
print("钉钉推送配置检查")
print("=" * 60)

db = RosterDB(DB_CONFIG)
if db.connect():
    sql = "SELECT * FROM dingtalk_schedule_config WHERE enabled = 1"
    configs = db.query(sql)
    print(f"\n启用的配置数量: {len(configs)}\n")
    
    for c in configs:
        print(f"配置ID: {c['id']}")
        print(f"Webhook (前50字符): {str(c['webhook_url'])[:50]}")
        print(f"推送时间: {c['schedule_times']}")
        print(f"时段: {c.get('time_slots')}")
        print(f"描述: {c.get('description', '')}")
        
        # 尝试解密
        decrypted = decrypt_webhook(c['webhook_url'])
        print(f"解密后Webhook (前50字符): {str(decrypted)[:50]}")
        print()
    
    db.close()
else:
    print("数据库连接失败")
    exit(1)

# 手动执行推送测试
print("\n" + "=" * 60)
print("执行推送测试")
print("=" * 60)

pusher = DingTalkSchedulePusher()

# 手动执行推送
if configs:
    config_id = configs[0]['id']
    print(f"\n开始执行配置ID {config_id} 的推送任务...")
    
    try:
        # 获取配置
        db = RosterDB(pusher.db_config)
        if not db.connect():
            print("[ERROR] 数据库连接失败")
            exit(1)
        
        sql = "SELECT * FROM dingtalk_schedule_config WHERE id = %s AND enabled = 1"
        results = db.query(sql, (config_id,))
        
        if not results:
            print(f"[WARNING] 未找到配置或配置已禁用 (ID: {config_id})")
            exit(1)
        
        config = results[0]
        encrypted_webhook = config['webhook_url']
        time_slots_json = config.get('time_slots')
        
        # 解密 Webhook URL
        webhook_url = decrypt_webhook(encrypted_webhook)
        print(f"\n解密后的Webhook: {webhook_url[:50]}...")
        
        # 解析时段列表
        import json
        time_slots = json.loads(time_slots_json) if time_slots_json else []
        print(f"时段列表: {time_slots}")
        
        db.close()
        
        # 构建消息（推送今天和明天的排班）
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        start_date = today.strftime('%Y-%m-%d')
        end_date = tomorrow.strftime('%Y-%m-%d')
        
        print(f"\n查询排班数据: {start_date} 至 {end_date}")
        msg_content = pusher.build_markdown_message(start_date, end_date, time_slots if time_slots else None)
        
        if not msg_content:
            print("[WARNING] 没有可推送的排班数据")
            exit(1)
        
        print(f"\n生成的消息内容 (前200字符):\n{msg_content[:200]}...")
        
        # 发送消息
        print("\n正在发送钉钉消息...")
        success = pusher.send_dingtalk_message(webhook_url, msg_content)
        
        if success:
            print("[SUCCESS] 推送成功！")
        else:
            print("[ERROR] 推送失败！")
            
    except Exception as e:
        print(f"[ERROR] 执行推送任务异常: {e}")
        import traceback
        traceback.print_exc()
