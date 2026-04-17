# Mac 应用打包说明

## 📦 快速打包

### 方法一：使用构建脚本（推荐）

```bash
# 1. 打开终端，进入项目目录
cd /Users/linziwang/PycharmProjects/wordToWord

# 2. 激活虚拟环境（可选，但推荐）
source .venv/bin/activate

# 3. 运行构建脚本
chmod +x build_app.sh
./build_app.sh
```

### 方法二：手动构建

```bash
# 1. 进入项目目录
cd /Users/linziwang/PycharmProjects/wordToWord

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 安装 py2app（如果未安装）
pip install py2app

# 4. 清理旧的构建文件
rm -rf build dist *.egg-info

# 5. 运行构建
python setup.py py2app
```

## 🚀 使用打包好的应用

构建完成后，会在 `dist` 目录下生成 `OPM 综合业务系统.app` 文件。

### 启动方式

**方式 1：双击启动**
1. 打开 Finder
2. 进入项目目录下的 `dist` 文件夹
3. 双击 `OPM 综合业务系统.app`

**方式 2：命令行启动**
```bash
open dist/OPM\ 综合业务系统.app
```

**方式 3：移动到应用程序文件夹**
```bash
# 复制到应用程序目录
cp -r dist/OPM\ 综合业务系统.app /Applications/

# 然后可以在 Launchpad 或应用程序文件夹中找到并启动
```

## ⚙️ 应用特性

- ✅ **自动打开浏览器**：启动后会自动在默认浏览器中打开 http://127.0.0.1:5001
- ✅ **独立运行**：无需安装 Python 或任何依赖
- ✅ **后台服务**：应用会在后台运行，菜单栏会显示 Python 图标
- ✅ **日志记录**：日志文件保存在 `logs/` 目录下

## 🛑 停止应用

有以下几种方式可以停止应用：

**方式 1：通过菜单栏**
1. 点击菜单栏的 Python 图标
2. 选择 "Quit"

**方式 2：强制退出**
1. 按 `Cmd + Q`
2. 或者右键点击应用图标，选择 "强制退出"

**方式 3：终端命令**
```bash
# 查找进程
ps aux | grep "OPM"

# 杀死进程
kill -9 <进程 ID>
```

## 📝 注意事项

1. **首次启动提示**：
   - macOS 可能会提示"无法打开，因为来自身份不明的开发者"
   - 解决方法：
     - 打开"系统偏好设置" → "安全性与隐私"
     - 点击"仍要打开"
     - 或者右键点击 .app 文件，选择"打开"

2. **端口占用**：
   - 应用默认使用 5001 端口
   - 如果端口被占用，应用可能无法启动
   - 可以通过设置环境变量修改端口：
     ```bash
     export PORT=5002
     open dist/OPM\ 综合业务系统.app
     ```

3. **文件大小**：
   - 打包后的应用约 200-300MB
   - 包含了所有必需的 Python 库和依赖

4. **性能**：
   - 首次启动可能较慢（10-20 秒）
   - 后续启动会更快

## 🔧 自定义配置

### 修改应用名称

编辑 `setup.py` 文件：
```python
OPTIONS = {
    'plist': {
        'CFBundleName': '你的应用名称',
        'CFBundleDisplayName': '你的显示名称',
        # ...
    }
}
```

### 添加应用图标

准备一个 `.icns` 格式的图标文件，然后在 `setup.py` 中指定：
```python
OPTIONS = {
    'iconfile': 'path/to/your/icon.icns',
    # ...
}
```

### 包含更多文件

如果需要包含其他文件或目录，在 `setup.py` 的 `DATA_FILES` 中添加：
```python
DATA_FILES = [
    'templates（弃用）',
    'static',
    'config.py',
    '.env',
    '你的其他文件',
]
```

## 🐛 常见问题

### 问题 1：应用无法启动
- 检查终端输出，查看错误信息
- 确保所有依赖都已正确安装
- 尝试重新构建：`rm -rf build dist && python setup.py py2app`

### 问题 2：页面显示异常
- 检查 `templates` 和 `static` 目录是否已正确打包
- 查看日志文件：`logs/app_YYYYMMDD.log`

### 问题 3：数据库连接失败
- 确保 `.env` 文件中的数据库配置正确
- 检查 MySQL 服务是否正在运行

### 问题 4：AI 功能不可用
- 检查 Ollama 服务是否正在运行
- 确认模型已正确下载：`ollama pull qwen3:4b`

## 📊 构建统计

- **构建时间**：通常 2-5 分钟
- **应用大小**：约 200-300MB
- **支持系统**：macOS 10.15 (Catalina) 及以上
- **架构支持**：Intel 和 Apple Silicon (M1/M2/M3)

## 🎯 下一步

构建完成后，你可以：
1. 将 `.app` 文件分发给其他用户
2. 创建安装包（.dmg 或 .pkg）
3. 提交到 Mac App Store（需要开发者账号）

---

**技术支持**：如有问题，请查看日志文件或联系开发团队。
