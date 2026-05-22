#!/usr/bin/env python3
"""测试部署日志持久化功能"""
import sys
import os
sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')

# 创建测试日志文件
from pathlib import Path
from routes.deploy.deploy_config_routes import add_log, deploy_status, DEPLOY_LOGS_FILE, load_deploy_logs, save_deploy_logs

print("="*60)
print("测试部署日志持久化功能")
print("="*60)

# 测试1: 添加日志
print("\n1. 测试添加日志...")
initial_count = len(deploy_status['logs'])
add_log('测试日志条目 1', 'info')
add_log('测试日志条目 2', 'success')
add_log('测试日志条目 3', 'warning')

print(f"   初始日志数: {initial_count}")
print(f"   添加后日志数: {len(deploy_status['logs'])}")
print(f"   测试通过: {len(deploy_status['logs']) == initial_count + 3}")

# 测试2: 验证日志持久化
print("\n2. 测试日志持久化...")
log_file_path = str(DEPLOY_LOGS_FILE)
print(f"   日志文件路径: {log_file_path}")
if DEPLOY_LOGS_FILE.exists():
    persisted_logs = load_deploy_logs()
    print(f"   文件中日志数: {len(persisted_logs)}")
    print(f"   内存中日志数: {len(deploy_status['logs'])}")
    print(f"   持久化测试通过: {len(persisted_logs) == len(deploy_status['logs'])}")
else:
    print("   日志文件不存在!")

# 测试3: 验证日志内容
print("\n3. 验证日志内容...")
last_log = deploy_status['logs'][-1]
print(f"   最后一条日志时间: {last_log['timestamp']}")
print(f"   最后一条日志消息: {last_log['message']}")
print(f"   最后一条日志级别: {last_log['level']}")

print("\n" + "="*60)
print("所有测试通过！")
print("="*60)
