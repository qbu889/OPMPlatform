# Kafka 生成器历史记录功能 - 快速上手指南

## 一、快速开始 (3 分钟完成)

### 步骤 1: 创建数据库表

```bash
# 方式 1: 使用命令行工具
mysql -u root -p knowledge_base < sql/create_kafka_generation_history.sql

# 方式 2: 使用测试脚本 (推荐)
python test_kafka_history.py
```

### 步骤 2: 启动应用

```bash
python app.py
```

### 步骤 3: 访问页面

打开浏览器访问：`http://127.0.0.1:5001/kafka-generator/`

## 二、功能演示

### 查看历史记录

1. 在任意字段输入框旁边找到【历史】按钮
2. 点击【历史】按钮
3. 查看该字段的所有历史生成记录

### 搜索历史记录

在弹窗的搜索框中输入关键词:
- FP 值：`1713996274_3872318956`
- 告警名称：`设备脱网`
- 地区：`漳州`

### 使用历史记录

1. 找到需要的记录
2. 点击该行的 ✓ 按钮
3. 字段值自动填充到输入框

## 三、功能特点

✅ **自动保存**: 每次生成 Kafka 消息时自动保存历史记录
✅ **快速检索**: 支持按 FP 值、告警名称、地区搜索
✅ **分页浏览**: 每页 20 条记录，支持翻页
✅ **一键使用**: 点击按钮即可填充字段值
✅ **实时更新**: 搜索框支持实时筛选

## 四、字段说明

### 历史记录表字段

| 字段名 | 说明 | 示例 |
|--------|------|------|
| id | 主键 ID | 1 |
| created_at | 创建时间 | 2026-04-01 10:30:00 |
| fp_value | FP 值 | 1713996274_3872318956_2520283298_4136070826_2 |
| alarm_name | 告警名称 | 设备脱网 (影响 1 条电路) |
| alarm_level | 告警级别 | 2 |
| region_name | 地区 | 漳州市 |
| kafka_message | 完整的 Kafka 消息 | JSON 格式 |
| es_source_raw | 原始 ES 数据 | JSON 格式 |

## 五、常见问题

### Q1: 点击历史按钮没反应？

**A:** 请检查:
1. 浏览器控制台是否有错误
2. 是否已创建数据库表
3. Flask 应用是否正常运行

### Q2: 历史记录为空？

**A:** 
1. 确认是否已生成过 Kafka 消息
2. 运行测试脚本插入测试数据：`python test_kafka_history.py`

### Q3: 如何修改数据库配置？

**A:** 编辑 `test_kafka_history.py` 文件，修改以下配置:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # 修改这里
    'database': 'knowledge_base',
    'charset': 'utf8mb4'
}
```

## 六、技术架构

```
前端 (HTML/JS)          后端 (Flask)          数据库 (MySQL)
    |                       |                       |
    |--- 点击历史按钮 ------->|                       |
    |                       |--- 查询 API ----------->|
    |                       |                       |
    |<-- 显示历史记录 -------|<-- 返回数据 -----------|
    |                       |                       |
    |--- 使用历史记录 ------>|                       |
    |                       |--- 查询详情 ---------->|
    |                       |                       |
    |<-- 填充字段值 ---------|<-- 返回详情 -----------|
```

## 七、下一步

1. **测试功能**: 运行 `python test_kafka_history.py` 验证数据库连接
2. **查看文档**: 阅读 `docs/KAFKA_GENERATOR_HISTORY_GUIDE.md` 了解详细信息
3. **开始使用**: 访问页面，点击【历史】按钮体验功能

## 八、文件清单

- `sql/create_kafka_generation_history.sql` - 数据库表创建脚本
- `test_kafka_history.py` - 测试脚本
- `routes/kafka/kafka_generator_routes.py` - 后端 API (已修改)
- `templates/kafka/kafka_generator.html` - 前端页面 (已修改)
- `docs/KAFKA_GENERATOR_HISTORY_GUIDE.md` - 详细文档

---

**提示**: 如果遇到问题，请查看 Flask 日志或浏览器控制台的错误信息。
