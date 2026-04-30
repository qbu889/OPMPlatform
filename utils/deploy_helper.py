"""
部署工具类 - 从数据库读取配置
"""
from models.deploy_config import DeployConfig


class DeployHelper:
    """部署辅助工具类"""
    
    @staticmethod
    def get_remote_config():
        """
        获取远程服务器配置
        
        Returns:
            dict: {
                'remote_host': '8.146.228.47',
                'remote_user': 'root',
                'remote_path': '/project/wordToWord',
                'backup_dir': '/project/backups',
                'ssh_port': 22,
                'ssh_timeout': 30
            }
        """
        return {
            'remote_host': DeployConfig.get_config('remote_host', '8.146.228.47'),
            'remote_user': DeployConfig.get_config('remote_user', 'root'),
            'remote_path': DeployConfig.get_config('remote_path', '/project/wordToWord'),
            'backup_dir': DeployConfig.get_config('backup_dir', '/project/backups'),
            'ssh_port': DeployConfig.get_config('ssh_port', 22),
            'ssh_timeout': DeployConfig.get_config('ssh_timeout', 30),
        }
    
    @staticmethod
    def get_deploy_config():
        """
        获取部署相关配置
        
        Returns:
            dict: {
                'deploy_timeout': 300,
                'rollback_timeout': 300,
                'git_branch': 'q/dev',
                'enable_auto_backup': True
            }
        """
        return {
            'deploy_timeout': DeployConfig.get_config('deploy_timeout', 300),
            'rollback_timeout': DeployConfig.get_config('rollback_timeout', 300),
            'git_branch': DeployConfig.get_config('git_branch', 'q/dev'),
            'enable_auto_backup': DeployConfig.get_config('enable_auto_backup', True),
        }
    
    @staticmethod
    def get_service_config():
        """
        获取服务端口配置
        
        Returns:
            dict: {
                'backend_port': 5004,
                'frontend_port': 5173
            }
        """
        return {
            'backend_port': DeployConfig.get_config('backend_port', 5004),
            'frontend_port': DeployConfig.get_config('frontend_port', 5173),
        }
    
    @staticmethod
    def get_backup_config():
        """
        获取备份配置
        
        Returns:
            dict: {
                'max_backup_count': 5,
                'backup_retention_days': 30
            }
        """
        return {
            'max_backup_count': DeployConfig.get_config('max_backup_count', 5),
            'backup_retention_days': DeployConfig.get_config('backup_retention_days', 30),
        }
    
    @staticmethod
    def build_ssh_command(cmd):
        """
        构建 SSH 命令（使用动态配置）
        
        Args:
            cmd: 要在远程服务器执行的命令
            
        Returns:
            str: 完整的 SSH 命令
        """
        config = DeployHelper.get_remote_config()
        return (
            f"ssh -o ConnectTimeout={config['ssh_timeout']} "
            f"-o StrictHostKeyChecking=no "
            f"-p {config['ssh_port']} "
            f"{config['remote_user']}@{config['remote_host']} "
            f"'{cmd}'"
        )
    
    @staticmethod
    def build_scp_command(local_file, remote_file):
        """
        构建 SCP 命令（使用动态配置）
        
        Args:
            local_file: 本地文件路径
            remote_file: 远程文件路径
            
        Returns:
            str: 完整的 SCP 命令
        """
        config = DeployHelper.get_remote_config()
        return (
            f"scp -P {config['ssh_port']} "
            f"-o ConnectTimeout={config['ssh_timeout']} "
            f"-o StrictHostKeyChecking=no "
            f"{local_file} "
            f"{config['remote_user']}@{config['remote_host']}:{remote_file}"
        )
