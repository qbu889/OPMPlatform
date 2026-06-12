#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署配置 - 日志功能测试
测试查询和下载服务器日志的功能
"""
import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask
from routes.deploy.deploy_config_routes import (
    deploy_config_bp,
    get_log_type_name,
    ssh_command,
)


class TestDeployConfigLogs:
    """日志功能测试类"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['DATABASE_URI'] = 'sqlite:///:memory:'

        # 注册蓝图
        app.register_blueprint(deploy_config_bp)

        return app.test_client()

    @pytest.fixture
    def mock_ssh_success(self):
        """成功的 SSH 命令模拟（用于查询）"""
        def ssh_command_mock(cmd, timeout=None):
            # 模拟成功返回日志内容
            mock_logs = "\n".join([
                f"{datetime.now().isoformat()} INFO Test log line {i}"
                for i in range(150)
            ])
            return True, mock_logs, ""
        return ssh_command_mock

    @pytest.fixture
    def mock_ssh_download(self, tmp_path):
        """成功的 SSH 命令模拟（用于下载测试）"""
        def ssh_command_mock(cmd, timeout=None):
            # 如果是 cat 命令（下载场景），创建临时文件
            if cmd.startswith('cat ') and cmd.endswith('.log'):
                # 解析目标文件路径
                target_file = cmd.split('> ')[-1].strip()
                # 写入模拟日志内容到目标文件
                mock_logs = "\n".join([
                    f"{datetime.now().isoformat()} INFO Test log line {i}"
                    for i in range(150)
                ])
                # 写入文件
                with open(target_file, 'w') as f:
                    f.write(mock_logs)
                return True, "", ""
            return True, "mock logs", ""
        return ssh_command_mock

    @pytest.fixture
    def mock_ssh_error(self):
        """失败的 SSH 命令模拟"""
        def ssh_command_mock(cmd, timeout=None):
            return False, "", "Connection refused: Connection timeout"
        return ssh_command_mock

    @pytest.fixture
    def mock_ssh_empty(self):
        """返回空日志的模拟"""
        def ssh_command_mock(cmd, timeout=None):
            return True, "", ""
        return ssh_command_mock

    # ==================== 查询日志功能测试 ====================

    def test_query_backend_logs_100_lines(self, client, mock_ssh_success):
        """测试查询后端日志 100 行"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs?type=backend&preset=100')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['type'] == 'backend'
            assert data['data']['type_name'] == '后端日志'
            assert data['data']['requested_lines'] == 100
            assert data['data']['preset'] == '100'

    def test_query_backend_logs_1000_lines(self, client, mock_ssh_success):
        """测试查询后端日志 1000 行"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs?type=backend&preset=1000')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['requested_lines'] == 1000
            assert data['data']['preset'] == '1000'

    def test_query_backend_logs_10000_lines(self, client, mock_ssh_success):
        """测试查询后端日志 10000 行"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs?type=backend&preset=10000')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['requested_lines'] == 10000
            assert data['data']['preset'] == '10000'

    def test_query_nginx_access_logs(self, client, mock_ssh_success):
        """测试查询 Nginx 访问日志"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs?type=nginx_access&preset=100')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['type'] == 'nginx_access'
            assert data['data']['type_name'] == 'Nginx 访问日志'

    def test_query_nginx_error_logs(self, client, mock_ssh_success):
        """测试查询 Nginx 错误日志"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs?type=nginx_error&preset=100')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['type'] == 'nginx_error'
            assert data['data']['type_name'] == 'Nginx 错误日志'

    def test_query_logs_default_preset(self, client, mock_ssh_success):
        """测试默认预设值（100 行）"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs?type=backend')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['requested_lines'] == 100
            assert data['data']['preset'] == '100'

    def test_query_logs_default_type(self, client, mock_ssh_success):
        """测试默认日志类型（backend）"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_success):
            response = client.get('/deploy-config/server-logs')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['type'] == 'backend'

    def test_query_logs_invalid_preset(self, client):
        """测试无效的 preset 参数"""
        response = client.get('/deploy-config/server-logs?type=backend&preset=invalid')
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] == False
        assert '预设参数错误' in data['message']

    def test_query_logs_invalid_preset_500(self, client):
        """测试不支持的 preset 值（500）"""
        response = client.get('/deploy-config/server-logs?type=backend&preset=500')
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data['success'] == False

    def test_query_logs_ssh_error(self, client, mock_ssh_error):
        """测试 SSH 命令执行失败"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_error):
            response = client.get('/deploy-config/server-logs?type=backend&preset=100')
            data = json.loads(response.data)

            assert response.status_code == 500
            assert data['success'] == False
            assert '获取日志失败' in data['message']

    def test_query_logs_empty_result(self, client, mock_ssh_empty):
        """测试空日志返回"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_empty):
            response = client.get('/deploy-config/server-logs?type=backend&preset=100')
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data['success'] == True
            assert data['data']['lines_count'] == 0  # 空字符串返回空列表
            assert data['data']['logs'] == ""

    def test_query_logs_lines_count(self, client):
        """测试返回的行数计算正确"""
        def mock_ssh_count(cmd, timeout=None):
            # 返回确切数量的日志行
            return True, "line1\nline2\nline3\nline4\nline5", ""

        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_count):
            response = client.get('/deploy-config/server-logs?type=backend&preset=100')
            data = json.loads(response.data)

            assert response.status_code == 200
            # line1\nline2\nline3\nline4\nline5 分割后得到 5 个元素
            assert data['data']['lines_count'] == 5

    # ==================== 下载日志功能测试 ====================

    def test_download_backend_logs(self, client, mock_ssh_download, tmp_path):
        """测试下载后端日志"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_download):
            response = client.get('/deploy-config/server-logs/download?type=backend')

            assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data.decode()}"
            # 检查 Content-Disposition header
            content_disposition = response.headers.get('Content-Disposition', '')
            assert 'attachment' in content_disposition
            assert 'backend_' in content_disposition
            # 检查 mimetype
            assert 'text/plain' in response.mimetype

    def test_download_nginx_access_logs(self, client, mock_ssh_download, tmp_path):
        """测试下载 Nginx 访问日志"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_download):
            response = client.get('/deploy-config/server-logs/download?type=nginx_access')

            assert response.status_code == 200
            content_disposition = response.headers.get('Content-Disposition', '')
            assert 'nginx_access_' in content_disposition

    def test_download_nginx_error_logs(self, client, mock_ssh_download, tmp_path):
        """测试下载 Nginx 错误日志"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_download):
            response = client.get('/deploy-config/server-logs/download?type=nginx_error')

            assert response.status_code == 200
            content_disposition = response.headers.get('Content-Disposition', '')
            assert 'nginx_error_' in content_disposition

    def test_download_logs_default_type(self, client, mock_ssh_download, tmp_path):
        """测试默认下载后端日志"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_download):
            response = client.get('/deploy-config/server-logs/download')

            assert response.status_code == 200
            content_disposition = response.headers.get('Content-Disposition', '')
            assert 'backend_' in content_disposition

    def test_download_logs_ssh_error(self, client, mock_ssh_error):
        """测试下载时 SSH 命令失败"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_error):
            response = client.get('/deploy-config/server-logs/download?type=backend')
            # 由于使用了 finally 清理，可能会抛出异常
            # 所以我们需要捕获这个情况
            try:
                data = json.loads(response.data)
                assert response.status_code == 500
                assert data['success'] == False
            except:
                # 如果无法解析 JSON，说明可能是异常响应
                assert response.status_code == 500

    def test_download_logs_filename_timestamp(self, client, mock_ssh_download, tmp_path):
        """测试下载文件名包含时间戳"""
        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh_download):
            response = client.get('/deploy-config/server-logs/download?type=backend')

            content_disposition = response.headers.get('Content-Disposition', '')
            # 解析文件名（格式：attachment; filename=backend_20260513_143025.log）
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1]
                # 检查文件名格式
                assert filename.startswith('backend_')
                assert filename.endswith('.log')
                # 检查时间戳格式（YYYYMMDD_HHMMSS）
                parts = filename[8:-4].split('_')
                assert len(parts) == 2
                assert len(parts[0]) == 8  # YYYYMMDD
                assert len(parts[1]) == 6  # HHMMSS
            else:
                pytest.fail(f"Filename not found in Content-Disposition: {content_disposition}")

    # ==================== 辅助函数测试 ====================

    def test_get_log_type_name_backend(self):
        """测试获取后端日志类型名称"""
        assert get_log_type_name('backend') == '后端日志'

    def test_get_log_type_name_nginx_access(self):
        """测试获取 Nginx 访问日志类型名称"""
        assert get_log_type_name('nginx_access') == 'Nginx 访问日志'

    def test_get_log_type_name_nginx_error(self):
        """测试获取 Nginx 错误日志类型名称"""
        assert get_log_type_name('nginx_error') == 'Nginx 错误日志'

    def test_get_log_type_name_unknown(self):
        """测试未知日志类型返回默认名称"""
        assert get_log_type_name('unknown') == '日志'


