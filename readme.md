# OPMPlatform 综合平台系统

## 📋 项目概述

OPMPlatform是一个基于Flask的综合业务平台，集成了多种实用功能模块，包括文档处理、数据转换、排班管理、认证系统等企业级应用功能。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Flask 3.0.1
- 相关依赖包（详见requirements-windows.txt）

### 安装步骤
1. 克隆项目到本地
2. 安装依赖包：
   ```bash
   pip install -r requirements-windows.txt --trusted-host mirrors.aliyun.com
   ```
3. 启动应用：
   ```bash
   python app.py
   ```
4. 访问地址：http://localhost:5000

## 🔧 系统功能模块

### 1. 认证系统
完整的用户认证和授权功能，支持：
- 用户注册和登录
- 安全问题设置和验证
- 密码修改和重置
- 基于角色的访问控制
- 会话管理

**技术架构：**
- 后端：Python 3.10.8 + Flask 2.2.5 + SQLite3
- 前端：Bootstrap 5 + JavaScript ES6+ + Font Awesome
- 安全：PBKDF2密码哈希算法

### 2. Kafka消息生成器
专业的Kafka消息生成和处理工具：
- 支持多种数据格式转换
- 灵活的字段映射配置
- 实时数据预览和验证
- 批量消息生成功能

**核心特性：**
- ✅ 字段映射准确率高（除动态字段外基本一致）
- ✅ TOPIC_PARTITION强制设置为固定值7
- ✅ 支持自定义字段覆盖
- ✅ 完整的数据验证机制

### 3. 文档处理模块
多种文档格式转换和处理功能：
- Excel转Word文档
- Markdown上传和处理
- Word转Markdown格式
- 文档格式化和清理

### 4. 排班管理系统
智能化排班解决方案：
- 自动排班算法
- 节假日系统集成
- 班次配置管理
- 排班结果导出

### 5. 数据处理工具
各类数据处理和转换功能：
- SQL格式化
- JSON数据清洗
- ES数据转Kafka
- 格式匹配和验证

## 🛠 技术架构

### 后端技术栈
```
Python 3.9.7
Flask 3.0.1
SQLite3 (内置数据库)
Bootstrap-Flask 2.5.0
Pydantic 1.10.12
BeautifulSoup4 4.14.3
Flask-Cors 5.0.0
```

### 前端技术栈
```
Bootstrap 5
JavaScript ES6+
jQuery
Font Awesome 图标库
现代化CSS3
响应式设计
```

### 项目结构
```
OPMPlatform/
├── app.py                 # 主应用入口
├── config.py              # 配置文件
├── models/                # 数据模型
│   └── auth_models.py     # 认证数据模型
├── routes/
   ├── __init__.py
   ├── fpa/                          # FPA 相关功能
   │   ├── __init__.py
   │   ├── fpa_generator_routes.py   # FPA 预估表生成器
   │   ├── fpa_async_routes.py       # FPA 异步任务
   │   ├── fpa_ai_expander.py        # FPA AI 扩展
   │   ├── fpa_category_rules_routes.py  # FPA 类别规则
   │   ├── adjustment_routes.py      # 调整因子管理
   │   ├── adjustment_calc_routes.py # 调整因子计算器
   │   ├── category_routes.py        # 专业领域管理
   │   ├── event_routes.py           # 事件管理
   │   └── sql_routes.py             # SQL 格式化
   ├── auth/                         # 认证相关功能
   │   ├── __init__.py
   │   └── auth_routes.py            # 登录/注册/密码找回
   ├── chat/                         # 聊天/客服功能
   │   ├── __init__.py
   │   ├── chatbot_routes.py         # 智能客服
   │   └── chatai_routes.py          # AI 聊天
   ├── document_convert/             # 文档转换功能
   │   ├── __init__.py
   │   ├── document_routes.py        # 文档处理
   │   ├── excel2word_routes.py      # Excel 转 Word
   │   ├── markdown_upload_routes.py # Markdown 上传
   │   ├── word_to_md_routes.py      # Word 转 Markdown
   │   └── mdtoword.py               # MD 转 Word
   ├── kafka/                        # Kafka 相关功能
   │   ├── __init__.py
   │   ├── kafka_routes.py           # Kafka 消息生成
   │   └── kafka_generator_routes.py # Kafka 生成器
   ├── schedule/                     # 排班相关功能
   │   ├── __init__.py
   │   └── schedule_config_routes.py # 排班配置
   └── 排班/                         # 排班子系统（保留原结构）

   templates/
   ├── fpa/                          # FPA 相关页面
   │   ├── fpa_generator.html
   │   ├── fpa_category_rules.html
   │   ├── adjustment_calculator.html
   │   └── adjustment_factor.html
   ├── auth/                         # 认证相关页面
   │   ├── login.html
   │   ├── register.html
   │   └── forgot_password.html
   ├── chat/                         # 聊天/客服页面
   │   ├── chatbot.html
   │   ├── chat.html
   │   └── faq_preview.html
   ├── document_convert/             # 文档转换页面
   │   ├── document_formatter.html
   │   ├── excel2word.html
   │   ├── excel2word_content.html
   │   ├── markdown_upload.html
   │   ├── word_to_md.html
   │   └── convert_upload.html
   ├── kafka/                        # Kafka 相关页面
   │   ├── generate_kafka.html
   │   ├── kafka_bp_new.html
   │   └── es_to_kafka.html
   ├── schedule/                     # 排班相关页面
   │   └── schedule_config.html
   └── 排班/                         # 排班子系统页面

├── static/                # 静态资源
│   ├── css/styles.css     # 样式文件
│   └── js/utils.js        # 工具函数
├── utils/                 # 工具类
│   ├── kafka/             # Kafka相关工具
│   ├── document_formatter.py  # 文档格式化
│   └── ...                # 其他工具
├── test/                  # 测试文件
└── uploads/               # 上传文件目录
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

## 📊 API接口文档

### 认证相关接口
```
POST /api/register          # 用户注册
POST /api/login             # 用户登录
POST /api/logout            # 用户登出
POST /api/change-password   # 修改密码
POST /api/forgot-password   # 忘记密码
```

### Kafka生成器接口
```
POST /api/generate-kafka    # 生成Kafka消息
POST /api/validate-kafka    # 验证Kafka消息
GET  /api/kafka-template    # 获取模板
```

### 文档处理接口
```
POST /api/excel-to-word     # Excel转Word
POST /api/markdown-upload   # Markdown上传
POST /api/word-to-markdown  # Word转Markdown
```

## 🐛 常见问题解决

### 1. 数据库连接失败
```
错误信息: 'cryptography' package is required for sha256_password or caching_sha2_password auth methods
解决方案: pip install cryptography
```

### 2. pip安装包时SSL证书问题
```
错误信息: WARNING: The repository located at mirrors.aliyun.com is not a trusted or secure host
解决方案: 
pip config set global.index-url http://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com
```

### 3. Flask版本兼容性问题
```
当前版本: Flask 3.0.1
如需降级: pip install Flask==2.3.3
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
1. 安装Python环境
2. 克隆项目代码
3. 安装依赖包
4. 配置环境变量
5. 启动开发服务器

### 生产环境部署建议
1. 使用Nginx作为反向代理
2. 配置SSL证书启用HTTPS
3. 设置适当的SECRET_KEY
4. 定期备份数据库
5. 监控系统日志和性能指标

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
### 运行命令
```
cd /Users/linziwang/PycharmProjects/wordToWord && lsof -ti:5001 | xargs kill -9 2>/dev/null; sleep 1
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
*最后更新时间：2026年3月*
