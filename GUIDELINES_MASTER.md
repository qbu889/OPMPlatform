# 👑 诺基亚 OPM 综合业务系统 - 核心开发规范手册 (V3.0)

**目的**: 本文档是所有新功能开发的唯一、强制性参考指南。所有代码的编写、测试和部署流程，必须严格遵循本文档的要求。
**版本**: v3.3
**上次更新**: 2026-06-11
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
*   **CityColor 颜色提取**: 输入内容智能提取专属配色方案，支持保存、导出 PNG。

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

#### 4.6.5 独立页面 Header 设计规范（通用）

**目的**: 统一独立页面的顶部导航栏设计，包含 Logo 和返回按钮，确保视觉风格一致。

**标准设计**：
```vue
<!-- 顶部导航栏标准写法 -->
<el-header class="header">
  <div class="header-content">
    <div class="logo" @click="$router.push('/')">
      <img src="/nokia-06.png" alt="NOKIA" class="logo-icon" />
      <span class="logo-text">OPM 系统</span>
    </div>
    <el-button size="small" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      <span>返回</span>
    </el-button>
  </div>
</el-header>
```

**样式约束**：
- ✅ **必须使用**: `el-header` 组件包裹整个头部
- ✅ **必须包含**: Logo 区域（点击返回首页）
- ✅ **必须包含**: 返回按钮（点击返回上一页）
- ✅ **按钮必须使用**: `size="small"` - 保持按钮尺寸统一
- ✅ **按钮必须使用**: `@click="$router.back()"` - 使用 Vue Router 的返回方法
- ✅ **按钮必须使用**: `<ArrowLeft />` 图标 - 从 `@element-plus/icons-vue` 导入
- ❌ **禁止使用**: `text` 属性 - 避免无边框样式
- ❌ **禁止使用**: `type="primary"` - 避免主色调样式

**样式支持**：
```scss
/* 顶部导航栏 */
.header {
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  height: 56px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover { opacity: 0.8 }
.logo-icon { height: 24px; margin-right: 12px }
.logo-text { color: #1d1d1f; font-weight: 600; font-size: 15px; letter-spacing: 0.5px }

.header .el-button {
  color: #0071e3;
  font-size: 14px;
}

.header .el-button:hover {
  background: rgba(0, 113, 227, 0.1);
}
```

**适用场景**：
- 独立功能页面（如：CityColor、HouseDesign、WheelLottery）
- 需要独立导航的子页面

**注意事项**：
- 确保已导入 `ArrowLeft` 图标：`import { ArrowLeft } from '@element-plus/icons-vue'`
- Logo 图片路径：`/nokia-06.png`（放置在 `public` 目录）
- 主内容区的 `min-height` 需要考虑 header 的高度（56px）

#### 4.6.6 CityColor 专项开发规范（颜色提取模块）

CityColor 是 OPM 系统的**颜色智能提取工具**，开发此类型页面时需特别注意以下模式：

