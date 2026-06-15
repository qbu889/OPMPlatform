# 诺基亚 OPM 综合业务系统 - 核心开发规范 (V3.0)

> 来源: GUIDELINES_MASTER.md + 项目框架规范与持续集成指南.md
> 学习日期: 2026-06-12

---

## 一、项目概述与架构

### 核心功能
- **文档转换**: Word/Excel/Markdown 互转、COSMIC 转换、ES 数据导出
- **Kafka 消息生成**: 自定义字段、历史缓存、推送消息生成
- **FPA 功能点估算**: SQL 转换、事件分类、规则管理
- **智能客服**: AI 对话、知识库管理、文档问答（OMLX/Ollama）
- **排班管理**: 定时推送、钉钉集成
- **在线表格**: 协同编辑、数据导出
- **图片水印清除**: AI 智能去水印（IOPaint LaMa 模型）
- **CityColor 颜色提取**: 智能配色方案

### 技术栈
| 类别 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 后端框架 | Flask | 2.2.5+ | Web API |
| 前端框架 | Vue 3 | 3.5.x+ | SPA (Composition API) |
| 构建工具 | Vite | 8.0.+ | 前端构建 |
| UI 框架 | Element Plus | 2.13.6+ | 组件库 |
| 数据库 | MySQL | 8.0+ | 持久化存储 |
| ORM | SQLAlchemy | 最新 | 数据模型 |
| AI 服务 | OMLX/Ollama SDK | - | LLM 推理 |
| Python | 3.13 | - | 开发/生产环境 |
| Node.js | 18+ | - | 前端构建 |

### 项目结构
```
wordToWord/
├── app.py                    # Flask 主入口
├── config.py                 # 全局配置（含 DB 连接）
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量（Git 忽略）
├── frontend/                 # Vue 3 SPA
│   ├── src/api/              # API 服务层
│   ├── src/components/       # 可复用组件 (PascalCase)
│   ├── src/views/            # 页面视图 (PascalCase)
│   ├── src/router/           # Vue Router
│   └── src/store/            # Pinia 状态管理
├── routes/                   # 后端路由蓝图
│   ├── auth/                 # 认证模块
│   ├── chat/                 # 智能客服
│   ├── document_convert/     # 文档转换
│   ├── kafka/                # Kafka 消息生成
│   ├── fpa/                  # FPA 功能点估算
│   ├── schedule/             # 排班管理
│   └── utils/                # 通用工具类
├── models/                   # SQLAlchemy 数据模型
├── test/                     # 自动化测试用例
├── logs/ /uploads/ /downloads/ /sql/ /docs/
```

### 端口映射
| 服务 | 开发环境 | 生产环境 |
|------|----------|----------|
| 前端 Vite | 5200 | 5173 |
| 后端 Flask | 5001 | 5004 |
| MySQL | 3306 | 3306 |
| OMLX | 8000 | 8000 |

---

## 二、硬约束（最高优先级，不可违反）

1. **修复尝试 ≤ 3次** — 同一问题连续失败 3 次必须停止并报告
2. **API/外部服务重试 ≤ 2次** — 超出立即捕获异常，返回 HTTP 4xx/5xx
3. **单次任务 ≤ 30秒** — 必须支持中断、分段处理，超时前报告进度
4. **单迭代文件修改 ≤ 10个** — 超出需人工 Review 确认
5. **敏感信息禁止硬编码** — 密码/密钥/API Key 必须通过 `.env` 或配置系统读取
6. **数据库查询必须参数化** — 防止 SQL 注入
7. **禁止裸 `except:`** — 必须捕获具体异常类型并记录 Traceback
8. **测试覆盖率** — 新增核心业务逻辑必须编写单元测试，不得删除已有通过的测试

---

## 三、代码规范

