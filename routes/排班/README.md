# 排班系统改进版

## 📋 概述

本次改进修复了排班系统中的核心轮换逻辑问题，实现了智能人员轮换、请假自动过滤、前一天排班延后等功能。

## 🎯 解决的问题

### 问题 1: 日常排班连续性问题
**现象**: 郑晨昊在 2026-02-02 排班后，2026-02-03、2026-02-06 又连续排班  
**原因**: 轮换索引未正确更新，每次都从队列开头选人  
**解决**: 实现智能轮换机制，每次排班后更新索引到正确位置

### 问题 2: 节假日排班连续性问题  
**现象**: 郑晨昊在 2026-02-08 排班后，2026-02-15 又排班  
**原因**: 节假日轮换独立但未正确维护索引  
**解决**: 节假日和日常排班各自维护独立轮换队列

### 问题 3: 缺少延后处理
**现象**: 前一天排过班的人，第二天还可能继续排  
**原因**: 没有考虑前一天已排班人员  
**解决**: 查询前一天排班记录，今天自动跳过这些人

## ✨ 核心功能

### 1. 智能轮换机制
- 从当前索引开始查找可用人员
- 自动过滤请假人员
- 自动跳过前一天已排班人员
- 选中后更新索引到下一位置

### 2. 前一天排班延后
- 查询前一天 8:00-12:00 或 18:00-21:00 的排班人员
- 今天在相同时间段自动跳过
- 从轮换队列中选择下一位

### 3. 请假处理优化
- 全天请假：过滤所有时段
- 时段请假：只过滤对应时段
- 无人可排时：默认排核心人员并添加备注

### 4. 数据库增强
- 添加 `is_main` 字段标识主班
- 添加 `rotation_index` 字段记录轮换索引
- 添加 `remark` 字段记录调整原因
- 添加 `created_at` 字段记录创建时间

## 📁 文件清单

### 核心文件
```
routes/排班/
├── paiBanNew_v2.py              # 新版排班逻辑 (主要改进)
├── paiBanNew.py                 # 旧版排班逻辑 (保留参考)
├── sch.sql                      # 表结构定义 (已更新)
└── alter_roster_table.sql       # 数据库迁移脚本
```

### 文档文件
```
routes/排班/
├── README.md                    # 本文件 (总览)
├── IMPROVEMENTS.md              # 详细改进说明
├── QUICK_START.md               # 快速使用指南
├── FIX_SUMMARY.md               # 问题修复总结
└── DEPLOYMENT_CHECKLIST.md      # 部署检查清单
```

### 测试文件
```
test/排班/
└── test_improved_roster.py      # 测试验证脚本
```

### 路由文件
```
routes/
└── schedule_config_routes.py    # API 路由 (已更新引用)
```

## 🚀 快速开始

### 1. 备份数据库
```bash
mysqldump -u root -p schedule roster > backup_$(date +%Y%m%d).sql
```

### 2. 执行数据库迁移
```bash
mysql -u root -p schedule < routes/排班/alter_roster_table.sql
```

### 3. 运行测试脚本
```bash
python test/排班/test_improved_roster.py
```

### 4. 生成排班
通过 API 或界面重新生成排班

## 📊 改进效果

### 日常排班对比

**改进前**:
```
2026-02-02: 郑晨昊
2026-02-03: 郑晨昊 ❌ 连续排班
2026-02-04: 林子旺
2026-02-05: 曾婷婷
2026-02-06: 郑晨昊 ❌ 频繁排班
```

**改进后**:
```
2026-02-02: 吴绍烨 ✓
2026-02-03: 郑晨昊 ✓
2026-02-04: 林子旺 ✓
2026-02-05: 曾婷婷 ✓
2026-02-06: 陈伟强 ✓
```

### 节假日排班对比

**改进前**:
```
2026-02-07: 陈伟强
2026-02-08: 郑晨昊
2026-02-15: 郑晨昊 ❌ 重复排班
```

**改进后**:
```
2026-02-07: 陈伟强 ✓
2026-02-08: 郑晨昊 ✓
2026-02-15: 林子旺 ✓
```

## 🔧 技术实现

### 关键方法

#### 1. 智能人员选择
```python
def _select_staff_from_queue(self, slot_type, available_staffs, exclude_staffs=None):
    """从轮换队列中选择人员"""
    for i in range(n):
        idx = (current_index + i) % n
        staff = order[idx]
        if staff in available_staffs and staff not in exclude_staffs:
            new_index = (idx + 1) % n
            return staff, new_index
```

#### 2. 前一天排班查询
```python
def _get_prev_day_staff(self, target_date, time_slot_pattern):
    """获取前一天某时段的排班人员"""
```

#### 3. 索引更新
```python
def _update_rotation_to_index(self, slot_type, new_index):
    """更新轮换索引到指定位置"""
```

## 📖 详细文档

- **IMPROVEMENTS.md** - 详细的技术实现和算法说明
- **QUICK_START.md** - 快速部署和使用指南
- **FIX_SUMMARY.md** - 问题分析与修复总结
- **DEPLOYMENT_CHECKLIST.md** - 完整的部署检查清单

## ✅ 验收标准

- [x] 郑晨昊不再频繁排班
- [x] 节假日排班正确轮换
- [x] 考虑前一天排班情况
- [x] 轮换索引正确更新
- [x] 请假人员自动过滤
- [x] 测试脚本全部通过

## 🎓 使用说明

### 配置人员
```bash
curl -X POST http://localhost:5000/schedule-config/api/staff-config \
  -H "Content-Type: application/json" \
  -d '{
    "core_staff": "郑晨昊",
    "test_staffs": ["林子旺", "曾婷婷", "陈伟强", "吴绍烨"]
  }'
```

### 生成排班
```bash
curl -X POST http://localhost:5000/schedule-config/api/generate-schedule \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-02-01",
    "end_date": "2026-02-23"
  }'
```

### 查询排班
```bash
curl "http://localhost:5000/schedule-config/api/schedule-records?start_date=2026-02-01&end_date=2026-02-23"
```

## 🔄 版本信息

- **原始版本**: paiBanNew.py
- **改进版本**: paiBanNew_v2.py
- **更新日期**: 2026-03-03
- **主要改进**: 轮换逻辑、延后处理、数据库结构

## 📞 技术支持

如有问题请查看相关文档或联系开发团队。
