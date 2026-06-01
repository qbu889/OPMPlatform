# 👑 诺基亚 OPM 综合业务系统 - 核心开发规范手册 (V3.0)

**目的**: 本文档是所有新功能开发的唯一、强制性参考指南。所有代码的编写、测试和部署流程，必须严格遵循本文档的要求。
**版本**: v3.2
**上次更新**: 2026-05-29
**适用范围**: 系统所有模块（前端/后端）的开发人员。

---

## 🚀 一、 项目概述与架构规范

### 1.1 项目目标
诺基亚 OPM 综合业务系统是一个企业级综合业务平台，提供以下核心功能：
*   **文档转换**: Word/Excel/Markdown 互转、COSMIC 转换、ES 数据导出。
*   **Kafka 消息生成**: 自定义字段、历史缓存、推送消息生成。
*   **FPA 功能点估算**: SQL 转换、事件分类、规则管理。
*   **智能客服**: AI 对话、知识库管理、文档问答（OMLX/Ollama）。
*   **排班管理**: 定时推送、钉钉集成。
*   **在线表格**: 协同编辑、数据导出。
*   **图片水印清除**: AI 智能去水印。

### 1.2 技术栈与环境配置
| 类别 | 技术 | 版本 (推荐) | 用途 |
| :--- | :--- | :--- | :--- |
| **后端框架** | Flask | 2.2.5+ | Web 服务层，API 构建。 |
| **前端框架** | Vue 3 | 3.5.x+ | 客户端SPA，使用 Composition API (`<script setup>`)。 |
| **构建工具/打包** | Vite | 8.0.+ | 前端项目构建和开发服务器。 |
| **数据库** | MySQL | 8.0+ | 主要持久化存储，必须使用参数化查询。 |
| **ORM/数据处理** | SQLAlchemy, pandas, openpyxl | 最新稳定版 | 数据模型定义与复杂业务计算。 |
| **AI 服务调用** | OMLX/Ollama SDK | N/A | 调用大型语言模型进行推理和内容生成。 |

### 1.3 项目结构规范 (Project Structure)

```
wordToWord/
├── app.py                      # Flask 主应用入口点
├── config.py                   # 全局配置管理，包含数据库连接参数。
├── requirements.txt            # Python 核心依赖（开发环境）。
├── .env                        # 环境变量配置文件 (MUST BE IGNORED by Git)
│
├── frontend/                   # 前端项目根目录 (Vue 3 SPA)
│   ├── src/
│   │   ├── api/               # API 请求服务层定义。
│   │   ├── components/        # 可复用 UI 组件 (PascalCase)。
│   │   ├── views/             # 页面视图组件 (PascalCase)。
│   │   ├── router/            # Vue Router 配置。
│   │   └── store/             # Pinia 状态管理模块。
│   ├── vite.config.js         # Vite 构建配置。
│   └── package.json           # 前端依赖和构建脚本。
│
├── routes/                     # 后端路由蓝图注册目录。
│   ├── auth/                  # 认证模块 (如: auth_routes.py)
│   ├── chat/                  # 智能客服模块 (如: chatbot_routes.py)
│   ├── document_convert/      # 文档转换核心逻辑。
│   ├── kafka/                 # Kafka消息生成与管理 (如: kafka_generator_routes.py)。
│   ├── fpa/                   # FPA 功能点估算模块。
│   ├── schedule/              # 排班任务与定时推送。
│   └── utils/                 # 业务通用的工具类，如 ollama_client.py。
│
├── models/                     # 数据库模型定义 (SQLAlchemy Base)。
│   ├── auth_models.py         # 用户和权限相关模型。
│   ├── fpa_category_rules.py  # FPA规则配置模型。
│   └── ...
│
├── test/                       # 所有自动化测试用例目录。
├── logs/                       # 系统运行时日志输出目录。
├── uploads/                    # 文件上传缓存/处理结果目录。
└── docs/                       # 项目文档和规范。
```

---

## 🔒 二、 硬约束与安全规则 (The Guardrails)

**以下规定属于最高级别限制，任何情况下都不得违反。**