### Python 后端
| 元素 | 命名约定 | 示例 |
|------|----------|------|
| 模块/文件 | `snake_case` | `kafka_generator_routes.py` |
| 类名 | `PascalCase` | `DingTalkSchedulePusher` |
| 函数/方法 | `snake_case` | `generate_kafka_message()` |
| 变量名 | `snake_case` | `user_name`, `max_file_size` |
| 常量 | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PAGE_SIZE` |
| 私有成员 | `_leading_underscore` | `self._internal_cache` |

**Docstring 要求**: 所有公共函数/类必须包含功能描述、参数列表（类型+描述）、返回值、可能抛出的异常。

### Vue 前端
1. 组件文件名 `PascalCase`（如 `KafkaGenerator.vue`）
2. 必须使用 `<script setup>` (Composition API)
3. 全局/复杂状态通过 Pinia 管理，避免组件内大量 ref
4. API 调用封装在 `api/` 服务层，业务组件只调用服务方法

---

## 四、开发流程规范

### Git 工作流
- **分支**: `master/develop → feature/* → bugfix/*`
- **Commit Message 格式**: `<type>(<scope>): <subject>` + body（为什么改）+ footer（Closes #Issue / Refs ticket）
- **Type**: `feat` (新功能), `fix` (Bug修复), `refactor` (重构), `chore` (构建/工具)

### 本地开发启动
```bash
source .venv/bin/activate       # 激活环境
./start_dev.sh                  # 后端 (端口 5001)
cd frontend && npm run dev      # 前端 (端口 5200)
```

### 代码质量检查（强制执行）
```bash
black . --check && isort . --check    # 格式化检查
flake8 routes/ utils/ models/ --max-line-length=120   # 静态分析
pytest test/ -v --maxfail=5 --disable-warnings        # 单元测试
pytest test/ --cov=. --cov-report=term-missing        # 覆盖率报告
```

### CI/CD 流程（GitHub Actions）
Lint → Frontend Build → Test (pytest + coverage) → Security Scan (bandit) → Deploy

---

## 五、新功能上线「三件套」强制要求

每次开发新页面/功能，**必须同步完成以下三项**：

| # | 检查项 | 文件路径 | 说明 |
|---|--------|----------|------|
| 1 | **首页入口** | `frontend/src/views/Home.vue` | 对应分类区域添加功能卡片 (`el-card`)，绑定 `@click="goTo('/路由')"` |
| 2 | **Header 导航** | `frontend/src/components/Header.vue` | 对应子菜单 (`el-sub-menu`) 添加 `router-link` |
| 3 | **Nginx 代理** | `nginx_5173.conf` (或对应配置) | 添加 API 路径的 `location` 块，proxy_pass 到 Flask 后端 |

### 完成标准检查清单
- [ ] `router/index.js` 中已注册路由（含 `meta.title`）
- [ ] `Home.vue` 对应分类区域有功能卡片，点击可跳转
- [ ] `Header.vue` 对应菜单下有导航入口（含 `pathMap` 映射）
- [ ] Nginx 配置文件中有对应的 `location` 代理块
- [ ] 前后端联调测试通过

### 前端构建验证（每次修改前端后必须执行）
```bash
cd frontend && npm run build          # 1. 构建，必须成功（exit code 0）
ls dist/assets/ | grep -i <模块名>    # 2. 验证产物存在
curl -s -o /dev/null -w "%{http_code}" http://<host>:5004/<路由>  # 3. 必须返回 200
curl -s http://<host>:5004/<路由> | grep '<modulepreload.*<模块名>'  # 4. chunk 引用正确
```

---

## 六、前端开发常见陷阱与规避

### Element Plus 图标
- ❌ `ColorSwitch` / `Save` / `Refresh` — 不存在，分别用 `Picture` / `Check` / `RefreshLeft` 替代
- ✅ 可用图标: Document, Files, Edit, DataBoard, Operation, Download, ArrowLeft, UserFilled, HomeFilled, Key, Platform, OfficeBuilding, ChatDotRound, Calendar, Bell, Cpu, Picture

### Vue 模板语法
- `<script setup>` 中函数名不能含空格，派生值必须用 `computed`
- 模板字符串避免嵌套双引号

### 响应式状态
- `reactive` 对象解构会丢失响应性，需直接通过对象访问
- 表单对象（多字段）用 `reactive`，单个值/列表用 `ref`，派生值用 `computed`

### API 调用
- JSON 请求体必须设 `Content-Type: application/json` + `JSON.stringify(body)`
- 文件下载用 `res.blob()` → `URL.createObjectURL(blob)` → `<a>` 标签触发
- GET 分页参数通过 URL query string: `/api/xxx?page=1&page_size=20`

### 构建与部署
- **每次修改前端后必须 `npm run build`**，否则线上 404
- 使用不存在的图标名会导致构建失败

---

## 七、独立页面 Header 设计规范（通用）

```vue
<el-header class="header">
  <div class="header-content">
    <div class="logo" @click="$router.push('/')">
      <img src="/nokia-06.png" alt="NOKIA" class="logo-icon" />
      <span class="logo-text">OPM 系统</span>
    </div>
    <el-button size="small" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>
  </div>
</el-header>
```

- ✅ 必须使用 `size="small"`，`@click="$router.back()"`，`<ArrowLeft />` 图标
- ❌ 禁止使用 `text` 属性和 `type="primary"`

---

## 八、Nginx 反向代理要点

- `worker_processes auto;`，`worker_connections 1024;`
- 启用 `gzip on;`，仅 TLSv1.2/1.3
- API 代理超时: `proxy_connect_timeout 60s`, `proxy_read_timeout 300s`
- SPA fallback: `try_files $uri $uri/ /index.html;`

---

## 九、pytest 配置速查

```ini
[pytest]
testpaths = test
python_files = test_*.py
markers = slow, integration, unit, api
addopts = -v --tb=short --maxfail=5 --disable-warnings -m "not slow"
```

常用命令:
```bash
pytest test/ -v                              # 运行所有测试
pytest test/kafka/ -v                        # 特定模块
pytest test/ --cov=. --cov-report=html       # 生成覆盖率报告
pytest test/ -v -m "not slow"                # 跳过慢速测试
```

---

## 十、环境变量 (.env) 模板

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
```

> ⚠️ `.env` 文件必须加入 `.gitignore`，禁止提交到 Git。