# 排班系统改进版 - 快速使用指南

## 问题修复说明

已修复的问题:
1. ✅ **日常排班连续性问题**: 郑晨昊不再频繁排班，按轮换顺序依次安排
2. ✅ **节假日排班连续性问题**: 节假日排班正确轮换，不会重复排同一人
3. ✅ **前一天排班延后处理**: 考虑前一天同时段已排班人员，今天自动延后

## 部署步骤

### 1. 更新数据库表结构

执行 SQL 迁移脚本添加备注字段:

```bash
# 方法 1: 使用命令行
mysql -u root -p schedule < routes/排班/alter_roster_table.sql

# 方法 2: 在 MySQL 客户端中直接执行
source /Users/linziwang/PycharmProjects/wordToWord/routes/排班/alter_roster_table.sql
```

### 2. 测试新的排班逻辑

运行测试脚本验证:

```bash
cd /Users/linziwang/PycharmProjects/wordToWord
python test/排班/test_improved_roster.py
```

期望输出:
- 日常排班轮换验证应全部显示 ✓
- 节假日排班轮换验证应全部显示 ✓

### 3. 配置人员 (通过 API)

```bash
curl -X POST http://localhost:5000/schedule-config/api/staff-config \
  -H "Content-Type: application/json" \
  -d '{
    "core_staff": "郑晨昊",
    "test_staffs": ["林子旺", "曾婷婷", "陈伟强", "吴绍烨"]
  }'
```

### 4. 配置节假日 (可选)

如果数据库中还没有节假日配置:

```sql
INSERT INTO holiday_config (holiday_date, is_working_day, description) 
VALUES 
('2026-02-07', 0, '春节'),
('2026-02-08', 0, '春节');
```

### 5. 生成排班

```bash
curl -X POST http://localhost:5000/schedule-config/api/generate-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-02-01",
    "end_date": "2026-02-23"
  }'
```

### 6. 查询排班结果

```bash
curl "http://localhost:5000/schedule-config/api/schedule-records?start_date=2026-02-01&end_date=2026-02-23"
```

## 核心改进点

### 1. 智能轮换机制

**旧逻辑问题**:
- 每次都从队列开头选人
- 不记录已排班人员
- 不考虑前一天排班情况

**新逻辑**:
```python
# 从当前索引开始查找可用人员
def _select_staff_from_queue(self, slot_type, available_staffs, exclude_staffs):
    for i in range(n):
        idx = (current_index + i) % n
        staff = order[idx]
        if staff in available_staffs and staff not in exclude_staffs:
            new_index = (idx + 1) % n
            return staff, new_index
```

### 2. 前一天排班延后

**规则**:
- 查询前一天 8:00-12:00 或 18:00-21:00 的排班人员
- 今天在相同时间段自动跳过这些人
- 从轮换队列中选择下一位

**示例**:
```
昨天早班：吴绍烨
今天队列：[吴绍烨，郑晨昊，林子旺，曾婷婷，陈伟强]
索引：0

选择过程:
1. 检查吴绍烨 (索引 0): 昨天排过→跳过
2. 检查郑晨昊 (索引 1): 可用→选郑晨昊
3. 更新索引：2
```

### 3. 请假处理优化

**过滤逻辑**:
```python
# 获取请假人员
leave_staffs = self._get_leave_staffs(target_date)

# 过滤后可用人员
available_staffs = [s for s in all_staffs if s not in leave_staffs]

# 从可用人员中选择
selected, new_index = self._select_staff_from_queue(
    slot_type, available_staffs, exclude_staffs
)
```

**无人可排时的默认处理**:
- 安排核心人员
- 添加备注到数据库:"因当前无可排人员默认排核心人员"

## 轮换示例

### 日常排班 (5 人轮换)

```
初始状态:
队列：[郑晨昊，林子旺，曾婷婷，陈伟强，吴绍烨]
索引：0

第 1 天 (2026-02-02):
- 选中：郑晨昊 (索引 0)
- 更新索引：1
- 次日可从：[林子旺，曾婷婷，陈伟强，吴绍烨，郑晨昊]

第 2 天 (2026-02-03):
- 从索引 1 开始：林子旺
- 但如果有排除人员 (昨天排过的),继续往后找
- 选中：吴绍烨
- 更新索引：根据选中位置计算

第 3 天 (2026-02-04):
- 继续轮换...
```

### 节假日排班 (独立轮换)

```
初始状态:
队列：[郑晨昊，林子旺，曾婷婷，陈伟强，吴绍烨]
索引：0

第 1 个节假日 (2026-02-07):
- 选中：陈伟强 (索引位置根据配置)
- 更新索引：下一个位置

第 2 个节假日 (2026-02-08):
- 从新索引开始
- 选中：郑晨昊
- 更新索引：继续往下

第 3 个节假日 (2026-02-15):
- 应该轮到其他人，不会再排郑晨昊
```

## 验证清单

生成排班后，请检查以下几点:

- [ ] 日常早班 (8:00-9:00) 每天不同人
- [ ] 日常晚班 (18:00-21:00) 与早班是同一人
- [ ] 节假日全天一人，且正确轮换
- [ ] 没有人在短时间内重复排班
- [ ] 轮换索引在每次排班后正确更新
- [ ] 请假人员没有被排班

## 调试技巧

### 1. 查看轮换索引

```sql
SELECT * FROM rotation_config;
```

### 2. 查看排班详情

```sql
SELECT date, time_slot, staff_name, rotation_index, remark
FROM roster 
WHERE date BETWEEN '2026-02-01' AND '2026-02-23'
ORDER BY date, time_slot;
```

### 3. 启用调试日志

在 `paiBanNew_v2.py` 中添加:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 在关键位置添加调试输出
debug(f"{target_date} 排班：{selected_staff}, 新索引：{new_index}")
```

## 常见问题处理

### Q1: 排班结果不符合预期

**解决步骤**:
1. 检查轮换索引是否正确：`SELECT * FROM rotation_config`
2. 清除旧数据重新生成：
   ```sql
   DELETE FROM roster WHERE date BETWEEN '开始日期' AND '结束日期';
   UPDATE rotation_config SET current_index = 0;
   ```
3. 重新运行测试脚本

### Q2: 有人频繁排班

**可能原因**:
- 轮换索引没有正确更新
- 人员配置不正确

**解决方法**:
1. 重置轮换索引
2. 检查人员配置：`SELECT * FROM staff_config`
3. 重新生成排班

### Q3: 请假人员仍被排班

**可能原因**:
- 请假记录时间格式不正确
- 时段匹配逻辑有问题

**解决方法**:
1. 检查请假记录：`SELECT * FROM leave_record`
2. 确保时间格式为 HH:MM
3. 重新生成排班

## 文件清单

改进后的核心文件:
- `routes/排班/paiBanNew_v2.py` - 新版排班逻辑
- `routes/schedule_config_routes.py` - API 路由 (已更新引用)
- `routes/排班/alter_roster_table.sql` - 数据库迁移脚本
- `test/排班/test_improved_roster.py` - 测试脚本
- `routes/排班/IMPROVEMENTS.md` - 详细改进文档

## 下一步

1. 在前端展示轮换状态
2. 添加手动调整功能
3. 实现排班冲突预警
4. 记录排班决策历史

## 技术支持

如有问题，请查看:
- 详细文档：`routes/排班/IMPROVEMENTS.md`
- 测试脚本：`test/排班/test_improved_roster.py`
- SQL 脚本:`routes/排班/alter_roster_table.sql`
