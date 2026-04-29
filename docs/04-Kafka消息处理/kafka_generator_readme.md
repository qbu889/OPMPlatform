# Kafka消息生成器使用说明

## 功能概述
该工具可以根据ES数据自动生成对应的Kafka消息，支持字段映射、自定义覆盖、历史记录管理和一键复制功能。

## 使用方法

### 1. Web界面使用
访问 `/kafka-generator/` 路径即可使用Web界面：

1. **输入ES数据**：在文本框中粘贴ES `_source` 对象的JSON数据
2. **自定义字段**（可选）：在自定义字段面板中覆盖特定字段值
   - 支持置顶常用字段
   - 支持查看字段字典（枚举值说明）
   - 支持查看和选择历史输入值
3. **生成消息**：点击"生成Kafka消息"按钮
4. **时间调整**（可选）：在结果区域调整延迟时间（分钟），自动重新计算时间字段
5. **测试前缀**（可选）：开启后会在网元名称前添加"【测试】"前缀
6. **复制结果**：使用"复制结果"或"复制FP值"按钮快速复制
7. **推送消息**：可生成简化的推送消息格式
8. **添加备注**：为生成的消息添加备注信息，便于后续追溯

### 2. API接口调用
```bash
POST /kafka-generator/generate
Content-Type: application/json

{
    "es_source_raw": "{ ... }",  // ES _source 数据的JSON字符串
    "custom_fields": {            // 自定义字段覆盖（可选）
        "EQP_LABEL": "自定义网元名称",
        "DELAY_TIME": 720
    },
    "delay_time": 15,             // 延迟时间（分钟），用于计算时间字段
    "add_test_prefix": false      // 是否添加【测试】前缀
}
```

**响应示例：**
```json
{
    "success": true,
    "data": {
        "ID": "uuid...",
        "FP0_FP1_FP2_FP3": "1745900000_1234567890_9876543210_1111111111_12345",
        "EVENT_TIME": "2026-04-29 10:30:00",
        ...
    },
    "history_id": 123,  // 历史记录ID
    "delay_time": 15
}
```

## 字段映射规则

### 特殊字段处理
以下字段会使用特殊逻辑生成，**不受数据库配置影响**：

#### 时间字段（3个）
- `EVENT_TIME`：事件发生时间
- `CREATION_EVENT_TIME`：事件发现时间  
- `EVENT_ARRIVAL_TIME`：事件到达时间

**计算规则**：
- 优先从ES数据的 `DELAY_TIME` 字段读取延迟时间（单位：分钟）
- 如果没有 `DELAY_TIME`，默认使用15小时（900分钟）
- 计算公式：`当前时间 - DELAY_TIME小时`
- 格式：`YYYY-MM-DD HH:MM:SS`

#### FP唯一标识字段（5个）
- `FP0_FP1_FP2_FP3`：事件流水号
- `CFP0_CFP1_CFP2_CFP3`：清除告警流水号
- `ORIG_ALARM_FP`：原始告警FP
- `ORIG_ALARM_CLEAR_FP`：原始告警清除FP
- `SRC_ORG_ID`：来源组织ID

**生成规则**：
- 所有FP字段在单次生成中使用**相同的值**，确保数据一致性
- 格式：`{timestamp}_{random1}_{random2}_{random3}_{random4}`
  - `timestamp`：当前时间戳减15分钟
  - `random1-3`：10位随机数字
  - `random4`：5位随机数字
- 示例：`1745900400_3763383435_3204552333_262808553_20260429`

### 普通字段映射
其他字段通过以下方式映射：

1. **数据库配置优先**：从 `kafka_field_meta` 表读取 `es_field` 配置
2. **内置规则兜底**：如果数据库未配置，使用代码中的默认映射规则
3. **ES字段提取**：从ES数据的 `_source.{es_field}` 路径提取值

**常见映射示例**：
```
ES字段                      → Kafka字段
NETWORK_TYPE_ID            → NETWORK_TYPE_TOP（一级专业ID）
ALARM_LEVEL                → ORG_SEVERITY（网管告警级别）
EQUIPMENT_NAME             → EQP_LABEL（网元名称）
NE_LABEL                   → NE_LABEL（告警对象网元名称）
EVENT_LOCATION             → LOCATE_INFO（事件定位信息）
VENDOR_NAME                → VENDOR_NAME（设备厂家名称）
ALARM_NAME                 → TITLE_TEXT（告警标题）
```

### 字段优先级
1. **用户自定义字段** > 数据库映射规则 > 内置默认规则
2. 特殊字段（时间、FP）**忽略数据库配置**，强制使用生成逻辑

## 技术特点

1. **智能映射**：
   - 支持数据库动态配置字段映射关系
   - 内置90+字段的默认映射规则作为兜底
   - 特殊字段（时间、FP）强制使用生成逻辑，确保数据正确性

2. **灵活覆盖**：
   - 支持前端自定义任意字段值
   - 自定义值优先级最高，可覆盖自动生成值
   - 支持置顶常用字段，提升操作效率

