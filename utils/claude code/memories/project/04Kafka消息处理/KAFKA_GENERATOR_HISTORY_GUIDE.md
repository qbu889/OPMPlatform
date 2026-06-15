# Kafka 生成器历史记录功能说明

## 功能概述

在 Kafka 消息生成器的每个字段输入框中新增了【历史】按钮，点击后可以查看该字段的历史生成记录。

## 数据库配置

### 1. 创建历史记录表

执行以下 SQL 脚本创建历史记录表:

```bash
mysql -u your_username -p your_database < sql/create_kafka_generation_history.sql
```

或手动执行 `sql/create_kafka_generation_history.sql` 文件中的 SQL 语句。

### 2. 表结构说明

`kafka_generation_history` 表包含以下字段:

- `id`: 主键 ID
- `es_source_raw`: 原始 ES 数据 (JSON 格式)
- `kafka_message`: 生成的 Kafka 消息 (JSON 格式)
- `created_at`: 创建时间
- `created_by`: 创建者 (默认为 system)
- `fp_value`: FP 值 (用于快速检索)
- `alarm_name`: 告警名称
- `alarm_level`: 告警级别
- `region_name`: 地区名称

## 使用方法

### 查看历史记录

1. 打开 Kafka 消息生成器页面：`http://127.0.0.1:5001/kafka-generator/`
2. 在任意字段输入框旁边，点击【历史】按钮
3. 弹出历史记录窗口，显示该字段的所有历史生成记录

### 搜索历史记录

在历史记录弹窗中:
- 使用搜索框输入关键词 (支持 FP 值、告警名称、地区)
- 系统会实时筛选匹配的记录
- 支持分页浏览，每页显示 20 条记录

### 使用历史记录

1. 在历史记录列表中找到需要的记录
2. 点击该行的"使用此记录"按钮 (✓图标)
3. 系统会自动将该记录的字段值填充到输入框中
4. 弹窗自动关闭，完成字段值填充

## 后端 API

### 获取历史记录列表

```
GET /kafka-generator/history
```

**参数:**
- `page`: 页码 (默认 1)
- `per_page`: 每页数量 (默认 20)
- `keyword`: 搜索关键词 (可选)

**响应示例:**
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "created_at": "2026-04-01 10:30:00",
        "fp_value": "1713996274_3872318956_2520283298_4136070826_2",
        "alarm_name": "设备脱网 (影响 1 条电路)",
        "alarm_level": "2",
        "region_name": "漳州市",
        "kafka_message": {...}
      }
    ],
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

### 获取单条历史记录详情

```
GET /kafka-generator/history/<id>
```

**响应示例:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "created_at": "2026-04-01 10:30:00",
    "fp_value": "1713996274_3872318956_2520283298_4136070826_2",
    "alarm_name": "设备脱网 (影响 1 条电路)",
    "alarm_level": "2",
    "region_name": "漳州市",
    "es_source_raw": {...},
    "kafka_message": {...}
  }
}
```

## 自动保存机制

每次生成 Kafka 消息时，系统会自动保存以下信息到历史记录:

1. 原始 ES 数据
2. 生成的 Kafka 消息
3. FP 值 (用于快速检索)
4. 告警名称
5. 告警级别
6. 地区名称

保存操作在后台异步执行，不会影响主流程的性能。

## 注意事项

1. **数据库依赖**: 需要确保 MySQL 数据库已正确配置并可访问
2. **性能考虑**: 历史记录表建议定期清理，避免数据量过大影响查询性能
3. **隐私保护**: 历史记录包含完整的 ES 数据和 Kafka 消息，请注意数据安全
4. **兼容性**: 需要 Bootstrap 4.x 或更高版本支持模态框功能

## 故障排查

### 问题：点击历史按钮无反应

**解决方案:**
1. 检查浏览器控制台是否有 JavaScript 错误
2. 确认 Bootstrap 库已正确加载
3. 检查网络连接是否正常

### 问题：加载历史记录失败

**解决方案:**
1. 检查 MySQL 数据库是否正常运行
2. 确认 `kafka_generation_history` 表已创建
3. 查看后端日志，确认 API 路由是否正常工作

### 问题：历史记录为空

**解决方案:**
1. 确认已经生成过 Kafka 消息
2. 检查后端日志，确认保存历史记录的 SQL 是否执行成功
3. 尝试手动插入测试数据验证查询功能

## 技术实现

### 前端技术栈
- Bootstrap 4.x (模态框、分页组件)
- Vanilla JavaScript (Fetch API)
- Font Awesome (图标)

### 后端技术栈
- Flask (路由、模板渲染)
- MySQL (数据存储)
- Python mysql-connector (数据库连接)

### 数据库索引

为提高查询性能，已创建以下索引:

```sql
CREATE INDEX `idx_created_at` ON `kafka_generation_history` (`created_at`);
CREATE INDEX `idx_fp_value` ON `kafka_generation_history` (`fp_value`);
CREATE INDEX `idx_alarm_name` ON `kafka_generation_history` (`alarm_name`);
```

## 更新日志

### v1.0 - 2026-04-01
- ✅ 新增历史记录查看功能
- ✅ 支持搜索和分页
- ✅ 支持一键使用历史值
- ✅ 自动保存生成记录
- ✅ 支持按 FP 值、告警名称、地区搜索