### 2.1 流程控制限制 (Anti-Loop & Anti-Resource Exhaustion)
1.  **修复尝试限制**: 遇到问题时，如果同一解决方案连续尝试超过 **3 次**仍未解决，必须停止操作并详细报告给用户/管理员，禁止盲目重试。
2.  **资源消耗限制**: API调用和外部服务访问最多重试 **2 次**。超过次数应立即捕获异常并返回明确的失败代码（HTTP 4xx/5xx）。
3.  **时间限制**: 单次复杂任务的执行时间不应超过 **30 秒**；必须设计可中断、分段处理的逻辑，并在超时前向用户报告进度。
4.  **文件操作限制**: 单个开发迭代中，新增或修改的文件数量最好不超过 **10 个**，超出需进行人工 Review 和确认。

### 2.2 代码安全与质量规则 (Security & Quality)
*   **敏感信息处理**: 密码、密钥 (`SECRET_KEY`)、API Key 等敏感数据**绝对禁止硬编码**在代码中；必须通过环境变量（`.env`）或安全的配置管理系统读取。
*   **数据库操作**: 所有涉及用户输入的数据库查询，必须使用 **参数化查询** 来防止 SQL 注入攻击。
*   **异常处理**: 禁止使用裸 `except:`。必须捕获具体的异常类型 (`except ValueError as e:`) 并记录堆栈信息（Traceback）。
*   **测试覆盖率**: 所有新增的核心业务逻辑功能，必须编写对应的单元测试用例，确保代码覆盖率的提升。不得删除或禁用已存在的、通过的测试用例。

---

## 📝 三、 代码规范 (Coding Style Guide)