**4.6.6.1 页面结构模板（固定布局）**
```vue
<template>
  <div class="city-color-container">
    <!-- 顶部导航栏（独立 Header，非全局） -->
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

    <!-- 主内容区：左右分栏 Grid 布局 -->
    <div class="main-content">
      <h1 class="page-title">CityColor 颜色提取器</h1>
      <p class="page-subtitle">输入内容，智能提取专属配色方案</p>

      <div class="content-wrapper" v-loading="isLoading">
        <!-- 左侧面板：输入 + 色板展示 -->
        <div class="left-panel">
          <!-- 输入区域：模式选择 + 内容输入 + 颜色数量 -->
          <el-card class="input-section" shadow="hover">
            <!-- 模式选择：auto/city/brand/random -->
            <el-radio-group v-model="inputForm.mode">
              <el-radio-button value="auto">智能识别</el-radio-button>
              <el-radio-button value="city">城市色彩</el-radio-button>
              <el-radio-button value="brand">品牌色系</el-radio-button>
              <el-radio-button value="random">随机配色</el-radio-button>
            </el-radio-group>
            <!-- 内容输入：textarea -->
            <el-input v-model="inputForm.content" type="textarea" :rows="4" />
            <!-- 颜色数量：slider (3-12) -->
            <el-slider v-model="inputForm.count" :min="3" :max="12" />
            <!-- 提取按钮 -->
            <el-button type="primary" @click="extractColors">提取颜色</el-button>
          </el-card>

          <!-- 色板展示区（有结果时显示） -->
          <el-card class="palette-section" v-if="resultColors.length > 0">
            <!-- 渐变预览 -->
            <div class="gradient-preview" :style="{ background: resultGradient }" />
            <!-- 色板列表：点击显示详情弹窗 -->
            <div class="color-swatches">
              <div v-for="(color, index) in resultColors" class="swatch-item">
                <div class="swatch-color" :style="{ backgroundColor: color.hex }" />
                <span>{{ color.name }}</span>
                <span>{{ color.hex }}</span>
              </div>
            </div>
            <!-- 操作按钮：保存 / 导出PNG / 重新提取 -->
          </el-card>

          <!-- 空状态（无结果时显示） -->
          <el-empty v-else description="输入内容后点击'提取颜色'" />
        </div>

        <!-- 右侧面板：已保存方案列表 -->
        <div class="right-panel">
          <el-card>
            <!-- 方案列表 + 分页 -->
            <div class="scheme-list">
              <div v-for="scheme in schemes" class="scheme-item">
                <!-- 迷你色板 -->
                <div class="mini-palette" v-for="hex in getSchemeHexes(scheme)" />
                <span>{{ scheme.title }}</span>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 弹窗：颜色详情 + 保存方案 -->
    <el-dialog v-model="detailVisible" title="颜色详情" />
    <el-dialog v-model="saveVisible" title="保存颜色方案">
      <el-input v-model="saveForm.title" placeholder="输入方案名称" />
    </el-dialog>
  </div>
</template>
```

**4.6.6.2 API 接口约定（前端调用）**

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| POST | `/api/city-color/extract` | `{ content, mode, count }` | 提取颜色，返回 `colors[]`, `gradient`, `palette_type` |
| POST | `/api/city-color/schemes` | `{ title, colors[], gradient, palette_type, source_text, extract_mode }` | 保存方案 |
| GET | `/api/city-color/schemes?page=N&page_size=M` | 分页参数 | 获取已保存方案列表 |
| GET | `/api/city-color/schemes/{id}` | 方案ID | 获取单个方案详情（加载到当前页面） |
| DELETE | `/api/city-color/schemes/{id}` | 方案ID | 删除方案 |
| POST | `/api/city-color/export/png` | `{ colors[], title }` | 导出为 PNG 图片（返回 blob） |

**4.6.6.3 状态变量命名约定**
```js
// 输入表单（reactive）
const inputForm = reactive({ content: '', mode: 'auto', count: 5 })

// 提取结果（ref）
const resultColors = ref([])           // [{ name, hex, rgb, ratio }]
const resultGradient = ref('')         // 渐变 CSS 字符串
const resultPaletteType = ref('')      // 'auto' | 'city' | 'brand' | 'random'

// 选中状态（ref）
const selectedResultIndex = ref(null)  // 当前选中的色板索引

// 已保存方案（ref）
const schemes = ref([])               // 方案列表
const totalSchemes = ref(0)           // 总数（分页用）
const currentPage = ref(1)            // 当前页码
const pageSize = ref(20)              // 每页条数

// 弹窗状态（ref）
const detailVisible = ref(false)      // 颜色详情弹窗
const saveVisible = ref(false)        // 保存方案弹窗
const saveForm = reactive({ title: '' })

// 加载状态（ref）
const isLoading = ref(false)          // 通用 loading
const isExtracting = ref(false)       // 提取中 loading
```

**4.6.6.4 计算属性（computed）使用规范**
- 选中的颜色详情必须用 `computed`，不可用函数：
```js
// ✅ 正确
const selectedResultColor = computed(() => resultColors.value[selectedResultIndex.value] || null)

// ❌ 错误：函数声明不能有空格，且模板中无法直接调用
function get selectedResultColor() { ... }
```

