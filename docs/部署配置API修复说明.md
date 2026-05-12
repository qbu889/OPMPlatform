# 部署配置API 404错误修复说明

## 问题描述

前端访问部署配置相关API时出现404错误，所有请求返回HTML页面而不是JSON数据：

```
DeployConfig.vue:457 加载部署状态失败: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
DeployConfig.vue:492 加载日志失败: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
DeployConfig.vue:572 加载备份列表失败: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
DeployConfig.vue:554 加载服务器日志失败: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
DeployConfig.vue:414 加载部署配置失败: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
stream:1  GET http://192.168.124.11:5200/deploy-config/logs/stream 404 (Not Found)
```

## 根本原因

1. **Nginx配置缺失**: Nginx配置文件中缺少对 `/deploy-config/` 路径的代理配置。当前端请求 `/deploy-config/*` API时，Nginx没有将其代理到后端Flask服务，而是返回了前端的 `index.html` 文件。

2. **Vite开发服务器配置缺失**: 在本地开发环境中，Vite开发服务器（端口5200）的代理配置中也缺少 `/deploy-config` 路径的代理规则。

## 解决方案

### 1. Nginx配置文件修复

已在以下Nginx配置文件中添加 `/deploy-config/` 路径的代理规则：

- `nginx_5173.conf` (生产环境)
- `nginx_5173_complete.conf` (完整配置)
- `nginx_5173_local.conf` (本地环境)
- `nginx_5173_local_dev.conf` (本地开发环境)

### 2. Vite开发服务器配置修复

在 `frontend/vite.config.js` 中添加了 `/deploy-config` 的代理规则。

添加的配置内容：

```nginx
# Deploy Config API
location /deploy-config/ {
    proxy_pass http://127.0.0.1:5004;  # 本地环境使用 5002
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    # SSE 支持（用于实时日志流）
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 86400s;
    proxy_send_timeout 86400s;
}
```

## 关键配置说明

1. **proxy_pass**: 将请求代理到后端Flask服务
   - 生产环境: `http://127.0.0.1:5004`
   - 本地环境: `http://127.0.0.1:5002`

2. **SSE支持**: 由于 `/deploy-config/logs/stream` 使用 Server-Sent Events (SSE) 技术推送实时日志，需要特殊配置：
   - `proxy_buffering off`: 禁用缓冲，确保实时推送
   - `proxy_cache off`: 禁用缓存
   - `proxy_read_timeout 86400s`: 设置长超时时间（24小时）

## 应用步骤

### 本地开发环境（使用Vite）

1. **重启Vite开发服务器**：
```bash
cd frontend
npm run dev
# 或
yarn dev
```

2. **如果使用Nginx代理**，重启Nginx服务：
```bash
sudo nginx -t                    # 测试配置
sudo nginx -s reload             # 重新加载配置
```

或者：
```bash
brew services restart nginx      # macOS
# 或
sudo systemctl restart nginx     # Linux
```

### 生产环境

1. 上传更新后的配置文件到服务器
2. 测试配置：
```bash
sudo nginx -t
```

3. 重新加载Nginx：
```bash
sudo nginx -s reload
```

## 验证方法

1. **清除浏览器缓存**：
   - Chrome: `Ctrl+Shift+Delete` (Windows) 或 `Cmd+Shift+Delete` (Mac)
   - 或者使用无痕模式测试

2. **重启开发服务器**（本地环境）：
```bash
cd frontend
# 停止当前运行的Vite服务器（Ctrl+C）
# 然后重新启动
npm run dev
```

3. **刷新页面**并检查浏览器控制台，应该不再出现404错误

4. **测试各个功能**：
   - 加载部署配置
   - 查看部署状态
   - 连接实时日志流
   - 加载备份列表
   - 查看服务器日志

## 涉及的API端点

以下API端点现在应该可以正常工作：

- `GET /deploy-config/config` - 获取部署配置
- `POST /deploy-config/config` - 更新部署配置
- `GET /deploy-config/status` - 获取部署状态
- `GET /deploy-config/logs` - 获取部署日志
- `GET /deploy-config/logs/stream` - 实时日志流（SSE）
- `GET /deploy-config/backups` - 获取备份列表
- `POST /deploy-config/deploy` - 开始部署
- `POST /deploy-config/backup` - 创建备份
- `POST /deploy-config/restart` - 重启服务
- `GET /deploy-config/server-logs` - 获取服务器日志

## 注意事项

1. 确保后端Flask服务正在运行
2. 确保后端端口配置正确（本地5002，生产5004）
3. SSE连接会保持长时间开启，这是正常现象
4. 如果仍有问题，检查Nginx错误日志：`/var/log/nginx/error.log` 或项目日志目录
