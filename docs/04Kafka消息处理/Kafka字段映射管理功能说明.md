# Kafka 字段映射管理功能说明

## 📋 功能概述

实现了 Kafka 消息生成器的**动态字段映射**功能，支持通过数据库配置 ES 字段到 Kafka 字段的映射关系，并提供可视化的 CRUD 管理界面。

## 🎯 解决的问题

### 原有问题
生成 Kafka 消息时，字段映射关系是硬编码在代码中的，例如：
```python
"STANDARD_ALARM_ID": "_source.ALARM_STANDARD_ID"
```

这导致：
1. ❌ 修改映射关系需要修改代码并重新部署
2. ❌ 无法灵活调整字段映射
3. ❌ 新增字段需要开发介入

### 解决方案
✅ **从数据库动态读取映射配置**
- 优先从 `kafka_field_meta` 表读取 `es_field` 配置
- 如果数据库中没有配置，回退到内置的默认映射规则
- 支持实时修改，无需重启服务

## 🗄️ 数据库表结构

### kafka_field_meta 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT UNSIGNED | 主键 ID |
| kafka_field | VARCHAR(64) | Kafka 字段名（唯一） |
| es_field | VARCHAR(128) | 对应的 ES 字段名 |
| db_cn | VARCHAR(255) | 数据库中文说明 |
| label_cn | VARCHAR(255) | 字段中文解释 |
| remark | VARCHAR(255) | 备注 |
| is_enabled | TINYINT | 是否启用（1=启用，0=禁用） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 🔧 后端实现

### 核心函数

#### 1. `load_field_meta_from_mysql()`
从数据库加载字段元数据，返回格式：
```python
{
    "STANDARD_ALARM_ID": {
        "label_cn": "网管告警ID",
        "es_field": "ALARM_STANDARD_ID",
        "db_cn": "告警标准化ID"
    },
    ...
}
```

#### 2. `build_dynamic_field_mapping(es_data, field_meta, user_delay_time)`
根据数据库配置动态构建字段映射规则：
- 如果数据库中配置了 `es_field`，使用 `_source.{es_field}` 
- 否则使用内置的默认映射规则

#### 3. `generate_es_to_kafka_mapping(es_data, user_delay_time)`
生成 Kafka 消息的主函数，调用上述两个函数实现动态映射。

### API 接口

#### GET `/kafka-generator/field-meta/list`
获取字段映射列表（支持分页和搜索）

**请求参数：**
- `page`: 页码（默认 1）
- `per_page`: 每页数量（默认 50）
- `keyword`: 搜索关键字（可选）

**响应示例：**
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "kafka_field": "STANDARD_ALARM_ID",
        "es_field": "ALARM_STANDARD_ID",
        "db_cn": "告警标准化ID",
        "label_cn": "网管告警ID",
        "remark": "",
        "is_enabled": 1,
        "created_at": "2026-04-28 17:00:00",
        "updated_at": "2026-04-28 17:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 50
  }
}
```

#### POST `/kafka-generator/field-meta`
新增字段映射配置

**请求体：**
```json
{
  "kafka_field": "STANDARD_ALARM_ID",
  "es_field": "ALARM_STANDARD_ID",
  "db_cn": "告警标准化ID",
  "label_cn": "网管告警ID",
  "remark": "备注信息"
}
```

#### PUT `/kafka-generator/field-meta/{id}`
更新字段映射配置

**请求体：**
```json
{
  "es_field": "ALARM_STANDARD_ID",
  "db_cn": "告警标准化ID",
  "label_cn": "网管告警ID",
  "remark": "更新后的备注",
  "is_enabled": 1
}
```

#### DELETE `/kafka-generator/field-meta/{id}`
删除字段映射配置（软删除，设置 `is_enabled=0`）

## 🎨 前端实现

### 页面路径
`http://localhost:5200/kafka-field-meta`

### 功能特性
1. ✅ **列表展示**：表格显示所有字段映射配置
2. ✅ **搜索功能**：支持按 Kafka 字段、ES 字段、中文说明搜索
3. ✅ **分页功能**：支持自定义每页显示数量
4. ✅ **新增映射**：弹窗表单新增字段映射
5. ✅ **编辑映射**：修改现有映射配置
6. ✅ **删除映射**：软删除（可恢复）
7. ✅ **状态管理**：启用/禁用切换

### 技术栈
- Vue 3 Composition API
- Element Plus UI 组件库
- Axios HTTP 客户端

## 📊 使用流程

### 场景 1：添加新的字段映射

1. 访问 http://localhost:5200/kafka-field-meta
2. 点击"新增映射"按钮
3. 填写表单：
   - **Kafka 字段**：`STANDARD_ALARM_ID`
   - **ES 字段**：`ALARM_STANDARD_ID`
   - **字段中文解释**：`网管告警ID`
   - **数据库中文**：`告警标准化ID`
4. 点击"确定"保存

### 场景 2：修改现有映射

1. 在列表中找到要修改的记录
2. 点击"编辑"按钮
3. 修改 ES 字段或其他信息
4. 点击"确定"保存

### 场景 3：验证映射效果

1. 访问 Kafka 消息生成器页面
2. 输入 ES 原始数据（包含 `ALARM_STANDARD_ID` 字段）
3. 点击"生成 Kafka 消息"
4. 检查生成的消息中 `STANDARD_ALARM_ID` 是否正确映射了 `ALARM_STANDARD_ID` 的值

## 🧪 测试方法

### 运行测试脚本
```bash
cd /Users/linziwang/PycharmProjects/wordToWord
source .venv/bin/activate
python test/kafka/test_field_mapping.py
```

### 测试内容
1. ✅ 获取字段映射列表
2. ✅ 新增字段映射
3. ✅ 搜索字段映射
4. ✅ 更新字段映射
5. ✅ 删除字段映射
6. ✅ 验证动态映射是否生效

## 🚀 部署步骤

### 1. 确保数据库表存在
执行 SQL 文件：
```bash
mysql -u root -p knowledge_base < sql/kafka_field_meta.sql
```

### 2. 导入初始数据（可选）
```bash
python scripts/import_kafka_field_meta.py --batch
```

### 3. 重启后端服务
```bash
# 停止旧服务
lsof -ti:5004 | xargs kill -9

# 启动新服务
PORT=5004 python app.py --host 0.0.0.0
```

### 4. 重启前端服务（如果需要）
```bash
cd frontend
npm run dev
```

## 💡 优势总结

1. **灵活性**：无需修改代码即可调整字段映射
2. **可维护性**：通过可视化界面管理，降低维护成本
3. **可扩展性**：轻松添加新字段映射
4. **向后兼容**：保留默认映射规则作为后备
5. **实时生效**：修改后立即生效，无需重启服务

## 📝 注意事项

1. **优先级**：数据库配置 > 内置默认映射
2. **唯一性**：`kafka_field` 字段必须唯一
3. **软删除**：删除操作只是设置 `is_enabled=0`，不会真正删除记录
4. **缓存**：每次生成 Kafka 消息都会重新查询数据库，无缓存
5. **性能**：建议为常用字段配置索引

## 🔗 相关文件

- 后端路由：`routes/kafka/kafka_generator_routes.py`
- 前端页面：`frontend/src/views/kafka/KafkaFieldMetaManager.vue`
- 路由配置：`frontend/src/router/index.js`
- Vite 代理：`frontend/vite.config.js`
- 数据库表：`sql/kafka_field_meta.sql`
- 测试脚本：`test/kafka/test_field_mapping.py`
