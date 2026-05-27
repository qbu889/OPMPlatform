# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 一、项目架构

### 1.1 项目概述

诺基亚 OPM 综合业务系统是一个企业级综合业务平台，提供以下核心功能：
- **文档转换**: Word/Excel/Markdown 互转、COSMIC 转换、ES 数据导出
- **Kafka 消息生成**: 自定义字段、历史缓存、推送消息生成
- **FPA 功能点估算**: SQL 转换、事件分类、规则管理
- **智能客服**: AI 对话、知识库管理、文档问答
- **排班管理**: 定时推送、钉钉集成
- **在线表格**: 协同编辑、数据导出
- **图片水印清除**: AI 智能去水印（IOPaint LaMa 模型）

### 1.2 技术栈

| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 后端框架 | Flask | 2.2.5 | Web 框架 |
| 前端框架 | Vue 3 | 3.5.32 | 前端框架 |
| 构建工具 | Vite | 8.0.4 | 前端构建 |
| 数据库 | MySQL | 8.0 | 数据存储 |
| ORM | SQLAlchemy | - | 数据库 ORM |
| AI | OMLX/Ollama | - | AI 模型调用 |
| 图像处理 | OpenCV | 4.8.1.78 | 水印处理 |
| 文档处理 | python-docx | 1.1.2 | Word 文档处理 |
| Excel | pandas + openpyxl | 1.5.3 + 3.1.5 | Excel 数据处理 |

### 1.3 项目结构

```
wordToWord/
├── app.py                      # Flask 主应用入口
├── config.py                   # 全局配置文件
├── requirements.txt            # Python 依赖（开发环境）
├── .env                        # 环境变量配置
│
├── frontend/                   # 前端项目（Vue 3 SPA）
│   ├── src/
│   │   ├── api/               # API 接口定义
│   │   ├── components/        # 公共组件
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   └── store/             # Pinia 状态管理
│
├── routes/                     # 后端路由模块
│   ├── auth/                  # 认证模块
│   ├── chat/                  # 智能客服模块
│   ├── document_convert/      # 文档转换模块
│   ├── kafka/                 # Kafka 模块
│   ├── fpa/                   # FPA 功能点估算模块
│   └── schedule/              # 排班管理模块
│
├── models/                     # 数据库模型
│   ├── auth_models.py         # 用户认证模型
│   ├── fpa_category_rules.py  # FPA 规则模型
│   ├── knowledge_base.py      # 知识库模型
│   └── visit_log.py           # 访问日志模型
│
├── tests/                       # 测试用例
├── logs/                       # 日志目录
└── docs/                       # 文档目录
```

### 1.4 核心模块职责

| 模块 | 职责 | 关键文件 |
|------|------|----------|
| **auth** | 用户认证与权限管理 | `routes/auth/auth_routes.py` |
| **chat** | AI 智能客服功能 | `routes/chat/chatbot_routes.py` |
| **document_convert** | 文档格式转换 | `routes/document_convert/` |
| **kafka** | Kafka 消息生成与管理 | `routes/kafka/kafka_generator_routes.py` |
| **fpa** | FPA 功能点估算 | `routes/fpa/` |
| **schedule** | 排班与定时推送 | `routes/schedule/` |

---

## 二、强约束规则

### 2.1 防止循环问题
- **禁止重复相同的修复尝试超过3次**：如果同一问题连续尝试3次修复仍未解决，应停止操作并向用户报告问题
- **禁止连续读取同一文件超过一次**：在单次任务中，同一文件只读一次，读取后应缓存内容
- **禁止无限递归调用**：所有递归函数必须设置明确的递归深度限制（最大10层）
- **禁止循环依赖**：禁止模块间循环导入，设计时需检查依赖关系

### 2.2 资源保护规则
- **禁止连续执行相同命令超过5次**：避免在无效路径上反复消耗资源
- **禁止无限制重试**：API 调用和外部服务访问最多重试2次，失败后立即返回错误
- **禁止长时间运行任务**：单任务执行时间不应超过30秒，复杂任务应分段执行
- **禁止创建过多文件**：单次任务最多创建/修改10个文件，超出时需用户确认

### 2.3 代码质量规则
- **禁止提交未测试代码**：所有新增功能必须有对应的测试用例
- **禁止删除现有测试**：不得删除或禁用已存在的测试用例
- **禁止修改测试以通过**：必须修复代码使测试通过，而非修改测试
- **禁止引入未使用的依赖**：新增依赖需有明确用途，且需在 requirements.txt 中声明

