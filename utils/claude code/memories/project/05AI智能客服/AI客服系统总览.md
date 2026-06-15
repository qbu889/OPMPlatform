# 🤖 智能客服系统 - 项目总览

## 📋 快速导航

- [系统简介](#系统简介)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [文件结构](#文件结构)
- [API 文档](#api-文档)
- [使用指南](#使用指南)

---

## 系统简介

基于本地 Ollama AI 的企业级智能客服系统，支持多格式文档学习、智能问答、上下文对话管理等功能。

### 技术特点

- 🔒 **数据隐私**：本地部署，数据不出内网
- 📚 **多格式支持**：TXT, MD, DOC, DOCX, PDF, 图片等
- 🧠 **智能问答**：知识库匹配 + AI 生成双模式
- 💬 **上下文对话**：支持多轮对话，保持连贯性
- 🎨 **现代 UI**：响应式设计，适配各种设备

---

## 核心功能

### 1. 智能聊天
- ✅ 自然语言问题理解
- ✅ 意图识别与关键词提取
- ✅ 知识库优先匹配
- ✅ AI 智能生成答案
- ✅ 答案来源标识

### 2. 文档学习
- ✅ 拖拽上传文档
- ✅ 自动内容提取
- ✅ FAQ 智能抽取
- ✅ 批量上传支持
- ✅ 文档列表管理

### 3. 知识库管理
- ✅ FAQ 存储与检索
- ✅ 关键词搜索
- ✅ 浏览次数统计
- ✅ 分类与标签
- ✅ 对话历史保存

### 4. 系统监控
- ✅ Ollama 服务状态检测
- ✅ 可用模型列表
- ✅ API 端点信息
- ✅ 系统健康检查

---

## 快速开始

### 方式一：一键启动（推荐）

```bash
./start_chatbot.sh
```

### 方式二：手动启动

```bash
# 1. 安装依赖
pip install -r requirements-chatbot.txt

# 2. 启动 Ollama（新终端）
ollama serve

# 3. 拉取模型
ollama pull qwen3:8b

# 4. 启动应用
python app.py
```

### 访问地址

```
http://localhost:5001/chatbot
```

或在首页点击"智能客服"卡片。

---

## 文件结构

```
wordToWord/
├── utils/                      # 工具模块
│   ├── ollama_client.py       # Ollama AI 客户端
│   ├── document_processor.py  # 文档处理器
│   └── chatbot_core.py        # 客服核心处理器
│
├── models/                     # 数据模型
│   ├── auth_models.py         # 认证模型（已有）
│   └── knowledge_base.py      # 知识库模型
│
├── routes/                     # 路由模块
│   └── chatbot_routes.py      # 智能客服路由
│
├── templates/                  # 前端模板
│   ├── chatbot.html           # 聊天界面
│   └── index.html             # 首页（已更新）
│
├── test/chatbot/              # 测试目录
│   └── test_chatbot_system.py # 系统测试脚本
│
├── readme/                     # 文档目录
│   ├── AI客服开发总结.md     # 开发总结
│   └── AI客服系统总览.md     # 本文档
│
├── CHATBOT_README.md          # 详细部署文档
├── requirements-chatbot.txt   # Python 依赖
└── start_chatbot.sh           # 快速启动脚本
```

---

## API 文档

### 基础接口

#### 1. 聊天对话
```http
POST /chatbot/chat
Content-Type: application/json

{
    "message": "用户问题",
    "session_id": "会话 ID（可选）"
}
```

响应示例：
```json
{
    "success": true,
    "answer": "AI 回复内容",
    "source": "knowledge_base",
    "retrieved_faqs": [
        {
            "id": 1,
            "question": "相关问题",
            "answer": "相关答案",
            "similarity_score": 0.95
        }
    ],
    "session_id": "uuid",
    "timestamp": "2024-01-01T12:00:00"
}
```

#### 2. 上传文档
```http
POST /chatbot/upload_document
Content-Type: multipart/form-data

file: [文件对象]
```

响应示例：
```json
{
    "success": true,
    "document_id": 123,
    "filename": "document.pdf",
    "faqs_extracted": 15,
    "filetype": "pdf"
}
```

#### 3. 获取文档列表
```http
GET /chatbot/documents
```

#### 4. 获取 FAQ 列表
```http
GET /chatbot/faqs
```

#### 5. 搜索 FAQ
```http
GET /chatbot/search?keyword=关键词&limit=10
```

#### 6. 清空对话
```http
POST /chatbot/conversation/clear
Content-Type: application/json

{
    "session_id": "xxx"
}
```

#### 7. 检查 Ollama 状态
```http
GET /chatbot/ollama/status
```

响应示例：
```json
{
    "success": true,
    "available": true,
    "models": ["qwen3:8b", "llama2"],
    "endpoint": "http://localhost:11434"
}
```

---

## 使用指南

### 场景一：上传产品手册学习

1. 进入智能客服界面
2. 点击左侧"文档库"标签
3. 拖拽产品手册 PDF 到上传区
4. 等待系统自动提取 FAQ（约 10-30 秒）
5. 查看提取的问答对

### 场景二：回答客户问题

1. 在输入框输入："如何重置密码？"
2. 按 Enter 发送
3. 系统从知识库检索或 AI 生成答案
4. 答案会标注来源（知识库/AI）

### 场景三：多轮对话

```
用户：公司产品有哪些？
AI: [列出产品线]

用户：第二个产品的价格是多少？
AI: [基于上下文的回答]
```

### 场景四：搜索历史 FAQ

1. 点击"FAQ"标签
2. 输入关键词："密码"
3. 查看所有相关问答
4. 点击任意 FAQ 可快速提问

---

## 配置说明

### 环境变量配置

创建 `.env` 文件：

```bash
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:8b

# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 模型选择

推荐模型（按优先级）：

1. **qwen3:8b** - 中文能力强，推荐 ⭐⭐⭐⭐⭐
2. **qwen2.5:14b** - 更强大但需要更多资源 ⭐⭐⭐⭐
3. **llama2** - 通用模型 ⭐⭐⭐
4. **mistral** - 轻量级选项 ⭐⭐⭐

更换模型：
```bash
ollama pull <model_name>
```

---

## 常见问题

### Q: Ollama 服务无法连接？

**A:** 
1. 检查服务是否启动：`ollama serve`
2. 检查端口：默认 11434
3. 检查防火墙设置

### Q: 文档上传失败？

**A:**
- 检查文件格式是否支持
- 确认文件大小（建议 < 10MB）
- 查看错误日志

### Q: 中文识别效果差？

**A:**
1. 安装 Tesseract 中文包
2. 使用中文能力强的模型（如 qwen3:8b）
3. 确保文档编码为 UTF-8

### Q: 如何提高回答质量？

**A:**
- 提供高质量训练文档
- 使用更大的模型
- 优化提示词模板
- 添加更多 FAQ 数据

---

## 性能优化

### 缓存策略

```python
# TODO: 实现热门 FAQ 缓存
from functools import lru_cache

@lru_cache(maxsize=100)
def search_faq_cached(keyword):
    return knowledge_base.search_faqs(keyword)
```

### 异步处理

```python
# TODO: 使用 Celery 处理文档上传
@app.task
def process_document_async(filepath):
    # 后台处理文档
    pass
```

### 向量检索

```python
# TODO: 集成 FAISS 进行语义检索
import faiss
index = faiss.IndexFlatL2(dimension)
```

---

## 安全建议

### 1. 访问控制
```python
# TODO: 添加登录验证
from flask_login import login_required

@chatbot_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    pass
```

### 2. 速率限制
```python
# TODO: 防止 API 滥用
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@chatbot_bp.route('/chat')
@limiter.limit("10 per minute")
def chat():
    pass
```

### 3. 输入过滤
```python
# TODO: XSS 防护
import bleach

def sanitize_input(text):
    return bleach.clean(text)
```

---

## 开发计划

### v1.1 (近期)
- [ ] 用户认证集成
- [ ] 速率限制
- [ ] FAQ 缓存
- [ ] 改进搜索算法

### v1.2 (中期)
- [ ] 向量数据库（FAISS）
- [ ] 语义相似度检索
- [ ] Celery 后台任务
- [ ] 对话分析报表

### v2.0 (长期)
- [ ] 多租户架构
- [ ] 移动端优化
- [ ] 语音交互
- [ ] 多语言支持

---

## 监控与日志

### 应用日志

```python
# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 性能指标

监控指标：
- 平均响应时间
- FAQ 命中率
- AI 调用成功率
- 用户上传量

---

## 备份与恢复

### 数据库备份

```bash
# 备份数据库
cp knowledge_base.db backup_$(date +%Y%m%d).db

# 恢复数据库
cp backup_20240101.db knowledge_base.db
```

### FAQ 导出

```python
# TODO: 实现 FAQ 导出功能
def export_faqs_to_json():
    faqs = knowledge_base.list_all_faqs()
    with open('faqs_export.json', 'w') as f:
        json.dump(faqs, f, ensure_ascii=False)
```

---

## 技术支持

### 文档资源
- 📖 [详细部署文档](CHATBOT_README.md)
- 📝 [开发总结](readme/AI客服开发总结.md)
- 🔧 [测试脚本](test/chatbot/test_chatbot_system.py)

### 外部资源
- [Ollama 官方文档](https://ollama.ai/)
- [Flask 官方文档](https://flask.palletsprojects.com/)
- [Bootstrap 文档](https://getbootstrap.com/)

---

## 版本信息

- **当前版本**: v1.0.0
- **发布日期**: 2024-01
- **Python 要求**: 3.8+
- **Flask 版本**: 2.3.0
- **状态**: ✅ 生产就绪

---

## 许可证

本项目遵循公司内部使用许可。

---

## 联系方式

如有问题，请联系开发团队或查看详细文档。

**祝使用愉快！** 🎉