class TestIntegration:
    """集成测试 - 测试完整的查询和下载流程"""

    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['DATABASE_URI'] = 'sqlite:///:memory:'
        app.register_blueprint(deploy_config_bp)
        return app.test_client()

    def test_query_then_download_workflow(self, client, tmp_path):
        """测试先查询后下载的完整工作流"""
        def mock_ssh(cmd, timeout=None):
            # 如果是 cat 命令（下载场景），创建临时文件
            if cmd.startswith('cat ') and '> ' in cmd:
                target_file = cmd.split('> ')[-1].strip()
                logs = "\n".join([f"2026-05-13 10:00:{i%60:02d} INFO Log message {i}" for i in range(200)])
                with open(target_file, 'w') as f:
                    f.write(logs)
                return True, "", ""
            # 查询场景
            return True, "\n".join([f"2026-05-13 10:00:{i%60:02d} INFO Log message {i}" for i in range(200)]), ""

        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh):
            # 步骤 1：查询 100 行日志
            query_response = client.get('/deploy-config/server-logs?type=backend&preset=100')
            query_data = json.loads(query_response.data)

            assert query_response.status_code == 200
            assert query_data['success'] == True
            assert query_data['data']['requested_lines'] == 100

            # 步骤 2：下载完整日志
            download_response = client.get('/deploy-config/server-logs/download?type=backend')

            assert download_response.status_code == 200, f"Download failed: {download_response.data.decode()}"
            assert 'attachment' in download_response.headers.get('Content-Disposition', '')

    def test_all_log_types_query(self, client):
        """测试查询所有类型的日志"""
        def mock_ssh(cmd, timeout=None):
            return True, "sample log content", ""

        with patch('routes.deploy.deploy_config_routes.ssh_command', side_effect=mock_ssh):
            log_types = [
                ('backend', '后端日志'),
                ('nginx_access', 'Nginx 访问日志'),
                ('nginx_error', 'Nginx 错误日志')
            ]

            for log_type, expected_name in log_types:
                response = client.get(f'/deploy-config/server-logs?type={log_type}&preset=100')
                data = json.loads(response.data)

                assert response.status_code == 200, f"Failed for {log_type}"
                assert data['success'] == True
                assert data['data']['type'] == log_type
                assert data['data']['type_name'] == expected_name


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
