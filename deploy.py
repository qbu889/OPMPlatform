#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deploy.py - Python版智能部署脚本
解决Shell脚本的转义问题、端口配置错误、Nginx配置生成等问题
用法: python deploy.py
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# 配置
REMOTE_USER = "root"
REMOTE_HOST = "8.146.228.47"
REMOTE_PATH = "/project/wordToWord"
BACKUP_DIR = "/project/backups"
LOCAL_PORT = 5002  # 后端实际运行端口
NGINX_PORT = 5173  # Nginx监听端口
PROJECT_ROOT = Path(__file__).parent

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_header(title):
    print(f"\n{Colors.BOLD}{'='*50}{Colors.END}")
    print(f"{Colors.BOLD}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*50}{Colors.END}\n")

def run_command(cmd, cwd=None, check=True, timeout=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=check,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, "", str(e)
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"

def ssh_command(cmd, timeout=60):
    """执行SSH远程命令"""
    full_cmd = f"ssh -o LogLevel=ERROR -o StrictHostKeyChecking=no {REMOTE_USER}@{REMOTE_HOST} \"{cmd}\""
    success, stdout, stderr = run_command(full_cmd, timeout=timeout)
    if not success and stderr:
        print_warning(f"SSH命令警告: {stderr[:200]}")
    return success, stdout, stderr

def scp_upload(local_path, remote_path, recursive=False):
    """SCP上传文件"""
    flag = "-r" if recursive else ""
    cmd = f"scp -o LogLevel=ERROR -o StrictHostKeyChecking=no {flag} {local_path} {REMOTE_USER}@{REMOTE_HOST}:{remote_path}"
    success, stdout, stderr = run_command(cmd)
    return success

def git_commit_and_push():
    """Git提交并推送"""
    print_header("步骤 1: Git 提交与推送")
    
    # 检查是否有未提交的更改
    success, stdout, _ = run_command("git status --porcelain", cwd=PROJECT_ROOT)
    if stdout:
        print_info("检测到未提交的更改，正在提交...")
        run_command("git add -A", cwd=PROJECT_ROOT)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_command(f'git commit -m "Auto deploy: {timestamp}"', cwd=PROJECT_ROOT)
        print_success("提交完成")
    
    # 推送到远程
    print_info("推送到 Git 仓库...")
    success, stdout, stderr = run_command("git push origin q/dev", cwd=PROJECT_ROOT)
    if success:
        print_success("Git 推送成功")
        return True
    else:
        print_error(f"Git 推送失败: {stderr}")
        return False

def detect_changed_files():
    """检测变更的文件（最近3次提交）"""
    print_header("步骤 2: 检测变更文件")
    
    # 获取最新提交信息
    _, last_commit, _ = run_command("git log -1 --oneline", cwd=PROJECT_ROOT)
    print_info(f"最新提交: {last_commit}")
    
    # 方法1: 获取最近3次提交的文件变更
    success, changed_files, _ = run_command(
        "git diff-tree --no-commit-id --name-only -r HEAD~3..HEAD",
        cwd=PROJECT_ROOT
    )
    
    # 方法2: 如果失败，尝试其他方式
    if not changed_files:
        print_warning("git diff-tree 未检测到变更，尝试其他方式...")
        success, changed_files, _ = run_command(
            "git diff --name-only HEAD~3 HEAD",
            cwd=PROJECT_ROOT
        )
    
    # 方法3: 检查未提交的修改
    if not changed_files:
        print_warning("未检测到已提交的变更，检查未提交文件...")
        success, changed_files, _ = run_command(
            "git ls-files --modified",
            cwd=PROJECT_ROOT
        )
    
    # 方法4: 使用默认核心文件
    if not changed_files:
        print_warning("未检测到任何变更，将上传核心文件...")
        changed_files = "app.py config.py routes/kafka/kafka_generator_routes.py"
    
    # 解析文件列表
    files = [f.strip() for f in changed_files.split('\n') if f.strip()]
    
    print(f"\n{Colors.CYAN}📦 检测到以下变更文件:{Colors.END}")
    for f in files[:20]:
        print(f"   - {f}")
    if len(files) > 20:
        print(f"   ... 还有 {len(files) - 20} 个文件")
    print(f"   总计: {len(files)} 个文件\n")
    
    return files

def classify_files(files):
    """分类前端和后端文件"""
    backend_files = []
    frontend_source_files = []
    need_frontend_build = False
    
    for file in files:
        if file.startswith('frontend/'):
            # 前端源码需要重新构建
            if 'dist/' not in file and 'node_modules/' not in file:
                frontend_source_files.append(file)
                need_frontend_build = True
        else:
            backend_files.append(file)
    
    return backend_files, frontend_source_files, need_frontend_build

def upload_backend_files(backend_files):
    """上传后端文件（打包方式）"""
    if not backend_files:
        print_info("无后端文件变更")
        return True
    
    print_header("步骤 3: 上传后端文件")
    print_info(f"准备上传 {len(backend_files)} 个后端文件...")
    
    # 创建临时目录
    import tempfile
    temp_dir = tempfile.mkdtemp()
    tar_path = os.path.join(temp_dir, "backend_update.tar.gz")
    
    try:
        # 复制文件到临时目录
        print_info("准备上传的文件列表:")
        for file in backend_files:
            src = PROJECT_ROOT / file
            if src.exists():
                dest = Path(temp_dir) / file
                dest.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(src, dest)
                print(f"      + {file}")
            else:
                print_warning(f"      {file} (文件不存在，跳过)")
        
        # 打包
        print_info("正在打包...")
        success, _, stderr = run_command(
            f"tar -czf {tar_path} .",
            cwd=temp_dir
        )
        
        if not success:
            print_error(f"打包失败: {stderr}")
            return False
        
        # 显示压缩包内容
        success, content, _ = run_command(f"tar -tzf {tar_path} | head -10", cwd=temp_dir)
        if content:
            print_info("压缩包内容预览:")
            for line in content.split('\n')[:5]:
                print(f"      {line}")
        
        # 上传压缩包
        print_info("上传压缩包...")
        remote_tar = "/tmp/backend_update.tar.gz"
        success = scp_upload(tar_path, remote_tar)
        
        if not success:
            print_error("上传压缩包失败")
            return False
        
        # 远程解压
        print_info("远程解压...")
        ssh_cmd = f"""cd {REMOTE_PATH} && \
                     tar -xzf {remote_tar} && \
                     rm -f {remote_tar} && \
                     echo '解压成功'"""
        
        success, stdout, stderr = ssh_command(ssh_cmd)
        
        if success:
            print_success("后端文件上传并解压成功")
            
            # 验证关键文件
            print_info("验证关键文件:")
            for file in backend_files[:5]:
                check_cmd = f"test -f {REMOTE_PATH}/{file} && echo '✓ {file}' || echo '✗ {file} (缺失)'"
                _, output, _ = ssh_command(check_cmd)
                print(f"      {output}")
            
            return True
        else:
            print_error(f"远程解压失败: {stderr}")
            return False
            
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def build_and_upload_frontend(need_frontend_build):
    """构建并上传前端"""
    print_header("步骤 4: 处理前端文件")
    
    frontend_dist = PROJECT_ROOT / "frontend" / "dist"
    
    # 如果需要重新构建或dist不存在
    if need_frontend_build or not (frontend_dist / "index.html").exists():
        print_info("前端需要重新构建...")
        success, stdout, stderr = run_command(
            "npm run build",
            cwd=PROJECT_ROOT / "frontend"
        )
        
        if not success:
            print_error(f"前端构建失败: {stderr}")
            return False
        
        print_success("前端构建成功")
    else:
        print_success("前端构建产物已存在")
    
    # 上传前端文件
    print_info("上传前端构建产物...")
    
    # 先清空远程dist目录
    ssh_command(f"rm -rf {REMOTE_PATH}/frontend/dist/*")
    
    # 上传整个dist目录
    local_dist = str(frontend_dist) + "/*"
    remote_dist = f"{REMOTE_PATH}/frontend/dist/"
    success = scp_upload(local_dist, remote_dist, recursive=True)
    
    if not success:
        print_error("前端文件上传失败")
        return False
    
    # 验证文件数量
    _, remote_count, _ = ssh_command(f"find {REMOTE_PATH}/frontend/dist -type f | wc -l")
    local_count = sum(1 for _ in frontend_dist.rglob('*') if _.is_file())
    
    print(f"   📊 本地文件数: {local_count}, 远程文件数: {remote_count}")
    
    if remote_count.strip().isdigit() and int(remote_count.strip()) > 0:
        print_success("前端文件上传成功")
        return True
    else:
        print_error("前端文件验证失败")
        return False

def generate_nginx_config():
    """生成Nginx配置文件（避免Shell转义问题）"""
    nginx_config = f"""server {{
    listen {NGINX_PORT};
    server_name {REMOTE_HOST} localhost opmvue.nokiafz.asia;
    
    root {REMOTE_PATH}/frontend/dist;
    index index.html;
    
    access_log {REMOTE_PATH}/logs/nginx_{NGINX_PORT}_access.log;
    error_log {REMOTE_PATH}/logs/nginx_{NGINX_PORT}_error.log;
    
    # 静态资源缓存控制
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires off;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        try_files $uri =404;
    }}
    
    # 通用 API 代理
    location /api/ {{
        proxy_pass http://127.0.0.1:{LOCAL_PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # 认证 API
    location = /login {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /register {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /forgot-password {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # DingTalk Push API
    location = /dingtalk-push/configs {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /dingtalk-push/test-webhook {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /dingtalk-push/history {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /dingtalk-push/statistics {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /dingtalk-push/preview {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /dingtalk-push/confirm-checkin {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /dingtalk-push/view-checkin {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Kafka Generator API
    location = /kafka-generator/field-meta {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /kafka-generator/field-meta/list {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /kafka-generator/field-cache {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /kafka-generator/field-order {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /kafka-generator/field-options {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /kafka-generator/generate {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location /kafka-generator/history {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /kafka-generator/field-history {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Schedule Config API
    location /schedule-config/api/ {{
        proxy_pass http://127.0.0.1:{LOCAL_PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # FPA Generator API
    location = /fpa-generator/upload {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location /fpa-generator/download/ {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location /fpa-generator/api/ {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # FPA Rules API
    location /fpa-rules {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Adjustment API
    location /adjustment {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location /adjustment-calc {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Chatbot API
    location /chatbot/upload_progress/ {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /chatbot/chat {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /chatbot/upload_document/preview {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /chatbot/upload_document/confirm {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location /chatbot/knowledge {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location /chatbot/session {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /chatbot/feedback {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Excel2Word API
    location /excel2word {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Word to Excel API
    location /word-to-excel/api {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Markdown Upload API
    location = /markdown-upload/upload {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /markdown-upload/convert {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    location = /markdown-upload/download {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Spreadsheet API
    location /spreadsheet {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # Swagger API
    location /swagger {{ proxy_pass http://127.0.0.1:{LOCAL_PORT}; }}
    
    # SPA 路由
    location / {{
        try_files $uri $uri/ /index.html;
    }}
    
    # 禁止访问隐藏文件
    location ~ /\\. {{
        deny all;
    }}
}}
"""
    return nginx_config

def update_nginx_config():
    """更新Nginx配置"""
    print_info("上传并应用Nginx配置...")
    
    # 生成Nginx配置
    nginx_config = generate_nginx_config()
    
    # 写入本地临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(nginx_config)
        local_nginx_conf = f.name
    
    try:
        # 上传Nginx配置
        remote_nginx_conf = "/tmp/nginx_deploy.conf"
        success = scp_upload(local_nginx_conf, remote_nginx_conf)
        
        if not success:
            print_warning("Nginx配置上传失败，跳过更新")
            return False
        
        # 分步执行远程命令（避免长命令超时）
        # 1. 复制配置文件
        ssh_command(f"cp {remote_nginx_conf} /www/server/panel/vhost/nginx/sql-formatter-{NGINX_PORT}.conf")
        
        # 2. 测试配置
        success, stdout, stderr = ssh_command("nginx -t")
        if success:
            print_success("Nginx配置测试通过")
        else:
            print_error(f"Nginx配置测试失败: {stderr[:200]}")
            return False
        
        # 3. 重载Nginx
        ssh_command("nginx -s reload")
        print_success("Nginx配置已更新")
        
        # 4. 修复权限
        ssh_command(f"chmod -R 755 {REMOTE_PATH}/frontend/dist/")
        ssh_command(f"chown -R www:www {REMOTE_PATH}/frontend/dist/")
        
        return True
        
    finally:
        # 清理临时文件
        os.unlink(local_nginx_conf)
        ssh_command(f"rm -f {remote_nginx_conf}")

def restart_services():
    """重启服务"""
    print_header("步骤 5: 远程备份并重启服务")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 1. 备份
    print_info("步骤 5.1: 备份现有项目")
    backup_cmd = f"""
    mkdir -p {BACKUP_DIR}
    cd /project
    tar -czf {BACKUP_DIR}/wordToWord_backup_{timestamp}.tar.gz \\
        --exclude='node_modules' \\
        --exclude='.venv' \\
        --exclude='__pycache__' \\
        --exclude='*.pyc' \\
        --exclude='logs/*.log' \\
        wordToWord/
    echo "备份完成"
    """
    success, stdout, stderr = ssh_command(backup_cmd, timeout=120)
    if success:
        print_success("备份完成")
    else:
        print_warning(f"备份可能有问题: {stderr[:100]}")
    
    # 2. 停止旧进程
    print_info("步骤 5.2: 停止现有服务")
    stop_cmd = f"""
    cd {REMOTE_PATH}
    pkill -f "python app.py" 2>/dev/null || true
    sleep 2
    echo "进程已停止"
    """
    ssh_command(stop_cmd)
    print_success("进程已停止")
    
    # 3. 启动新服务
    print_info("步骤 5.3: 启动新服务")
    
    # 更新Nginx配置
    update_nginx_config()
    
    # 启动后端
    start_cmd = f"""
    cd {REMOTE_PATH}
    source .venv/bin/activate
    export PORT={LOCAL_PORT}
    nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
    echo "后端已启动 (PID: $!)"
    """
    
    success, stdout, stderr = ssh_command(start_cmd)
    print_success("后端服务已启动")
    
    # 4. 验证服务状态
    print_info("步骤 5.4: 验证服务状态")
    
    # 检查进程
    _, processes, _ = ssh_command("ps -ef | grep 'python app.py' | grep -v grep")
    if processes:
        print_success("后端进程运行中:")
        print(f"   {processes}")
    
    # 检查端口
    _, port_check, _ = ssh_command(f"lsof -i:{LOCAL_PORT} | head -3")
    if port_check:
        print_success(f"端口 {LOCAL_PORT} 监听正常")
    
    # 查看日志
    _, logs, _ = ssh_command(f"cd {REMOTE_PATH} && tail -10 logs/backend.log")
    if logs:
        print_info("后端日志（最后10行）:")
        for line in logs.split('\n')[-10:]:
            print(f"   {line}")

def test_api():
    """测试API接口"""
    print_header("步骤 6: 测试API接口")
    
    test_data = {
        "data": [{
            "EVENT_FP": "TEST_DEPLOY",
            "DISPATCH_INFO": {"DISPATCH_REASON": "部署测试"}
        }]
    }
    
    import urllib.request
    import urllib.error
    
    url = f"http://{REMOTE_HOST}:{NGINX_PORT}/api/clean-event/process"
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(test_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode('utf-8'))
        
        if result.get('success'):
            print_success("API接口测试通过！")
            print_info(f"返回数据: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}...")
            return True
        else:
            print_error(f"API返回失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print_error(f"API测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    print_header("🚀 Python智能部署脚本")
    print_info(f"目标服务器: {REMOTE_USER}@{REMOTE_HOST}")
    print_info(f"后端端口: {LOCAL_PORT}, Nginx端口: {NGINX_PORT}")
    print()
    
    try:
        # 1. Git提交和推送
        if not git_commit_and_push():
            print_error("Git操作失败，终止部署")
            sys.exit(1)
        
        # 2. 检测变更文件
        changed_files = detect_changed_files()
        
        # 3. 分类文件
        backend_files, frontend_files, need_build = classify_files(changed_files)
        
        # 4. 上传后端文件
        if backend_files:
            if not upload_backend_files(backend_files):
                print_error("后端文件上传失败")
                sys.exit(1)
        
        # 5. 构建并上传前端
        if not build_and_upload_frontend(need_build):
            print_error("前端文件上传失败")
            sys.exit(1)
        
        # 6. 重启服务
        restart_services()
        
        # 7. 等待服务完全启动
        print_info("等待服务完全启动...")
        time.sleep(5)
        
        # 8. 测试API
        test_api()
        
        print_header("✅ 部署完成！")
        print(f"{Colors.GREEN}📍 访问地址:{Colors.END}")
        print(f"   后端: http://{REMOTE_HOST}:{LOCAL_PORT}")
        print(f"   前端: http://{REMOTE_HOST}:{NGINX_PORT}")
        print()
        print(f"{Colors.CYAN}💡 提示:{Colors.END}")
        print("   1. 请清除浏览器缓存后访问前端页面")
        print("   2. Mac: Cmd+Shift+R, Windows: Ctrl+Shift+R")
        print("   3. 查看日志: ssh root@8.146.228.47 'tail -f /project/wordToWord/logs/backend.log'")
        
    except KeyboardInterrupt:
        print_warning("\n用户中断部署")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n部署过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