### 3.1 Python 后端规范
| 元素 | 命名约定 | 示例 | 规则描述 |
| :--- | :--- | :--- | :--- |
| **模块/文件** | `snake_case` | `kafka_generator_routes.py` | 全小写，用下划线分隔。 |
| **类名** | `PascalCase` | `DingTalkSchedulePusher` | 每个单词首字母大写。 |
| **函数/方法** | `snake_case` | `generate_kafka_message()` | 小驼峰风格的实现，使用下划线。 |
| **变量名** | `snake_case` | `user_name`, `max_file_size` | 全小写，用下划线分隔。 |
| **常量** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PAGE_SIZE` | 全大写，用下划线分隔。 |
| **私有成员** | `_leading_underscore` | `self._internal_cache` | 用于标记内部使用、外部不应直接调用的方法或变量。 |

**文档字符串 (Docstring) 规范**: 所有公共函数和类必须包含完整的 Docstring，包括：
*   **功能描述 (Description)**: 该函数做什么。
*   **参数列表 (Args)**: `param_name`: 类型, 描述。
*   **返回值 (Returns)**: 返回值的类型和描述。
*   **异常/错误 (Raises)**: 可能抛出的自定义异常及条件。

### 3.2 Vue 前端规范
1.  **组件命名**: 组件文件名应使用 `PascalCase` (`KafkaGenerator.vue`)。
2.  **结构**: 必须遵循 `<script setup>` (Composition API) 的模式，确保代码的可读性和响应性。
3.  **状态管理**: 所有全局或复杂的状态逻辑必须通过 Pinia 进行管理，避免在组件内部使用大量 `ref` 和本地计算属性。
4.  **API 调用**: 封装统一的 API 服务层 (`api/`)，并在业务组件中调用服务方法，而不是直接发起网络请求。

---

## 🛠️ 四、 开发流程与工具链 (Workflow & DevOps)

### 4.1 本地开发环境启动 (Dev Setup)
1.  **激活环境**: `source .venv/bin/activate`
2.  **后端启动 (Flask)**: `./start_dev.sh` (默认端口: 5001)
3.  **前端启动 (Vite)**: `cd frontend && npm run dev` (默认端口: 5200)

### 4.2 Git 工作流与 Commit Message
*   **分支流程**: 严格遵循 **Git Flow** (`master/develop -> feature/* -> bugfix/*`)。
*   **Commit Message 模板**: 必须使用以下结构：
    ```
    <type>(<scope>): <subject>

    <body>
        - 详细描述本次提交的改动点和原因 (Why)。
        - 如果涉及多个模块，列出每个模块的变动。

    <footer>
    Closes #IssueNumber / Refs ticket-ABCDE
    ```
*   **Type**: `feat` (新功能), `fix` (Bug修复), `refactor` (重构), `chore` (构建/工具)。

### 4.3 代码质量自动化检查（强制执行）
在任何代码修改完成后，必须按以下顺序和流程自动运行：

1.  **格式化检查**: 确保代码风格符合规范。
    ```bash
    black . --check && isort . --check
    # 如果失败，则手动修复: black . && isort .
    ```
2.  **静态分析 (Linter)**: 使用 `flake8` 进行质量和规则检查。
    ```bash
    flake8 routes/ utils/ models/ --max-line-length=120 
    # 注意：必须配置 flake8 和 black 的排除目录（如 .venv, node_modules）
    ```
3.  **单元测试 (Unit Tests)**: 运行所有非慢速、核心功能测试。
    ```bash
    pytest test/ -v --maxfail=5 --disable-warnings
    ```
4.  **覆盖率报告**: 生成并检查代码覆盖率，确保新增代码块已被测试捕获。
    ```bash
    pytest test/ --cov=. --cov-report=term-missing 
    # 关注终端输出的缺失行，必须补齐测试用例。
    ```

### 4.4 CI/CD 自动化流程 (GitHub Actions)
CI/CD 管道是强制性的验收标准。任何代码合并到 `develop` 或更高分支前，都必须通过以下 Job：
1.  **Lint**: Flake8, Black, Isort 检查（无误可提交）。
2.  **Frontend Build**: 前端构建和 Lint (确保静态资源可用)。
3.  **Test**: 运行 `pytest` 并生成 **Coverage XML/HTML**。

### 4.6 新功能上线检查清单 (New Feature Launch Checklist)

**目的**: 每次开发新页面/功能时，必须同步完成以下三处入口配置，缺一不可。这是防止"功能已开发但用户找不到"的强制规范。

#### 4.6.1 入口配置三件套

| # | 检查项 | 文件路径 | 说明 |
|---|--------|----------|------|
| 1 | **首页入口** | `frontend/src/views/Home.vue` | 在对应分类区域添加功能卡片（`el-card`），包含图标、标题、描述，绑定 `@click="goTo('/路由路径')"` |
| 2 | **Header 导航** | `frontend/src/components/Header.vue` | 在对应的子菜单（`el-sub-menu`）中添加 `router-link`，包含图标和文字标签 |
| 3 | **Nginx 代理** | `nginx_5173.conf`（或对应配置文件） | 添加 API 路径的 `location` 块，代理到 Flask 后端（`proxy_pass http://127.0.0.1:5004`） |

#### 4.6.2 操作示例（以 `/content-to-excel` 为例）

**Step 1 — Home.vue**: 在"高效工具"区域（`el-row`）内追加卡片：
```vue
<el-col :xs="24" :sm="12" :lg="8">
  <el-card class="feature-card" shadow="hover" @click="goTo('/content-to-excel')">
    <div class="feature-icon" style="background: #e8f5e9">
      <el-icon size="40" color="#67c23a"><Document /></el-icon>
    </div>
    <h3>内容转 Excel</h3>
    <p>上传升级申请文档，自动生成标准化 Excel 装载记录表</p>
  </el-card>
</el-col>
```

**Step 2 — Header.vue**: 在对应 `el-sub-menu` 的 `router-link` 列表末尾追加：
```vue
<router-link to="/content-to-excel" custom v-slot="{ navigate, href }">
  <a :href="href" class="menu-link" @click="navigate">
    <el-menu-item index="/content-to-excel">
      <el-icon><Document /></el-icon>
      <span>内容转 Excel</span>
    </el-menu-item>
  </a>
</router-link>
```

**Step 3 — Nginx**: 在 `location /api/` 块之后追加：
```nginx
# Content To Excel API
location /api/content-to-excel/ {
    proxy_pass http://127.0.0.1:5004;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

#### 4.6.3 完成标准

新功能开发完成后，必须确认以下全部通过：
- [ ] `router/index.js` 中已注册路由（含 `meta.title`）
- [ ] `Home.vue` 对应分类区域有功能卡片，点击可跳转
- [ ] `Header.vue` 对应菜单下有导航入口
- [ ] Nginx 配置文件中有对应的 `location` 代理块
- [ ] 前后端联调测试通过

> ⚠️ **Agent 注意**: 每次生成新页面时，请主动检查以上三项是否已配置。如果缺失，请在本次提交中一并补全，不要等待后续单独处理。

---

## 📈 五、 参考命令速查表

**目的**: 所有生产环境和测试环境的对外服务，必须通过 Nginx 进行反向代理和负载均衡。

#### 4.5.1 基础配置要求
| 配置项 | 推荐值/说明 | 作用 |
| :--- | :--- | :--- |
| **工作模式** | `worker_processes auto;` | 根据 CPU 核心数自动调整 worker 进程。 |
| **连接数** | `worker_connections 1024;` (可调整) | 单个 worker 的最大连接数。 |
| **HTTP 压缩** | `gzip on;` (启用) | 减少传输数据量，提升响应速度。 |
| **SSL/TLS** | `ssl_protocols TLSv1.2 TLSv1.3;` | 仅启用安全的 TLS 协议版本。 |
| **超时设置** | `proxy_connect_timeout 60s;`<br>`proxy_read_timeout 300s;` | 防止长时间请求阻塞连接。 |

#### 4.5.2 标准反向代理配置模板
```nginx
# /etc/nginx/conf.d/wordtoword.conf

upstream flask_backend {
    server 127.0.0.1:5001;  # Flask 后端服务地址
    keepalive 32;           # 保持长连接池
}

upstream vue_frontend {
    server 127.0.0.1:5200;  # Vite 开发服务器 (生产环境指向 dist/)
}

server {
    listen 80;
    server_name your-domain.com;  # 替换为实际域名

    # 重定向 HTTP 到 HTTPS (生产环境)
    # return 301 https://$server_name$request_uri;

    # 静态文件服务 (Vue 构建产物)
    location /static/ {
        alias /path/to/frontend/dist/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 请求转发到 Flask 后端
    location /api/ {
        proxy_pass http://flask_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持 (如需)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # 缓冲区优化
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Vue SPA 路由支持 (fallback)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 健康检查端点 (可选)
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }

    # 日志格式 (结构化)
    access_log /var/log/nginx/wordtoword_access.log combined;
    error_log /var/log/nginx/wordtoword_error.log warn;

    # 安全头 (生产环境)
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}

# HTTPS 配置 (生产环境启用)
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 其他配置与 HTTP server 块相同
}
```

#### 4.5.3 Nginx 操作命令速查
| 目的 | 命令 (Linux) | 说明 |
| :--- | :--- | :--- |
| **测试配置语法** | `nginx -t` | 检查配置文件是否有错误。 |
| **重载配置** | `nginx -s reload` | 平滑重新加载配置文件，不中断服务。 |
| **查看状态** | `nginx -s status` 或 `systemctl status nginx` | 检查 Nginx 运行状态。 |
| **停止服务** | `nginx -s stop` 或 `systemctl stop nginx` | 立即停止 Nginx。 |
| **查看连接数** | `ss -tn \| grep 80 \| wc -l` | 查看当前 HTTP 连接数。 |
| **日志分析** | `tail -f /var/log/nginx/access.log` | 实时查看访问日志。 |

#### 4.5.4 生产环境部署检查清单
- [ ] Nginx 版本 >= 1.18 (推荐最新稳定版)
- [ ] SSL 证书有效且配置正确 (HTTPS)
- [ ] 防火墙规则已开放 80/443 端口
- [ ] `proxy_pass` 后端服务地址正确且可达
- [ ] 静态文件路径配置正确 (`alias` 或 `root`)
- [ ] 日志轮转 (logrotate) 已配置，避免磁盘占满
- [ ] 性能调优：`worker_connections`, `keepalive_timeout` 已根据业务调整
- [ ] 安全加固：禁用不安全的协议和加密套件

---

## 📈 五、 参考命令速查表

| 目的          | 命令 (Linux/Mac) | Notes |
|:------------| :--- | :--- |
| **启动前后端开发** | `./start_all_prod.sh` | 确保已激活 `.venv`。 |
| **安装所有依赖**  | `pip install -r requirements.txt` | 仅在 CI/CD 或首次搭建环境时执行。 |
| **运行全量测试**  | `pytest test/ -v --cov=. --cov-report=html` | 生成 HTML 报告到 `htmlcov/`。 |
| **查看覆盖率**   | `pytest test/ -v --cov=. --cov-report=term-missing` | 在终端显示未覆盖的行数和文件。 |
| **生成部署版本**  | `cd frontend && npm run build` | 构建生产环境静态资源。 |

---
***（End of Guide）***