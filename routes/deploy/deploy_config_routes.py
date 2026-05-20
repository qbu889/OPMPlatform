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

# 配置存储文件
CONFIG_FILE = Path(__file__).parent / 'deploy_config.json'

# 默认配置
DEFAULT_CONFIG = {
    'remote_user': 'root',
    'remote_host': '8.146.228.47',
    'remote_path': '/project/wordToWord',
    'backup_dir': '/project/backups',
    'local_port': 5004,
    'nginx_port': 5173,
    'git_branch': 'q/dev',
    'ssh_timeout': 60,
    'deploy_timeout': 120
}


def get_deploy_config():
    """获取配置"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()


def save_deploy_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# 加载配置
config = get_deploy_config()

# 动态配置
REMOTE_USER = config.get('remote_user', DEFAULT_CONFIG['remote_user'])
REMOTE_HOST = config.get('remote_host', DEFAULT_CONFIG['remote_host'])
REMOTE_PATH = config.get('remote_path', DEFAULT_CONFIG['remote_path'])
BACKUP_DIR = config.get('backup_dir', DEFAULT_CONFIG['backup_dir'])
LOCAL_PORT = config.get('local_port', DEFAULT_CONFIG['local_port'])
NGINX_PORT = config.get('nginx_port', DEFAULT_CONFIG['nginx_port'])
# PROJECT_ROOT 指向项目根目录（deploy.py 所在位置）
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 部署状态存储（生产环境应使用Redis）
deploy_status = {
    'is_deploying': False,
    'current_step': '',
    'progress': 0,
    'logs': [],
    'last_deploy_time': None,
    'last_deploy_status': None
}


def ssh_command(cmd, timeout=None):
    """执行SSH远程命令（如果在本地则直接执行）"""
    if timeout is None:
        timeout = config.get('ssh_timeout', DEFAULT_CONFIG['ssh_timeout'])

    # 检查是否是本地执行：通过尝试读取 REMOTE_PATH 下的文件来判断
    # 如果 REMOTE_PATH 存在且可访问，说明已经在目标服务器上
    is_local = os.path.exists(REMOTE_PATH)

    # 强制写入调试信息到文件
    with open('/tmp/ssh_debug.log', 'a') as f:
        f.write(f"{datetime.now()} - is_local: {is_local}, REMOTE_PATH: {REMOTE_PATH}, cmd: {cmd[:50]}\n")

    logger.info(f"ssh_command - is_local: {is_local}, REMOTE_PATH: {REMOTE_PATH}")

    if is_local:
        # 本地直接执行
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=REMOTE_PATH
            )
            logger.info(f"本地执行成功: {cmd[:50]}")
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            logger.warning(f"本地执行命令失败: {e}, 尝试 SSH")
            # 如果本地执行失败，回退到 SSH
            pass

    # 远程执行（SSH）
    logger.info(f"使用 SSH 执行: {config['remote_user']}@{config['remote_host']}")
    full_cmd = f'ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no {config["remote_user"]}@{config["remote_host"]} "{cmd}"'
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


@deploy_config_bp.route('/backups/<filename>', methods=['DELETE'])
def delete_backup(filename):
    """删除备份文件"""
    try:
        backup_path = f"{BACKUP_DIR}/{filename}"
        
        # 验证文件存在
        _, check, _ = ssh_command(f"test -f {backup_path} && echo 'exists' || echo 'not found'")
        if 'exists' not in check:
            return jsonify({
                'success': False,
                'message': f'备份文件不存在: {filename}'
            }), 404
        
        # 删除文件
        ssh_command(f"rm -f {backup_path}")
        
        # 验证删除成功
        _, verify, _ = ssh_command(f"test -f {backup_path} && echo 'exists' || echo 'deleted'")
        if 'deleted' in verify:
            add_log(f'🗑️ 已删除备份: {filename}', 'info')
            return jsonify({
                'success': True,
                'message': f'备份 {filename} 已删除'
            })
        else:
            return jsonify({
                'success': False,
                'message': '删除失败'
            }), 500
            
    except Exception as e:
        logger.error(f"删除备份失败: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@deploy_config_bp.route('/backups/<filename>/download', methods=['GET'])
def download_backup(filename):
    """下载备份文件"""
    try:
        import tempfile
        import shutil
        
        backup_path = f"{BACKUP_DIR}/{filename}"
        
        # 验证文件存在
        _, check, _ = ssh_command(f"test -f {backup_path} && echo 'exists' || echo 'not found'")
        if 'exists' not in check:
            return jsonify({
                'success': False,
                'message': f'备份文件不存在: {filename}'
            }), 404
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        local_file = os.path.join(temp_dir, filename)
        
        try:
            # 从远程服务器下载文件
            scp_cmd = f"scp -o LogLevel=ERROR -o StrictHostKeyChecking=no {REMOTE_USER}@{REMOTE_HOST}:{backup_path} {local_file}"
            success, stdout, stderr = run_local_command(scp_cmd)
            
            if not success:
                return jsonify({
                    'success': False,
                    'message': f'下载失败: {stderr}'
                }), 500
            
            # 返回文件
            return send_file(
                local_file,
                mimetype='application/gzip',
                as_attachment=True,
                download_name=filename
            )
        finally:
            # 清理临时文件（延迟删除，让 Flask 先发送文件）
            import threading
            def cleanup():
                time.sleep(2)
                shutil.rmtree(temp_dir, ignore_errors=True)
            threading.Thread(target=cleanup, daemon=True).start()
            
    except Exception as e:
        logger.error(f"下载备份失败: {e}")
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


def execute_fast_deploy(skip_initial_steps=False):
    """执行快速部署

    Args:
        skip_initial_steps: 是否跳过前面的步骤（由 execute_full_deploy 调用时使用）
    """
    if not skip_initial_steps:
        add_log('🚀 开始快速部署...', 'info')
        add_log('=' * 50, 'info')

        # ====== 步骤 1: 检测变更文件 ======
        deploy_status['current_step'] = '检测变更文件'
        deploy_status['progress'] = 10
        add_log('📝 步骤 1: 检测变更文件', 'info')

        # 获取最新提交信息
        _, last_commit, _ = run_local_command("git log -1 --oneline", cwd=str(PROJECT_ROOT))
        if last_commit:
            add_log(f'   最新提交: {last_commit}', 'info')

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
            add_log('️ 未检测到变更文件，将使用默认核心文件', 'warning')
            changed_files = "app.py config.py routes/kafka/kafka_generator_routes.py"

        files = [f.strip() for f in changed_files.split('\n') if f.strip()]
        add_log(f'📦 检测到 {len(files)} 个变更文件', 'info')

        # 显示文件列表（前20个）
        for i, f in enumerate(files[:20]):
            add_log(f'   - {f}', 'info')
        if len(files) > 20:
            add_log(f'   ... 还有 {len(files) - 20} 个文件', 'info')

        # 分类文件
        backend_files = [f for f in files if f.endswith('.py')]
        frontend_files = [f for f in files if f.startswith('frontend/src/') or f.endswith('.vue') or f.endswith('.js')]

        add_log(f'   后端文件: {len(backend_files)} 个', 'info')
        add_log(f'   前端文件: {len(frontend_files)} 个', 'info')
    else:
        # 从完整部署调用，进度从 20% 开始
        backend_files = []
        frontend_files = []

    # ====== 步骤 2: 创建备份 ======
    deploy_status['current_step'] = '创建备份'
    deploy_status['progress'] = 20
    if skip_initial_steps:
        add_log('📝 步骤 2: 创建远程备份', 'info')
    else:
        add_log('', 'info')
        add_log('📝 步骤 2: 创建远程备份', 'info')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"wordToWord_backup_{timestamp}.tar.gz"
    backup_path = f"{BACKUP_DIR}/{backup_name}"

    backup_cmd = f"""mkdir -p {BACKUP_DIR} && cd /project && tar -czf {backup_path} --exclude='node_modules' --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='logs/*.log' wordToWord/"""

    success, stdout, stderr = ssh_command(backup_cmd, timeout=120)
    if success:
        add_log(f'✅ 备份创建成功: {backup_name}', 'success')
    else:
        add_log(f'⚠️ 备份可能有问题: {stderr[:100]}', 'warning')

    # ====== 步骤 3: 上传后端文件 ======
    if backend_files:
        deploy_status['current_step'] = '上传后端文件'
        deploy_status['progress'] = 30
        add_log('', 'info')
        add_log('📝 步骤 3: 上传后端文件（打包方式）', 'info')
        add_log(f'   准备上传 {len(backend_files)} 个后端文件...', 'info')

        # 准备文件列表
        add_log('   准备上传的文件列表:', 'info')
        upload_list = []
        for file in backend_files:
            local_path = PROJECT_ROOT / file
            if local_path.exists():
                upload_list.append(file)
                add_log(f'      + {file}', 'info')
            else:
                add_log(f'      ⚠️ {file} (文件不存在，跳过)', 'warning')

        # 打包上传
        if upload_list:
            import tempfile
            import shutil
            temp_dir = tempfile.mkdtemp()
            tar_path = os.path.join(temp_dir, "backend_update.tar.gz")

            try:
                # 复制文件到临时目录
                for file in upload_list:
                    src = PROJECT_ROOT / file
                    dest = Path(temp_dir) / file
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)

                # 打包
                add_log('   正在打包...', 'info')
                success, _, stderr = run_local_command(
                    f"tar -czf {tar_path} .",
                    cwd=temp_dir
                )

                if not success:
                    add_log(f'   ❌ 打包失败: {stderr}', 'error')
                else:
                    # 显示压缩包内容
                    success, content, _ = run_local_command(f"tar -tzf {tar_path} | head -10", cwd=temp_dir)
                    if content:
                        add_log('   压缩包内容预览:', 'info')
                        for line in content.split('\n')[:5]:
                            add_log(f'      {line}', 'info')

                    # 上传压缩包
                    add_log('   上传压缩包到服务器...', 'info')
                    remote_tar = "/tmp/backend_update.tar.gz"
                    flag = "-r"
                    scp_cmd = f"scp -o LogLevel=ERROR -o StrictHostKeyChecking=no {flag} {tar_path} {REMOTE_USER}@{REMOTE_HOST}:{remote_tar}"
                    scp_success, _, _ = run_local_command(scp_cmd)

                    if not scp_success:
                        add_log('   ❌ 上传压缩包失败', 'error')
                    else:
                        # 远程解压
                        add_log('   远程解压...', 'info')
                        ssh_cmd = f"""cd {REMOTE_PATH} && tar -xzf {remote_tar} && rm -f {remote_tar} && echo '解压成功'"""
                        success, stdout, stderr = ssh_command(ssh_cmd)

                        if success:
                            add_log('   ✅ 后端文件上传并解压成功', 'success')

                            # 验证关键文件（前5个）
                            add_log('   验证关键文件:', 'info')
                            for file in upload_list[:5]:
                                check_cmd = f"test -f {REMOTE_PATH}/{file} && echo '✓ {file}' || echo '✗ {file} (缺失)'"
                                _, output, _ = ssh_command(check_cmd)
                                add_log(f'      {output}', 'info')
                        else:
                            add_log(f'    远程解压失败: {stderr}', 'error')

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

    # ====== 步骤 4: 处理前端文件 ======
    if frontend_files:
        deploy_status['current_step'] = '构建前端'
        deploy_status['progress'] = 50
        add_log('', 'info')
        add_log('📝 步骤 4: 处理前端文件', 'info')
        add_log('🔨 检测到前端文件变更，开始构建...', 'info')

        success, stdout, stderr = run_local_command(
            "npm run build",
            cwd=str(PROJECT_ROOT / "frontend"),
            timeout=180
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
            flag = "-r"
            scp_cmd = f"scp -o LogLevel=ERROR -o StrictHostKeyChecking=no {flag} {local_dist} {REMOTE_USER}@{REMOTE_HOST}:{remote_dist}"
            scp_success, _, _ = run_local_command(scp_cmd, timeout=120)

            if scp_success:
                # 验证文件数量
                _, remote_count, _ = ssh_command(f"find {REMOTE_PATH}/frontend/dist -type f | wc -l")
                local_count = sum(1 for _ in (PROJECT_ROOT / "frontend" / "dist").rglob('*') if _.is_file())

                add_log(f'   📊 本地文件数: {local_count}, 远程文件数: {remote_count.strip()}', 'info')

                if remote_count.strip().isdigit() and int(remote_count.strip()) > 0:
                    add_log('✅ 前端文件上传成功', 'success')
                else:
                    add_log('❌ 前端文件验证失败', 'error')
            else:
                add_log('❌ 前端文件上传失败', 'error')
        else:
            add_log(f'❌ 前端构建失败: {stderr[:200]}', 'error')
    else:
        add_log('ℹ️ 无前端文件变更，跳过构建', 'info')

    # ====== 步骤 5: 重启服务 ======
    deploy_status['current_step'] = '重启服务'
    deploy_status['progress'] = 90
    add_log('', 'info')
    add_log('📝 步骤 5: 重启后端服务', 'info')

    # 5.1 停止旧进程（强制清理，避免僵尸进程）
    add_log('   5.1 停止现有服务...', 'info')
    ssh_command(f"cd {REMOTE_PATH} && pkill -9 -f '.venv/bin/python.*app.py' || true")
    time.sleep(2)
    
    # 验证进程已清理
    _, remaining, _ = ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | wc -l")
    if remaining and int(remaining.strip()) > 0:
        add_log(f'   ⚠️ 发现 {remaining.strip()} 个残留进程，强制清理...', 'warning')
        ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true")
        time.sleep(1)
    
    add_log('   ✅ 进程已停止', 'success')

    # 5.2 启动新服务
    add_log('   5.2 启动新服务...', 'info')
    start_cmd = f"""
    cd {REMOTE_PATH}
    source .venv/bin/activate
    export PORT={LOCAL_PORT}
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    echo $!
    """

    success, pid, stderr = ssh_command(start_cmd)
    if success and pid.strip().isdigit():
        add_log(f'   ✅ 后端服务已启动 (PID: {pid.strip()})', 'success')
    else:
        add_log(f'   ️ 服务启动输出: {pid}', 'warning')

    # 等待服务启动
    time.sleep(3)

    # 5.3 验证服务状态
    add_log('   5.3 验证服务状态...', 'info')

    # 检查进程
    _, processes, _ = ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | head -3")
    if processes:
        add_log('   ✅ 后端进程运行中:', 'success')
        for line in processes.split('\n')[:2]:
            add_log(f'      {line.strip()}', 'info')
    else:
        add_log('   ⚠️ 未找到后端进程', 'warning')

    # 检查端口
    _, port_check, _ = ssh_command(f"lsof -i:{LOCAL_PORT} | head -3")
    if port_check:
        add_log(f'   ✅ 端口 {LOCAL_PORT} 监听正常', 'success')
    else:
        add_log(f'   ⚠️ 端口 {LOCAL_PORT} 未监听', 'warning')

    # 查看日志
    _, logs, _ = ssh_command(f"cd {REMOTE_PATH} && tail -10 logs/backend.log")
    if logs:
        add_log('   后端日志（最后10行）:', 'info')
        for line in logs.split('\n')[-10:]:
            if line.strip():
                add_log(f'      {line}', 'info')

    add_log('', 'info')
    add_log('=' * 50, 'info')


def execute_full_deploy():
    """执行完整部署（调用 deploy.py 脚本）"""
    add_log('🚀 开始完整部署（使用 deploy.py）...', 'info')
    add_log('=' * 50, 'info')

    # ====== 步骤 1: Git 提交与推送 ======
    deploy_status['current_step'] = 'Git提交'
    deploy_status['progress'] = 5
    add_log('📝 步骤 1: Git 提交与推送', 'info')

    # 检查是否有未提交的更改
    _, status, _ = run_local_command("git status --porcelain", cwd=str(PROJECT_ROOT))
    if status:
        add_log('   检测到未提交的更改，正在提交...', 'info')
        run_local_command("git add -A", cwd=str(PROJECT_ROOT))
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_local_command(f'git commit -m "Auto deploy: {timestamp}"', cwd=str(PROJECT_ROOT))
        add_log('   ✅ 提交完成', 'success')
    else:
        add_log('   ℹ️ 无未提交的更改', 'info')

    # Git推送
    deploy_status['current_step'] = 'Git推送'
    deploy_status['progress'] = 15
    add_log('   📤 Git推送到远程仓库...', 'info')

    # 增加超时时间到 120 秒
    success, stdout, stderr = run_local_command("git push origin q/dev", cwd=str(PROJECT_ROOT), timeout=120)
    if success:
        add_log('   ✅ Git推送成功', 'success')
        deploy_status['progress'] = 20
    else:
        add_log(f'   ❌ Git推送失败: {stderr[:200]}', 'error')
        add_log('   ⚠️ 继续执行后续部署步骤...', 'warning')
        deploy_status['progress'] = 20

    # ====== 步骤 2: 调用 deploy.py 进行完整部署 ======
    deploy_status['current_step'] = '执行完整部署'
    deploy_status['progress'] = 25
    add_log('', 'info')
    add_log('📝 步骤 2: 调用 deploy.py 进行完整部署', 'info')
    add_log('   这将包括：', 'info')
    add_log('   - 检测变更文件', 'info')
    add_log('   - 前端构建', 'info')
    add_log('   - 创建备份', 'info')
    add_log('   - 上传文件', 'info')
    add_log('   - 重启服务', 'info')
    add_log('   - 自动执行 SQL（如有）', 'info')

    # 执行 deploy.py（完整部署，不使用 --fast）
    deploy_script = PROJECT_ROOT / 'deploy.py'
    if not deploy_script.exists():
        add_log(f'   ❌ deploy.py 不存在: {deploy_script}', 'error')
        return

    add_log('   正在执行 python deploy.py ...', 'info')
    
    # 设置进度回调（通过子进程输出监控）
    import subprocess
    import threading
    
    def monitor_progress(proc):
        """监控子进程输出并更新进度"""
        for line in iter(proc.stdout.readline, ''):
            if line:
                line = line.strip()
                # 根据输出内容更新进度
                if '步骤 1:' in line or 'Git' in line:
                    deploy_status['progress'] = 30
                elif '步骤 2:' in line or '检测' in line:
                    deploy_status['progress'] = 40
                elif '步骤 3:' in line or '前端' in line or '构建' in line:
                    deploy_status['progress'] = 50
                elif '步骤 4:' in line or '备份' in line:
                    deploy_status['progress'] = 60
                elif '步骤 5:' in line or '上传' in line:
                    deploy_status['progress'] = 70
                elif '步骤 6:' in line or '重启' in line or '启动' in line:
                    deploy_status['progress'] = 85
                elif '✅' in line or '成功' in line:
                    pass  # 保持当前进度
                
                # 添加日志
                if line and len(line) < 200:  # 过滤过长的行
                    add_log(f'   [deploy.py] {line}', 'info')
    
    try:
        # 执行 deploy.py（完整部署）
        proc = subprocess.Popen(
            ['python', str(deploy_script)],  # 不使用 --fast 参数
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=os.environ.copy()
        )
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor_progress, args=(proc,), daemon=True)
        monitor_thread.start()
        
        # 等待完成（最多 10 分钟）
        proc.wait(timeout=600)
        
        if proc.returncode == 0:
            add_log('   ✅ deploy.py 执行成功', 'success')
            deploy_status['progress'] = 95
        else:
            add_log(f'   ❌ deploy.py 执行失败，返回码: {proc.returncode}', 'error')
            # 尝试获取最后几行输出
            remaining_output = proc.stdout.read()
            if remaining_output:
                for line in remaining_output.split('\n')[-10:]:
                    if line.strip():
                        add_log(f'   {line.strip()}', 'error')
    except subprocess.TimeoutExpired:
        add_log('   ❌ deploy.py 执行超时（超过10分钟）', 'error')
        proc.kill()
    except Exception as e:
        add_log(f'   ❌ 执行 deploy.py 时出错: {str(e)}', 'error')
        import traceback
        add_log(f'   错误详情: {traceback.format_exc()}', 'error')


def execute_restore(backup_file):
    """执行恢复操作"""
    add_log(f'🔄 开始恢复到备份: {backup_file}', 'info')
    add_log('=' * 50, 'info')

    # 验证备份文件存在
    backup_path = f"{BACKUP_DIR}/{backup_file}"
    _, check, _ = ssh_command(f"test -f {backup_path} && echo 'exists' || echo 'not found'")
    if 'exists' not in check:
        add_log(f' 备份文件不存在: {backup_path}', 'error')
        return

    # 获取备份文件信息
    _, size_info, _ = ssh_command(f"ls -lh {backup_path} | awk '{{print $5}}'")
    add_log(f' 备份文件大小: {size_info.strip()}', 'info')

    deploy_status['current_step'] = '停止服务'
    deploy_status['progress'] = 20
    add_log('⏹️ 步骤 1: 停止当前服务...', 'info')
    
    # 强制清理所有相关进程
    ssh_command(f"cd {REMOTE_PATH} && pkill -9 -f '.venv/bin/python.*app.py' || true")
    time.sleep(2)
    
    # 验证清理
    _, remaining, _ = ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | wc -l")
    if remaining and int(remaining.strip()) > 0:
        add_log(f'   ⚠️ 发现残留进程，二次清理...', 'warning')
        ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true")
        time.sleep(1)
    
    add_log('   ✅ 服务已停止', 'success')

    deploy_status['current_step'] = '恢复备份'
    deploy_status['progress'] = 50
    add_log('📦 步骤 2: 解压备份文件...', 'info')
    add_log(f'   备份路径: {backup_path}', 'info')
    add_log('    正在解压（可能需要几分钟）...', 'info')

    restore_cmd = f"""
    cd /project
    tar -xzf {backup_path}
    echo "恢复完成"
    """

    success, stdout, stderr = ssh_command(restore_cmd, timeout=180)

    if success:
        add_log('   ✅ 备份恢复成功', 'success')

        # 验证关键文件
        add_log('   验证关键文件:', 'info')
        check_files = ['app.py', 'config.py', 'routes/kafka/kafka_generator_routes.py']
        for file in check_files:
            _, output, _ = ssh_command(f"test -f {REMOTE_PATH}/{file} && echo '✓ {file}' || echo '✗ {file}'")
            add_log(f'      {output.strip()}', 'info')
    else:
        add_log(f'   恢复失败: {stderr[:200]}', 'error')
        return

    # 重启服务
    deploy_status['current_step'] = '重启服务'
    deploy_status['progress'] = 80
    add_log('🔄 步骤 3: 重启服务...', 'info')

    start_cmd = f"""
    cd {REMOTE_PATH}
    source .venv/bin/activate
    export PORT={LOCAL_PORT}
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    echo $!
    """

    success, pid, stderr = ssh_command(start_cmd)
    if success and pid.strip().isdigit():
        add_log(f'   ✅ 后端服务已启动 (PID: {pid.strip()})', 'success')
    else:
        add_log(f'    服务启动输出: {pid}', 'warning')

    time.sleep(3)

    # 验证
    add_log('   验证服务状态:', 'info')
    _, port_check, _ = ssh_command(f"lsof -i:{LOCAL_PORT} | head -2")
    if port_check:
        add_log(f'   ✅ 端口 {LOCAL_PORT} 监听正常', 'success')
    else:
        add_log(f'    端口 {LOCAL_PORT} 未监听', 'warning')

    add_log('', 'info')
    add_log('=' * 50, 'info')


def execute_create_backup():
    """创建备份"""
    add_log('💾 创建远程备份...', 'info')
    add_log('=' * 50, 'info')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"wordToWord_backup_{timestamp}.tar.gz"
    backup_path = f"{BACKUP_DIR}/{backup_name}"

    add_log(f'📦 备份文件名: {backup_name}', 'info')
    add_log(f' 备份路径: {backup_path}', 'info')

    add_log('🔍 排除项:', 'info')
    add_log('   - node_modules/', 'info')
    add_log('   - .venv/', 'info')
    add_log('   - __pycache__/', 'info')
    add_log('   - *.pyc', 'info')
    add_log('   - logs/*.log', 'info')

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
    echo "备份完成"
    """

    add_log('⏳ 正在创建备份（可能需要几分钟）...', 'info')
    success, stdout, stderr = ssh_command(backup_cmd, timeout=180)

    if success:
        # 获取备份文件大小
        _, size_info, _ = ssh_command(f"ls -lh {backup_path} | awk '{{print $5}}'")
        add_log(f'✅ 备份创建成功!', 'success')
        add_log(f'    文件名: {backup_name}', 'success')
        add_log(f'    文件大小: {size_info.strip()}', 'success')
        return backup_name
    else:
        add_log(f'❌ 备份失败: {stderr[:200]}', 'error')
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

        # 停止（强制清理）
        ssh_command(f"cd {REMOTE_PATH} && pkill -9 -f '.venv/bin/python.*app.py' || true")
        time.sleep(2)
        
        # 验证清理
        _, remaining, _ = ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | wc -l")
        if remaining and int(remaining.strip()) > 0:
            add_log(f'   ⚠️ 发现残留进程，强制清理...', 'warning')
            ssh_command("ps aux | grep '.venv/bin/python.*app.py' | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true")
            time.sleep(1)

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
    """获取服务器日志

    参数：
        type: 日志类型 (backend/nginx_access/nginx_error)
        preset: 预设行数 (100|1000|10000)，默认 100
    """
    preset = request.args.get('preset', '100')
    log_type = request.args.get('type', 'backend')

    PRESET_LINES = {'100': 100, '1000': 1000, '10000': 10000}

    if preset not in PRESET_LINES:
        return jsonify({
            'success': False,
            'message': f'预设参数错误，支持的 preset: 100, 1000, 10000'
        }), 400

    lines_count = PRESET_LINES[preset]

    try:
        if log_type == 'backend':
            cmd = f"cd {REMOTE_PATH} && tail -n {lines_count} logs/backend.log"
        elif log_type == 'nginx_access':
            cmd = f"tail -n {lines_count} {REMOTE_PATH}/logs/nginx_{NGINX_PORT}_access.log"
        elif log_type == 'nginx_error':
            cmd = f"tail -n {lines_count} {REMOTE_PATH}/logs/nginx_{NGINX_PORT}_error.log"
        else:
            cmd = f"cd {REMOTE_PATH} && tail -n {lines_count} logs/backend.log"
            log_type = 'backend'

        success, stdout, stderr = ssh_command(cmd, timeout=60)

        if success:
            log_lines = stdout.split('\n') if stdout else []
            return jsonify({
                'success': True,
                'data': {
                    'logs': stdout,
                    'lines_count': len(log_lines),
                    'requested_lines': lines_count,
                    'preset': preset,
                    'type': log_type,
                    'type_name': get_log_type_name(log_type)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': f'获取日志失败：{stderr}'
            }), 500

    except Exception as e:
        logger.error(f"查询日志失败：{e}")
        return jsonify({'success': False, 'message': str(e)}), 500


def get_log_type_name(log_type):
    """获取日志类型的中文名称"""
    return {'backend': '后端日志', 'nginx_access': 'Nginx 访问日志', 'nginx_error': 'Nginx 错误日志'}.get(log_type, '日志')



@deploy_config_bp.route('/server-logs/download', methods=['GET'])
def download_server_logs():
    """下载完整的服务器日志文件"""
    log_type = request.args.get('type', 'backend')

    try:
        import tempfile
        import shutil

        # 确定日志文件路径和前缀
        if log_type == 'backend':
            log_file = f"{REMOTE_PATH}/logs/backend.log"
            filename_prefix = "backend"
        elif log_type == 'nginx_access':
            log_file = f"{REMOTE_PATH}/logs/nginx_{NGINX_PORT}_access.log"
            filename_prefix = "nginx_access"
        elif log_type == 'nginx_error':
            log_file = f"{REMOTE_PATH}/logs/nginx_{NGINX_PORT}_error.log"
            filename_prefix = "nginx_error"
        else:
            log_file = f"{REMOTE_PATH}/logs/backend.log"
            filename_prefix = "backend"

        # 创建临时目录和文件
        temp_dir = tempfile.mkdtemp()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_file = os.path.join(temp_dir, f"{filename_prefix}_{timestamp}.log")

        try:
            # 从远程服务器复制完整日志文件到临时文件
            cmd = f"cat {log_file} > {temp_file}"
            success, stdout, stderr = ssh_command(cmd, timeout=120)

            if success and os.path.exists(temp_file):
                from flask import send_file
                return send_file(
                    temp_file,
                    as_attachment=True,
                    download_name=f"{filename_prefix}_{timestamp}.log",
                    mimetype='text/plain'
                )
            else:
                return jsonify({
                    'success': False,
                    'message': f'下载日志失败：{stderr}'
                }), 500

        finally:
            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        logger.error(f"下载日志失败：{e}")
        return jsonify({'success': False, 'message': str(e)}), 500



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
    cmd = f"scp -o LogLevel=ERROR -o StrictHostKeyChecking=no {flag} {local_path} {config['remote_user']}@{config['remote_host']}:{remote_path}"
    success, _, _ = run_local_command(cmd)
    return success


@deploy_config_bp.route('/config', methods=['GET'])
def get_config():
    """获取部署配置"""
    return jsonify({
        'success': True,
        'data': config
    })


@deploy_config_bp.route('/config', methods=['POST'])
def update_config():
    """更新部署配置"""
    global REMOTE_USER, REMOTE_HOST, REMOTE_PATH, BACKUP_DIR, LOCAL_PORT, NGINX_PORT

    data = request.get_json()
    if not data:
        return jsonify({
            'success': False,
            'message': '请求数据不能为空'
        }), 400

    # 验证必填字段
    required_fields = ['remote_user', 'remote_host', 'remote_path', 'backup_dir', 'local_port', 'nginx_port']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'success': False,
                'message': f'缺少必填字段: {field}'
            }), 400

    # 验证端口号
    try:
        local_port = int(data['local_port'])
        nginx_port = int(data['nginx_port'])
        if not (0 < local_port < 65536) or not (0 < nginx_port < 65536):
            raise ValueError('端口号超出范围')
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': f'端口号格式错误: {str(e)}'
        }), 400

    # 更新配置
    config.update(data)
    config['local_port'] = local_port
    config['nginx_port'] = nginx_port

    # 保存到文件
    try:
        save_deploy_config(config)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'保存配置失败: {str(e)}'
        }), 500

    # 更新全局变量
    REMOTE_USER = config['remote_user']
    REMOTE_HOST = config['remote_host']
    REMOTE_PATH = config['remote_path']
    BACKUP_DIR = config['backup_dir']
    LOCAL_PORT = config['local_port']
    NGINX_PORT = config['nginx_port']

    add_log('✅ 部署配置已更新', 'success')

    return jsonify({
        'success': True,
        'message': '配置更新成功',
        'data': config
    })
