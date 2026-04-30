# OPM 平台部署管理系统设计方案

## 📋 文档信息

- **版本**: v1.0
- **创建日期**: 2026-04-29
- **作者**: OPM 开发团队
- **状态**: 设计阶段

---

## 🎯 项目背景

当前 OPM 平台使用 Shell 脚本进行部署和回滚操作，存在以下痛点：

1. **操作门槛高**：需要熟悉命令行和 SSH 操作
2. **缺乏可视化**：无法直观查看部署历史和备份状态
3. **监控不便**：需要手动登录服务器查看日志和服务状态
4. **协作困难**：团队成员无法共享部署信息和操作记录
5. **配置硬编码**：服务器IP、路径等配置写死在代码中，修改需重新部署

本方案旨在将现有的 `deploy.sh`、`deploy_with_backup.sh` 和 `rollback.sh` 脚本集成到 OPM 平台，提供可视化的部署管理界面，并实现**动态配置管理**，所有参数可通过页面修改，无需改代码。

---

## 🏗️ 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    前端界面 (Vue3)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 部署管理  │ │ 回滚管理  │ │ 备份管理  │ │ 服务监控  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────┐
│                  后端服务 (Flask)                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │          部署管理 API (deploy_routes.py)          │  │
│  │  - POST /api/deploy/quick    快速部署             │  │
│  │  - POST /api/deploy/full     全量部署             │  │
│  │  - GET  /api/rollback/list   获取备份列表         │  │
│  │  - POST /api/rollback/execute 执行回滚            │  │
│  │  - GET  /api/service/status  服务状态查询         │  │
│  │  - GET  /api/logs/tail       实时日志查看         │  │
│  │  - POST /api/backup/create   手动创建备份         │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │ SSH / Subprocess
┌──────────────────────▼──────────────────────────────────┐
│              远程服务器 (8.146.228.47)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ deploy_*.sh  │  │ rollback.sh  │  │ backups/     │  │
│  │ 部署脚本      │  │ 回滚脚本      │  │ 备份文件      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │ app.py       │  │ logs/        │                     │
│  │ Flask 后端    │  │ 应用日志      │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 功能模块设计

### 1. 部署管理模块

#### 1.1 功能清单

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 快速部署 | 执行 `deploy_with_backup.sh`，自动备份后部署 | P0 |
| 全量部署 | 重新构建前端并上传所有文件 | P1 |
| 增量部署 | 只上传变更的文件（现有逻辑） | P0 |
| 部署历史 | 记录每次部署的时间、版本、操作人、结果 | P1 |
| 部署确认 | 二次确认对话框，防止误操作 | P0 |
| 实时日志 | 显示部署过程中的实时输出 | P0 |

#### 1.2 API 设计

