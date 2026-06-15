# 彩色抽奖转盘系统 - 开发设计文档
**文件路径**：/Users/linziwang/PycharmProjects/wordToWord/GUIDELINES_MASTER.md
**项目技术栈**：Python(FastAPI) + Vue3 + Vite
**项目名称**：ColorWheelLottery 彩色抽奖转盘
**文档版本**：V1.0
**编写日期**：2026-06-11

---

## 一、项目概述
### 1.1 项目目标
开发一款**前后端分离**的彩色抽奖转盘系统，支持可视化配置转盘分区、自定义分区颜色/名称，点击抽奖触发转盘流畅动画，后端实现随机抽取逻辑并返回结果，完成前后端数据交互与状态联动。系统轻量化、易部署、动画效果流畅，满足日常抽奖、随机选择场景使用。

### 1.2 应用场景
趣味抽奖、随机选人/选物、课堂互动、活动小游戏等。

### 1.3 核心特性
1. 可视化配置转盘分区：支持新增、编辑、删除分区，自定义**分区颜色、分区名称**（可选配置抽奖权重）；
2. 高性能转盘动画：三段式旋转动画（加速→匀速→缓停定格），视觉效果顺滑；
3. 标准前后端交互：后端提供RESTful接口，统一数据格式，解耦业务与视图；
4. 数据持久化：转盘配置本地持久化，重启服务不丢失配置；
5. 结果实时展示：抽奖结束后弹窗/文字展示中奖分区信息。

---

## 二、功能需求清单
### 2.1 核心功能
| 功能模块 | 功能描述 |
| ---- | ---- |
| 转盘配置管理 | 1. 新增转盘分区，设置分区名称、背景色<br>2. 修改已有分区的名称/颜色<br>3. 删除指定分区<br>4. 一键重置所有分区 |
| 转盘渲染 | 根据后端返回的分区数据，动态渲染扇形分区、分区文字、中心指针 |
| 抽奖功能 | 1. 点击抽奖按钮触发交互<br>2. 后端执行随机算法，返回中奖分区<br>3. 前端驱动转盘动画，精准定格在中奖分区 |
| 动画特效 | 转盘无限旋转、渐变加速、减速缓停、定位锁定，搭配过渡动画 |
| 数据持久化 | 转盘配置自动保存，服务重启后加载历史配置 |
| 结果展示 | 动画结束后展示中奖名称、对应颜色信息 |

### 2.2 拓展功能（可选）
1. 权重概率抽奖：不同分区设置权重，实现**非等概率随机抽取**；
2. 抽奖历史记录：记录每一次抽奖结果；
3. 转盘样式自定义：调整转盘大小、边框、背景、指针样式；
4. 音效搭配：抽奖旋转/定格音效；
5. 移动端自适应布局。

---

## 三、技术选型
### 3.1 后端技术（Python）
| 技术/框架 | 选型说明 |
| ---- | ---- |
| 核心框架 | **FastAPI** <br> 轻量异步Web框架，自动生成接口文档、原生支持JSON、跨域配置简单，适配前后端分离场景，开发效率高 |
| 数据存储 | **JSON文件** <br> 项目轻量化需求，无需额外数据库，配置直接落地为本地`config.json`；<br>拓展方案：SQLite（小型嵌入式数据库） |
| 依赖库 | `uvicorn`（ASGI运行服务）、`python-multipart`（表单解析）、`fastapi-cors`（跨域处理） |
| 算法 | Python内置`random`模块（等概率随机），自定义权重随机算法（拓展） |

### 3.2 前端技术（Vue）
| 技术/框架 | 选型说明 |
| ---- | ---- |
| 核心框架 | **Vue3 + Composition API** <br> 主流前端框架，组件化开发，便于拆分转盘、配置、结果等模块 |
| 构建工具 | **Vite** <br> 启动速度快、热更新高效，开发体验优于Webpack |
| UI组件库 | **Element Plus** <br> 提供表单、按钮、弹窗组件，快速实现分区配置表单 |
| 动画方案 | 1. **CSS3 过渡/旋转动画**（基础旋转）<br>2. **GSAP (GreenSock)**（专业动画库，实现变速、缓停、精准定位，推荐主力使用） |
| 样式方案 | SCSS 预处理器，统一样式管理 |
| 网络请求 | **Axios** 封装HTTP请求，对接后端接口，统一拦截异常 |

