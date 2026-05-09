"""
部署相关 API
"""
from flask import Blueprint, jsonify, request
import subprocess
import os

deploy_api_bp = Blueprint('deploy_api', __name__)

@deploy_api_bp.route('/deploy-config', methods=['POST'])
def deploy_config():
    """调用 deploy.py 自动化部署脚本
    该接口接受空请求体，直接执行项目根目录下的 deploy.py
    返回脚本 stdout, stderr 以及 exit code
    """
    try:
        # 计算部署脚本路径
        deploy_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'deploy.py'))
        # 以子进程方式执行脚本，捕获输出
        result = subprocess.run(
            ['python', deploy_script],
            cwd=os.path.dirname(deploy_script),
            capture_output=True,
            text=True
        )
        resp = {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        if result.returncode == 0:
            return jsonify(resp)
        else:
            return jsonify(resp), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
"""