```python
# routes/deploy/deploy_routes.py

from flask import Blueprint, jsonify, request, session
import subprocess
import os
import json
from datetime import datetime
from models.operation_log import OperationLog
from models import db

deploy_bp = Blueprint('deploy', __name__, url_prefix='/api/deploy')

REMOTE_USER = "root"
REMOTE_HOST = "8.146.228.47"
REMOTE_PATH = "/project/wordToWord"
BACKUP_DIR = "/project/backups"


@deploy_bp.route('/quick', methods=['POST'])
def quick_deploy():
    """
    快速部署（带自动备份）
    
    Request Body:
    {
        "confirm": true  // 用户确认标志
    }
    
    Response:
    {
        "success": true,
        "task_id": "deploy_20260429_120000",
        "message": "部署任务已启动"
    }
    """
    try:
        # 权限检查
        if not _check_admin_permission():
            return jsonify({'success': False, 'error': '需要管理员权限'}), 403
        
        # 异步执行部署脚本
        task_id = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_deploy():
            result = subprocess.run(
                ['./deploy_with_backup.sh'],
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 记录操作日志
            _log_operation('DEPLOY', {
                'task_id': task_id,
                'type': 'quick',
                'success': result.returncode == 0,
                'output': result.stdout[:2000],  # 限制日志长度
                'error': result.stderr[:500]
            })
        
        # 启动后台线程
        import threading
        thread = threading.Thread(target=run_deploy)
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '部署任务已启动，请查看实时日志'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@deploy_bp.route('/full', methods=['POST'])
def full_deploy():
    """
    全量部署（重新构建前端）
    """
    # TODO: 实现全量部署逻辑
    pass


@deploy_bp.route('/history', methods=['GET'])
def get_deploy_history():
    """
    获取部署历史记录
    
    Query Parameters:
    - page: 页码（默认1）
    - limit: 每页数量（默认20）
    
    Response:
    {
        "success": true,
        "data": [
            {
                "id": 1,
                "task_id": "deploy_20260429_120000",
                "type": "quick",
                "operator": "admin",
                "timestamp": "2026-04-29 12:00:00",
                "status": "success",
                "duration": 45,
                "backup_file": "wordToWord_backup_20260429_115900.tar.gz"
            }
        ],
        "total": 50,
        "page": 1,
        "limit": 20
    }
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    query = OperationLog.query.filter_by(operation='DEPLOY')
    pagination = query.order_by(OperationLog.timestamp.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': [log.to_dict() for log in pagination.items],
        'total': pagination.total,
        'page': page,
        'limit': limit
    })
```

---

### 2. 回滚管理模块

#### 2.1 功能清单

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 备份列表 | 展示所有可用备份（时间、大小、版本信息） | P0 |
| 智能回滚 | 自动选择最新备份进行回滚 | P0 |
| 指定版本回滚 | 从列表中选择特定备份版本回滚 | P0 |
| 回滚预览 | 显示即将回滚的版本详细信息 | P1 |
| 回滚确认 | 二次确认 + 密码验证 | P0 |
| 回滚历史 | 记录所有回滚操作 | P1 |
| 失败保护 | 回滚失败时自动恢复到回滚前状态 | P0 |

#### 2.2 API 设计

```python
# routes/deploy/rollback_routes.py

from flask import Blueprint, jsonify, request
import subprocess
import os

rollback_bp = Blueprint('rollback', __name__, url_prefix='/api/rollback')


@rollback_bp.route('/list', methods=['GET'])
def list_backups():
    """
    获取备份文件列表
    
    Response:
    {
        "success": true,
        "backups": [
            {
                "filename": "wordToWord_backup_20260429_120000.tar.gz",
                "size": "125M",
                "date": "Apr 29 12:00",
                "path": "/project/backups/wordToWord_backup_20260429_120000.tar.gz",
                "is_latest": true
            },
            {
                "filename": "wordToWord_backup_20260428_180000.tar.gz",
                "size": "123M",
                "date": "Apr 28 18:00",
                "path": "/project/backups/wordToWord_backup_20260428_180000.tar.gz",
                "is_latest": false
            }
        ],
        "total": 5
    }
    """
    try:
        cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'ls -lt {BACKUP_DIR}/wordToWord_backup_*.tar.gz 2>/dev/null'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        backups = []
        lines = result.stdout.strip().split('\n')
        
        for idx, line in enumerate(lines):
            if not line:
                continue
            
            parts = line.split()
            if len(parts) >= 9:
                filename = parts[-1]
                basename = os.path.basename(filename)
                
                backups.append({
                    'filename': basename,
                    'size': parts[4],
                    'date': ' '.join(parts[5:8]),
                    'path': filename,
                    'is_latest': (idx == 0)
                })
        
        return jsonify({
            'success': True,
            'backups': backups,
            'total': len(backups)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@rollback_bp.route('/execute', methods=['POST'])
def execute_rollback():
    """
    执行回滚操作
    
    Request Body:
    {
        "backup_file": "wordToWord_backup_20260429_120000.tar.gz",  // 可选，不传则使用最新备份
        "confirm": true,
        "password": "******"  // 管理员密码验证
    }
    
    Response:
    {
        "success": true,
        "task_id": "rollback_20260429_130000",
        "message": "回滚任务已启动"
    }
    """
    try:
        # 权限和密码验证
        if not _verify_admin_password(request.json.get('password')):
            return jsonify({'success': False, 'error': '密码验证失败'}), 403
        
        backup_file = request.json.get('backup_file', '')
        task_id = f"rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        def run_rollback():
            cmd = f"./rollback.sh {backup_file}" if backup_file else "./rollback.sh"
            result = subprocess.run(
                cmd.split(),
                cwd=os.getcwd(),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 记录操作日志
            _log_operation('ROLLBACK', {
                'task_id': task_id,
                'backup_file': backup_file or 'latest',
                'success': result.returncode == 0,
                'output': result.stdout[:2000],
                'error': result.stderr[:500]
            })
        
        import threading
        thread = threading.Thread(target=run_rollback)
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': '回滚任务已启动'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

### 3. 备份管理模块

#### 3.1 功能清单

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 备份列表 | 查看所有备份文件及详细信息 | P0 |
| 手动备份 | 随时创建新的备份点 | P1 |
| 备份清理 | 删除过期备份（支持批量删除） | P1 |
| 保留策略 | 配置备份保留规则（按天数/数量） | P2 |
| 备份下载 | 下载备份文件到本地 | P2 |
| 备份统计 | 显示备份占用空间、数量等统计信息 | P2 |

#### 3.2 API 设计

```python
# routes/deploy/backup_routes.py

