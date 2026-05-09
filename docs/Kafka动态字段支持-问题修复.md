# Kafka 动态字段支持 - 问题修复总结

## 问题描述

用户反馈:在字段映射管理中配置了 `ASSIGN_TENANCE_GROUP` 字段,ES 源数据中也有这个字段,但生成的 Kafka 消息中没有包含这个字段。

**具体表现**:
- ES 源数据中有: `"ASSIGN_TENANCE_GROUP": "莆田仙游海格怡创公司传输线路维护组1"`
- 数据库中有配置:`kafka_field_meta` 表中 `kafka_field=ASSIGN_TENANCE_GROUP`, `es_field=ASSIGN_TENANCE_GROUP`, `is_enabled=1`
- 但生成的 Kafka 消息中**没有** `ASSIGN_TENANCE_GROUP` 字段

## 根本原因

### 1. 字段生成逻辑限制

原有代码只遍历 `STANDARD_FIELD_ORDER` 列表中的字段:

```python
# 原代码 (generate_es_to_kafka_mapping 函数)
for kafka_field in STANDARD_FIELD_ORDER:
    # 处理字段...
```

**问题**: `ASSIGN_TENANCE_GROUP` 不在 `STANDARD_FIELD_ORDER` 列表中,所以即使数据库中有配置,也不会被处理。

### 2. 缺少历史记录字段

数据库表 `kafka_generation_history` 缺少 `selected_fields` 字段,无法记录用户选中的字段列表。

## 解决方案

### 1. 添加数据库字段

创建 SQL 文件添加 `selected_fields` 字段:

```sql
-- sql/add_selected_fields_to_kafka_history.sql
ALTER TABLE `knowledge_base`.`kafka_generation_history` 
ADD COLUMN `selected_fields` LONGTEXT COMMENT '用户选中的字段列表 (JSON 数组格式)' 
AFTER `custom_fields`;
```

执行:
```bash
mysql -u root -p'12345678' knowledge_base < /tmp/add_selected_fields_to_kafka_history.sql
```

### 2. 修改后端生成逻辑

#### 2.1 接收 selected_fields 参数

```python
# routes/kafka/kafka_generator_routes.py - generate_kafka_message 函数
selected_fields = request.json.get('selected_fields', [])  # 用户选中的字段列表
```

#### 2.2 保存 selected_fields 到数据库

```python
# save_generation_history_with_custom_fields 函数
def save_generation_history_with_custom_fields(es_data, kafka_message, custom_fields=None, selected_fields=None):
    # ...
    selected_fields_json = json.dumps(selected_fields, ensure_ascii=False) if selected_fields else None
    
    query = """
        INSERT INTO knowledge_base.kafka_generation_history 
        (es_source_raw, kafka_message, fp_value, alarm_name, alarm_level, region_name, custom_fields, selected_fields)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    # ...
```

#### 2.3 历史查询返回 selected_fields

```python
# get_generation_history 函数
data_query = """
    SELECT id, created_at, fp_value, alarm_name, alarm_level, region_name, 
           es_source_raw, kafka_message, custom_fields, selected_fields, remark
    FROM knowledge_base.kafka_generation_history 
    ...
"""
```

### 3. 支持动态字段生成 ⭐核心改进

#### 3.1 修改 build_dynamic_field_mapping 函数

增加对数据库中配置但不在 `STANDARD_FIELD_ORDER` 中的字段的支持:

```python
def build_dynamic_field_mapping(es_data, field_meta, user_delay_time=None):
    field_mapping = {}
    
    # 1. 先处理 STANDARD_FIELD_ORDER 中的标准字段
    for kafka_field in STANDARD_FIELD_ORDER:
        meta = field_meta.get(kafka_field, {})
        es_field = meta.get('es_field', '')
        
        if kafka_field in SPECIAL_FIELDS:
            field_mapping[kafka_field] = get_default_mapping_rule(kafka_field, es_data, user_delay_time)
        elif es_field:
            field_mapping[kafka_field] = f"_source.{es_field}"
        else:
            field_mapping[kafka_field] = get_default_mapping_rule(kafka_field, es_data, user_delay_time)
    
    # 2. 再处理数据库中配置但不在 STANDARD_FIELD_ORDER 中的额外字段 ⭐新增
    for kafka_field, meta in field_meta.items():
        # 跳过已经处理过的字段
        if kafka_field in field_mapping:
            continue
        
        # 跳过特殊字段
        if kafka_field in SPECIAL_FIELDS:
            continue
        
        es_field = meta.get('es_field', '')
        is_enabled = meta.get('is_enabled', 1)
        
        # 只处理已启用且有 es_field 配置的字段
        if is_enabled and es_field:
            field_mapping[kafka_field] = f"_source.{es_field}"
            logger.debug(f"[DYNAMIC_FIELD] 添加动态字段: {kafka_field} -> {es_field}")
    
    return field_mapping
```