### 2.4 安全规则
- **禁止硬编码敏感信息**：密码、密钥、API Key 必须通过环境变量或配置文件管理
- **禁止 SQL 注入风险**：所有数据库查询必须使用参数化查询
- **禁止未授权访问**：API 接口必须进行身份验证和权限检查

---

## 三、自检流程

### 3.1 代码修改后的必做步骤

```
代码修改 → 运行 Linter → 运行测试 → 验证结果 → 提交/回滚
```

### 3.2 自动检测清单

**修改代码后，必须按顺序执行以下操作：**

#### 步骤 1: 代码格式检查
```bash
# 检查代码格式
black . --check
isort . --check

# 如果需要自动修复
black .
isort .
```

#### 步骤 2: 代码质量检查
```bash
# 使用 flake8 检查代码质量
flake8 routes/ models/ --max-line-length=120
```

#### 步骤 3: 运行相关测试
```bash
# 运行所有测试（排除慢速测试）
pytest test/ -v -m "not slow" --maxfail=5

# 或运行特定模块测试
pytest test/kafka/ -v
pytest test/fpa/ -v
```

#### 步骤 4: 验证测试覆盖率
```bash
# 生成覆盖率报告
pytest test/ --cov=. --cov-report=term-missing
```

#### 步骤 5: 前端构建检查（如涉及前端修改）
```bash
cd frontend && npm run build
```

### 3.3 自检失败处理

| 失败类型 | 处理策略 |
|----------|----------|
| **Linter 报错** | 自动修复或手动修改代码以满足规范 |
| **测试失败** | 分析失败原因，修复代码后重新运行测试 |
| **覆盖率下降** | 补充测试用例，确保新增代码被覆盖 |
| **构建失败** | 检查依赖和配置，修复后重新构建 |

### 3.4 反馈机制

- **成功**: 所有检查通过后，向用户汇报修改内容和测试结果
- **失败**: 立即停止操作，向用户报告具体错误信息和失败原因
- **不确定**: 当无法判断问题时，向用户提供详细分析并请求指导

---

## 四、常用命令

| 目的 | 命令 | 备注 |
|------|------|------|
| 启动后端 | `./.venv/bin/python -m flask run --port 5001` | 需要先创建并激活虚拟环境 |
| 启动前端 | `cd frontend && npm run dev` | 默认端口 5200 |
| 安装依赖 | `pip install -r requirements.txt` | 运行前请确保已激活 `.venv` |
| 运行全部测试 | `pytest test/ -v -m "not slow"` | 排除慢速测试，快速验证 |
| 运行单个测试 | `pytest test/test_*.py::TestCase::test_method -v` | 精确测试 |
| 代码格式检查 | `black . --check && isort . --check` | 保持风格一致 |
| 代码格式化 | `black . && isort .` | 自动修复格式问题 |
| 代码质量检查 | `flake8 routes/ models/ --max-line-length=120` | 检查代码质量 |
| 生成覆盖率报告 | `pytest test/ --cov=. --cov-report=html` | 生成 HTML 报告 |
| 前端构建 | `cd frontend && npm run build` | 构建生产版本 |

---

## 五、协作规范

### 5.1 Git 工作流

采用 Git Flow 工作流：
- `master/main`: 生产分支
- `develop`: 开发分支
- `feature/*`: 功能分支
- `bugfix/*`: Bug 修复分支
- `hotfix/*`: 紧急修复分支

### 5.2 Commit Message 规范

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**: `feat`(新功能)、`fix`(Bug修复)、`docs`(文档)、`style`(格式)、`refactor`(重构)、`test`(测试)、`chore`(构建)

### 5.3 代码审查要点

- [ ] 所有公共函数都有文档字符串
- [ ] 异常处理正确（没有裸 except）
- [ ] 日志记录适当
- [ ] 输入验证完整
- [ ] 数据库查询使用参数化
- [ ] 敏感信息不在代码中硬编码
- [ ] API 返回格式统一
- [ ] 测试用例覆盖新功能

---

## 六、环境配置参考

### 6.1 环境变量文件 `.env`

```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=12345678
OMLX_BASE_URL=http://localhost:8000/v1
LOG_LEVEL=INFO
PORT=5001
```

### 6.2 端口映射

| 服务 | 开发环境 | 生产环境 |
|------|----------|----------|
| 前端 Vite | 5200 | 5173 |
| 后端 Flask | 5001 | 5004 |
| MySQL | 3306 | 3306 |
| OMLX | 8000 | 8000 |

---

**文档版本**: v2.0  
**更新时间**: 2026-05-19  
**适用范围**: Claude Code 操作指南