from flask import Blueprint, jsonify, request, send_file
import subprocess
import os

backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')


@backup_bp.route('/create', methods=['POST'])
def create_backup():
    """
    手动创建备份
    
    Request Body:
    {
        "description": "版本v1.2.3发布前备份"  // 可选
    }
    
    Response:
    {
        "success": true,
        "backup_file": "wordToWord_backup_20260429_140000.tar.gz",
        "size": "125M"
    }
    """
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"wordToWord_backup_{timestamp}.tar.gz"
        
        cmd = f"""ssh {REMOTE_USER}@{REMOTE_HOST} << 'EOF'
            cd /project
            mkdir -p {BACKUP_DIR}
            tar -czf {BACKUP_DIR}/{backup_filename} \\
                --exclude='node_modules' \\
                --exclude='.venv' \\
                --exclude='__pycache__' \\
                --exclude='*.pyc' \\
                --exclude='logs/*.log' \\
                wordToWord/
            du -h {BACKUP_DIR}/{backup_filename} | cut -f1
        EOF"""
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            size = result.stdout.strip()
            
            _log_operation('BACKUP_CREATE', {
                'backup_file': backup_filename,
                'size': size,
                'description': request.json.get('description', '')
            })
            
            return jsonify({
                'success': True,
                'backup_file': backup_filename,
                'size': size
            })
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@backup_bp.route('/delete', methods=['DELETE'])
def delete_backup():
    """
    删除指定备份文件
    
    Request Body:
    {
        "filename": "wordToWord_backup_20260429_120000.tar.gz"
    }
    """
    filename = request.json.get('filename')
    
    if not filename:
        return jsonify({'success': False, 'error': '缺少文件名参数'}), 400
    
    try:
        cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'rm -f {BACKUP_DIR}/{filename}'"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            _log_operation('BACKUP_DELETE', {'filename': filename})
            return jsonify({'success': True, 'message': '备份已删除'})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@backup_bp.route('/stats', methods=['GET'])
def backup_stats():
    """
    获取备份统计信息
    
    Response:
    {
        "success": true,
        "stats": {
            "total_count": 5,
            "total_size": "625M",
            "oldest_backup": "2026-04-25 10:00:00",
            "newest_backup": "2026-04-29 12:00:00",
            "disk_usage_percent": 12.5
        }
    }
    """
    # TODO: 实现备份统计逻辑
    pass
