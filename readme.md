# 诺基亚 OPM 综合业务系统

## 📋 项目概述

诺基亚 OPM（Operation & Maintenance Platform）是一个基于 Flask 的企业级综合业务平台，集成了 FPA 功能点估算、Kafka 消息生成、智能客服、文档转换、排班管理等多种实用功能模块。

## 🚀 快速开始

### 环境要求
- Python 3.13+
- Flask 3.0.0+
- MySQL 5.7+（可选，用于部分功能）
- Ollama（可选，用于 AI 功能）

### 安装步骤
1. 克隆项目到本地
2. 创建虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件配置数据库和 AI 服务
   ```
5. 启动应用：
   ```bash
   .venv/bin/python -m flask run --port 5001
   ```
6. 访问地址：http://127.0.0.1:5001

## 🔧 系统功能模块

### 1. FPA 功能点估算系统
专业的软件功能点估算工具，支持：
- 从需求文档自动提取功能点
- UFP（未调整功能点）计算
- AFP（调整功能点）计算
- 调整因子管理（14 个通用系统特性）
- AI 辅助功能点扩展
- 预估表自动生成

**技术架构：**
- 后端：Python 3.13 + Flask 3.0.0
- AI 模型：Ollama (qwen3:4b) / OMLX (Qwen3.5-4B-OptiQ-4bit)
- 数据库：MySQL + SQLite
- 前端：Bootstrap 5 + JavaScript

### 2. Kafka 消息生成器
企业级 Kafka 消息生成和处理工具：
- ES 数据转 Kafka 消息
- 灵活的字段映射配置
- 维表数据关联查询
- 实时数据预览和验证
- 批量消息生成
- JSON 格式修复工具

**核心特性：**
- ✅ 支持 28 个 Kafka 字段映射
- ✅ TOPIC_PARTITION 强制设置为固定值 7
- ✅ 地域字段智能映射（省部接口保障）
- ✅ 完整的维表查询系统
- ✅ JSON 格式自动修复

### 3. 智能客服系统
基于知识库的智能问答系统：
- FAQ 知识库管理
- 专业领域分类
- AI 智能问答
- 文档上传和解析
- 问题去重检测
- 聊天上下文记忆

**技术特色：**
- 支持 PDF/Word 文档解析
- 并行 FAQ 提取（大文档优化）
- 语义相似度匹配
- 本地 AI 模型集成

### 4. 文档转换模块
多种文档格式转换和处理功能：
- Excel 转 Word 文档
- Markdown 上传和处理
- Word 转 Markdown 格式
- Markdown 转 Word 文档
- 文档格式化和清理
- 格式匹配度检查

### 5. 排班管理系统
智能化排班解决方案：
- 自动排班算法
- 节假日系统集成
- 班次配置管理
- 人员配置管理
- 请假记录管理
- 排班结果导出

### 6. 数据处理工具
各类数据处理和转换功能：
- SQL ID 格式化
- JSON 数据清洗
- ES 数据转 Kafka
- 事件数据清洗
- 格式匹配和验证

## 🛠 技术架构

### 后端技术栈
```
Python 3.13
Flask 3.0.0
Flask-SQLAlchemy 3.1.1
Flask-Cors 5.0.0
MySQL Connector
BeautifulSoup4 4.14.3
python-docx
markdownify
Pydantic
```

### 前端技术栈
```
Bootstrap 5.1.3
jQuery 3.6.0
JavaScript ES6+
Font Awesome 6.0.0
现代化 CSS3
响应式设计
```

### AI 服务
```
Ollama (本地): qwen3:4b
OMLX (在线): Qwen3.5-4B-OptiQ-4bit
支持切换和降级
```

### 项目结构
```
wordToWord/
├── app.py                          # 主应用入口
├── config.py                       # 配置文件
├── .env                            # 环境变量配置
├── requirements.txt                # 项目依赖
│
├── models/                         # 数据模型层
│   ├── __init__.py
│   ├── auth_models.py              # 认证数据模型
│   ├── knowledge_base.py           # 知识库数据模型
│   └── visit_log.py                # 访问日志模型
│
├── routes/                         # 路由控制器
│   ├── __init__.py
│   ├── fpa/                        # FPA 相关功能
│   │   ├── __init__.py
│   │   ├── fpa_generator_routes.py # FPA 预估表生成器
│   │   ├── fpa_async_routes.py     # FPA 异步任务
│   │   ├── fpa_ai_expander.py      # FPA AI 扩展
│   │   ├── fpa_category_rules_routes.py  # FPA 类别规则
│   │   ├── adjustment_routes.py    # 调整因子管理
│   │   ├── adjustment_calc_routes.py # 调整因子计算器
│   │   ├── category_routes.py      # 专业领域管理
│   │   ├── event_routes.py         # 事件管理
│   │   └── sql_routes.py           # SQL 格式化
│   │
│   ├── auth/                       # 认证相关功能
│   │   ├── __init__.py
│   │   └── auth_routes.py          # 登录/注册/密码找回
│   │
│   ├── chat/                       # 聊天/客服功能
│   │   ├── __init__.py
│   │   ├── chatbot_routes.py       # 智能客服
│   │   └── chatai_routes.py        # AI 聊天
│   │
│   ├── document_convert/           # 文档转换功能
│   │   ├── __init__.py
│   │   ├── document_routes.py      # 文档处理
│   │   ├── excel2word_routes.py    # Excel 转 Word
│   │   ├── markdown_upload_routes.py # Markdown 上传
│   │   ├── word_to_md_routes.py    # Word 转 Markdown
│   │   └── mdtoword.py             # MD 转 Word
│   │
│   ├── kafka/                      # Kafka 相关功能
│   │   ├── __init__.py
│   │   ├── kafka_routes.py         # Kafka 消息生成
│   │   └── kafka_generator_routes.py # Kafka 生成器
│   │
│   ├── schedule/                   # 排班相关功能
│   │   ├── __init__.py
│   │   └── schedule_config_routes.py # 排班配置
│   │
│   └── 排班/                       # 排班子系统（保留原结构）
│
├── templates/                      # HTML 模板
│   ├── base.html                   # 基础模板
│   ├── index.html                  # 首页
│   ├── index_modern.html           # 现代化首页
│   ├── fpa/                        # FPA 相关页面
│   ├── auth/                       # 认证相关页面
│   ├── chat/                       # 聊天/客服页面
│   ├── document_convert/           # 文档转换页面
│   ├── kafka/                      # Kafka 相关页面
│   ├── schedule/                   # 排班相关页面
│   └── 排班/                       # 排班子系统页面
│
├── utils/                          # 工具函数
│   ├── __init__.py
│   ├── ollama_client.py            # Ollama AI 客户端
│   ├── mysql_helper.py             # MySQL 数据库助手
│   ├── chatbot_core.py             # 聊天机器人核心
│   ├── document_processor.py       # 文档处理器
│   └── ...                         # 其他工具
│
├── static/                         # 静态资源
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── utils.js
│   └── vendor/                     # 第三方库
│
├── uploads/                        # 上传文件目录
│   ├── fpa_input/                  # FPA 输入文件
│   ├── fpa_output/                 # FPA 输出文件
│   └── other/                      # 其他文件
│
├── test/                           # 测试文件
└── logs/                           # 日志文件
```

## 🔒 安全特性

### 认证安全
- PBKDF2密码哈希算法（100,000次迭代）
- 随机盐值防止彩虹表攻击
- 登录失败5次后锁定30分钟
- JWT风格会话令牌（24小时有效期）
- IP地址和User-Agent绑定

### 数据安全
- 敏感信息加密存储
- SQL注入防护
- XSS攻击防护
- CSRF保护机制

## 📊 主要 API 接口

### FPA 相关接口
```
POST   /fpa-generator/upload              # 上传需求文档生成 FPA
GET    /fpa-generator/adjustment-factor   # 获取调整因子
POST   /fpa-generator/calculate-afp       # 计算 AFP
GET    /api/category/list                 # 获取专业领域列表
POST   /api/category/add                  # 添加专业领域
```

### Kafka 相关接口
```
POST   /kafka-generator/generate          # 生成 Kafka 消息
GET    /kafka-generator/field-meta        # 获取字段元数据
GET    /kafka-generator/field-options     # 获取字段选项
POST   /kafka-generator/fix-json          # 修复 JSON 格式
```

### 智能客服接口
```
POST   /chatbot/chat                      # 聊天接口
POST   /chatbot/upload_document/preview   # 上传文档预览 FAQ
GET    /chatbot/faq_preview               # FAQ 预览
GET    /api/category/page                 # 专业领域管理页面
```

### 文档转换接口
```
POST   /excel2word                        # Excel 转 Word
POST   /markdown-upload                   # Markdown 上传
POST   /word-to-md                        # Word 转 Markdown
POST   /format-check                       # 文档格式检查
```

### 排班管理接口
```
GET    /schedule-config/api/staff-config  # 获取人员配置
POST   /schedule-config/api/staff-config  # 更新人员配置
GET    /schedule-config/api/leave-records # 获取请假记录
POST   /schedule-config/api/leave-records # 添加请假记录
```

## 🐛 常见问题解决

### 1. Flask 启动失败 - 端口被占用
```
错误信息：Address already in use, Port 5001 is in use
解决方案:
lsof -ti:5001 | xargs kill -9 2>/dev/null; sleep 1
.venv/bin/python -m flask run --port 5001
```

### 2. 数据库连接失败
```
错误信息：'cryptography' package is required
解决方案：pip install cryptography
```

### 3. AI 服务无法连接
```
错误信息：Ollama service unavailable
解决方案:
1. 检查 Ollama 服务是否启动：ollama list
2. 启动 Ollama 服务：ollama serve
3. 拉取模型：ollama pull qwen3:4b
```

### 4. 模板文件未找到
```
错误信息：TemplateNotFound: xxx.html
解决方案:
检查 templates 目录下是否有对应文件，路径是否正确
确保路由中 render_template 使用正确的相对路径
```

### 5. 虚拟环境激活失败
```
Windows: .venv\Scripts\activate
Mac/Linux: source .venv/bin/activate
```

### 6. 依赖安装失败
```
建议使用国内镜像源：
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
```

## 📈 系统性能指标

### 响应时间
- 页面加载：< 2秒
- API响应：< 500ms
- 文件处理：< 5秒（取决于文件大小）

### 并发处理
- 支持同时在线用户数：100+
- 最大并发请求数：50+

## 🔄 部署指南

### 开发环境部署
1. 安装 Python 3.13 环境
2. 克隆项目代码
3. 创建并激活虚拟环境
4. 安装依赖包
5. 配置 .env 环境变量
6. 启动 Ollama 服务（可选）
7. 启动开发服务器

### 生产环境部署建议
1. 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
2. 使用 Nginx 作为反向代理
3. 配置 SSL 证书启用 HTTPS
4. 设置适当的 SECRET_KEY
5. 配置 MySQL 数据库
6. 定期备份数据库
7. 监控系统日志和性能指标
8. 配置日志轮转

### 环境变量配置示例
```bash
# Flask 配置
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=opm_platform

# AI 服务配置
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
USE_OMLX_FOR_CHATBOT=false
```

## 📝 开发规范

### 代码规范
- 遵循PEP8编码规范
- 函数和类添加必要注释
- 变量命名使用小写字母加下划线
- 常量命名使用大写字母

### Git提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```
## 📝 常用命令

### 启动应用
```bash
# Mac/Linux
lsof -ti:5001 | xargs kill -9 2>/dev/null; sleep 1
.venv/bin/python -m flask run --port 5001

# Windows
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *5001*"
.venv\python -m flask run --port 5001
```

### 数据库操作
```bash
# 初始化数据库
python scripts/init_all_databases.sql

# 导入调整因子数据
python scripts/import_adjustment_factor_excel.py

# 导入维表数据
python scripts/import_dimension_table.py
```

### 清理和维护
```bash
# 清理缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# 检查依赖
pip check
pip install --upgrade pip
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork项目到自己的仓库
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证，详情请参见LICENSE文件。

## 📞 技术支持

如有问题，请通过以下方式联系我：
- 提交GitHub Issue
- 发送邮件至技术支持邮箱:524722511@qq.com
- 查看详细的FAQ文档

---
*最后更新时间：2026 年 3 月 18 日*
*当前版本：v2.1.0*
