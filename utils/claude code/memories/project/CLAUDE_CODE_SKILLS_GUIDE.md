# Claude Code Skills 使用指南

## 📋 目录
- [快速开始](#快速开始)
- [已安装的 Skills](#已安装的-skills)
- [使用方式](#使用方式)
- [各 Skill 详细说明](#各-skill-详细说明)
- [常见问题](#常见问题)

---

## 🚀 快速开始

### 启动 Claude Code

```bash
# 进入项目目录
cd /Users/linziwang/PycharmProjects/wordToWord

# 启动交互式会话
claude

# 或直接执行命令（非交互模式）
claude -p "帮我分析这个项目的结构"
```

### 重要提示

✅ **不需要手动加载 skills** - 它们会自动生效  
✅ **不需要特殊命令** - 直接用自然语言描述需求  
✅ **智能匹配** - Claude 会根据你的请求自动调用合适的 skill

---

## 📦 已安装的 Skills

| Skill 包 | 版本 | 主要功能 |
|---------|------|---------|
| claude-skill-lord | 2.2.0 | 165个skills、43个agents、代码审查、TDD |
| claude-code-skills | 0.5.0 | 综合性技能集合（94个依赖） |
| claude-skill | 1.2.1 | PRD工作流框架、Hooks自动应用 |
| claude-code-skill-security-check | 2.5.2 | 安全扫描和漏洞检测 |
| claude-code-workflow | 7.3.14 | 工作流管理、自动化流程 |
| claude-code-templates | 1.28.16 | 代码模板和组件追踪 |
| claude-code-autoconfig | 1.0.185 | 自动配置管理 |
| @iamdangavin/claude-skill-vitepress-docs | 3.1.7 | VitePress文档生成 |
| @musistudio/claude-code-router | 2.0.0 | LLM路由和模型选择 |
| @anthropic-ai/claude-code | 2.1.132 | 官方核心包 |

---

## 💡 使用方式

### 方式一：自然语言对话（推荐）

在 Claude Code 交互模式中，直接用自然语言描述你的需求：

#### 🔍 代码审查
```
用户: 请审查 routes/fpa 目录下的代码质量
用户: 检查 auth_routes.py 是否有安全问题
用户: 这个函数需要重构吗？
```

#### 🛡️ 安全检查
```
用户: 扫描当前项目的安全漏洞
用户: 检查数据库连接是否安全
用户: 分析 API 接口的安全性
```

#### 📝 文档生成
```
用户: 为这个项目生成技术文档
用户: 创建 API 接口文档
用户: 生成部署说明文档
```

#### 🔄 工作流管理
```
用户: 创建一个代码审查工作流
用户: 设置自动化测试流程
用户: 帮我规划开发任务
```

#### 🎯 模板使用
```
用户: 创建一个新的 Flask 路由模板
用户: 生成标准的 Python 类结构
用户: 初始化项目配置文件
```

### 方式二：命令行直接执行

```bash
# 代码审查
claude -p "审查 app.py 的代码质量"

# 安全检查
claude -p "检查项目的安全配置"

# 生成文档
claude -p "为 routes 目录生成文档"

# 分析项目
claude -p "分析当前项目的架构"
```

### 方式三：使用专用命令（可选）

某些 skills 提供了专用命令：

```bash
# Skill Lord 工具
csl help                    # 查看帮助
skill-lord list             # 列出可用 agents

# Workflow 工具
ccw --help                  # 查看工作流帮助
ccw-mcp                     # 启动 MCP 服务

# Templates 工具
cct                         # 创建 Claude 配置
claude-code-templates       # 模板管理

# Autoconfig
claude-code-autoconfig      # 自动配置
```

---

## 📖 各 Skill 详细说明

### 1. claude-skill-lord ⭐ 推荐

**功能最全面的 skill 包**

包含：
- ✅ 43 个 Agents（专业助手）
- ✅ 165 个 Skills（专业技能）
- ✅ 114 个 Commands（快捷命令）
- ✅ 11 种语言规则

**典型使用场景：**

```
# 代码审查
用户: 作为代码审查员，检查我的认证模块

# TDD 开发
用户: 用 TDD 方式实现用户登录功能

# 质量管理
用户: 检查代码是否符合最佳实践

# 多语言支持
用户: 用中文解释这段代码的逻辑
```

**专用命令：**
```bash
csl                          # 启动 skill-lord
skill-lord list              # 查看所有可用 skills
skill-lord <skill-name>      # 使用特定 skill
```

---

### 2. claude-code-skill-security-check 🔒

**专业的安全扫描工具**

**使用场景：**

```
用户: 检查整个项目的安全漏洞
用户: 扫描 SQL 注入风险
用户: 检查 API 密钥是否泄露
用户: 分析权限控制是否完善
```

**会检查：**
- SQL 注入漏洞
- XSS 攻击风险
- 硬编码密钥
- 权限配置问题
- 依赖包漏洞
- 敏感信息泄露

---

### 3. claude-code-workflow 🔄

**工作流自动化管理**

**使用场景：**

```
用户: 创建代码提交流程
用户: 设置 CI/CD 工作流
用户: 建立代码审查流程
用户: 自动化测试流程
```

**功能：**
- 自定义工作流定义
- 自动化任务编排
- Dashboard 可视化
- MCP 协议支持

**专用命令：**
```bash
ccw                          # 工作流管理
ccw-mcp                      # MCP 服务器
```

---

### 4. claude-code-templates 📋

**代码模板库**

**使用场景：**

```
用户: 创建 Flask 路由模板
用户: 生成 Python 单元测试模板
用户: 初始化 package.json
用户: 创建 Dockerfile 模板
```

**包含模板：**
- Flask/Django 路由模板
- 数据库模型模板
- API 接口模板
- 测试文件模板
- 配置文件模板

**专用命令：**
```bash
cct                          # 创建配置
claude-code-templates        # 模板管理
```

---

### 5. @iamdangavin/claude-skill-vitepress-docs 📚

**VitePress 文档生成**

**使用场景：**

```
用户: 用 VitePress 生成项目文档
用户: 创建 API 文档站点
用户: 生成开发者指南
用户: 更新现有文档
```

**功能：**
- 自动生成 VitePress 配置
- 从代码提取文档
- 截图集成
- 品牌定制
- 文档同步

**专用命令：**
```bash
claude-skill-vitepress-docs  # 安装/更新
```

---

### 6. claude-code-autoconfig ⚙️

**自动配置管理**

**使用场景：**

```
用户: 优化 Claude Code 配置
用户: 根据项目类型自动配置
用户: 重置默认配置
```

**功能：**
- 智能检测项目类型
- 自动调整配置
- 环境变量管理
- 插件兼容性检查

---

### 7. @musistudio/claude-code-router 🎯

**LLM 路由和模型选择**

**使用场景：**

```
用户: 选择最适合的 AI 模型
用户: 优化 API 调用成本
用户: 配置多模型路由
```

**功能：**
- 智能模型选择
- 负载均衡
- 成本优化
- 故障转移

**专用命令：**
```bash
ccr                          # 路由管理
```

---

### 8. claude-code-skills 🎨

**综合技能集合**

包含多种实用技能，涵盖：
- 代码生成
- 重构建议
- 性能优化
- 调试辅助
- 测试编写

---

### 9. claude-skill 🔧

**PRD 工作流框架**

**特点：**
- Hook 机制自动应用 skills
- PRD 驱动的开发流程
- 结构化工作方法

---

## 🎯 实际使用示例

### 示例 1：完整项目开发流程

```bash
# 1. 启动 Claude Code
claude

# 2. 在对话中：
用户: 帮我创建一个新的用户管理模块

Claude 会自动：
- 使用 templates skill 生成代码结构
- 使用 skill-lord 确保代码质量
- 使用 security-check 检查安全性
- 使用 workflow 创建开发流程

用户: 为这个模块编写单元测试

Claude 会使用测试相关的 skills 生成测试代码

用户: 生成 API 文档

Claude 会使用文档 skill 创建文档
```

### 示例 2：代码审查

```bash
claude -p "全面审查 routes/auth 目录的代码，包括：
1. 代码质量和最佳实践
2. 安全漏洞检查
3. 性能优化建议
4. 文档完整性"

# Claude 会自动调用多个 skills 进行综合分析
```

### 示例 3：项目分析

```bash
claude -p "分析当前项目的架构，并给出：
1. 系统架构图
2. 模块依赖关系
3. 改进建议
4. 技术栈评估"
```

---

## ❓ 常见问题

### Q1: 需要每次手动加载 skills 吗？
**A:** 不需要！所有全局安装的 skills 会自动加载。

### Q2: 如何知道某个 skill 是否在工作？
**A:** Claude 会在响应中说明使用了哪些 tools/skills。你也可以问："你用了什么 skill 来分析这个？"

### Q3: 可以禁用某个 skill 吗？
**A:** 可以卸载不需要的 skill：
```bash
npm uninstall -g <package-name>
```

### Q4: skills 会冲突吗？
**A:** 通常不会。Claude 会智能选择合适的 skill。如果有冲突，可以在对话中指定："使用 skill-lord 来审查代码"

### Q5: 如何更新 skills？
```bash
# 更新所有
npm update -g

# 更新特定 skill
npm update -g claude-skill-lord
```

### Q6: 如何查看某个 skill 的详细信息？
```bash
npm info claude-skill-lord
```

### Q7: Skills 会影响性能吗？
**A:** 影响很小。Skills 是按需加载的，只在需要时激活。

### Q8: 可以为不同项目使用不同的 skills 吗？
**A:** 可以。在项目根目录创建 `.claude/settings.local.json` 来配置项目特定的 settings。

---

## 🔧 管理 Skills

### 查看已安装
```bash
npm list -g --depth=0 | grep claude
```

### 安装新 skill
```bash
npm install -g <skill-package-name>
```

### 卸载 skill
```bash
npm uninstall -g <skill-package-name>
```

### 更新 skills
```bash
npm update -g
```

### 查看 skill 详情
```bash
npm info <skill-package-name>
```

---

## 📚 学习资源

- **Claude Code 官方文档**: https://docs.anthropic.com/claude-code
- **Skill 市场**: 通过 `claude-plugins search` 搜索
- **GitHub Awesome Skills**: 搜索 "awesome-claude-skills"

---

## 💡 最佳实践

1. **用自然语言表达** - 不需要记忆命令
2. **明确你的需求** - 越具体，Claude 越能匹配合适的 skill
3. **组合使用** - 一个任务可能触发多个 skills 协作
4. **反馈调整** - 如果不满意，告诉 Claude 换种方式
5. **定期更新** - 保持 skills 最新版本

---

## 🎉 总结

✅ **无需特殊命令** - 用自然语言即可  
✅ **自动智能匹配** - Claude 自动选择最合适的 skill  
✅ **开箱即用** - 安装后立即生效  
✅ **灵活组合** - 多个 skills 协同工作  
✅ **持续进化** - 定期更新获取新功能  

**开始使用吧！**
```bash
cd /Users/linziwang/PycharmProjects/wordToWord
claude
```

然后直接说："帮我分析一下这个项目" 🚀