```

---

### 4. 服务监控模块

#### 4.1 功能清单

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 服务状态 | 显示前后端进程状态、PID、启动时间 | P0 |
| 实时日志 | 查看后端/前端实时日志（支持刷新） | P0 |
| 健康检查 | 检测 API 接口可用性 | P1 |
| 资源监控 | CPU、内存使用情况（可选） | P2 |
| 重启服务 | 一键重启前后端服务 | P1 |

#### 4.2 API 设计

```python
# routes/deploy/monitor_routes.py

from flask import Blueprint, jsonify, request
import subprocess

monitor_bp = Blueprint('monitor', __name__, url_prefix='/api/monitor')


@monitor_bp.route('/status', methods=['GET'])
def service_status():
    """
    获取服务运行状态
    
    Response:
    {
        "success": true,
        "backend": {
            "running": true,
            "pid": 12345,
            "uptime": "2h 30m",
            "port": 5004
        },
        "frontend": {
            "running": true,
            "pid": 12346,
            "uptime": "2h 28m",
            "port": 5173
        },
        "last_check": "2026-04-29 14:30:00"
    }
    """
    try:
        # 检查后端进程
        backend_cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'ps -ef | grep \"python app.py\" | grep -v grep'"
        backend_result = subprocess.run(backend_cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        # 检查前端进程
        frontend_cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'ps -ef | grep \"vite preview\" | grep -v grep'"
        frontend_result = subprocess.run(frontend_cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        backend_running = backend_result.returncode == 0 and backend_result.stdout.strip()
        frontend_running = frontend_result.returncode == 0 and frontend_result.stdout.strip()
        
        return jsonify({
            'success': True,
            'backend': {
                'running': backend_running,
                'pid': _extract_pid(backend_result.stdout) if backend_running else None,
                'port': 5004
            },
            'frontend': {
                'running': frontend_running,
                'pid': _extract_pid(frontend_result.stdout) if frontend_running else None,
                'port': 5173
            },
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@monitor_bp.route('/logs', methods=['GET'])
def tail_logs():
    """
    查看实时日志
    
    Query Parameters:
    - type: backend 或 frontend
    - lines: 行数（默认50，最大200）
    
    Response:
    {
        "success": true,
        "logs": "2026-04-29 14:30:00 INFO: Server started...\n...",
        "type": "backend",
        "lines": 50
    }
    """
    log_type = request.args.get('type', 'backend')
    lines = min(request.args.get('lines', 50, type=int), 200)
    
    try:
        if log_type == 'backend':
            cmd = f"""ssh {REMOTE_USER}@{REMOTE_HOST} 'cd {REMOTE_PATH} && 
                     ls -t logs/app_*.log 2>/dev/null | head -1 | xargs tail -{lines}'"""
        else:
            cmd = f"ssh {REMOTE_USER}@{REMOTE_HOST} 'tail -{lines} {REMOTE_PATH}/logs/frontend.log'"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        return jsonify({
            'success': True,
            'logs': result.stdout,
            'type': log_type,
            'lines': lines
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@monitor_bp.route('/restart', methods=['POST'])
def restart_service():
    """
    重启服务
    
    Request Body:
    {
        "service": "backend"  // backend, frontend, 或 all
    }
    """
    service = request.json.get('service', 'all')
    
    # TODO: 实现服务重启逻辑
    pass


def _extract_pid(process_info):
    """从进程信息中提取 PID"""
    if process_info:
        parts = process_info.strip().split()
        if len(parts) >= 2:
            return int(parts[1])
    return None
```

---

## ⚙️ 动态配置管理（核心特性）

### 设计目标

**所有部署相关参数都支持通过页面动态修改，无需改代码、无需重启服务！**

### 配置分类

| 分类 | 配置项示例 | 说明 |
|------|-----------|------|
| **服务器配置** | remote_host, remote_user, ssh_port | 远程服务器连接信息 |
| **部署配置** | deploy_timeout, git_branch, enable_auto_backup | 部署相关参数 |
| **备份配置** | max_backup_count, backup_retention_days | 备份保留策略 |
| **监控配置** | log_lines_default, health_check_interval | 监控相关参数 |

### 数据库设计

```sql
CREATE TABLE deploy_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT NOT NULL COMMENT '配置值',
    config_type VARCHAR(20) DEFAULT 'string' COMMENT '配置类型: string, number, boolean, json',
    description VARCHAR(500) COMMENT '配置说明',
    category VARCHAR(50) DEFAULT 'general' COMMENT '配置分类',
    is_sensitive BOOLEAN DEFAULT FALSE COMMENT '是否敏感信息',
    updated_by INT COMMENT '最后更新人ID',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_category (category),
    INDEX idx_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### API 设计

```python
# routes/deploy/config_routes.py

from flask import Blueprint, jsonify, request
from models.deploy_config import DeployConfig

config_bp = Blueprint('deploy_config', __name__, url_prefix='/api/deploy/config')

@config_bp.route('/list', methods=['GET'])
def list_configs():
    """获取所有配置（支持按分类过滤）"""
    category = request.args.get('category')
    configs = DeployConfig.get_all_configs(category=category)
    return jsonify({'success': True, 'configs': configs})

@config_bp.route('/update', methods=['POST'])
def update_config():
    """更新单个配置"""
    data = request.json
    DeployConfig.set_config(data['config_key'], data['config_value'])
    return jsonify({'success': True, 'message': '配置更新成功'})

@config_bp.route('/batch-update', methods=['POST'])
def batch_update_configs():
    """批量更新配置"""
    configs = request.json.get('configs', [])
    for item in configs:
        DeployConfig.set_config(item['config_key'], item['config_value'])
    return jsonify({'success': True, 'updated_count': len(configs)})

@config_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """测试 SSH 连接"""
    # 使用传入的配置测试连接
    pass
```

### 工具类封装

```python
# utils/deploy_helper.py

class DeployHelper:
    """部署辅助工具类 - 从数据库读取配置"""
    
    @staticmethod
    def get_remote_config():
        """获取远程服务器配置"""
        return {
            'remote_host': DeployConfig.get_config('remote_host', '8.146.228.47'),
            'remote_user': DeployConfig.get_config('remote_user', 'root'),
            'ssh_port': DeployConfig.get_config('ssh_port', 22),
            # ...
        }
    
    @staticmethod
    def build_ssh_command(cmd):
        """构建 SSH 命令（使用动态配置）"""
        config = DeployHelper.get_remote_config()
        return f"ssh -p {config['ssh_port']} {config['remote_user']}@{config['remote_host']} '{cmd}'"
```

### 前端界面

![配置管理界面](../images/deploy-config-ui.png)

**功能特性**：
- ✅ 分类展示（服务器、部署、备份、监控）
- ✅ 实时编辑（输入框、开关、数字选择器）
- ✅ 敏感信息隐藏（密码字段）
- ✅ 一键测试连接（SSH 连通性测试）
- ✅ 批量保存
- ✅ 恢复默认配置

---

## 🗄️ 数据库设计

### 操作日志表 (operation_logs)

```sql
CREATE TABLE operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    operation VARCHAR(50) NOT NULL COMMENT '操作类型: DEPLOY, ROLLBACK, BACKUP_CREATE, BACKUP_DELETE',
    task_id VARCHAR(100) COMMENT '任务ID',
    operator_id INT COMMENT '操作人ID',
    operator_name VARCHAR(100) COMMENT '操作人姓名',
    details JSON COMMENT '操作详情（JSON格式）',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending, success, failed',
    ip_address VARCHAR(50) COMMENT '操作IP地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    
    INDEX idx_operation (operation),
    INDEX idx_created_at (created_at),
    INDEX idx_operator (operator_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部署操作日志表';
```

### 部署历史表 (deploy_history)

```sql
CREATE TABLE deploy_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_id VARCHAR(100) UNIQUE NOT NULL COMMENT '任务ID',
    deploy_type VARCHAR(20) NOT NULL COMMENT '部署类型: quick, full, incremental',
    git_commit VARCHAR(100) COMMENT 'Git Commit Hash',
    git_branch VARCHAR(100) DEFAULT 'q/dev' COMMENT 'Git 分支',
    backup_file VARCHAR(255) COMMENT '备份文件名',
    changed_files JSON COMMENT '变更文件列表',
    duration_seconds INT COMMENT '耗时（秒）',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending, success, failed',
    error_message TEXT COMMENT '错误信息',
    operator_id INT COMMENT '操作人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    
    INDEX idx_task_id (task_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='部署历史记录表';
```

---

## 🎨 前端界面设计

### 页面结构

```
frontend/src/views/deploy/
├── DeployManager.vue          # 部署管理主页面
├── RollbackManager.vue        # 回滚管理页面
├── BackupManager.vue          # 备份管理页面
├── ServiceMonitor.vue         # 服务监控页面
└── components/
    ├── DeployHistoryTable.vue # 部署历史表格组件
    ├── BackupList.vue         # 备份列表组件
    ├── LogViewer.vue          # 日志查看器组件
    └── ServiceStatusCard.vue  # 服务状态卡片组件
```

### 路由配置

```javascript
// frontend/src/router/index.js

{
  path: '/deploy',
  name: 'Deploy',
  component: () => import('@/views/deploy/DeployManager.vue'),
  meta: { 
    title: '部署管理',
    requiresAuth: true,
    requiresAdmin: true  // 仅管理员可访问
  }
},
{
  path: '/rollback',
  name: 'Rollback',
  component: () => import('@/views/deploy/RollbackManager.vue'),
  meta: { 
    title: '回滚管理',
    requiresAuth: true,
    requiresAdmin: true
  }
},
{
  path: '/backup',
  name: 'Backup',
  component: () => import('@/views/deploy/BackupManager.vue'),
  meta: { 
    title: '备份管理',
    requiresAuth: true,
    requiresAdmin: true
  }
},
{
  path: '/monitor',
  name: 'Monitor',
  component: () => import('@/views/deploy/ServiceMonitor.vue'),
  meta: { 
    title: '服务监控',
    requiresAuth: true
  }
}
```

---

## 🔒 安全设计

### 1. 权限控制

```python
# utils/deploy_auth.py

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.auth_models import User

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or user.role != 'admin':
                return jsonify({
                    'success': False,
                    'error': '需要管理员权限才能执行此操作'
                }), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'success': False, 'error': '认证失败'}), 401
    
    return decorated_function


def verify_deploy_password(password):
    """验证部署操作密码（二次确认）"""
    # 从环境变量读取部署密码
    deploy_password = os.getenv('DEPLOY_PASSWORD')
    
    if not deploy_password:
        # 如果没有设置部署密码，使用管理员密码
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return user and user.check_password(password)
    
    return password == deploy_password
```

### 2. 操作审计

所有部署、回滚、备份操作都必须记录到数据库，包括：
- 操作人信息
- 操作时间
- 操作IP地址
- 操作详情
- 执行结果

### 3. SSH 密钥管理

**禁止在代码中硬编码 SSH 密码！**

推荐方案：
1. 使用 SSH 密钥认证（已在 `deploy_with_backup.sh` 中配置）
2. 将私钥存储在服务器的安全位置（如 `/root/.ssh/id_rsa`）
3. 设置严格的文件权限：`chmod 600 /root/.ssh/id_rsa`

---

## 📊 实施计划

### 第一阶段：基础功能（1-2周）✅

**目标**：实现核心的部署和回滚功能

**后端任务**：
- [ ] 创建 `routes/deploy/` 目录结构
- [ ] 实现 `deploy_routes.py`（快速部署 API）
- [ ] 实现 `rollback_routes.py`（回滚 API）
- [ ] 创建 `operation_logs` 数据表
- [ ] 实现操作日志记录功能
- [ ] 添加管理员权限验证

**前端任务**：
- [ ] 创建 `views/deploy/` 目录结构
- [ ] 实现 `DeployManager.vue`（部署管理页面）
- [ ] 实现 `RollbackManager.vue`（回滚管理页面）
- [ ] 添加路由配置和权限控制
- [ ] 实现实时日志显示组件

**测试任务**：
- [ ] 单元测试：API 接口测试
- [ ] 集成测试：完整部署流程测试
- [ ] 安全测试：权限验证测试

---

### 第二阶段：增强功能（1-2周）

**目标**：完善备份管理和监控功能

**后端任务**：
- [ ] 实现 `backup_routes.py`（备份管理 API）
- [ ] 实现 `monitor_routes.py`（服务监控 API）
- [ ] 创建 `deploy_history` 数据表
- [ ] 实现部署历史查询功能
- [ ] 实现服务状态检测功能

**前端任务**：
- [ ] 实现 `BackupManager.vue`（备份管理页面）
- [ ] 实现 `ServiceMonitor.vue`（服务监控页面）
- [ ] 实现备份列表组件
- [ ] 实现日志查看器组件
- [ ] 实现服务状态卡片组件

---

### 第三阶段：高级功能（2-3周）

**目标**：提升用户体验和系统可靠性

**功能扩展**：
- [ ] 灰度发布支持
- [ ] 自动化测试集成（部署前自动运行测试）
- [ ] 失败自动回滚机制
- [ ] 钉钉通知集成（部署成功/失败通知）
- [ ] 部署报告生成（每周/每月汇总）
- [ ] 资源监控（CPU、内存使用率）

**优化改进**：
- [ ] WebSocket 实时日志推送（替代轮询）
- [ ] 部署进度条显示
- [ ] 并发部署限制（防止同时多次部署）
- [ ] 备份压缩优化（减少存储空间）
- [ ] 日志归档和清理策略

---

## 🧪 测试方案

### 单元测试

```python
# test/test_deploy_routes.py

import unittest
from app import create_app
from models import db

class TestDeployRoutes(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def test_quick_deploy_requires_auth(self):
        """测试未登录用户无法执行部署"""
        response = self.client.post('/api/deploy/quick')
        self.assertEqual(response.status_code, 401)
    
    def test_quick_deploy_requires_admin(self):
        """测试普通用户无法执行部署"""
        token = self._get_user_token('user@example.com')
        response = self.client.post(
            '/api/deploy/quick',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 403)
    
    def test_quick_deploy_success(self):
        """测试管理员成功执行部署"""
        token = self._get_user_token('admin@example.com')
        response = self.client.post(
            '/api/deploy/quick',
            json={'confirm': True},
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['success'])
    
    def _get_user_token(self, email):
        """获取用户 JWT Token"""
        response = self.client.post('/api/auth/login', json={
            'email': email,
            'password': 'password123'
        })
        return response.json['access_token']
```

### 集成测试

```bash
# 测试完整部署流程
./test_deploy_integration.sh

# 测试回滚流程
./test_rollback_integration.sh
```

---

## 📈 性能优化

### 1. 异步任务处理

使用 Celery 或 threading 处理耗时的部署任务，避免阻塞主线程：

```python
from celery import Celery

celery = Celery('deploy_tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True)
def deploy_task(self, task_id):
    """异步执行部署任务"""
    result = subprocess.run(
        ['./deploy_with_backup.sh'],
        cwd=os.getcwd(),
        capture_output=True,
        text=True,
        timeout=300
    )
    
    # 更新任务状态
    self.update_state(state='SUCCESS', meta={
        'output': result.stdout,
        'error': result.stderr
    })
    
    return result.returncode == 0
```

### 2. 日志分页加载

前端日志查看器采用分页加载，避免一次性加载大量日志：

```javascript
const loadLogs = async (page = 1, lines = 50) => {
  const response = await axios.get('/api/monitor/logs', {
    params: { type: 'backend', lines, page }
  })
  
  if (page === 1) {
    logs.value = response.data.logs
  } else {
    logs.value = response.data.logs + '\n' + logs.value
  }
}
```

### 3. 缓存优化

缓存服务状态，减少频繁查询：

```python
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=30, key_prefix='service_status')
def get_cached_service_status():
    """缓存服务状态30秒"""
    return _query_service_status()
```

---

## 🚀 部署指南

### 1. 环境准备

```bash
# 安装依赖
pip install flask-caching celery redis

# 创建数据表
python scripts/init_deploy_tables.py
```

### 2. 配置环境变量

```bash
# .env 文件
DEPLOY_PASSWORD=your_secure_password_here
SSH_KEY_PATH=/root/.ssh/id_rsa
BACKUP_RETENTION_DAYS=30
MAX_BACKUP_COUNT=10
```

### 3. 注册蓝图

```python
# app.py

from routes.deploy.deploy_routes import deploy_bp
from routes.deploy.rollback_routes import rollback_bp
from routes.deploy.backup_routes import backup_bp
from routes.deploy.monitor_routes import monitor_bp

app.register_blueprint(deploy_bp)
app.register_blueprint(rollback_bp)
app.register_blueprint(backup_bp)
app.register_blueprint(monitor_bp)
```

### 4. 前端构建

```bash
cd frontend
npm run build
```

---

## 📝 运维手册

### 常见问题排查

#### 1. 部署失败

**现象**：点击部署按钮后提示失败

**排查步骤**：
1. 查看后端日志：`tail -f logs/backend.log`
2. 检查 SSH 连接：`ssh root@8.146.228.47`
3. 验证脚本权限：`chmod +x deploy_with_backup.sh`
4. 检查磁盘空间：`df -h`

#### 2. 回滚失败

**现象**：回滚后服务无法启动

**解决方案**：
1. 检查回滚前备份是否完整
2. 手动恢复：`tar -xzf backup_file.tar.gz -C /project/`
3. 重新启动服务：`./start_all_prod.sh`

#### 3. 日志无法查看

**现象**：日志查看器显示空白

**排查步骤**：
1. 检查日志文件是否存在：`ls -l logs/`
2. 验证文件权限：`chmod 644 logs/*.log`
3. 检查 SSH 命令是否正确

---

## 🔮 未来规划

### 短期（1-3个月）
- [ ] 支持多环境部署（开发、测试、生产）
- [ ] 集成 GitLab CI/CD
- [ ] 实现蓝绿部署策略
- [ ] 添加部署模板功能

### 中期（3-6个月）
- [ ] Kubernetes 集群部署支持
- [ ] Docker 容器化部署
- [ ] 自动化性能测试集成
- [ ] 智能告警系统

### 长期（6-12个月）
- [ ] 多云平台支持（阿里云、腾讯云、AWS）
- [ ] AI 辅助部署决策
- [ ] 自动化容量规划
- [ ] 零停机部署方案

---

## 📚 参考资料

- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Vue3 官方文档](https://vuejs.org/)
- [Element Plus 组件库](https://element-plus.org/)
- [Celery 分布式任务队列](https://docs.celeryq.dev/)
- [SSH 密钥认证指南](https://www.ssh.com/academy/ssh/keygen)

---

## 👥 团队成员

| 角色 | 姓名 | 职责 |
|------|------|------|
| 项目负责人 | - | 整体规划和协调 |
| 后端开发 | - | API 开发和数据库设计 |
| 前端开发 | - | 界面开发和交互优化 |
| 测试工程师 | - | 测试用例编写和执行 |
| 运维工程师 | - | 服务器配置和监控 |

---

## 📞 联系方式

如有问题或建议，请联系：
- Email: opm-team@example.com
- Slack: #opm-deploy channel
- 内部 Wiki: http://wiki.example.com/opm

---

**文档版本历史**：
- v1.0 (2026-04-29): 初始版本，完成整体方案设计
