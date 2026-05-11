#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署管理路由 - Web化部署接口
提供部署、备份、恢复、日志查看等功能
"""
from flask import Blueprint, jsonify, request, Response
import subprocess
import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

deploy_config_bp = Blueprint('deploy_config_bp', __name__, url_prefix='/deploy-config')

# 配置
REMOTE_USER = "root"
REMOTE_HOST = "8.146.228.47"
REMOTE_PATH = "/project/wordToWord"
BACKUP_DIR = "/project/backups"
LOCAL_PORT = 5004
NGINX_PORT = 5173
PROJECT_ROOT = Path(__file__).parent.parent

# 部署状态存储（生产环境应使用Redis）
deploy_status = {
    'is_deploying': False,
    'current_step': '',
    'progress': 0,
    'logs': [],
    'last_deploy_time': None,
    'last_deploy_status': None
}

def ssh_command(cmd, timeout=60):
    """执行SSH远程命令"""
    full_cmd = f'ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no {REMOTE_USER}@{REMOTE_HOST} "{cmd}"'
    try:
        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def add_log(message, level='info'):
    """添加日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = {
        'timestamp': timestamp,
        'message': message,
        'level': level
    }
    deploy_status['logs'].append(log_entry)
    # 只保留最近100条日志
    if len(deploy_status['logs']) > 100:
        deploy_status['logs'] = deploy_status['logs'][-100:]

@deploy_config_bp.route('/status')
def get_deploy_status():
    """获取部署状态"""
    return jsonify({
        'success': True,
        'data': {
            'is_deploying': deploy_status['is_deploying'],
            'current_step': deploy_status['current_step'],
            'progress': deploy_status['progress'],
            'last_deploy_time': deploy_status['last_deploy_time'],
            'last_deploy_status': deploy_status['last_deploy_status']
        }
    })

@deploy_config_bp.route('/logs')
def get_deploy_logs():
    """获取部署日志"""
    return jsonify({
        'success': True,
        'data': {
            'logs': deploy_status['logs'],
            'count': len(deploy_status['logs'])
        }
    })

