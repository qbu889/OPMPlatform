# Kafka消息生成器使用说明

## 功能概述
该工具可以根据ES数据自动生成对应的Kafka消息，支持字段映射、自定义覆盖和一键复制功能。

## 使用方法

### 1. Web界面使用
访问 `/kafka-generator/` 路径即可使用Web界面：

1. **输入ES数据**：在文本框中粘贴ES `_source` 对象的JSON数据
2. **自定义字段**（可选）：在自定义字段面板中覆盖特定字段值
3. **生成消息**：点击"生成Kafka消息"按钮
4. **复制结果**：使用"复制结果"按钮一键复制生成的JSON

### 2. API接口调用
```
POST /kafka-generator/generate
Content-Type: application/json

{
    "es_source": { /* ES _source 数据 */ },
    "custom_fields": { /* 自定义字段覆盖 */ }
}
```

## 字段映射规则

### 自动生成规则
- **时间字段**：`EVENT_TIME`、`CREATION_EVENT_TIME`、`EVENT_ARRIVAL_TIME` 自动设置为当前时间减15分钟
- **唯一标识**：`FP0_FP1_FP2_FP3`、`CFP0_CFP1_CFP2_CFP3`、`ORIG_ALARM_FP`、`ORIG_ALARM_CLEAR_FP` 自动生成唯一值
- **默认值**：部分字段有预设的默认值

### 字段映射示例
```
ES字段 → Kafka字段
EVENT_ID → ID
NETWORK_TYPE_ID → NETWORK_TYPE_TOP
ALARM_LEVEL → ORG_SEVERITY
PROVINCE_NAME → REGION_NAME
...
```

## 技术特点

1. **智能映射**：基于提供的demo数据建立完整的字段映射关系
2. **灵活覆盖**：支持自定义字段值覆盖自动生成的值
3. **唯一性保证**：FP相关字段每次生成都保证唯一性
4. **时间处理**：自动处理时间格式和时区
5. **错误处理**：完善的异常处理和用户提示

## 部署说明

### 文件结构
```
routes/
  └── kafka_generator_routes.py    # 后端路由和业务逻辑
templates/
  └── kafka_generator.html         # 前端页面
app.py                             # 主应用（已注册蓝图）
```

### 蓝图注册
已在 `app.py` 中注册：
```python
from routes.kafka_generator_routes import kafka_generator_bp
app.register_blueprint(kafka_generator_bp)
```

## 测试验证
运行测试脚本验证功能：
```bash
python test_kafka_generator.py
```

## 注意事项
1. 输入的ES数据必须是有效的JSON格式
2. 时间字段会自动调整为当前时间减15分钟
3. FP字段每次都会生成新的唯一值
4. 自定义字段优先级高于自动映射值