3. **唯一性保证**：
   - FP相关字段在单次生成中使用同一个随机值
   - 确保 `FP0_FP1_FP2_FP3`、`CFP0_CFP1_CFP2_CFP3` 等字段完全一致
   - 每次重新生成都会产生新的唯一值

4. **时间处理**：
   - 自动从ES数据中提取 `DELAY_TIME` 进行时间计算
   - 支持前端手动调整延迟时间（0-1440分钟）
   - 三个时间字段保持同步，确保时序一致性

5. **历史记录**：
   - 自动保存每次生成的记录到 `kafka_generation_history` 表
   - 支持查看、搜索历史生成记录
   - 支持从历史记录中快速填充字段值
   - 支持为历史记录添加备注

6. **字段字典**：
   - 为枚举类型字段提供字典查询功能
   - 支持查看字段的合法取值和说明
   - 涵盖15+个枚举字段（如告警级别、专业类型等）

7. **错误处理**：
   - 完善的JSON格式校验和错误提示
   - 数据库异常自动降级到内置规则
   - 详细的日志记录便于问题排查

## 部署说明

### 文件结构
```
routes/
  └── kafka/
      ├── kafka_generator_routes.py    # 后端路由和业务逻辑（主文件）
      └── __init__.py                  # 蓝图初始化

frontend/src/views/tools/
  └── KafkaGenerator.vue               # Vue前端页面

sql/
  ├── kafka_field_meta.sql             # 字段元数据表结构
  ├── create_kafka_generation_history.sql  # 生成历史表结构
  └── create_es_field_mapping.sql      # ES字段映射表（参考）

app.py                                 # 主应用（已注册蓝图）
```

### 数据库表结构

#### 1. kafka_field_meta（字段元数据表）
存储Kafka字段与ES字段的映射关系，支持动态配置。

#### 2. kafka_generation_history（生成历史表）
记录每次生成的完整数据，支持追溯和复用。

#### 3. kafka_field_cache（字段缓存表）
缓存用户输入的字段值，提供快捷输入建议。

### 蓝图注册
已在 `app.py` 中注册：
```python
from routes.kafka.kafka_generator_routes import kafka_generator_bp
app.register_blueprint(kafka_generator_bp)
```

### 依赖安装
```bash
pip install flask flask-cors pymysql cryptography
```

## 测试验证

### 1. 运行测试脚本
```bash
python test_kafka_generator.py
```

### 2. 手动测试流程
1. 启动后端服务：`python app.py`
2. 访问前端页面：`http://localhost:5173/kafka-generator`
3. 粘贴ES数据（可从Kibana复制 `_source` JSON）
4. 点击"生成Kafka消息"
5. 验证生成的JSON格式和字段值

### 3. 关键验证点
- ✅ FP字段是否生成了统一格式的10位数字组合
- ✅ 三个时间字段是否保持一致
- ✅ 时间计算是否符合DELAY_TIME的逻辑
- ✅ 自定义字段是否正确覆盖了自动生成值
- ✅ 开启"【测试】前缀"后，EQP_LABEL和NE_LABEL是否添加了前缀

## 注意事项

### 数据输入
1. ES数据必须是有效的JSON格式，建议从Kibana直接复制 `_source` 对象
2. 如果ES数据中包含嵌套对象（如 `BUSINESS_TAG`、`NE_TAG`），会自动展开提取
3. 支持Python三引号格式的字符串，可使用"强制格式化"按钮转换为标准JSON

### 字段生成
4. 时间字段会根据 ES 数据中的 `DELAY_TIME` 自动计算（单位：分钟），如果没有则默认使用15小时（900分钟）
5. FP相关字段（FP0_FP1_FP2_FP3、CFP0_CFP1_CFP2_CFP3、ORIG_ALARM_FP、ORIG_ALARM_CLEAR_FP、SRC_ORG_ID）每次都会生成相同的唯一值，确保数据一致性
6. 自定义字段优先级高于自动映射值，但特殊字段（时间、FP）会忽略自定义值

### 数据库配置
7. 数据库中的 `kafka_field_meta` 表可以动态配置字段映射，但**不会影响特殊字段**
8. 如果数据库连接失败，系统会自动降级使用内置的默认映射规则
9. 修改数据库配置后，刷新页面即可生效，无需重启服务

### 性能优化
10. 历史记录会自动分页加载，每页20条，避免一次性加载过多数据
11. 字段字典数据会在页面加载时一次性获取，减少重复请求
12. 大数据量的ES文档（>10MB）可能会导致解析缓慢，建议精简后再输入

### 常见问题
**Q: 为什么FP字段没有生成？**  
A: 检查数据库中是否为FP字段配置了 `es_field`，如果有配置会被误认为从ES读取。现在已修复，FP字段强制使用生成逻辑。

**Q: 时间字段为什么不准确？**  
A: 确认ES数据中是否包含 `DELAY_TIME` 字段，该字段单位为分钟。如果没有，会使用默认的15小时延迟。

**Q: 如何批量生成多条消息？**  
A: 目前支持单条生成，如需批量处理，可多次调用API接口或在循环中调用生成函数。