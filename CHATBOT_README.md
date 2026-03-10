# 智能客服系统部署指南

## 📋 目录

- [系统概述](#系统概述)
- [环境要求](#环境要求)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [常见问题](#常见问题)

---

## 系统概述

基于本地部署的 Ollama AI 的智能客服系统，具备以下功能：

- ✅ **多格式文档学习**：支持 TXT、MD、DOC、DOCX、PDF、图片等格式
- ✅ **智能问答**：基于知识库和 AI 模型生成准确答案
- ✅ **上下文对话管理**：支持多轮对话，保持对话连贯性
- ✅ **FAQ 自动抽取**：从文档中自动提取问答对
- ✅ **知识库管理**：文档和 FAQ 的存储、检索、浏览
- ✅ **现代化 UI**：响应式设计，支持拖拽上传

---

## 环境要求

### 基础环境
- Python 3.8+
- Node.js 14+ (可选，用于前端开发)

### Ollama 要求
- Ollama 已安装并运行在本地（默认端口 11434）
- 推荐模型：`qwen2.5:7b` 或其他中文能力较强的模型

### Python 依赖
```bash
pip install -r requirements-chatbot.txt
```

### OCR 额外要求（如需图片识别）
```bash
# macOS
brew install tesseract
brew install leptonica

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev

# Windows
# 下载安装：https://github.com/tesseract-ocr/tesseract/releases
```

---

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd /path/to/wordToWord
pip install -r requirements-chatbot.txt
```

### 2. 安装 Ollama

**macOS:**
```bash
brew install ollama
```

**Ubuntu/Debian:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
下载安装包：https://ollama.ai/download

### 3. 启动 Ollama 服务

```bash
ollama serve
```

### 4. 拉取 AI 模型

```bash
# 推荐模型
ollama pull qwen2.5:7b

# 或者其他模型
ollama pull llama2
ollama pull mistral
```

### 5. 配置环境变量（可选）

创建 `.env` 文件或设置系统环境变量：

```bash
# Ollama API 地址
OLLAMA_BASE_URL=http://localhost:11434

# 默认模型
OLLAMA_MODEL=qwen2.5:7b
```

### 6. 启动 Flask 应用

```bash
python app.py
```

访问：http://localhost:5001/chatbot

---

## 配置说明

### Ollama 客户端配置

在 `utils/ollama_client.py` 中修改默认配置：

```python
ollama_client = OllamaClient(
    base_url="http://localhost:11434",
    model="qwen2.5:7b"
)
```

### 数据库配置

系统使用 SQLite 数据库，文件位于项目根目录：

- `knowledge_base.db`: 知识库数据库
- `users.db`: 用户认证数据库

### 上传文件配置

在 `config.py` 中修改上传目录：

```python
UPLOAD_FOLDER = 'uploads'
```

---

## 使用指南

### 访问智能客服界面

1. 启动应用后，访问：`http://localhost:5001/chatbot`
2. 系统会自动创建会话 ID，无需登录即可使用

### 聊天功能

1. **提问**：在输入框中输入问题，按 Enter 或点击"发送"
2. **查看历史**：聊天记录实时显示
3. **清空对话**：点击"清空"按钮清除当前会话

### 文档上传与学习

1. **上传文档**：
   - 点击左侧"文档库"标签
   - 点击上传区域或拖拽文件到上传区
   - 支持格式：TXT, MD, DOC, DOCX, PDF, JPG, PNG

2. **自动 FAQ 抽取**：
   - 上传后系统自动从文档中提取 FAQ
   - 提取结果保存在知识库中

3. **查看文档列表**：
   - 上传的文档会显示在"文档库"列表中
   - 显示文件名、类型、上传时间等信息

### FAQ 管理

1. **浏览 FAQ**：
   - 点击"FAQ"标签查看所有已学习的问答对

2. **搜索 FAQ**：
   - 在搜索框输入关键词
   - 系统实时过滤匹配的 FAQ

3. **使用 FAQ**：
   - 点击任意 FAQ 条目
   - 问题自动填充到输入框
   - 可以进一步追问

### 系统状态监控

点击"状态"标签查看：

- ✅ Ollama 服务状态
- ✅ 可用模型列表
- ✅ API 端点信息

---

## API 接口说明

### 聊天接口

```http
POST /chatbot/chat
Content-Type: application/json

{
    "message": "用户问题",
    "session_id": "会话 ID（可选）"
}
```

响应：
```json
{
    "success": true,
    "answer": "AI 回复",
    "source": "knowledge_base|ai_generated",
    "retrieved_faqs": [...],
    "session_id": "xxx",
    "timestamp": "2024-01-01T12:00:00"
}
```

### 上传文档接口

```http
POST /chatbot/upload_document
Content-Type: multipart/form-data

file: [文件对象]
```

### 获取文档列表

```http
GET /chatbot/documents
```

### 获取 FAQ 列表

```http
GET /chatbot/faqs
```

### 搜索 FAQ

```http
GET /chatbot/search?keyword=关键词&limit=10
```

### 检查 Ollama 状态

```http
GET /chatbot/ollama/status
```

---

## 常见问题

### Q1: Ollama 服务无法连接

**解决方案：**
1. 检查 Ollama 是否启动：`ollama serve`
2. 检查端口是否正确（默认 11434）
3. 检查防火墙设置

### Q2: 文档上传失败

**可能原因：**
1. 文件格式不支持
2. 文件损坏
3. 缺少相关依赖库

**解决方案：**
```bash
# 重新安装依赖
pip install -r requirements-chatbot.txt

# 检查 OCR 工具（如需要）
tesseract --version
```

### Q3: AI 回答质量不佳

**优化建议：**
1. 使用更大的模型（如 qwen2.5:14b）
2. 提供更多高质量的训练文档
3. 调整提示词模板

### Q4: 中文识别效果不好

**解决方案：**
1. 确保安装了中文语言包（OCR）
2. 使用中文能力更强的模型
3. 在提示词中明确要求使用中文回答

### Q5: 如何更换模型？

**方法一：环境变量**
```bash
export OLLAMA_MODEL=llama2
```

**方法二：代码修改**
在 `utils/ollama_client.py` 中修改默认模型参数。

---

## 性能优化建议

### 1. 缓存机制
- 对常见问题答案进行缓存
- 减少重复的 AI 调用

### 2. 向量检索（未来升级）
- 使用句子 transformers 进行语义相似度计算
- 提高检索准确率

### 3. 异步处理
- 文档上传和 FAQ 抽取改为后台任务
- 提高用户体验

---

## 安全建议

1. **访问控制**：建议添加用户认证
2. **速率限制**：防止 API 滥用
3. **数据备份**：定期备份知识库数据库
4. **日志审计**：记录重要操作日志

---

## 开发计划

- [ ] 支持更多文档格式（Excel, PPT）
- [ ] 向量数据库集成（FAISS, ChromaDB）
- [ ] 多租户支持
- [ ] 对话分析报表
- [ ] 移动端适配优化
- [ ] 语音交互支持

---

## 技术支持

如有问题，请查看：

1. [Ollama 官方文档](https://ollama.ai/)
2. [Flask 官方文档](https://flask.palletsprojects.com/)
3. 项目 README.md

---

## 更新日志

### v1.0.0 (2024-01-01)
- ✨ 初始版本发布
- ✅ 基础聊天功能
- ✅ 文档上传与 FAQ 抽取
- ✅ 知识库管理
- ✅ 上下文对话管理
