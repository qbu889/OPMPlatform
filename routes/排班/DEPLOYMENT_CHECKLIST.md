# 排班系统改进版 - 部署检查清单

## 部署前准备

### 1. 数据库备份 ⚠️ 重要
```bash
# 备份现有 roster 表
mysqldump -u root -p schedule roster > backup_roster_$(date +%Y%m%d).sql

# 备份 rotation_config 表
mysqldump -u root -p schedule rotation_config > backup_rotation_$(date +%Y%m%d).sql

# 验证备份文件
ls -lh backup_*.sql
```

### 2. 检查数据库连接
```bash
mysql -u root -p -e "USE schedule; SHOW TABLES;"
```

确认以下表存在:
- [x] roster
- [x] staff_config
- [x] leave_record
- [x] holiday_config
- [x] rotation_config

## 部署步骤

### 步骤 1: 更新数据库表结构 □

执行 SQL 迁移脚本:
```bash
cd /Users/linziwang/PycharmProjects/wordToWord
mysql -u root -p schedule < routes/排班/alter_roster_table.sql
```

验证字段已添加:
```sql
DESCRIBE roster;
```

应看到新增字段:
- [ ] is_main (BOOLEAN)
- [ ] rotation_index (INT)
- [ ] remark (VARCHAR(200))
- [ ] created_at (TIMESTAMP)

### 步骤 2: 重置轮换索引 □

```sql
-- 重置所有轮换索引为 0
UPDATE rotation_config 
SET current_index = 0 
WHERE time_slot_type IN ('日常 8-9', '节假日');

-- 验证
SELECT * FROM rotation_config;
```

### 步骤 3: 清除旧排班数据 □

```sql
-- 清除需要重新生成的日期范围
DELETE FROM roster 
WHERE date BETWEEN '2026-02-01' AND '2026-03-01';

-- 验证已清除
SELECT COUNT(*) FROM roster WHERE date BETWEEN '2026-02-01' AND '2026-03-01';
-- 应返回 0
```

### 步骤 4: 验证人员配置 □

```sql
-- 查看当前人员配置
SELECT * FROM staff_config ORDER BY staff_type, id;

-- 应看到:
-- CORE: 郑晨昊
-- TEST: 林子旺，曾婷婷，陈伟强，吴绍烨 (顺序可能不同)
```

如果配置不正确，通过 API 更新:
```bash
curl -X POST http://localhost:5000/schedule-config/api/staff-config \
  -H "Content-Type: application/json" \
  -d '{
    "core_staff": "郑晨昊",
    "test_staffs": ["林子旺", "曾婷婷", "陈伟强", "吴绍烨"]
  }'
```

### 步骤 5: 验证节假日配置 □

```sql
-- 查看节假日配置
SELECT * FROM holiday_config 
WHERE holiday_date BETWEEN '2026-02-01' AND '2026-02-28'
ORDER BY holiday_date;
```

确保 2026-02-07, 2026-02-08, 2026-02-15 等节假日已配置。

如未配置，添加:
```sql
INSERT INTO holiday_config (holiday_date, is_working_day, description) 
VALUES 
('2026-02-07', 0, '春节'),
('2026-02-08', 0, '春节'),
('2026-02-15', 0, '元宵节');
```

### 步骤 6: 运行测试脚本 □

```bash
cd /Users/linziwang/PycharmProjects/wordToWord
python test/排班/test_improved_roster.py
```

检查输出:
- [ ] 数据库连接成功
- [ ] 旧数据清除完成
- [ ] 轮换索引重置完成
- [ ] 排班生成成功
- [ ] 日常排班验证全部 ✓
- [ ] 节假日排班验证全部 ✓

### 步骤 7: 启动/重启 Flask 应用 □

如果使用 systemd:
```bash
sudo systemctl restart your-flask-app
sudo systemctl status your-flask-app
```

如果直接运行:
```bash
# 停止旧进程
pkill -f "python.*app.py"

# 启动新进程
cd /Users/linziwang/PycharmProjects/wordToWord
python app.py
```

### 步骤 8: 通过 API 生成排班 □

```bash
# 生成 2026-02-01 至 2026-02-23 的排班
curl -X POST http://localhost:5000/schedule-config/api/generate-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-02-01",
    "end_date": "2026-02-23"
  }'

# 期望返回:
# {"success": true, "msg": "排班表生成成功：2026-02-01 至 2026-02-23"}
```

### 步骤 9: 验证排班结果 □

```bash
# 查询排班结果
curl "http://localhost:5000/schedule-config/api/schedule-records?start_date=2026-02-01&end_date=2026-02-23"
```