### 3.3 通用规范
1. 数据交互格式：统一使用 **JSON**；
2. 接口风格：RESTful 规范；
3. 跨域处理：后端开启CORS跨域，解决前后端本地联调跨域问题。

---

## 四、系统整体架构
### 4.1 架构模式
采用**前后端分离架构**，无模板渲染，职责完全拆分：
```
用户操作 → Vue前端(视图+动画+交互) → HTTP请求 → Python后端(接口+业务逻辑+数据存储)
后端计算结果 → HTTP响应 → Vue前端(解析数据+驱动动画+展示结果)
```

### 4.2 架构分层
#### 后端分层（FastAPI）
1. **路由层(Router)**：接收前端请求，分发接口；
2. **服务层(Service)**：实现抽奖算法、配置增删改查核心逻辑；
3. **数据层(Data)**：读写JSON配置文件，负责数据持久化；
4. **公共工具层(Utils)**：通用函数、异常处理。

#### 前端分层（Vue3）
1. **视图层(Page)**：主页面，整合配置表单、转盘组件、结果展示；
2. **组件层(Component)**：拆分独立组件（转盘核心组件、配置表单组件、结果弹窗）；
3. **网络层(Api)**：封装Axios请求，统一管理后端接口地址；
4. **状态层(Store)**：Pinia 管理全局状态（转盘配置、抽奖状态、加载状态）；
5. **动画层(Animation)**：封装GSAP/CSS动画逻辑。

### 4.3 整体数据流
1. 页面初始化：前端请求`获取配置接口` → 后端读取JSON配置 → 返回分区数据 → 前端渲染转盘与表单；
2. 配置修改：前端提交新分区数据 → 后端接收并写入JSON文件 → 返回保存结果 → 前端刷新视图；
3. 抽奖流程：前端点击抽奖 → 调用`抽奖接口` → 后端执行随机算法返回中奖分区 → 前端接收结果 → 启动转盘动画 → 动画定格 → 展示中奖信息。

---

## 五、后端详细设计（Python + FastAPI）
### 5.1 数据模型定义
转盘分区为核心数据单元，定义结构体（Pydantic模型做参数校验）：
```python
# 单分区模型
class WheelItem(BaseModel):
    id: int               # 分区唯一ID
    name: str             # 分区名称（展示文字）
    color: str            # 分区背景色（十六进制色值，如 #ff0000）
    weight: int = 1       # 权重（默认1，等概率；拓展概率抽奖使用）

# 转盘整体配置模型
class WheelConfig(BaseModel):
    items: list[WheelItem]  # 所有分区列表
```

### 5.2 数据存储设计
- 存储文件：`/Users/linziwang/PycharmProjects/wordToWord/backend/config.json`
- 文件格式：标准JSON，持久化所有分区配置；
- 读写规则：接口调用时**同步读写**，简单场景无需加锁；高并发场景可增加文件锁。

**config.json 示例结构**
```json
{
  "items": [
    {"id": 1, "name": "一等奖", "color": "#FF4444", "weight": 1},
    {"id": 2, "name": "二等奖", "color": "#44FF44", "weight": 1},
    {"id": 3, "name": "谢谢参与", "color": "#4444FF", "weight": 2}
  ]
}
```

### 5.3 接口设计（RESTful）
基础地址：`http://127.0.0.1:8000/api`

