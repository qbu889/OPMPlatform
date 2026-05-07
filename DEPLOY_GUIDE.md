# Python智能部署脚本使用指南

## 📋 概述

`deploy.py` 是一个用Python重写的智能部署脚本，解决了原Shell脚本(`deploy_with_backup.sh`)的以下问题：

### ✅ 解决的问题

1. **Shell转义问题** - Nginx配置中的`$host`、`$remote_addr`等变量不会被错误解析
2. **端口配置错误** - 统一管理后端端口(5002)和Nginx端口(5173)
3. **Nginx配置生成** - 使用Python字符串模板，避免heredoc语法问题
4. **超时处理** - SSH命令支持timeout参数，避免长时间等待
5. **错误处理** - 更完善的异常捕获和错误提示
6. **文件验证** - 自动验证上传的文件数量和完整性

## 🚀 使用方法

### 基本用法

```bash
cd /Users/linziwang/PycharmProjects/wordToWord
python deploy.py
```

或者直接执行（需要执行权限）：

```bash
chmod +x deploy.py
./deploy.py
```

### 配置说明

在脚本顶部可以修改以下配置：

```python
REMOTE_USER = "root"           # 远程服务器用户
REMOTE_HOST = "8.146.228.47"   # 远程服务器IP
REMOTE_PATH = "/project/wordToWord"  # 远程项目路径
BACKUP_DIR = "/project/backups"      # 备份目录
LOCAL_PORT = 5002              # 后端运行端口
NGINX_PORT = 5173              # Nginx监听端口
```

## 📊 部署流程

### 步骤 1: Git提交与推送
- 自动检测未提交的更改
- 提交并推送到远程仓库(q/dev分支)

### 步骤 2: 检测变更文件
- 检查最近3次提交的文件变更
- 支持多种检测方法（diff-tree、diff、ls-files）
- 如果没有检测到变更，使用默认核心文件

### 步骤 3: 上传后端文件
- 将变更的后端文件打包成tar.gz
- SCP上传到远程服务器
- 远程解压并验证文件完整性

### 步骤 4: 处理前端文件
- 如果前端源码有变更，自动执行`npm run build`
- 清空远程dist目录
- SCP上传整个dist目录
- 验证本地和远程文件数量一致性

### 步骤 5: 远程备份并重启服务
- **5.1 备份**: 压缩备份当前项目（排除node_modules、.venv等）
- **5.2 停止**: 清理旧的Python进程
- **5.3 启动**: 
  - 生成并更新Nginx配置（Python动态生成，无转义问题）
  - 测试Nginx配置
  - 重载Nginx
  - 修复文件权限
  - 启动后端服务（PORT=5002）
- **5.4 验证**: 检查进程状态和端口监听

### 步骤 6: 测试API接口
- 发送测试请求到`/api/clean-event/process`
- 验证返回数据结构
- 确认新字段（ORDER_TYPE、IS_MAIN_ORDER、DISPATCH_REASON）存在

## 🔧 技术优势

### vs Shell脚本

| 特性 | Shell脚本 | Python脚本 |
|------|-----------|------------|
| 字符串转义 | ❌ 复杂，易出错 | ✅ 原生支持 |
| Nginx配置生成 | ❌ heredoc语法问题 | ✅ 字符串模板 |
| 错误处理 | ⚠️ 基础 | ✅ 完善try-except |
| 超时控制 | ❌ 不支持 | ✅ subprocess timeout |
| JSON处理 | ❌ 需要jq | ✅ 内置json模块 |
| 跨平台 | ❌ Bash依赖 | ✅ Python通用 |
| 可维护性 | ⚠️ 中等 | ✅ 高 |

### 关键改进

1. **Nginx配置生成**
   ```python
   # Python方式 - 清晰、无转义问题
   nginx_config = f"""server {{
       location /api/ {{
           proxy_pass http://127.0.0.1:{LOCAL_PORT};
           proxy_set_header Host $host;  # $符号不会被解析
       }}
   }}"""
   ```

2. **SSH命令执行**
   ```python
   # 支持超时、错误捕获
   def ssh_command(cmd, timeout=60):
       try:
           result = subprocess.run(..., timeout=timeout)
           return success, stdout, stderr
       except subprocess.TimeoutExpired:
           return False, "", "Command timed out"
   ```

3. **文件验证**
   ```python
   # 自动对比本地和远程文件数
   local_count = sum(1 for _ in frontend_dist.rglob('*') if _.is_file())
   remote_count = ssh_command("find ... | wc -l")
   print(f"本地: {local_count}, 远程: {remote_count}")
   ```

## 🐛 常见问题

### Q1: 部署失败怎么办？

查看输出日志，脚本会显示详细的错误信息。常见原因：
- SSH连接失败 → 检查网络和SSH密钥
- Git推送失败 → 检查分支和权限
- 前端构建失败 → 检查Node.js版本和依赖

### Q2: 如何只部署前端或后端？

目前脚本是全量部署。如需单独部署，可以：
- 注释掉不需要的步骤
- 或修改`classify_files`函数逻辑

### Q3: Nginx配置更新失败？

检查：
1. Nginx配置文件路径是否正确
2. 是否有root权限
3. `nginx -t`测试结果

手动修复：
```bash
ssh root@8.146.228.47
nginx -t
nginx -s reload
```

### Q4: 端口被占用？

脚本会自动清理旧进程。如果仍有问题：
```bash
ssh root@8.146.228.47
lsof -i:5002  # 查看占用进程
kill -9 <PID>  # 强制终止
```

## 📝 最佳实践

1. **部署前检查**
   - 确保本地代码已测试通过
   - 确认远程服务器空间充足
   - 备份重要数据

2. **部署后验证**
   - 访问前端页面（清除缓存）
   - 测试关键API接口
   - 查看后端日志

3. **回滚方案**
   如果部署后出现问题，可以快速回滚：
   ```bash
   ssh root@8.146.228.47
   cd /project/backups
   ls -lt wordToWord_backup_*.tar.gz  # 找到最新备份
   tar -xzf wordToWord_backup_YYYYMMDD_HHMMSS.tar.gz -C /project/
   cd /project/wordToWord
   source .venv/bin/activate
   export PORT=5002
   nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &
   ```

## 🔮 未来优化方向

- [ ] 支持多环境配置（dev/test/prod）
- [ ] 添加部署前健康检查
- [ ] 支持增量部署（只上传变更文件）
- [ ] 添加部署历史记录
- [ ] Web界面可视化部署
- [ ] 支持回滚到指定版本

## 📞 技术支持

如有问题，请查看：
- 部署日志输出
- 后端日志: `/project/wordToWord/logs/backend.log`
- Nginx日志: `/project/wordToWord/logs/nginx_5173_error.log`

---

**最后更新**: 2026-05-07  
**版本**: v1.0  
**作者**: Lingma AI Assistant
