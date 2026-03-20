# 日志等级配置 - 快速参考

## 🚀 快速使用

### 只输出错误日志（生产环境推荐）
```bash
# 在 .env 文件中设置
LOG_LEVEL=ERROR
```

### 输出错误 + 警告
```bash
LOG_LEVEL=WARNING
```

### 输出所有日志（开发调试推荐）
```bash
LOG_LEVEL=DEBUG
```

## 📊 日志级别对比

| 级别 | 输出内容 | 适用场景 |
|------|---------|---------|
| **ERROR** | 只输出错误 | 生产环境，只关注系统错误 |
| **WARNING** | 错误 + 警告 | 生产环境，关注潜在问题 |
| **INFO** ⭐ | 错误 + 警告 + 信息 | 开发环境、日常运维（默认） |
| **DEBUG** | 所有日志（含调试详情） | 开发调试、问题排查 |

## 💡 常用配置示例

### 1. 生产环境（最小化输出）
```bash
LOG_LEVEL=ERROR
LOG_TO_CONSOLE=True
LOG_TO_FILE=True
```

### 2. 开发环境（详细输出）
```bash
LOG_LEVEL=DEBUG
LOG_TO_CONSOLE=True
LOG_TO_FILE=True
```

### 3. 仅文件日志（静默模式）
```bash
LOG_LEVEL=INFO
LOG_TO_CONSOLE=False
LOG_TO_FILE=True
```

### 4. 临时调试（命令行）
```bash
# Linux/Mac
LOG_LEVEL=DEBUG python app.py

# Windows
set LOG_LEVEL=DEBUG && python app.py
```

## 🔧 配置文件位置

- **.env** - 环境变量配置文件（项目根目录）
- **logs/** - 日志文件存储目录
- **test_log_levels.py** - 测试脚本

## ✅ 验证配置

运行测试脚本验证各个级别的效果：
```bash
python test_log_levels.py
```

## 📝 修改后记得重启应用

环境变量在应用启动时读取，修改配置后需要重启应用才能生效。
