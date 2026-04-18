# 图片水印清除系统 - 快速启动指南

## 🚀 5分钟快速上手

### 第一步：确认依赖已安装

```bash
# 检查OpenCV和Pillow是否已安装
pip list | grep -E "opencv|Pillow"
```

如果未安装，执行：
```bash
pip install opencv-python Pillow
```

### 第二步：启动后端服务

在项目根目录执行：
```bash
python app.py
```

看到以下输出表示成功：
```
启动 Flask 应用 (开发环境)，端口：5001
```

### 第三步：访问应用

浏览器打开：
```
http://127.0.0.1:5001/watermark-remover
```

或者通过前端开发服务器（如果需要热更新）：
```bash
cd frontend
npm run dev
```
然后访问：`http://localhost:5173/watermark-remover`

## 📝 使用示例

### 示例1：手动去除右下角水印

1. 上传带水印的图片
2. 选择"手动框选"模式
3. 在右下角水印区域拖拽画框
4. 点击"开始处理"
5. 查看结果，满意则下载

### 示例2：自动去除常见位置水印

1. 上传图片
2. 选择"自动识别"模式
3. 点击"开始处理"
4. 系统自动检测并去除底部/角落的水印

### 示例3：调整参数优化效果

如果默认效果不理想：
1. 尝试切换算法（Telea ↔ Navier-Stokes）
2. 调整修复半径（建议3-5之间）
3. 重新处理查看效果

## 🧪 运行测试

```bash
python test_watermark_removal.py
```

测试将自动：
- 创建测试图片
- 测试上传功能
- 测试手动去除
- 测试自动去除
- 测试下载功能
- 测试清理功能

## 📂 文件位置

- **上传的图片**：`uploads/watermark/`
- **处理结果**：`uploads/watermark/results/`
- **测试图片**：`test_uploads/test_watermark.jpg`

## ⚙️ 配置说明

### 修改上传大小限制

编辑 `app.py`：
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 改为需要的值
```

### 修改支持的文件格式

编辑 `routes/document_convert/watermark_routes.py`：
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}  # 添加新格式
```

### 修改临时文件保留时间

编辑 `watermark_routes.py` 的 cleanup 函数：
```python
cutoff_time = now - timedelta(hours=24)  # 改为需要的小时数
```

## ❓ 常见问题

### Q: 为什么Canvas无法显示图片？
A: 检查浏览器控制台是否有CORS错误，确保后端服务正在运行。

### Q: 处理后的图片质量下降？
A: 这是正常的，OpenCV inpaint会有一定程度的模糊。可以尝试：
- 减小修复半径
- 更精确地框选水印区域
- 使用Navier-Stokes算法

### Q: 自动识别没有检测到水印？
A: 自动识别主要针对常见位置（底部、角落）的浅色水印。对于复杂水印，建议使用手动模式。

### Q: 可以批量处理吗？
A: 当前版本不支持批量处理，可以逐个上传处理。批量功能是计划中的扩展功能。

## 🎯 最佳实践

1. **选择合适的修复半径**
   - 小水印：半径 2-3
   - 中等水印：半径 3-5
   - 大水印：半径 5-8

2. **精确框选**
   - 尽量只框选水印部分
   - 避免包含过多背景
   - 多个小区域比一个大区域效果好

3. **算法选择**
   - 简单背景：Telea（速度快）
   - 复杂背景：Navier-Stokes（效果好）

4. **文件格式**
   - 优先使用PNG（无损）
   - JPG会有压缩损失
   - 避免多次保存JPG

## 🔗 相关链接

- [完整文档](./WATERMARK_REMOVER_README.md)
- [需求文档](./图片去除水印.md)
- [API接口文档](./WATERMARK_REMOVER_README.md#api接口文档)

## 💡 提示

- 临时文件会在24小时后自动清理
- 处理大图片可能需要几秒到十几秒
- 建议在光线充足的环境下查看处理结果
- 可以多次尝试不同参数找到最佳效果

---

**祝使用愉快！** 🎉
