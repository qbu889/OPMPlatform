"""
部署配置管理 API
"""
from flask import Blueprint, jsonify, request
# from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity  # 暂时禁用JWT
from models.deploy_config import DeployConfig
from models import db

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