#### 3.2 修改 generate_es_to_kafka_mapping 函数

增加对动态字段的生成处理:

```python
def generate_es_to_kafka_mapping(es_data, user_delay_time=None):
    # ... 原有标准字段处理逻辑 ...
    
    # 处理动态字段(数据库中配置但不在 STANDARD_FIELD_ORDER 中的字段) ⭐新增
    for kafka_field, mapping_rule in field_mapping.items():
        # 跳过已经处理过的标准字段
        if kafka_field in STANDARD_FIELD_ORDER:
            continue
        
        try:
            if isinstance(mapping_rule, str) and mapping_rule.startswith("_source."):
                # 如果是 ES 字段路径
                es_path = mapping_rule.replace("_source.", "")
                value = get_nested_value(es_data, es_path)
                if value is not None:
                    kafka_message[kafka_field] = str(value)
                    logger.debug(f"[DYNAMIC_FIELD] 生成动态字段: {kafka_field} = {value}")
                else:
                    kafka_message[kafka_field] = ""
            else:
                kafka_message[kafka_field] = ""
        except Exception as e:
            logger.debug(f"处理动态字段 {kafka_field} 时出错:{e}")
            kafka_message[kafka_field] = ""
    
    # 重新生成ORG_TEXT字段
    kafka_message["ORG_TEXT"] = generate_org_text(dict(kafka_message))
    
    return kafka_message
```

## 使用效果

### 修复前

```json
// ES 源数据
{
  "_source": {
    "ASSIGN_TENANCE_GROUP": "莆田仙游海格怡创公司传输线路维护组1",
    // ...其他字段
  }
}

// 生成的 Kafka 消息 (缺少 ASSIGN_TENANCE_GROUP)
{
  "TITLE_TEXT": "...",
  "MAINTAIN_GROUP": "...",
  // 没有 ASSIGN_TENANCE_GROUP ❌
}
```

### 修复后

```json
// ES 源数据
{
  "_source": {
    "ASSIGN_TENANCE_GROUP": "莆田仙游海格怡创公司传输线路维护组1",
    // ...其他字段
  }
}

// 生成的 Kafka 消息 (包含 ASSIGN_TENANCE_GROUP) ✅
{
  "TITLE_TEXT": "...",
  "MAINTAIN_GROUP": "...",
  "ASSIGN_TENANCE_GROUP": "莆田仙游海格怡创公司传输线路维护组1",  // ✅ 自动生成
  // ...其他字段
}
```

## 优势

1. **无需修改代码**: 在字段映射管理中添加新字段后,立即生效,无需修改 `STANDARD_FIELD_ORDER`
2. **灵活扩展**: 支持任意数量的自定义字段,只要在数据库中配置即可
3. **自动检测**: 系统会自动检测并生成数据库中配置的所有已启用字段
4. **向后兼容**: 不影响现有的标准字段生成逻辑

## 使用方法

### 添加新字段

1. 访问"字段映射管理"页面
2. 点击"新增字段"
3. 填写:
   - **Kafka 字段名**: `ASSIGN_TENANCE_GROUP`
   - **ES 字段名**: `ASSIGN_TENANCE_GROUP`
   - **是否启用**: ✓
4. 保存

### 生成 Kafka 消息

下次生成时,系统会**自动**包含这个新字段(如果 ES 数据中存在)。

## 注意事项

1. **字段必须在 ES 数据中存在**: 如果 ES 数据中没有该字段,生成的值为空字符串
2. **特殊字段不受影响**: `FP0_FP1_FP2_FP3`, `EVENT_TIME` 等特殊字段仍然使用固定规则生成
3. **字段顺序**: 动态字段会追加在标准字段之后,ORG_TEXT 之前

## 相关文件

- `routes/kafka/kafka_generator_routes.py` - 后端生成逻辑
- `sql/add_selected_fields_to_kafka_history.sql` - 数据库迁移脚本
- `frontend/src/views/tools/KafkaGenerator.vue` - 前端界面(待更新传递 selected_fields)

## 后续优化建议

1. **前端传递 selected_fields**: 修改前端,在生成时传递用户选中的字段列表
2. **字段排序**: 允许用户在界面上拖拽调整字段顺序
3. **字段分组**: 支持将字段分组显示(标准字段/自定义字段)
4. **字段验证**: 添加字段名合法性校验
