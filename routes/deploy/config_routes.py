"""
部署配置管理 API
"""
from flask import Blueprint, jsonify, request, send_file
# from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity  # 暂时禁用JWT
from models.deploy_config import DeployConfig
from models import db
import os
import subprocess

config_bp = Blueprint('deploy_config', __name__, url_prefix='/api/deploy/config')


def admin_required(f):
    """管理员权限装饰器 - 开发环境暂时禁用"""
    # 直接返回原函数，不添加任何验证逻辑
    return f


@config_bp.route('/list', methods=['GET'])
# @admin_required  # 暂时禁用权限验证
def list_configs():
    """
    获取所有配置（支持按分类过滤）
    
    Query Parameters:
    - category: 配置分类（server, deployment, backup, monitor）
    - hide_sensitive: 是否隐藏敏感信息（默认true）
    
    Response:
    {
        "success": true,
        "configs": [...],
        "categories": ["server", "deployment", "backup", "monitor"]
    }
    """
    try:
        category = request.args.get('category')
        hide_sensitive = request.args.get('hide_sensitive', 'true').lower() == 'true'
        
        configs = DeployConfig.get_all_configs(
            category=category if category else None,
            hide_sensitive=hide_sensitive
        )
        
        # 获取所有分类
        categories = db.session.query(DeployConfig.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'configs': configs,
            'categories': category_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/get/<key>', methods=['GET'])
@admin_required
def get_config(key):
    """
    获取单个配置值
    
    Response:
    {
        "success": true,
        "config": {
            "config_key": "remote_host",
            "config_value": "8.146.228.47",
            "config_type": "string",
            "description": "远程服务器IP地址"
        }
    }
    """
    try:
        config = DeployConfig.query.filter_by(config_key=key).first()
        
        if not config:
            return jsonify({'success': False, 'error': '配置不存在'}), 404
        
        return jsonify({
            'success': True,
            'config': config.to_dict(hide_sensitive=False)  # 管理员可查看完整信息
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/update', methods=['POST'])
@admin_required
def update_config():
    """
    更新配置
    
    Request Body:
    {
        "config_key": "remote_host",
        "config_value": "192.168.1.100"
    }
    
    Response:
    {
        "success": true,
        "message": "配置更新成功"
    }
    """
    try:
        data = request.json
        config_key = data.get('config_key')
        config_value = data.get('config_value')
        
        if not config_key or config_value is None:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        # 获取当前用户ID（暂时设为None）
        # user_id = get_jwt_identity()
        user_id = None
        
        # 更新配置
        DeployConfig.set_config(config_key, config_value, updated_by=user_id)
        
        return jsonify({
            'success': True,
            'message': '配置更新成功'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/batch-update', methods=['POST'])
# @admin_required  # 已禁用权限验证
def batch_update_configs():
    """
    批量更新配置
    
    Request Body:
    {
        "configs": [
            {"config_key": "remote_host", "config_value": "192.168.1.100"},
            {"config_key": "backend_port", "config_value": "5005"}
        ]
    }
    
    Response:
    {
        "success": true,
        "updated_count": 2,
        "message": "批量更新成功"
    }
    """
    print("[DEBUG] ===== BATCH_UPDATE_CONFIGS CALLED =====")
    try:
        print("[DEBUG] batch_update_configs called")
        data = request.json
        print(f"[DEBUG] Received data: {data}")
        configs = data.get('configs', [])
        print(f"[DEBUG] Configs count: {len(configs)}")
        
        if not configs:
            return jsonify({'success': False, 'error': '没有提供配置数据'}), 400
        
        # user_id = get_jwt_identity()
        user_id = None
        print(f"[DEBUG] Starting to update configs with user_id={user_id}")
        updated_count = 0
        
        for item in configs:
            config_key = item.get('config_key')
            config_value = item.get('config_value')
            print(f"[DEBUG] Updating {config_key} = {config_value}")
            
            if config_key and config_value is not None:
                DeployConfig.set_config(config_key, config_value, updated_by=user_id)
                updated_count += 1
        
        print(f"[DEBUG] Updated {updated_count} configs successfully")
        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'message': f'成功更新 {updated_count} 个配置'
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] batch_update_configs exception:\n{error_trace}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/reset/<key>', methods=['POST'])
@admin_required
def reset_config(key):
    """
    重置配置为默认值
    
    Response:
    {
        "success": true,
        "message": "配置已重置"
    }
    """
    try:
        # 定义默认配置
        default_configs = {
            'remote_host': '8.146.228.47',
            'remote_user': 'root',
            'remote_path': '/project/wordToWord',
            'backup_dir': '/project/backups',
            'ssh_port': '22',
            'backend_port': '5004',
            'frontend_port': '5173',
            'git_branch': 'q/dev',
        }
        
        if key not in default_configs:
            return jsonify({'success': False, 'error': '该配置不支持重置'}), 400
        
        # user_id = get_jwt_identity()
        user_id = None
        DeployConfig.set_config(key, default_configs[key], updated_by=user_id)
        
        return jsonify({
            'success': True,
            'message': '配置已重置为默认值'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/test-connection', methods=['POST'])
@admin_required
def test_connection():
    """
    测试 SSH 连接
    
    Request Body:
    {
        "remote_host": "8.146.228.47",
        "remote_user": "root",
        "ssh_port": 22
    }
    
    Response:
    {
        "success": true,
        "message": "SSH 连接成功",
        "details": "Connected to 8.146.228.47:22"
    }
    """
    try:
        import subprocess
        
        data = request.json
        remote_host = data.get('remote_host')
        remote_user = data.get('remote_user')
        ssh_port = data.get('ssh_port', 22)
        
        if not remote_host or not remote_user:
            return jsonify({'success': False, 'error': '缺少必要参数'}), 400
        
        # 测试 SSH 连接
        cmd = f"ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -p {ssh_port} {remote_user}@{remote_host} 'echo Connection successful'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'SSH 连接成功',
                'details': result.stdout.strip()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'SSH 连接失败',
                'error': result.stderr.strip()[:200]
            }), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'message': 'SSH 连接超时',
            'error': '连接超时，请检查网络或防火墙设置'
        }), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 备份管理 API ====================

@config_bp.route('/backup/history', methods=['GET'])
def get_backup_history():
    """
    获取备份历史列表
    
    Response:
    {
        "success": true,
        "backups": [
            {
                "filename": "wordToWord_backup_20260430_120000.tar.gz",
                "size": "15.2 MB",
                "size_bytes": 15938355,
                "created_at": "2026-04-30 12:00:00",
                "path": "/project/backups/wordToWord_backup_20260430_120000.tar.gz"
            }
        ],
        "total_count": 5
    }
    """
    try:
        # 从配置获取备份目录
        backup_dir = DeployConfig.get_config('backup_dir', '/project/backups')
        
        # 检查目录是否存在
        if not os.path.exists(backup_dir):
            return jsonify({
                'success': False,
                'error': '备份目录不存在',
                'backup_dir': backup_dir
            }), 404
        
        # 获取所有备份文件
        backup_files = []
        for filename in os.listdir(backup_dir):
            if filename.startswith('wordToWord_backup_') and filename.endswith('.tar.gz'):
                filepath = os.path.join(backup_dir, filename)
                
                # 获取文件信息
                stat = os.stat(filepath)
                size_bytes = stat.st_size
                
                # 格式化文件大小
                if size_bytes < 1024:
                    size_str = f"{size_bytes} B"
                elif size_bytes < 1024 * 1024:
                    size_str = f"{size_bytes / 1024:.1f} KB"
                elif size_bytes < 1024 * 1024 * 1024:
                    size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                
                # 从文件名解析时间戳
                # 格式：wordToWord_backup_20260430_120000.tar.gz
                try:
                    timestamp_str = filename.replace('wordToWord_backup_', '').replace('.tar.gz', '')
                    created_at = f"{timestamp_str[:4]}-{timestamp_str[4:6]}-{timestamp_str[6:8]} {timestamp_str[9:11]}:{timestamp_str[11:13]}:{timestamp_str[13:15]}"
                except:
                    created_at = "Unknown"
                
                backup_files.append({
                    'filename': filename,
                    'size': size_str,
                    'size_bytes': size_bytes,
                    'created_at': created_at,
                    'path': filepath
                })
        
        # 按时间排序（最新的在前）
        backup_files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'success': True,
            'backups': backup_files,
            'total_count': len(backup_files)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/backup/delete', methods=['POST'])
def delete_backup():
    """
    删除指定备份文件
    
    Request Body:
    {
        "filename": "wordToWord_backup_20260430_120000.tar.gz"
    }
    
    Response:
    {
        "success": true,
        "message": "备份文件已删除"
    }
    """
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': '缺少文件名参数'}), 400
        
        # 安全检查：防止路径穿越
        if '..' in filename or filename.startswith('/'):
            return jsonify({'success': False, 'error': '非法的文件名'}), 400
        
        # 从配置获取备份目录
        backup_dir = DeployConfig.get_config('backup_dir', '/project/backups')
        filepath = os.path.join(backup_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': '备份文件不存在'}), 404
        
        # 删除文件
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'备份文件 {filename} 已删除'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/backup/restore', methods=['POST'])
def restore_backup():
    """
    从备份恢复项目
    
    Request Body:
    {
        "filename": "wordToWord_backup_20260430_120000.tar.gz"
    }
    
    Response:
    {
        "success": true,
        "message": "正在恢复备份，请稍候..."
    }
    """
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'success': False, 'error': '缺少文件名参数'}), 400
        
        # 安全检查
        if '..' in filename or filename.startswith('/'):
            return jsonify({'success': False, 'error': '非法的文件名'}), 400
        
        # 从配置获取路径
        backup_dir = DeployConfig.get_config('backup_dir', '/project/backups')
        remote_path = DeployConfig.get_config('remote_path', '/project/wordToWord')
        
        backup_file = os.path.join(backup_dir, filename)
        
        # 检查备份文件是否存在
        if not os.path.exists(backup_file):
            return jsonify({'success': False, 'error': '备份文件不存在'}), 404
        
        # 异步恢复操作（在后台执行）
        def do_restore():
            try:
                # 1. 停止当前服务
                subprocess.run('pkill -f "python app.py"', shell=True, timeout=10)
                subprocess.run('pkill -f "vite"', shell=True, timeout=10)
                
                # 2. 解压备份文件
                # 备份到临时目录
                restore_dir = f"{remote_path}_restore_{os.getpid()}"
                os.makedirs(restore_dir, exist_ok=True)
                
                subprocess.run(
                    f"cd {restore_dir} && tar -xzf {backup_file}",
                    shell=True,
                    timeout=300
                )
                
                # 3. 替换当前项目
                subprocess.run(f"rm -rf {remote_path}/*", shell=True)
                subprocess.run(f"mv {restore_dir}/wordToWord/* {remote_path}/", shell=True)
                subprocess.run(f"rm -rf {restore_dir}", shell=True)
                
                # 4. 重启服务
                subprocess.run(
                    f"cd {remote_path} && source .venv/bin/activate && "
                    f"export PORT=5004 && nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &",
                    shell=True
                )
            except Exception as e:
                print(f"恢复失败: {e}")
        
        import threading
        thread = threading.Thread(target=do_restore)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '正在恢复备份，请稍候...'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 日志管理 API ====================

@config_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    获取日志内容
    
    Query Parameters:
    - type: 日志类型（backend 或 frontend）
    - lines: 获取行数（默认50）
    
    Response:
    {
        "success": true,
        "content": "日志内容...",
        "lines": 50
    }
    """
    try:
        log_type = request.args.get('type', 'backend')
        lines = int(request.args.get('lines', 50))
        
        # 确定日志文件路径
        if log_type == 'backend':
            # 尝试获取当天的日志文件
            log_dir = 'logs'
            today = datetime.now().strftime('%Y%m%d')
            log_files = [
                f'logs/app_{today}.log',
                'logs/backend.log'
            ]
        elif log_type == 'frontend':
            log_files = ['logs/frontend.log']
        else:
            return jsonify({
                'success': False,
                'error': '不支持的日志类型'
            }), 400
        
        # 查找存在的日志文件
        log_file = None
        for file in log_files:
            if os.path.exists(file):
                log_file = file
                break
        
        if not log_file:
            return jsonify({
                'success': False,
                'error': '日志文件不存在'
            }), 404
        
        # 读取日志内容（最后N行）
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            content = ''.join(recent_lines)
        
        return jsonify({
            'success': True,
            'content': content,
            'lines': len(recent_lines),
            'total_lines': len(all_lines)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@config_bp.route('/logs/download', methods=['GET'])
def download_logs():
    """
    下载日志文件
    
    Query Parameters:
    - type: 日志类型（backend 或 frontend）
    
    Response:
    文件下载
    """
    try:
        log_type = request.args.get('type', 'backend')
        
        # 确定日志文件路径
        if log_type == 'backend':
            today = datetime.now().strftime('%Y%m%d')
            log_files = [
                f'logs/app_{today}.log',
                'logs/backend.log'
            ]
        elif log_type == 'frontend':
            log_files = ['logs/frontend.log']
        else:
            return jsonify({
                'success': False,
                'error': '不支持的日志类型'
            }), 400
        
        # 查找存在的日志文件
        log_file = None
        for file in log_files:
            if os.path.exists(file):
                log_file = file
                break
        
        if not log_file:
            return jsonify({
                'success': False,
                'error': '日志文件不存在'
            }), 404
        
        # 发送文件
        return send_file(
            log_file,
            as_attachment=True,
            download_name=f'{log_type}.log'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
