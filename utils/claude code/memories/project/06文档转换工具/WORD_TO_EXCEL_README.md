# Word 转 Excel - 软件资产清单自动生成

## 功能概述

自动解析 Word 技术规范书，提取功能点并生成标准化的 Excel 软件资产清单。

## 访问地址

- **上传页面**: http://127.0.0.1:5001/word-to-excel/
- **使用说明**: http://127.0.0.1:5001/word-to-excel/help

## 核心功能

### 1. 智能层级识别

根据 Word 文档中的编号自动识别层级关系：

| 层级 | 编号示例 | 提取内容 |
|------|----------|----------|
| 一级分类 | `3.1.1.2` | 监控管理应用 |
| 二级分类 | `3.1.1.2.1` | 分级调度管理 |
| 功能模块 | `3.1.1.2.1.1` | 分级调度派发 |
| 功能点名称 | `3.1.1.2.1.1.1` | 派发智能体自动修复 |

### 2. 功能点描述提取

- 自动提取功能点下方的详细描述文本
- 过滤图片、特殊符号等非文本内容
- 保留完整的处理流程和步骤说明

### 3. Excel 自动生成

生成的 Excel 文件包含以下列：
- 一级分类
- 二级分类
- 功能模块
- 序号
- 功能点名称
- 功能点描述

## 使用方法

### 方法一：通过 Web 界面

1. 访问 http://127.0.0.1:5001/word-to-excel/
2. 点击"选择文件"按钮，选择要上传的 Word 文档 (.docx)
3. 点击"上传并转换"按钮
4. 等待转换完成
5. 点击"下载 Excel 文件"按钮下载结果

### 方法二：使用 Python 脚本

```python
from utils.word_to_excel import quick_convert

# 简单转换
excel_path = quick_convert('技术规范书.docx')
print(f'Excel 文件已生成：{excel_path}')

# 指定输出目录
excel_path = quick_convert('技术规范书.docx', output_dir='./output')
```

### 方法三：使用完整 API

```python
from utils.word_to_excel import parse_word_to_excel

# 执行转换
success = parse_word_to_excel(
    input_path='技术规范书.docx',
    output_path='软件资产清单.xlsx'
)

if success:
    print('转换成功！')
```

## 支持的文档格式

- **文件格式**: .docx (Microsoft Word 2007+)
- **文件大小**: 最大 50MB
- **内容格式**: 包含层级编号的技术规范书

## 提取规则详解

### 层级编号识别

系统使用正则表达式匹配层级编号：

```python
pattern = r'^(\d+(?:\.\d+)*)[\s、](.+)$'
```

匹配的编号格式：
- `3.1.1.2` → 4 级编号 → 一级分类
- `3.1.1.2.1` → 5 级编号 → 二级分类
- `3.1.1.2.1.1` → 6 级编号 → 功能模块
- `3.1.1.2.1.1.1` → 7 级编号 → 功能点名称

### 功能点描述提取

1. **直接描述**: 功能点标题后的段落内容
2. **多段描述**: 支持多个自然段的描述文本
3. **列表格式**: 保留编号列表（如 1. 2. 3.）
4. **过滤内容**: 
   - ✅ 保留：纯文本、编号列表、换行符
   - ❌ 过滤：图片、表格、特殊符号（、等）

## 技术架构

### 后端

- **框架**: Flask
- **Word 解析**: python-docx
- **Excel 生成**: pandas + openpyxl
- **日志系统**: logging 模块

### 前端

- **模板**: Jinja2 (继承 base.html)
- **样式**: Bootstrap 5
- **交互**: 原生 JavaScript + Fetch API

### 核心文件

```
wordToWord/
├── utils/
│   └── word_to_excel.py          # Word 解析核心模块
├── routes/
│   └── word_to_excel/
│       └── word_to_excel_routes.py  # Flask 路由
├── templates/
│   └── word_to_excel.html        # 前端页面
└── test_word_to_excel.py         # 测试脚本
```