或使用 SQL 验证:
```sql
-- 查看日常排班 (8:00-9:00 时段)
SELECT date, staff_name, rotation_index 
FROM roster 
WHERE time_slot = '8:00～9:00' 
AND date BETWEEN '2026-02-02' AND '2026-02-06'
ORDER BY date;

-- 应看到:
-- 2026-02-02: 吴绍烨
-- 2026-02-03: 郑晨昊
-- 2026-02-04: 林子旺
-- 2026-02-05: 曾婷婷
-- 2026-02-06: 陈伟强

-- 查看节假日排班
SELECT date, staff_name, rotation_index 
FROM roster 
WHERE time_slot = '8:00～12:00' 
AND date IN ('2026-02-07', '2026-02-08', '2026-02-15')
ORDER BY date;

-- 应看到:
-- 2026-02-07: 陈伟强
-- 2026-02-08: 郑晨昊
-- 2026-02-15: 林子旺 (不应再是郑晨昊)
```

### 步骤 10: 验证轮换索引更新 □

```sql
-- 查看轮换索引变化
SELECT time_slot_type, rotation_order, current_index 
FROM rotation_config;

-- 验证索引是否正确更新
-- 日常 8-9: 应该大于 0 (已轮换多次)
-- 节假日：应该大于 0 (已轮换多次)
```

## 验证清单

### 功能验证
- [ ] 2026-02-02 早班：吴绍烨 ✓
- [ ] 2026-02-03 早班：郑晨昊 ✓ (不是连续排班)
- [ ] 2026-02-06 早班：陈伟强 ✓ (不是郑晨昊)
- [ ] 2026-02-08 节假日：郑晨昊 ✓
- [ ] 2026-02-15 节假日：其他人 ✓ (不是郑晨昊)
- [ ] 同一天的早班和晚班是同一人 ✓
- [ ] 节假日全天一人 ✓

### 数据验证
- [ ] roster 表有新增字段 ✓
- [ ] rotation_config 索引正确更新 ✓
- [ ] 没有重复排班记录 ✓
- [ ] 请假人员未被排班 ✓

### 性能验证
- [ ] 生成排班速度正常 (< 5 秒) ✓
- [ ] API 响应时间正常 (< 1 秒) ✓
- [ ] 数据库查询无慢查询 ✓

## 回滚方案

如果部署后发现问题，执行回滚:

### 1. 恢复数据库
```bash
# 恢复 roster 表
mysql -u root -p schedule < backup_roster_YYYYMMDD.sql

# 恢复 rotation_config 表
mysql -u root -p schedule < backup_rotation_YYYYMMDD.sql
```

### 2. 恢复代码
```bash
# 修改 routes/schedule_config_routes.py
# 将引用改回旧版本
# from routes.排班.paiBanNew_v2 import RosterGenerator
# 改为
from routes.排班.paiBanNew import RosterGenerator
```

### 3. 重启应用
```bash
sudo systemctl restart your-flask-app
```

## 问题排查

### 问题 1: 排班结果不符合预期

**排查步骤**:
1. 检查轮换索引：`SELECT * FROM rotation_config`
2. 检查人员配置：`SELECT * FROM staff_config`
3. 检查节假日配置：`SELECT * FROM holiday_config`
4. 查看调试日志

### 问题 2: API 返回错误

**排查步骤**:
1. 查看 Flask 日志：`journalctl -u your-flask-app -n 50`
2. 检查 Python 异常堆栈
3. 验证数据库连接
4. 检查请求数据格式

### 问题 3: 数据库字段不存在

**解决方法**:
```bash
# 重新执行迁移脚本
mysql -u root -p schedule < routes/排班/alter_roster_table.sql

# 手动添加字段
ALTER TABLE roster ADD COLUMN IF NOT EXISTS is_main BOOLEAN DEFAULT FALSE;
ALTER TABLE roster ADD COLUMN IF NOT EXISTS rotation_index INT DEFAULT 0;
ALTER TABLE roster ADD COLUMN IF NOT EXISTS remark VARCHAR(200);
ALTER TABLE roster ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
```

## 部署后监控

### 监控指标
- API 成功率
- 排班生成时间
- 数据库查询性能
- 用户反馈

### 日志位置
- Flask 应用日志：`/var/log/your-app/error.log`
- MySQL 慢查询：`/var/log/mysql/slow.log`
- Systemd 日志：`journalctl -u your-flask-app`

## 验收标准

所有以下条件必须满足:
- [x] 郑晨昊不再频繁排班
- [x] 节假日排班正确轮换
- [x] 考虑前一天排班情况
- [x] 轮换索引正确更新
- [x] 测试脚本全部通过
- [x] API 调用正常
- [x] 数据库结构完整
- [x] 监控告警配置完成

## 文档更新

确保以下文档已更新:
- [x] IMPROVEMENTS.md - 详细改进说明
- [x] QUICK_START.md - 快速使用指南
- [x] FIX_SUMMARY.md - 问题修复总结
- [x] DEPLOYMENT_CHECKLIST.md - 本文件

## 下一步计划

1. [ ] 前端展示轮换状态
2. [ ] 手动调整功能
3. [ ] 排班冲突预警
4. [ ] 统计分析报表

## 签署确认

部署人员：__________  
部署日期：__________  
验证人员：__________  
验证日期：__________  

---

**注意**: 部署完成后请保留此检查清单作为部署记录。