| 接口名称 | 请求方式 | 接口地址 | 请求参数 | 返回数据 | 功能说明 |
| ---- | ---- | ---- | ---- | ---- | ---- |
| 获取转盘配置 | GET | `/wheel/config` | 无 | WheelConfig 完整配置 | 页面初始化加载分区数据 |
| 保存/更新配置 | POST | `/wheel/config` | Body: WheelConfig | {code:200, msg:"成功"} | 前端修改分区后提交保存 |
| 执行抽奖 | POST | `/wheel/lottery` | 无（自动读取本地配置） | {code:200, data: WheelItem} | 核心接口，返回随机中奖分区 |
| 重置配置 | POST | `/wheel/reset` | 无 | {code:200, msg:"重置成功"} | 清空所有分区，恢复默认 |

### 5.4 核心业务逻辑
#### 5.4.1 等概率随机抽奖算法
读取所有分区列表，通过`random.choice`随机选取一个分区，逻辑简单、公平。
#### 5.4.2 权重随机算法（拓展）
根据分区`weight`权重分配概率，权重越大被抽中概率越高，实现个性化抽奖。
#### 5.4.3 文件读写工具
封装通用函数，统一读取/写入`config.json`，避免重复代码。

### 5.5 跨域配置
后端全局开启CORS跨域，允许前端Vue项目（默认`http://localhost:5173`）跨域请求。

---

## 六、前端详细设计（Vue3 + Vite）
### 6.1 页面与组件拆分（模块化）
前端采用**组件化拆分**，低耦合易维护，整体分为3大核心组件：

1. **主页面 `Index.vue`**
   - 页面布局：左侧【配置表单区】 + 右侧【转盘展示区】 + 底部【操作按钮区】
   - 职责：整合所有子组件、全局状态管理、页面生命周期初始化。

2. **分区配置组件 `WheelConfig.vue`**
   - 功能：新增/编辑/删除分区表单、色值选择器、名称输入框、列表展示；
   - 依赖：Element Plus `el-form`、`el-input`、`el-color-picker`、`el-table`。

3. **转盘核心组件 `WheelCanvas.vue`（核心）**
   - DOM结构：外层转盘容器 + 扇形分区（动态生成） + 中心固定指针；
   - 职责：动态渲染分区颜色/文字、执行旋转动画、接收中奖结果并定格。

4. **结果弹窗组件 `ResultModal.vue`**
   - 功能：动画结束后弹出，展示中奖名称、对应颜色。

### 6.2 布局设计
- 桌面端：左右分栏布局（配置区 + 转盘区）；
- 移动端（拓展）：上下流式布局，自动适配屏幕宽度；
- 转盘样式：圆形转盘、均分扇形分区、分区内居中显示文字、顶部固定指针（指针不旋转）。

### 6.3 动画方案设计（重点）
#### 6.3.1 动画选型
使用 **GSAP 动画库** 实现转盘旋转，相比原生CSS动画，支持**变速、缓动、精准角度定位**，是转盘动画最优方案。

#### 6.3.2 动画三段式逻辑（核心流程）
整个抽奖动画分为**3个阶段**，视觉体验流畅自然：
1. **加速阶段（0~1.5s）**：转盘由慢到快旋转，角速度持续提升；
2. **匀速阶段（1.5~4s）**：转盘高速匀速旋转，营造随机感；
3. **减速定格阶段（4s~结束）**：转盘逐步减速，使用**缓动函数(easeOut)** 缓慢停下，**精准停在后端返回的中奖分区**。

#### 6.3.3 角度计算规则
1. 转盘为360°圆形，根据分区数量`n`，计算**单分区扇形角度**：`singleAngle = 360 / n`；
2. 根据中奖分区索引，计算目标停止角度；
3. 动画总旋转圈数建议 **8~12圈**（多圈旋转增强抽奖氛围），最终角度对齐目标分区中心。

#### 6.3.4 动画约束
- 抽奖过程中**禁用抽奖按钮**，防止重复点击；
- 动画未结束时，禁止修改分区配置；
- 指针固定不动，仅转盘本体旋转。