## API 接口

### 1. 上传并转换

**请求**:
```http
POST /word-to-excel/upload
Content-Type: multipart/form-data

file: <Word 文件对象>
```

**响应**:
```json
{
  "success": true,
  "message": "转换成功，共提取 3 条功能点",
  "download_url": "/word-to-excel/download/abc123",
  "filename": "技术规范书_软件资产清单.xlsx",
  "stats": {
    "total_functions": 3,
    "file_size": "6 KB"
  }
}
```

### 2. 下载文件

**请求**:
```http
GET /word-to-excel/download/{download_id}
```

**响应**: Excel 文件（附件下载）

### 3. 帮助页面

**请求**:
```http
GET /word-to-excel/help
```

**响应**: HTML 帮助文档

## 测试

### 运行自动化测试

```bash
cd /Users/linziwang/PycharmProjects/wordToWord
python test_word_to_excel.py
```

测试脚本将：
1. 创建示例 Word 文档
2. 执行转换
3. 显示 Excel 内容预览

### 手动测试

1. 访问 http://127.0.0.1:5001/word-to-excel/
2. 上传测试文档（位于 `test_uploads/技术规范书_测试文档.docx`）
3. 验证转换结果

## 注意事项

### 文档格式要求

1. **层级编号必须规范**:
   - ✅ 正确：`3.1.1.2.1 功能名称`
   - ❌ 错误：`第 3.1.1.2.1 节 功能名称`

2. **功能点描述格式**:
   - 功能点标题后紧跟描述段落
   - 避免在标题和描述之间插入其他内容

3. **编号连续性**:
   - 确保编号层级递进（如 3.1 → 3.1.1 → 3.1.1.1）
   - 避免跳跃式编号

### 性能建议

- **小文件** (< 1MB): 即时转换 (< 5 秒)
- **中等文件** (1-10MB): 快速转换 (5-15 秒)
- **大文件** (> 10MB): 可能需要 15-30 秒

### 安全限制

- 最大文件大小：50MB
- 仅支持 .docx 格式
- 临时文件保存期限：7 天

## 常见问题

### Q1: 为什么我的文档没有提取到任何内容？

**A**: 可能的原因：
1. 文档中没有符合编号规则的层级结构
2. 编号格式不正确（如使用了中文括号）
3. 文档是纯文本格式，没有使用 Word 的样式功能

**解决方案**: 
- 检查文档是否包含类似 `3.1.1.2.1` 的编号
- 确保编号后有空格或顿号分隔标题

### Q2: 提取的功能点描述不完整怎么办？

**A**: 功能点描述会自动收集后续段落，直到遇到下一个编号标题。如果描述被截断：
1. 确保描述内容紧跟在功能点标题后
2. 避免在描述中间插入其他编号

### Q3: Excel 中的换行符显示异常怎么办？

**A**: Excel 会自动处理换行符。如果需要调整格式：
1. 在 Excel 中选中单元格
2. 设置"自动换行"
3. 调整行高以显示完整内容

## 开发计划

### 已实现功能 ✅

- [x] Word 文档解析
- [x] 层级结构识别
- [x] 功能点提取
- [x] Excel 生成
- [x] Web 上传界面
- [x] 文件下载功能

### 计划中功能 🚧

- [ ] 支持更多编号格式（如 一、二、三）
- [ ] 支持表格内容提取
- [ ] 批量文档处理
- [ ] 导出多种格式（CSV、JSON）
- [ ] 历史记录查看
- [ ] 在线预览和编辑

## 更新日志

### v1.0.0 (2026-03-24)

- ✨ 初始版本发布
- 🎯 支持基本的层级识别
- 📊 支持 Excel 生成和下载
- 🌐 提供友好的 Web 界面

## 技术支持

如有问题或建议，请查看：
- 项目文档：`/docs/` 目录
- 测试用例：`test_word_to_excel.py`
- 核心源码：`utils/word_to_excel.py`