**4.6.6.5 工具函数模板**
```js
// 色板 HEX 提取（兼容 JSON 字符串和数组两种格式）
function getSchemeHexes(scheme) {
  const colors = typeof scheme.colors === 'string' ? JSON.parse(scheme.colors) : scheme.colors
  return colors.map(c => typeof c === 'string' ? c : (c.hex || '#000000'))
}

// 调色板类型标签映射（用于 el-tag type）
function getPaletteTypeTag(type) {
  const map = { 'auto': '', 'city': 'success', 'brand': 'warning', 'random': 'info' }
  return map[type] || ''
}

// 调色板类型名称映射（用于显示）
function getPaletteTypeName(type) {
  const map = { 'auto': '智能识别', 'city': '城市色彩', 'brand': '品牌色系' }
  return map[type] || type
}

// 日期格式化
function formatDate(isoString) {
  return isoString ? new Date(isoString).toLocaleDateString('zh-CN') : ''
}

// 复制颜色（带 fallback）
function copyColor(hex) {
  navigator.clipboard.writeText(hex).then(() => {
    ElMessage.success(`已复制 ${hex}`)
  }).catch(() => {
    // fallback: textarea + execCommand('copy')
  })
}
```

#### 4.6.3 完成标准

新功能开发完成后，必须确认以下全部通过：
- [ ] `router/index.js` 中已注册路由（含 `meta.title`）
- [ ] `Home.vue` 对应分类区域有功能卡片，点击可跳转
- [ ] `Header.vue` 对应菜单下有导航入口（含 `pathMap` 映射）
- [ ] Nginx 配置文件中有对应的 `location` 代理块
- [ ] 前后端联调测试通过

> ⚠️ **Agent 注意**: 每次生成新页面时，请主动检查以上三项是否已配置。如果缺失，请在本次提交中一并补全，不要等待后续单独处理。

#### 4.6.4 前端构建与部署规范（强制）

**每次修改前端页面后，必须重新构建并验证产物。** 这是防止 404 和运行时错误的唯一手段。

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 构建前端 | `cd frontend && npm run build` | 必须成功返回，无编译错误 |
| 2. 验证产物 | `ls dist/assets/ \| grep -i <模块名>` | 确认新页面 JS/CSS chunk 已生成 |
| 3. 验证路由 | `curl -s -o /dev/null -w "%{http_code}" http://<host>:5004/<路由>` | 必须返回 `200` |
| 4. 验证 chunk 引用 | `curl -s http://<host>:5004/<路由> \| grep '<modulepreload.*<模块名>'` | 确认 JS chunk 被正确引用 |

> ⚠️ **Agent 注意**: 每次前端代码修改后，**必须执行 `npm run build`**。不构建直接部署会导致 404。

---

## 🚨 六、前端开发常见陷阱与规避 (Frontend Pitfalls)

**目的**: 记录历史踩坑经验，形成可查询的陷阱清单。每次开发新页面前必须通读本节，避免重复犯错。**所有错误都应在编码阶段通过构建验证发现，而非运行时。**

### 6.1 Element Plus 图标陷阱

**问题**: `@element-plus/icons-vue` 中不存在所有可能的图标名，使用不存在的图标会导致构建失败。

**已验证可用的图标清单（按分类）**：

| 分类 | 可用图标名 |
|------|-----------|
| 文档类 | `Document`, `Files`, `Edit`, `EditPen` |
| 数据类 | `DataBoard`, `DataAnalysis`, `Grid` |
| 操作类 | `Operation`, `Download`, `Filter`, `Setting`, `ArrowLeft` |
| 用户类 | `UserFilled`, `Avatar`, `HomeFilled`, `Key` |
| 其他 | `Platform`, `OfficeBuilding`, `ChatDotRound`, `Calendar`, `Bell`, `Cpu`, `Picture` |

**不可用的图标名（禁止使用）**：
- ❌ `ColorSwitch` — 不存在，颜色相关用 `Picture` 替代
- ❌ `Save` — 不存在，保存操作用 `Check` 替代
- ❌ `Refresh` — 不存在，刷新操作用 `RefreshLeft` 替代

**排查方法**:
```bash
# 查看当前项目已安装的所有可用图标名
grep -oE '[A-Z][a-zA-Z]+' node_modules/@element-plus/icons-vue/dist/index.cjs | sort -u
```

**修复策略**: 当构建报错 `Missing export: XXXX` 时，先确认图标是否存在，再替换为可用图标。

### 6.2 Vue 模板语法陷阱

**问题**: `<script setup>` 中函数声明的命名和调用方式有严格限制。

