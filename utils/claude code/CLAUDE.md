# CLAUDE.md

本文档为 Claude Code (claude.ai/code) 在此仓库中编写代码时提供指导。

## 项目背景

本目录（`utils/claude code/`）是**诺基亚 OPM 综合业务系统** (OPM Platform) 下的一个子目录。如需了解整个项目的架构、命令和约定，请参阅父目录的 [`../CLAUDE.md`](../CLAUDE.md)。

## 概述

本目录包含一个独立的 Claude API 集成原型（`claude_code.py`），演示如何通过 LM Studio 桥接方式调用 Anthropic Messages API。这是一个自包含的示例/实验项目，不属于主 OPMPlatform 应用的一部分。

## Key Files

| 文件 | 说明 |
|------|------|
| `claude_code.py` | 核心实现：封装了 `anthropic` Python SDK，并实现了**本地记忆系统**。包含 `claude_with_memory()` 函数和 `LocalMemoryStore` 类，用于持久化的基于文件的记忆存储。 |
| `start_with_claude.sh` | 启动脚本，支持三种模式：`direct`（直接模式）、`bridge`（桥接模式）和 **`memory`**（交互式记忆系统）。 |
| `.env.claude` | 环境配置：包含 `ANTHROPIC_BASE_URL`、`ANTHROPIC_API_KEY` 和默认模型。 |
| `memories/` | 自动创建的目录，用于存储记忆条目（JSON 格式），按类别组织。 |

## 使用方法

```bash
# 直接模式（读取 .env.claude）
./start_with_claude.sh direct

# LM Studio 桥接模式
./start_with_claude.sh bridge

# 交互式记忆系统（新功能！）
./start_with_claude.sh memory

# 直接运行 Python 示例
python3 claude_code.py --demo
```

### 记忆系统使用示例

```python
from claude_code import LocalMemoryStore, claude_with_memory

# 1. 基本记忆存储
memory = LocalMemoryStore()
memory.save_memory("key_name", "内容", category="project")

# 2. 检索记忆
memories = memory.get_memories(key="key_name")
all_project = memory.get_memories(category="project")

# 3. 获取格式化上下文（用于提示词）
context = memory.get_memory_context(key="key_name", max_memories=5)

# 4. 交互模式
./start_with_claude.sh memory
# 可用命令：save、get、list、stats、clear、quit
```

更多使用示例，请参见 `claude_code.py`。

## 环境变量（`.env.claude`）

| 变量名 | 默认值 / 示例 | 说明 |
|--------|---------------|------|
| `ANTHROPIC_BASE_URL` | `http://localhost:1234` | API 端点（LM Studio 桥接或兼容代理） |
| `ANTHROPIC_API_KEY` | `sk-lm-...` | 身份验证用的 API 密钥 |
| `ANTHROPIC_MODEL` | `qwen3-coder-30b-a3b-instruct-mlx@6bit` | 默认模型（另有多个已注释的备选模型） |

## 实现说明

- `claude_code.py` 是一个**原型/示例**，不与主 OPMPlatform 应用集成。
- `LocalMemoryStore` 类提供了**完整实现**的基于文件的记忆存储，支持分类、检索和删除功能。
- `claude_with_memory()` 函数将 Claude API 调用与记忆系统集成，自动在提示词中加载相关记忆。
- 记忆条目以 JSON 文件形式存储在 `memories/<category>/` 目录下。
- API 调用中硬编码的模型（`claude-3-5-sonnet-latest`）在部署时应更新为与 `.env.claude` 中配置的实际模型一致。
- 依赖项：仅需 `anthropic`（Python SDK），无需外部数据库。

## 依赖

```
anthropic  # Claude API 访问的 Python SDK
"""
