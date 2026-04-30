"""
初始化部署配置表
用法: python scripts/init_deploy_config.py
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db
from models.deploy_config import DeployConfig


def init_deploy_config():
    """初始化部署配置表并插入默认配置"""
    
    app = create_app('development')
    
    with app.app_context():
        # 创建表
        print("📊 正在创建 deploy_config 表...")
        db.create_all()
        print("✅ 表创建成功")
        
        # 检查是否已有配置
        existing_count = DeployConfig.query.count()
        if existing_count > 0:
            print(f"⚠️  检测到已有 {existing_count} 条配置记录")
            response = input("是否重新初始化？(yes/no): ")
            if response.lower() != 'yes':
                print("❌ 取消初始化")
                return
        
        # 删除旧配置（如果有）
        if existing_count > 0:
            print("🗑️  清空旧配置...")
            DeployConfig.query.delete()
            db.session.commit()
        
        # 插入默认配置
        print("📝 正在插入默认配置...")
        
        default_configs = [
            # 服务器配置
            ('remote_host', '8.146.228.47', 'string', '远程服务器IP地址', 'server', False),
            ('remote_user', 'root', 'string', '远程服务器用户名', 'server', False),
            ('remote_path', '/project/wordToWord', 'string', '远程项目路径', 'server', False),
            ('backup_dir', '/project/backups', 'string', '备份文件存储目录', 'backup', False),
            ('ssh_port', '22', 'number', 'SSH端口号', 'server', False),
            ('ssh_timeout', '30', 'number', 'SSH连接超时时间（秒）', 'server', False),
            
            # 部署配置
            ('deploy_timeout', '300', 'number', '部署脚本执行超时时间（秒）', 'deployment', False),
            ('rollback_timeout', '300', 'number', '回滚脚本执行超时时间（秒）', 'deployment', False),
            ('git_branch', 'q/dev', 'string', 'Git部署分支', 'deployment', False),
            ('deploy_password', '', 'string', '部署操作密码（二次验证）', 'deployment', True),
            ('enable_auto_backup', 'true', 'boolean', '是否启用自动备份', 'deployment', False),
            
            # 备份配置
            ('max_backup_count', '5', 'number', '最大备份保留数量', 'backup', False),
            ('backup_retention_days', '30', 'number', '备份保留天数', 'backup', False),
            
            # 服务配置
            ('backend_port', '5004', 'number', '后端服务端口', 'server', False),
            ('frontend_port', '5173', 'number', '前端服务端口', 'server', False),
            
            # 监控配置
            ('log_lines_default', '50', 'number', '日志查看默认行数', 'monitor', False),
            ('health_check_interval', '60', 'number', '健康检查间隔（秒）', 'monitor', False),
        ]
        
        for key, value, config_type, description, category, is_sensitive in default_configs:
            config = DeployConfig(
                config_key=key,
                config_value=value,
                config_type=config_type,
                description=description,
                category=category,
                is_sensitive=is_sensitive
            )
            db.session.add(config)
        
        db.session.commit()
        print(f"✅ 成功插入 {len(default_configs)} 条默认配置")
        
        # 验证
        count = DeployConfig.query.count()
        print(f"\n📊 当前配置总数: {count}")
        
        # 显示部分配置
        print("\n📋 配置示例:")
        configs = DeployConfig.query.limit(5).all()
        for config in configs:
            print(f"   - {config.config_key}: {config.config_value} ({config.category})")


if __name__ == '__main__':
    try:
        init_deploy_config()
        print("\n✅ 部署配置初始化完成！")
        print("\n💡 提示:")
        print("   1. 访问 http://localhost:5004/vue/deploy-config 管理配置")
        print("   2. 在页面中可以动态修改服务器、部署、备份等参数")
        print("   3. 修改后无需重启服务，立即生效")
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
