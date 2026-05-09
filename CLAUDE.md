# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 常用命令

| 目的 | 命令 | 备注 |
|------|------|------|
| 启动项目 | `./.venv/bin/python -m flask run --port 5001` | 需要先创建并激活虚拟环境。
| 安装依赖 | `pip install -r requirements.txt` | 运行前请确保已激活 `.venv`。
| 运行单个测试 | `pytest tests/test_*.py::TestCase::test_method -q` | `pytest` 会自动收集 `tests/` 下的模块。
| 运行全部测试 | `pytest -q` |
| 代码格式检查 | `black . --check` | 与 `isort .` 一起使用可保持风格一致。
| 代码格式化 | `black .` 和 `isort .` |
| 生成数据库迁移 | `flask db upgrade` | 仅在需要时使用。

## 高层架构

- **后端**：Python 3.13 + Flask 3.0.0，使用 Flask‑SQLAlchemy 进行 ORM。所有业务逻辑都放在 `routes/` 目录下，子目录按照功能区分（`fpa/`, `auth/`, `chat/`, `document_convert/`, `kafka/`, `schedule/` 等）。每个子目录都有自己的路由模块，统一通过 `app.py` 注册。
- **数据模型**：位于 `models/`，公开的 `__init__.py` 用于导出模型，避免在路由层直接依赖文件结构。
- **AI**：本地使用 Ollama（qwen3:4b），可切换到远端 OMLX。AI 相关接口集中在 `chat/` 和 `fpa/` 的 AI 扩展路由中。
- **文档处理**：`document_convert/` 提供 Excel → Word、Markdown 上传、Word → Markdown 等功能，使用 `python-docx`、`markdownify` 等第三方库。
- **Kafka**：`kafka/` 包含消息生成器与 Kafka 交互，配置文件在 `.env` 中维护。核心逻辑在 `kafka_generator_routes.py`。
- **排班**：`schedule/` 与保留的旧子系统 `排班/` 共同实现排班管理，数据库表通过 `models/visit_log.py` 和 `models/visit_log.py`。
- **配置**：`config.py` 加载 `.env`，通过 Flask‑Config 加载环境变量。常见参数如 `DATABASE_URI`, `OLLAMA_HOST` 等。
- **路由注册**：`app.py` 通过 `from routes import *` 并 `app.register_blueprint()`，保持入口单一。

以上结构使得在添加新模块时只需在 `routes/` 添加蓝图并在 `app.py` 注册，即可完成路由层集成。