### 6.4 网络请求封装
1. 使用Axios统一封装请求地址、超时时间、请求头；
2. 封装API函数，对应后端4个接口，集中管理；
3. 增加异常捕获：接口请求失败、网络异常、配置为空等场景提示。

### 6.5 状态管理（Pinia）
全局统一管理状态：
- `wheelList`：当前所有分区数据；
- `isLottering`：抽奖动画状态（是否正在抽奖，控制按钮禁用）；
- `lotteryResult`：最新中奖结果。

---

## 七、前后端完整交互流程
### 7.1 初始化流程（页面加载）
1. 前端Vue页面挂载完成；
2. 前端调用 `GET /api/wheel/config` 接口；
3. 后端读取本地 `config.json` 配置文件，返回分区列表；
4. 前端接收数据，存入Pinia全局状态；
5. 动态渲染**配置表单**和**彩色转盘**，页面初始化完成。

### 7.2 配置修改&保存流程
1. 用户在表单中新增/编辑/删除分区、修改颜色/名称；
2. 点击【保存配置】按钮；
3. 前端组装最新分区数据，调用 `POST /api/wheel/config`；
4. 后端接收数据，覆盖写入 `config.json`；
5. 后端返回保存成功，前端刷新转盘视图。

### 7.3 抽奖核心流程（最关键）
1. 用户点击【开始抽奖】按钮；
2. 前端校验：判断分区数量是否≥1、是否正在抽奖；
3. 按钮置灰禁用，标记`isLottering = true`；
4. 前端调用 `POST /api/wheel/lottery` 抽奖接口；
5. 后端读取`config.json`，执行随机算法，返回**中奖分区信息**；
6. 前端接收中奖数据，计算转盘目标停止角度；
7. 调用GSAP启动三段式旋转动画，转盘开始旋转；
8. 动画执行至最后阶段，缓慢减速并**精准定格**在中奖分区；
9. 动画结束，`isLottering = false`，恢复按钮可用；
10. 弹出结果弹窗，展示中奖名称+颜色，流程结束。

### 7.4 重置流程
1. 点击【重置配置】；
2. 前端调用 `POST /api/wheel/reset`；
3. 后端清空`config.json`，写入默认分区；
4. 前端重新拉取配置，刷新页面视图。

---

## 八、项目目录结构
项目根目录：`/Users/linziwang/PycharmProjects/wordToWord/`
```
wordToWord/
├── GUIDELINES_MASTER.md       # 本开发设计文档
├── backend/                   # Python 后端项目
│   ├── main.py                # FastAPI 入口文件 + 路由
│   ├── models.py              # Pydantic 数据模型
│   ├── service.py             # 业务逻辑（抽奖、配置读写）
│   ├── utils.py               # 工具函数（文件读写、随机算法）
│   ├── config.json            # 转盘配置持久化文件
│   └── requirements.txt       # Python 依赖清单
└── frontend/                  # Vue3 + Vite 前端项目
    ├── package.json
    ├── vite.config.js         # Vite 配置（代理、端口）
    ├── src/
    │   ├── main.js            # Vue 入口
    │   ├── api/               # 接口请求封装
    │   ├── store/             # Pinia 状态管理
    │   ├── components/        # 全局组件
    │   │   ├── WheelConfig.vue    # 分区配置组件
    │   │   ├── WheelCanvas.vue    # 转盘核心组件
    │   │   └── ResultModal.vue   # 结果弹窗
    │   ├── views/
    │   │   └── Index.vue      # 主页面
    │   ├── style/             # 全局样式 & SCSS
    │   └── utils/             # 前端工具（动画、角度计算）
    └── public/                # 静态资源
```

---

## 九、环境部署与运行指南
### 9.1 后端环境（Python）
1. 版本要求：Python 3.8+
2. 安装依赖
   ```bash
   cd /Users/linziwang/PycharmProjects/wordToWord/backend
   pip install -r requirements.txt
   ```
3. 启动后端服务
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
4. 后端访问地址：`http://127.0.0.1:8000`，接口文档：`http://127.0.0.1:8000/docs`

