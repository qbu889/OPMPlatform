# 部署脚本使用指南

## 🚀 三种部署模式

### 1. 完整部署（默认）
适用于重大更新、首次部署或前端代码变更。

```bash
python deploy.py
```

**执行流程：**
- ✅ Git提交并推送
- ✅ 检测变更文件
- ✅ 打包上传后端文件
- ✅ 构建并上传前端
- ✅ 更新Nginx配置
- ✅ 重启所有服务
- ✅ API测试验证

**耗时：** 约2-5分钟

---

### 2. ⚡ 快速部署（推荐日常使用）
适用于仅修改后端Python文件的小改动。

```bash
python deploy.py --fast
```

**执行流程：**
- ✅ 自动检测最近变更的文件
- ✅ 直接SCP上传（不打包）
- ✅ 询问是否重启后端服务
- ❌ 跳过Git操作
- ❌ 跳过前端构建
- ❌ 不更新Nginx配置

**耗时：** 约10-30秒

**示例输出：**
```
⚡ 快速部署模式
检测最近变更的文件...
检测到 2 个变更文件

📤 上传 2 个后端文件
上传: routes/kafka/kafka_generator_routes.py -> /project/wordToWord/routes/kafka/kafka_generator_routes.py
✓ kafka_generator_routes.py
上传: app.py -> /project/wordToWord/app.py
✓ app.py

是否重启后端服务？(y/n): y
重启后端服务...
后端服务已重启 (PID: 12345)
端口 5004 监听正常

✅ 快速部署完成！
```

---

### 3. 📁 指定文件部署
精确控制要部署的文件。

```bash
# 部署单个文件
python deploy.py --file routes/kafka/kafka_generator_routes.py

# 部署多个文件
python deploy.py --file app.py config.py routes/kafka/kafka_generator_routes.py
```

---

## 💡 使用场景对比

| 场景 | 推荐命令 | 原因 |
|------|---------|------|
| 修改了Kafka生成器逻辑 | `python deploy.py --fast` | 只改了Python文件，无需重新构建前端 |
| 修改了Vue组件 | `python deploy.py` | 需要重新构建前端 |
| 紧急修复Bug | `python deploy.py --file app.py` | 只上传关键文件，最快 |
| 首次部署 | `python deploy.py` | 完整初始化所有配置 |
| 更新了Nginx配置 | `python deploy.py` | 需要更新Nginx配置 |
| 只改了配置文件 | `python deploy.py --fast --no-restart` | 上传后手动决定何时重启 |

---

## 🔧 高级选项

### 不重启服务
```bash
python deploy.py --fast --no-restart
```
适用于：配置文件变更、静态资源更新等不需要重启的场景。

### 混合使用
```bash
# 快速部署指定文件且不重启
python deploy.py --file config.py --no-restart
```

---

## ⚠️ 注意事项

### 快速模式的限制
1. **不支持前端变更**：如果检测到 `.vue` 或 `.js` 文件变更，会提示使用完整模式
2. **不更新Nginx**：如果修改了路由或API端点，需要使用完整模式
3. **无备份**：快速模式不会创建备份，重要变更前建议手动备份

### 何时必须使用完整模式
- ✅ 前端代码变更（`.vue`, `.js`, `.css`）
- ✅ 新增API路由
- ✅ 修改Nginx配置相关
- ✅ 数据库结构变更
- ✅ 依赖包更新

### 何时可以使用快速模式
- ✅ 修改现有Python业务逻辑
- ✅ 修复Bug
- ✅ 调整配置参数
- ✅ 小范围代码优化

---

## 📊 性能对比

| 操作 | 完整模式 | 快速模式 |
|------|---------|---------|
| Git操作 | ~5s | ❌ 跳过 |
| 文件检测 | ~2s | ~1s |
| 文件上传 | ~10-30s | ~5-10s |
| 前端构建 | ~30-60s | ❌ 跳过 |
| Nginx更新 | ~5s | ❌ 跳过 |
| 服务重启 | ~10s | ~5s（可选）|
| **总计** | **~60-120s** | **~10-30s** |

**速度提升：约 4-8 倍！**

---

## 🎯 最佳实践

### 开发阶段
```bash
# 日常小改动
python deploy.py --fast

# 改完多个文件后统一提交
git add -A
git commit -m "feat: xxx"
python deploy.py --fast
```

### 发布阶段
```bash
# 正式发布前完整测试
python deploy.py
```

### 紧急修复
```bash
# 最快速度上线修复
python deploy.py --file routes/xxx/fix_bug.py --no-restart
# 验证无误后再重启
ssh root@8.146.228.47 "cd /project/wordToWord && pkill -f 'python app.py' && sleep 2 && source .venv/bin/activate && nohup python app.py --host 0.0.0.0 > logs/backend.log 2>&1 &"
```

---

## 🔍 故障排查

### 快速模式上传失败
```bash
# 检查网络连接
ping 8.146.228.47

# 手动测试SCP
scp test.txt root@8.146.228.47:/tmp/

# 切换到完整模式
python deploy.py
```

### 服务重启后无法访问
```bash
# 查看日志
ssh root@8.146.228.47 "tail -f /project/wordToWord/logs/backend.log"

# 检查进程
ssh root@8.146.228.47 "ps -ef | grep 'python app.py'"

# 检查端口
ssh root@8.146.228.47 "lsof -i:5004"
```

---

## 📝 总结

- **日常开发** → `python deploy.py --fast` （快！）
- **前端变更** → `python deploy.py` （稳！）
- **紧急修复** → `python deploy.py --file xxx.py` （准！）

选择合适的模式，让部署更高效！🚀
