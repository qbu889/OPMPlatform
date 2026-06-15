# 图片水印清除系统

基于现有框架开发的图片水印清除工具，支持手动框选和自动识别两种模式去除图片水印。

## 功能特性

- ✅ **图片上传**：支持拖拽和点击上传，限制JPG/PNG/BMP格式，最大10MB
- ✅ **手动框选**：通过Canvas交互式框选水印区域，支持多区域选择
- ✅ **自动识别**：智能检测常见位置的水印（底部、角落等）
- ✅ **图像修复**：基于OpenCV inpaint算法（Telea和Navier-Stokes两种方法）
- ✅ **结果对比**：原图与处理后图片并排对比显示
- ✅ **一键下载**：处理完成后直接下载结果图片
- ✅ **临时文件管理**：24小时自动清理机制

## 技术栈

### 后端
- Flask (Python)
- OpenCV-Python (图像处理)
- Pillow (图片操作)
- NumPy (数值计算)

### 前端
- Vue.js 3
- Element Plus (UI组件库)
- Axios (HTTP请求)
- Canvas API (图像交互)

## 快速开始

### 1. 安装依赖

```bash
pip install opencv-python Pillow
```

或更新requirements.txt后：

```bash
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python app.py
```

服务将在 `http://127.0.0.1:5001` 启动

### 3. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

### 4. 访问应用

浏览器打开：`http://localhost:5173/watermark-remover`

## API接口文档

### 1. 上传图片

**接口**: `POST /api/watermark/upload`

**请求**:
- Content-Type: multipart/form-data
- 参数: `image` (文件)

**响应**:
```json
{
  "success": true,
  "filename": "uuid.jpg",
  "original_name": "test.jpg",
  "size": 1024000,
  "upload_time": "2024-01-01 12:00:00",
  "message": "上传成功"
}
```

### 2. 手动去除水印

**接口**: `POST /api/watermark/remove`

**请求体**:
```json
{
  "filename": "uuid.jpg",
  "bboxes": [[x, y, w, h], ...],
  "algorithm": "telea",
  "radius": 3
}
```

**参数说明**:
- `filename`: 上传后的文件名
- `bboxes`: 边界框数组，每个元素为 [x, y, width, height]
- `algorithm`: 修复算法，可选 "telea" 或 "ns"
- `radius`: 修复半径，1-10之间

**响应**:
```json
{
  "success": true,
  "output_filename": "result_uuid.jpg",
  "image_data": "data:image/jpeg;base64,...",
  "processing_time": 2.5,
  "message": "水印清除成功"
}
```

### 3. 自动去除水印

**接口**: `POST /api/watermark/auto-remove`

**请求体**:
```json
{
  "filename": "uuid.jpg",
  "algorithm": "telea",
  "radius": 3
}
```

**响应**: 同上

### 4. 下载图片

**接口**: `GET /api/watermark/download/<filename>`

**响应**: 文件流

### 5. 预览图片

**接口**: `GET /api/watermark/preview/<filename>`

**响应**: 图片文件

### 6. 清理临时文件

**接口**: `POST /api/watermark/cleanup`

**请求体** (可选):
```json
{
  "filename": "uuid.jpg"
}
```

如果不指定filename，将清理所有超过24小时的文件。

## 使用流程

1. **上传图片**
   - 拖拽图片到上传区域，或点击选择文件
   - 支持JPG、PNG、BMP格式
   - 文件大小不超过10MB

2. **选择水印区域**
   - **手动模式**：在图片上拖拽框选水印区域，可添加多个区域
   - **自动模式**：点击"开始处理"，系统自动检测并去除水印

3. **调整参数**（可选）
   - 修复算法：Telea（默认）或 Navier-Stokes
   - 修复半径：1-10，值越大修复范围越广

4. **查看结果**
   - 左右对比查看原图和处理后的图片
   - 查看处理耗时

5. **下载或重试**
   - 满意则点击下载
   - 不满意则重新处理，调整参数

## 测试

运行自动化测试脚本：

```bash
python test_watermark_removal.py
```

测试内容包括：
- 图片上传
- 手动去除水印
- 自动去除水印
- 图片下载
- 临时文件清理

## 项目结构

```
wordToWord/
├── routes/document_convert/
│   └── watermark_routes.py      # 后端路由模块
├── frontend/src/
│   ├── api/
│   │   └── watermark.js          # API工具函数
│   ├── components/watermark/
│   │   ├── ImageUploader.vue     # 上传组件
│   │   ├── WatermarkSelector.vue # 水印选择器
│   │   └── ResultViewer.vue      # 结果查看器
│   └── views/tools/
│       └── WatermarkRemover.vue  # 主页面
├── uploads/watermark/             # 上传文件目录
│   └── results/                   # 处理结果目录
└── test_watermark_removal.py      # 测试脚本
```

## 注意事项

1. **性能优化**
   - 大图片会自动缩放到最大800px宽度进行处理
   - 保持原图分辨率不变

2. **安全性**
   - 文件名使用UUID防止冲突
   - 路径安全检查防止遍历攻击
   - 文件类型严格验证

3. **临时文件**
   - 上传和处理结果保存在 `uploads/watermark/` 目录
   - 系统每小时检查并清理超过24小时的文件

4. **算法选择**
   - **Telea**: 快速，适合小区域修复
   - **Navier-Stokes**: 更精确，适合复杂背景

## 扩展建议

未来可以考虑的功能增强：

- [ ] 批量处理多张图片
- [ ] AI智能识别水印（深度学习模型）
- [ ] 视频水印去除
- [ ] 历史记录保存
- [ ] 用户自定义水印模板
- [ ] 更多图像格式支持（WebP、TIFF等）

## 故障排查

### 问题1: OpenCV导入失败
```bash
pip install opencv-python
```

### 问题2: 图片上传失败
- 检查文件大小是否超过10MB
- 确认文件格式是否为JPG/PNG/BMP
- 查看后端日志获取详细错误信息

### 问题3: Canvas无法绘制
- 检查浏览器是否支持Canvas API
- 确认图片URL可访问（CORS配置）
- 清除浏览器缓存后重试

### 问题4: 处理效果不佳
- 尝试调整修复半径（增大或减小）
- 切换修复算法（Telea vs Navier-Stokes）
- 手动模式下更精确地框选水印区域

## 许可证

本项目基于现有框架开发，遵循项目整体许可证。

## 联系方式

如有问题或建议，请联系开发团队。