### 9.2 前端环境（Node.js）
1. 版本要求：Node.js 16+
2. 安装依赖
   ```bash
   cd /Users/linziwang/PycharmProjects/wordToWord/frontend
   npm install
   ```
3. 启动前端开发服务
   ```bash
   npm run dev
   ```
4. 前端访问地址：`http://localhost:5173`

### 9.3 联调说明
- 前端Vite可配置`proxy`代理，简化接口请求地址；
- 先后启动**后端**，再启动**前端**，保证接口可正常访问。

---

## 十、核心代码片段（参考实现）
### 10.1 后端核心代码（backend/main.py 节选）
```python
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from models import WheelConfig, WheelItem
from service import get_wheel_config, save_wheel_config, lottery_draw, reset_config

app = FastAPI(title="彩色转盘抽奖接口")

# 配置跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取配置
@app.get("/api/wheel/config")
def get_config():
    return {"code": 200, "data": get_wheel_config()}

# 保存配置
@app.post("/api/wheel/config")
def save_config(config: WheelConfig = Body(...)):
    save_wheel_config(config.dict())
    return {"code": 200, "msg": "配置保存成功"}

# 抽奖接口
@app.post("/api/wheel/lottery")
def lottery():
    result = lottery_draw()
    return {"code": 200, "data": result}

# 重置配置
@app.post("/api/wheel/reset")
def reset():
    reset_config()
    return {"code": 200, "msg": "配置重置成功"}
```

### 10.2 前端动画核心（WheelCanvas.vue + GSAP）
```javascript
import gsap from 'gsap'

// 计算分区角度
const totalAngle = 360
const singleAngle = totalAngle / wheelList.value.length
// 目标分区索引
const targetIndex = res.data.id - 1
// 计算最终停止角度
const targetAngle = (totalAngle - (targetIndex * singleAngle + singleAngle / 2)) % 360
// 总旋转圈数 + 目标角度
const totalRotate = 360 * 10 + targetAngle

// 启动三段式动画
gsap.to(wheelRef.value, {
    rotation: totalRotate,
    duration: 5,
    ease: "power4.out", // 缓停动画曲线
    onComplete: () => {
        isLottering.value = false
        // 展示结果弹窗
        showResult(res.data)
    }
})
```

---

## 十一、优化、扩展与风险说明
### 11.1 优化方向
1. **动画优化**：增加旋转音效、粒子特效，提升视觉体验；
2. **性能优化**：大量分区时优化DOM渲染，使用Canvas绘制转盘；
3. **交互优化**：增加加载状态、Toast提示、操作二次确认；
4. **样式优化**：增加转盘阴影、渐变、立体效果。

### 11.2 功能扩展
1. 接入SQLite/MySQL数据库，支持多用户、多转盘模板；
2. 增加抽奖历史记录表、数据统计；
3. 支持导出配置、导入配置模板；
4. 增加后台登录、权限控制。

### 11.3 风险与解决方案
| 风险点 | 解决方案 |
| ---- | ---- |
| 前后端跨域 | 后端全局开启CORS，前端配置Vite代理 |
| 重复点击抽奖 | 抽奖过程中禁用按钮，增加状态锁 |
| 配置文件损坏 | 增加配置文件异常捕获，自动恢复默认配置 |
| 动画卡顿 | 减少DOM节点，使用Canvas绘制转盘，优化GSAP动画参数 |
| 分区为空导致抽奖报错 | 前端前置校验，分区数量为0时禁止抽奖 |

---

## 十二、文档总结
本项目基于 **Python FastAPI + Vue3** 实现前后端分离彩色抽奖转盘，核心围绕**分区配置、随机抽奖、流畅动画、数据持久化**四大能力设计。架构清晰、模块解耦，代码易维护、易扩展，动画采用行业主流GSAP方案保证视觉效果，接口遵循RESTful规范，可直接基于本设计文档进行编码开发、测试与部署。