@deploy_config_bp.route('/logs/stream')
def stream_logs():
    """实时日志流（SSE）"""
    def generate():
        last_count = 0
        while True:
            current_count = len(deploy_status['logs'])
            if current_count > last_count:
                new_logs = deploy_status['logs'][last_count:]
                for log in new_logs:
                    yield f"data: {json.dumps(log)}\n\n"
                last_count = current_count
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@deploy_config_bp.route('/backups', methods=['GET'])
def list_backups():
    """列出所有备份版本"""
    try:
        success, stdout, stderr = ssh_command(f"ls -lt {BACKUP_DIR}/*.tar.gz 2>/dev/null | head -50")
        
        backups = []
        if success and stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 9:
                        filename = parts[-1]
                        size = parts[4]
                        date_str = ' '.join(parts[5:8])
                        
                        # 解析文件名中的时间戳
                        backup_name = os.path.basename(filename)
                        timestamp_str = backup_name.replace('wordToWord_backup_', '').replace('.tar.gz', '')
                        
                        backups.append({
                            'filename': backup_name,
                            'path': filename,
                            'size': size,
                            'date': date_str,
                            'timestamp': timestamp_str,
                            'display_name': f"备份 {timestamp_str}"
                        })
        
        return jsonify({
            'success': True,
            'data': {
                'backups': backups,
                'total': len(backups)
            }
        })
    except Exception as e:
        logger.error(f"获取备份列表失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@deploy_config_bp.route('/deploy', methods=['POST'])
def start_deploy():
    """开始部署"""
    if deploy_status['is_deploying']:
        return jsonify({
            'success': False,
            'message': '部署正在进行中，请稍后再试'
        }), 400
    
    data = request.get_json()
    deploy_type = data.get('type', 'fast')  # fast, full, restore
    backup_file = data.get('backup_file')  # 恢复时指定备份文件
    
    # 启动部署线程
    thread = threading.Thread(
        target=execute_deploy,
        args=(deploy_type, backup_file),
        daemon=True
    )
    thread.start()
    
    return jsonify({
        'success': True,
        'message': '部署任务已启动'
    })

def execute_deploy(deploy_type, backup_file=None):
    """执行部署"""
    try:
        deploy_status['is_deploying'] = True
        deploy_status['logs'] = []
        deploy_status['progress'] = 0
        deploy_status['last_deploy_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if deploy_type == 'restore' and backup_file:
            execute_restore(backup_file)
        elif deploy_type == 'full':
            execute_full_deploy()
        else:
            execute_fast_deploy()
        
        deploy_status['last_deploy_status'] = 'success'
        add_log('✅ 部署完成！', 'success')
        
    except Exception as e:
        logger.error(f"部署失败: {e}")
        add_log(f'❌ 部署失败: {str(e)}', 'error')
        deploy_status['last_deploy_status'] = 'failed'
    finally:
        deploy_status['is_deploying'] = False
        deploy_status['progress'] = 100

def execute_fast_deploy():
    """执行快速部署"""
    add_log('🚀 开始快速部署...', 'info')
    deploy_status['current_step'] = '检测变更文件'
    deploy_status['progress'] = 10
    
    # 检测变更文件
    _, changed_files, _ = run_local_command(
        "git diff --name-only HEAD~1 HEAD",
        cwd=str(PROJECT_ROOT)
    )
    
    if not changed_files:
        _, changed_files, _ = run_local_command(
            "git ls-files --modified",
            cwd=str(PROJECT_ROOT)
        )
    
    if not changed_files:
        add_log('⚠️ 未检测到变更文件', 'warning')
        return
    
    files = [f.strip() for f in changed_files.split('\n') if f.strip()]
    add_log(f'📦 检测到 {len(files)} 个变更文件', 'info')
    
    # 分类文件
    backend_files = [f for f in files if f.endswith('.py')]
    frontend_files = [f for f in files if f.startswith('frontend/src/') or f.endswith('.vue')]
    
    # 上传后端文件
    if backend_files:
        deploy_status['current_step'] = '上传后端文件'
        deploy_status['progress'] = 30
        add_log(f'📤 上传 {len(backend_files)} 个后端文件...', 'info')
        
        for file in backend_files:
            local_path = PROJECT_ROOT / file
            if local_path.exists():
                remote_path = f"{REMOTE_PATH}/{file}"
                success = scp_upload(str(local_path), remote_path)
                if success:
                    add_log(f'✓ {file}', 'success')
                else:
                    add_log(f'✗ {file} 上传失败', 'error')
    
    # 上传前端文件（需要构建）
    if frontend_files:
        deploy_status['current_step'] = '构建前端'
        deploy_status['progress'] = 50
        add_log('🔨 检测到前端文件变更，开始构建...', 'info')
        
        success, stdout, stderr = run_local_command(
            "npm run build",
            cwd=str(PROJECT_ROOT / "frontend")
        )
        
        if success:
            add_log('✅ 前端构建成功', 'success')
            
            deploy_status['current_step'] = '上传前端文件'
            deploy_status['progress'] = 70
            add_log('📤 上传前端构建产物...', 'info')
            
            # 清空远程dist
            ssh_command(f"rm -rf {REMOTE_PATH}/frontend/dist/*")
            
            # 上传dist
            local_dist = str(PROJECT_ROOT / "frontend" / "dist") + "/*"
            remote_dist = f"{REMOTE_PATH}/frontend/dist/"
            success = scp_upload(local_dist, remote_dist, recursive=True)
            
            if success:
                add_log('✅ 前端文件上传成功', 'success')
            else:
                add_log('❌ 前端文件上传失败', 'error')
        else:
            add_log(f'❌ 前端构建失败: {stderr}', 'error')
    
    # 重启服务
    deploy_status['current_step'] = '重启服务'
    deploy_status['progress'] = 90
    add_log('🔄 重启后端服务...', 'info')
    
    ssh_command(f"cd {REMOTE_PATH} && pkill -f 'python app.py' || true")
    time.sleep(2)
    
    start_cmd = f"""
    cd {REMOTE_PATH}
    source .venv/bin/activate
    export PORT={LOCAL_PORT}
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    """
    
    ssh_command(start_cmd)
    time.sleep(3)
    
    # 验证
    _, port_check, _ = ssh_command(f"lsof -i:{LOCAL_PORT} | head -2")
    if port_check:
        add_log(f'✅ 服务重启成功，端口 {LOCAL_PORT} 监听正常', 'success')
    else:
        add_log('⚠️ 端口未监听，请检查日志', 'warning')

def execute_full_deploy():
    """执行完整部署"""
    add_log('🚀 开始完整部署...', 'info')
    
    # Git提交
    deploy_status['current_step'] = 'Git提交'
    deploy_status['progress'] = 10
    add_log('📝 Git提交...', 'info')
    
    _, status, _ = run_local_command("git status --porcelain", cwd=str(PROJECT_ROOT))
    if status:
        run_local_command("git add -A", cwd=str(PROJECT_ROOT))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_local_command(f'git commit -m "Auto deploy: {timestamp}"', cwd=str(PROJECT_ROOT))
        add_log('✅ Git提交完成', 'success')
    
    # Git推送
    deploy_status['current_step'] = 'Git推送'
    deploy_status['progress'] = 20
    add_log('📤 Git推送到远程...', 'info')
    
    success, _, stderr = run_local_command("git push origin q/dev", cwd=str(PROJECT_ROOT))
    if success:
        add_log('✅ Git推送成功', 'success')
    else:
        add_log(f'❌ Git推送失败: {stderr}', 'error')
        return
    
    # 执行快速部署的剩余步骤
    execute_fast_deploy()

def execute_restore(backup_file):
    """执行恢复操作"""
    add_log(f'🔄 开始恢复到备份: {backup_file}', 'info')
    
    deploy_status['current_step'] = '停止服务'
    deploy_status['progress'] = 20
    add_log('⏹️ 停止当前服务...', 'info')
    ssh_command(f"cd {REMOTE_PATH} && pkill -f 'python app.py' || true")
    time.sleep(2)
    
    deploy_status['current_step'] = '恢复备份'
    deploy_status['progress'] = 50
    add_log('📦 解压备份文件...', 'info')
    
    backup_path = f"{BACKUP_DIR}/{backup_file}"
    restore_cmd = f"""
    cd /project
    tar -xzf {backup_path}
    echo "恢复完成"
    """
    
    success, stdout, stderr = ssh_command(restore_cmd, timeout=120)
    
    if success:
        add_log('✅ 备份恢复成功', 'success')
    else:
        add_log(f'❌ 恢复失败: {stderr}', 'error')
        return
    
    # 重启服务
    deploy_status['current_step'] = '重启服务'
    deploy_status['progress'] = 80
    add_log('🔄 重启服务...', 'info')
    
    start_cmd = f"""
    cd {REMOTE_PATH}
    source .venv/bin/activate
    export PORT={LOCAL_PORT}
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    """
    
    ssh_command(start_cmd)
    time.sleep(3)
    
    # 验证
    _, port_check, _ = ssh_command(f"lsof -i:{LOCAL_PORT} | head -2")
    if port_check:
        add_log('✅ 服务重启成功', 'success')
    else:
        add_log('⚠️ 端口未监听', 'warning')

def execute_create_backup():
    """创建备份"""
    add_log('💾 创建备份...', 'info')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"wordToWord_backup_{timestamp}.tar.gz"
    backup_path = f"{BACKUP_DIR}/{backup_name}"
    
    backup_cmd = f"""
    mkdir -p {BACKUP_DIR}
    cd /project
    tar -czf {backup_path} \\
        --exclude='node_modules' \\
        --exclude='.venv' \\
        --exclude='__pycache__' \\
        --exclude='*.pyc' \\
        --exclude='logs/*.log' \\
        wordToWord/
    echo "备份完成: {backup_name}"
    """
    
    success, stdout, stderr = ssh_command(backup_cmd, timeout=120)
    
    if success:
        add_log(f'✅ 备份创建成功: {backup_name}', 'success')
        return backup_name
    else:
        add_log(f'❌ 备份失败: {stderr}', 'error')
        return None

@deploy_config_bp.route('/backup', methods=['POST'])
def create_backup():
    """创建备份"""
    if deploy_status['is_deploying']:
        return jsonify({
            'success': False,
            'message': '部署正在进行中，请稍后再试'
        }), 400
    
    thread = threading.Thread(target=execute_create_backup, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': '备份任务已启动'
    })

@deploy_config_bp.route('/restart', methods=['POST'])
def restart_service():
    """重启服务"""
    if deploy_status['is_deploying']:
        return jsonify({
            'success': False,
            'message': '部署正在进行中，请稍后再试'
        }), 400
    
    try:
        add_log('🔄 手动重启服务...', 'info')
        
        # 停止
        ssh_command(f"cd {REMOTE_PATH} && pkill -f 'python app.py' || true")
        time.sleep(2)
        
        # 启动
        start_cmd = f"""
        cd {REMOTE_PATH}
        source .venv/bin/activate
        export PORT={LOCAL_PORT}
        nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
        """
        
        ssh_command(start_cmd)
        time.sleep(3)
        
        # 验证
        _, port_check, _ = ssh_command(f"lsof -i:{LOCAL_PORT} | head -2")
        if port_check:
            add_log('✅ 服务重启成功', 'success')
            return jsonify({'success': True, 'message': '服务重启成功'})
        else:
            add_log('⚠️ 端口未监听', 'warning')
            return jsonify({'success': False, 'message': '服务重启失败，请检查日志'})
            
    except Exception as e:
        add_log(f'❌ 重启失败: {str(e)}', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500

@deploy_config_bp.route('/server-logs', methods=['GET'])
def get_server_logs():
    """获取服务器日志"""
    lines = request.args.get('lines', 50, type=int)
    log_type = request.args.get('type', 'backend')  # backend, nginx, error
    
    try:
        if log_type == 'backend':
            cmd = f"cd {REMOTE_PATH} && tail -n {lines} logs/backend.log"
        elif log_type == 'nginx':
            cmd = f"tail -n {lines} {REMOTE_PATH}/logs/nginx_{NGINX_PORT}_access.log"
        elif log_type == 'error':
            cmd = f"tail -n {lines} {REMOTE_PATH}/logs/nginx_{NGINX_PORT}_error.log"
        else:
            cmd = f"cd {REMOTE_PATH} && tail -n {lines} logs/backend.log"
        
        success, stdout, stderr = ssh_command(cmd)
        
        if success:
            return jsonify({
                'success': True,
                'data': {
                    'logs': stdout,
                    'lines': lines,
                    'type': log_type
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'获取日志失败: {stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

def run_local_command(cmd, cwd=None, timeout=60):
    """执行本地命令"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def scp_upload(local_path, remote_path, recursive=False):
    """SCP上传文件"""
    flag = "-r" if recursive else ""
    cmd = f"scp -o LogLevel=ERROR -o StrictHostKeyChecking=no {flag} {local_path} {REMOTE_USER}@{REMOTE_HOST}:{remote_path}"
    success, _, _ = run_local_command(cmd)
    return success
