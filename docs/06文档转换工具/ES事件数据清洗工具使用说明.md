# ES事件数据清洗工具使用说明

## 功能概述

ES事件数据清洗工具用于解析Elasticsearch查询结果，自动识别主单和子单，并提供多种复制方式。

## 访问地址

- **前端页面**: http://192.168.124.8:5200/clean-event-page
- **后端API**: `/api/clean-event/parse-es`

## 主单/子单判断规则

根据 `DISPATCH_INFO.DISPATCH_REASON` 字段的值进行判断：

- **主单**: `DISPATCH_REASON == "工单派发成功"`
- **子单**: 其他所有情况（如"同源合并成功"、"追单派单成功"等）

## 使用步骤

### 1. 准备ES查询结果

从Kibana或其他ES客户端获取查询结果的完整JSON，格式如下：

```json
{
  "took": 237,
  "timed_out": false,
  "hits": {
    "total": {
      "value": 2,
      "relation": "eq"
    },
    "max_score": 1.0,
    "hits": [
      {
        "_index": "mw_em_master",
        "_id": "338239308",
        "_source": {
          "EVENT_ID": 338239308,
          "EVENT_NAME": "虚拟化中兴UPF链路异常事件-smartgroup进入无保护状态",
          "EQUIPMENT_NAME": "ZHZUPF602BZX",
          "ALARM_NAME": "smartgroup进入无保护状态",
          "EVENT_TIME": "2026-05-04 18:43:40",
          "ORDER_ID": "FJ-076-20260505-1087",
          "DISPATCH_INFO": {
            "DISPATCH_REASON": "同源合并成功",
            ...
          },
          ...
        }
      },
      ...
    ]
  }
}
```

### 2. 粘贴JSON数据

将完整的ES查询结果JSON粘贴到页面的文本框中。

### 3. 点击"解析数据"

系统会自动：
- 解析JSON结构
- 提取 `hits.hits` 数组中的所有事件
- 根据 `DISPATCH_INFO.DISPATCH_REASON` 判断主单/子单
- 显示统计信息（总数、主单数、子单数）

### 4. 查看结果

结果以表格形式展示，包含以下字段：
- **#**: 序号
- **类型**: 主单（绿色标签）或子单（橙色标签）
- **事件ID**: EVENT_ID
- **事件名称**: EVENT_NAME
- **设备名称**: EQUIPMENT_NAME
- **告警名称**: ALARM_NAME
- **事件时间**: EVENT_TIME
- **工单ID**: ORDER_ID
- **派发原因**: DISPATCH_REASON
- **操作**: 各种复制按钮

## 复制功能

### 1. 复制全部
点击顶部的"复制全部"按钮，复制所有记录的完整 `_source` 数据（格式化JSON）。

### 2. 复制本条
在每条记录的操作列，点击"复制本条"按钮，复制该条记录的完整 `_source` 数据。

### 3. 复制所有子单
在任意**子单**记录的操作列，点击"复制所有子单"按钮，复制所有子单的完整数据（数组格式）。

### 4. 复制主单
在**主单**记录的操作列，点击"复制主单"按钮，复制该主单的完整数据。

## 技术实现

### 后端API

**路由**: `POST /api/clean-event/parse-es`

**请求体**:
```json
{
  "json_data": "<ES查询结果的JSON字符串>"
}
```

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "order_type": "主单",
      "is_main_order": true,
      "dispatch_reason": "工单派发成功",
      "event_id": 338239307,
      "event_name": "...",
      "equipment_name": "...",
      "alarm_name": "...",
      "event_time": "2026-05-04 18:43:40",
      "order_id": "FJ-076-20260505-1087",
      "full_source": { ... }
    }
  ],
  "total": 2,
  "main_count": 1,
  "sub_count": 1
}
```

### 前端组件

- **文件**: `frontend/src/views/tools/CleanEventPage.vue`
- **路由**: `/clean-event-page`
- **框架**: Vue 3 + Element Plus

## 注意事项

1. **JSON格式**: 必须是有效的ES查询结果格式，包含 `hits.hits` 数组
2. **剪贴板权限**: 现代浏览器在HTTP环境下可能限制剪贴板API，已实现降级方案（使用 `document.execCommand('copy')`）
3. **大数据量**: 如果事件数量很多（>100条），建议分批处理以避免浏览器性能问题
4. **完整数据**: 复制的内容是完整的 `_source` 对象，保留了所有原始字段

## 示例场景

### 场景1: 单个主单 + 多个子单

假设ES返回3条记录：
- 记录1: `DISPATCH_REASON = "工单派发成功"` → 主单
- 记录2: `DISPATCH_REASON = "同源合并成功"` → 子单
- 记录3: `DISPATCH_REASON = "同源合并成功"` → 子单

操作：
- 点击"复制全部" → 复制3条记录的完整数据
- 在记录2或3点击"复制所有子单" → 复制记录2和3的数据
- 在记录1点击"复制主单" → 复制记录1的数据

### 场景2: 只有子单

如果所有记录的 `DISPATCH_REASON` 都不是"工单派发成功"，则全部标记为子单。

操作：
- 点击"复制所有子单"可以一次性复制所有数据

## 更新日志

- **2026-05-06**: 
  - 新增主单/子单自动识别功能
  - 新增多种复制方式（全部、单条、所有子单、主单）
  - 优化剪贴板兼容性（支持HTTP环境）
  - 添加统计信息展示