| 错误写法 | 正确写法 | 原因 |
|---------|---------|------|
| `function get selectedResultColor() {}` | `const selectedResultColor = computed(() => ...)` | 函数名不能含空格；模板中调用计算属性更简洁 |
| `const getSchemeHexes = function(scheme) {}` | `function getSchemeHexes(scheme) {}` | 函数声明比箭头函数更清晰（可选） |
| `v-model="inputForm.mode"` 在 `<el-radio-group>` 外 | 必须在组件内部使用 | Vue 3 响应式限制 |

**嵌套引号陷阱**:
```vue
<!-- ❌ 错误：模板中字符串包含双引号导致解析失败 -->
<el-button title="提取颜色">"提取颜色"</el-button>

<!-- ✅ 正确：使用单引号或纯文本 -->
<el-button title="提取颜色">提取颜色</el-button>
```

### 6.3 响应式状态陷阱

**问题**: `reactive` 和 `ref` 混用时的常见错误。

| 场景 | 推荐方式 | 示例 |
|------|---------|------|
| 表单对象（多个字段） | `reactive` | `const inputForm = reactive({ content: '', mode: 'auto' })` |
| 单个值（列表、布尔） | `ref` | `const resultColors = ref([])` |
| 派生值（从其他状态计算） | `computed` | `const selectedResultColor = computed(() => ...)` |

**常见错误**:
```js
// ❌ 错误：reactive 对象解构丢失响应性
const { content, mode } = inputForm  // content 和 mode 不再是响应式的

// ✅ 正确：直接通过对象访问
inputForm.content = 'new value'  // 保持响应式
```

### 6.4 API 调用陷阱

**问题**: 前端直接 `fetch` 调用后端接口时的常见错误。

| 场景 | 正确做法 |
|------|---------|
| JSON 请求体 | `headers: { 'Content-Type': 'application/json' }` + `JSON.stringify(body)` |
| 文件下载（blob） | `res.blob()` → `URL.createObjectURL(blob)` → `<a>` 标签触发下载 |
| 错误处理 | 检查 `res.ok`，解析 `error.json()` 获取后端错误信息 |
| 分页参数 | GET 请求通过 URL query string: `/api/xxx?page=1&page_size=20` |

### 6.5 构建与部署陷阱

**问题**: 前端代码修改后未重新构建，导致线上 404。

| 错误现象 | 原因 | 解决方案 |
|---------|------|---------|
| 访问新页面返回 404 | 未执行 `npm run build`，旧产物中无新路由 | 每次修改前端后必须构建 |
| `Missing export: XXXX` 构建失败 | 使用了不存在的图标或组件名 | 检查可用图标清单，替换为有效名称 |
| `Unexpected token` 构建失败 | 模板中有语法错误（嵌套引号、函数名含空格） | 检查构建日志中的行号和错误类型 |
| chunk 文件过大 (>500KB) | 单页面功能过多，未做代码分割 | 使用动态 `import()` 或调整 chunkSizeWarningLimit |

**构建验证流程（强制执行）**：
```bash
# 1. 执行构建
cd frontend && npm run build

# 2. 检查是否有错误（exit code != 0）
echo $?  # 必须为 0

# 3. 验证新页面产物是否存在
ls dist/assets/ | grep -i <模块名>

# 4. 验证路由可访问
curl -s -o /dev/null -w "%{http_code}" http://<host>:5004/<路由>
# 必须返回 200

# 5. 验证 JS chunk 被正确引用
curl -s http://<host>:5004/<路由> | grep '<modulepreload.*<模块名>'
# 必须返回匹配的 chunk 路径
```

---

## 📈 七、参考命令速查表

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

| 目的          | 命令 (Linux/Mac) | Notes |
|:------------| :--- | :--- |
| **启动前后端开发** | `./start_all_prod.sh` | 确保已激活 `.venv`。 |
| **安装所有依赖**  | `pip install -r requirements.txt` | 仅在 CI/CD 或首次搭建环境时执行。 |
| **运行全量测试**  | `pytest test/ -v --cov=. --cov-report=html` | 生成 HTML 报告到 `htmlcov/`。 |
| **查看覆盖率**   | `pytest test/ -v --cov=. --cov-report=term-missing` | 在终端显示未覆盖的行数和文件。 |
| **生成部署版本**  | `cd frontend && npm run build` | 构建生产环境静态资源。 |

---
***（End of Guide）***