# 排班系统设计文档

## 📋 系统概述

排班系统是一个基于规则的自动化排班解决方案，支持日常和节假日两种不同排班模式，具备请假管理、人员轮换、冲突检测等功能。

**技术架构：**
- **前端**: Vue 3 + Element Plus (单页应用)
- **后端**: Flask Blueprint API
- **数据库**: MySQL (schedule 数据库)
- **定时推送**: APScheduler + 钉钉机器人

## 👥 人员配置

### 核心人员结构
- **核心主班人员**: 郑晨昊（默认）
- **测试人员**: 林子旺、曾婷婷、陈伟强、吴绍烨（默认）
- **总人员**: 5人团队

### 人员类型与配置表
```sql
-- staff_config 表结构
CREATE TABLE staff_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(50) NOT NULL,  -- 人员姓名
    staff_type VARCHAR(20) NOT NULL,  -- CORE(核心) / TEST(测试)
    sort_order INT DEFAULT 0,         -- 排序顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 动态人员配置
系统从 `staff_config` 表动态读取人员配置，支持运行时修改：
- **CORE 类型**: 核心主班人员，通常担任上午班主班
- **TEST 类型**: 测试人员，参与轮换和辅助工作
- **全部人员**: TEST + CORE 组合

## ⏰ 时段配置

### 日常工作日时段（周一至周五，非节假日）
| 时段 | 说明 | 排班规则 |
|------|------|----------|
| 8:00～9:00 | 早班第一时段 | 1人轮换（与18:00～21:00同一人） |
| 9:00～12:00 | 上午班时段 | 主班1人 + 辅班3人 |
| 13:30～18:00 | 下午班时段 | 全员参与（除请假人员） |
| 18:00～21:00 | 晚班时段 | 1人轮换（与8:00～9:00同一人） |

### 节假日时段（周末及法定节假日）
| 时段 | 说明 | 排班规则 |
|------|------|----------|
| 8:00～12:00 | 上午班 | 1人轮换 |
| 13:30～17:30 | 下午班 | 同上午班人员 |
| 17:30～21:30 | 晚班 | 同上午班人员 |

**注意**: 节假日三个时段由同一人负责全天值班。

## 🔄 排班核心逻辑

### 1. 日期类型判断
系统通过以下方式判断日期类型：
- **优先查询** `holiday_config` 表中的配置
  - `is_working_day = 1`: 日常工作日
  - `is_working_day = 0`: 节假日
- **若表中无记录**，则根据周末判断（周六、周日为节假日）

```python
def _get_date_type(self, target_date: date) -> str:
    # 查询 holiday_config 表
    sql = "SELECT is_working_day FROM holiday_config WHERE holiday_date = %s"
    result = self.db.query(sql, (target_date.strftime('%Y-%m-%d'),))
    
    if result:
        return "日常" if result[0]["is_working_day"] == 1 else "节假日"
    
    # 无记录则判断周末
    weekday = target_date.weekday()
    return "节假日" if weekday >= 5 else "日常"
```

### 2. 轮换配置机制

#### 轮换配置表结构
```sql
CREATE TABLE rotation_config (
    time_slot_type VARCHAR(20) PRIMARY KEY,  -- 轮换类型：'日常 8-9' / '节假日'
    rotation_order TEXT NOT NULL,            -- 轮换顺序（逗号分隔的姓名列表）
    current_index INT DEFAULT 0,             -- 当前轮换索引位置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 轮换类型
1. **日常 8-9**: 控制日常 8:00～9:00 和 18:00～21:00 时段的轮换
2. **节假日**: 控制节假日所有时段的轮换

#### 轮换更新逻辑
```python
def _update_rotation_to_index(self, slot_type: str, new_index: int):
    """更新轮换索引到指定位置"""
    # 更新内存缓存
    self.rotation_config[slot_type]["index"] = new_index
    # 同步更新数据库
    sql = "UPDATE rotation_config SET current_index = %s WHERE time_slot_type = %s"
    self.db.execute(sql, (new_index, slot_type))
```

### 3. 避让规则（核心算法）

#### 日常排班避让规则
- **早班避让**: 前一天晚班（18:00～21:00 或 17:30～21:30）人员，今天不参与 8:00～9:00 轮换
- **实现方式**: 从轮换队列中排除前一天晚班人员，顺延选择下一位

#### 节假日排班避让规则
- **早班避让**: 前一天早班（8:00～12:00）人员，今天不参与轮换
- **实现方式**: 从轮换队列中排除前一天早班人员，顺延选择下一位

#### 通用避让逻辑
```python
def _select_staff_from_queue(self, slot_type, available_staffs, exclude_staffs=None):
    """从轮换队列中选择人员，自动跳过排除人员"""
    rotation = self.rotation_config[slot_type]
    order = rotation["order"]
    current_index = rotation["index"]
    
    # 从当前索引开始遍历，找到第一个未被排除且可用的人员
    n = len(order)
    for i in range(n):
        idx = (current_index + i) % n
        staff = order[idx]
        if staff in available_staffs and staff not in exclude_staffs:
            new_index = (idx + 1) % n  # 选中后索引指向下一位
            return staff, new_index
    
    # 无人可选时的兜底逻辑
    return available_staffs[0] if available_staffs else None, current_index
```

### 4. 请假处理逻辑

#### 请假类型
1. **全天请假**: `is_full_day = TRUE`，该人员全天不参与任何时段排班
2. **时段请假**: `is_full_day = FALSE` + 具体时间段，仅在该时段不参与排班

#### 请假数据表
```sql
CREATE TABLE leave_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(50) NOT NULL,
    leave_date DATE NOT NULL,
    start_time TIME,                    -- 时段请假开始时间
    end_time TIME,                      -- 时段请假结束时间
    is_full_day BOOLEAN DEFAULT FALSE,  -- 是否全天请假
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 请假处理流程
```python
def _get_leave_staffs(self, target_date: date, time_slot: str = None) -> Set[str]:
    """获取指定日期/时段的请假人员"""
    leave_staffs = set()
    
    # 1. 查询全天请假人员
    sql_all = "SELECT staff_name FROM leave_record WHERE leave_date = %s AND is_full_day = TRUE"
    all_leave = self.db.query(sql_all, (target_date,))
    leave_staffs.update([item["staff_name"] for item in all_leave])
    
    # 2. 查询时段请假人员（时间重叠判断）
    if time_slot:
        start_str, end_str = time_slot.split("～")
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()
        
        sql_slot = """
        SELECT staff_name FROM leave_record 
        WHERE leave_date = %s AND is_full_day = FALSE 
        AND start_time <= %s AND end_time >= %s
        """
        slot_leave = self.db.query(sql_slot, (target_date, start, end))
        leave_staffs.update([item["staff_name"] for item in slot_leave])
    
    return leave_staffs
```

### 5. 日常排班生成流程

```python
def _get_daily_roster(self, target_date: date) -> List[Dict]:
    """生成日常排班数据"""
    roster_list = []
    
    # 步骤1: 获取当日请假人员
    all_leave_staffs = self._get_leave_staffs(target_date)
    available_staffs = [s for s in self.all_staffs if s not in all_leave_staffs]
    
    # 步骤2: 生成备注信息（如有请假）
    remark = f"因请假调整（{', '.join(all_leave_staffs)}）" if all_leave_staffs else None
    
    # 步骤3: 8:00～9:00 和 18:00～21:00 轮换（同一人）
    prev_evening_staff = self._get_prev_day_staff(target_date, "evening")  # 前一天晚班人员
    selected_staff, new_index = self._select_staff_from_queue(
        "日常 8-9", available_staffs, prev_evening_staff
    )
    
    if selected_staff:
        # 两个时段安排同一人
        roster_list.append({"date": target_date, "time_slot": "8:00～9:00", 
                          "staff_name": selected_staff, "is_main": False, "remark": remark})
        roster_list.append({"date": target_date, "time_slot": "18:00～21:00", 
                          "staff_name": selected_staff, "is_main": False, "remark": remark})
        self._update_rotation_to_index("日常 8-9", new_index)  # 更新轮换索引
    else:
        # 无人可用，默认核心人员
        roster_list.append(...{"staff_name": self.core_staff, ...})
    
    # 步骤4: 9:00～12:00 主辅班制
    main_staff = self.core_staff if self.core_staff not in leave_9_12 else None
    if not main_staff:
        # 核心请假，从测试人员中选主班
        main_staff = next((s for s in self.test_staffs if s not in leave_9_12), None)
    
    if main_staff:
        roster_list.append({"date": target_date, "time_slot": "9:00～12:00",
                          "staff_name": main_staff, "is_main": True, "remark": remark})
        
        # 辅班：从测试人员中选3人（排除主班）
        aux_candidates = [s for s in self.test_staffs 
                         if s not in leave_9_12 and s != main_staff]
        for aux in aux_candidates[:3]:
            roster_list.append({"date": target_date, "time_slot": "9:00～12:00",
                              "staff_name": aux, "is_main": False, "remark": remark})
    
    # 步骤5: 13:30～18:00 全员参与
    available_afternoon = [s for s in available_staffs if s not in leave_13_18]
    for staff in available_afternoon:
        roster_list.append({"date": target_date, "time_slot": "13:30～18:00",
                          "staff_name": staff, "is_main": False, "remark": remark})
    
    return roster_list
```

### 6. 节假日排班生成流程

```python
def _get_holiday_roster(self, target_date: date) -> List[Dict]:
    """生成节假日排班数据（一天一人轮流）"""
    roster_list = []
    
    # 步骤1: 获取当日请假人员
    all_leave_staffs = self._get_leave_staffs(target_date)
    available_staffs = [s for s in rotation_holiday["order"] if s not in all_leave_staffs]
    
    # 步骤2: 获取前一天早班人员（需避让）
    prev_morning_staff = self._get_prev_day_staff(target_date, "morning")
    
    # 步骤3: 选择轮换人员
    if available_staffs:
        selected_staff, new_index = self._select_staff_from_queue(
            "节假日", available_staffs, prev_morning_staff
        )
        self._update_rotation_to_index("节假日", new_index)
    else:
        # 无人可用，默认核心人员
        selected_staff = self.core_staff
    
    # 步骤4: 为三个时段安排同一人
    remark = f"因请假调整（{', '.join(all_leave_staffs)}）" if all_leave_staffs else None
    for slot in ["8:00～12:00", "13:30～17:30", "17:30～21:30"]:
        roster_list.append({"date": target_date, "time_slot": slot,
                          "staff_name": selected_staff, "is_main": False, "remark": remark})
    
    return roster_list
```

### 7. 排班生成主流程

```python
def generate_roster(self, start_date: date, end_date: date):
    """生成指定日期范围的排班表"""
    # 步骤1: 初始化轮换配置（从数据库加载）
    self.rotation_config = self._load_rotation_config()
    
    # 步骤2: 删除已有排班数据（避免重复）
    delete_sql = "DELETE FROM roster WHERE date BETWEEN %s AND %s"
    self.db.execute(delete_sql, (start_date, end_date))
    
    # 步骤3: 遍历每一天生成排班
    current_date = start_date
    while current_date <= end_date:
        # 判断日期类型
        date_type = self._get_date_type(current_date)
        
        # 生成对应排班数据
        if date_type == "日常":
            daily_roster = self._get_daily_roster(current_date)
            self._save_roster(daily_roster)
        else:  # 节假日
            holiday_roster = self._get_holiday_roster(current_date)
            self._save_roster(holiday_roster)
        
        current_date += timedelta(days=1)
    
    print(f"排班表生成成功：{start_date} 至 {end_date}")
```

## 📅 轮换机制

### 轮换配置表结构
```sql
CREATE TABLE rotation_config (
    time_slot_type VARCHAR(20),     # 时段类型
    rotation_order TEXT,            # 轮换顺序（逗号分隔）
    current_index INT               # 当前轮换索引
);
```

### 轮换类型
1. **日常8-9轮换**: 8:00～9:00和18:00～21:00时段
2. **节假日轮换**: 节假日所有时段

### 轮换更新逻辑
```python
def _update_rotation_index(self, slot_type: str):
    # 索引+1，超出人数时重置为0
    new_index = (current_index + 1) % len(rotation_order)
```

## 🚫 请假管理

### 请假类型
1. **全天请假**: `is_full_day = TRUE`
2. **时段请假**: `is_full_day = FALSE` + 具体时间段

### 请假数据表
```sql
CREATE TABLE leave_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(50) NOT NULL,
    leave_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    is_full_day BOOLEAN DEFAULT FALSE
);
```

### 请假处理逻辑
```python
def _get_leave_staffs(self, target_date: date, time_slot: str = None):
    # 1. 查询全天请假人员
    # 2. 查询时段请假人员（根据时间段匹配）
    # 3. 返回请假人员集合
```

## 🎯 核心算法流程

### 排班生成主流程
```python
def generate_roster(self, start_date: date, end_date: date):
    1. 初始化轮换配置
    2. 遍历每一天：
       a. 判断日期类型（日常/节假日）
       b. 生成对应排班数据
       c. 写入数据库
       d. 更新轮换索引
```

### 日常排班生成
```python
def _get_daily_roster(self, target_date: date):
    1. 获取当日请假人员
    2. 生成8:00～9:00和18:00～21:00排班（同一人）
    3. 生成9:00～12:00排班（主辅班制）
    4. 生成13:30～18:00排班（全员参与）
```

### 节假日排班生成
```python
def _get_holiday_roster(self, target_date: date):
    1. 获取当日请假人员
    2. 从轮换队列中选择可用人员
    3. 为所有节假日时段安排同一人
    4. 更新轮换索引
```

## 🗄️ 数据库设计

### 主要数据表

#### 1. 排班表 (roster)
```sql
CREATE TABLE roster (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,              -- 排班日期
    time_slot VARCHAR(20) NOT NULL,  -- 时间段
    staff_name VARCHAR(50) NOT NULL, -- 员工姓名
    is_main BOOLEAN DEFAULT FALSE,   -- 是否为主班（仅9:00～12:00使用）
    remark VARCHAR(200),             -- 备注（如请假调整说明）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_date (date),
    INDEX idx_date_slot (date, time_slot)
);
```

#### 2. 人员配置表 (staff_config)
```sql
CREATE TABLE staff_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(50) NOT NULL,  -- 人员姓名
    staff_type VARCHAR(20) NOT NULL,  -- CORE(核心) / TEST(测试)
    sort_order INT DEFAULT 0,         -- 排序顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_staff_name (staff_name)
);
```

#### 3. 请假记录表 (leave_record)
```sql
CREATE TABLE leave_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    staff_name VARCHAR(50) NOT NULL,
    leave_date DATE NOT NULL,
    start_time TIME,                   -- 时段请假开始时间
    end_time TIME,                     -- 时段请假结束时间
    is_full_day BOOLEAN DEFAULT FALSE, -- 是否全天请假
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_staff_date (staff_name, leave_date),
    INDEX idx_date (leave_date)
);
```

#### 4. 轮换配置表 (rotation_config)
```sql
CREATE TABLE rotation_config (
    time_slot_type VARCHAR(20) PRIMARY KEY,  -- '日常 8-9' / '节假日'
    rotation_order TEXT NOT NULL,            -- 轮换顺序（逗号分隔）
    current_index INT DEFAULT 0,             -- 当前索引位置
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 5. 节假日配置表 (holiday_config)
```sql
CREATE TABLE holiday_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    holiday_date DATE NOT NULL,     -- 节假日日期
    is_working_day BOOLEAN,         -- 1=工作日, 0=节假日
    description VARCHAR(100),       -- 描述（如"春节"、"国庆"）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_holiday_date (holiday_date)
);
```

#### 6. 钉钉定时推送配置表 (dingtalk_schedule_config)
```sql
CREATE TABLE dingtalk_schedule_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    webhook_url TEXT NOT NULL,       -- 加密后的 Webhook URL
    time_slots JSON,                 -- 推送时段列表（JSON数组）
    schedule_times JSON,             -- 推送时间点（如["08:00", "09:00", "18:00"]）
    enabled BOOLEAN DEFAULT TRUE,    -- 是否启用
    description VARCHAR(200),        -- 配置描述
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## ⚙️ 系统配置

### 环境变量配置
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=12345678
DB_NAME=schedule
```

### 默认配置
- **字符集**: utf8mb4
- **时区**: 系统默认时区
- **连接池**: 单连接模式

## 🔧 API接口

### 基础路径
所有接口前缀: `/schedule-config`

### 人员配置接口
- **GET** `/api/staff-config` - 获取人员配置
- **POST** `/api/staff-config` - 更新人员配置

### 请假管理接口
- **GET** `/api/leave-records?start_date=&end_date=` - 获取请假记录
- **POST** `/api/leave-records` - 添加请假记录
- **DELETE** `/api/leave-records` - 删除请假记录

### 排班生成与查询接口
- **POST** `/api/generate-schedule` - 生成排班表
  ```json
  {"start_date": "2026-03-01", "end_date": "2026-03-31"}
  ```
- **GET** `/api/schedule-records?start_date=&end_date=` - 查询排班记录
- **GET** `/api/check-existing-roster?start_date=&end_date=` - 检查现有排班
- **POST** `/api/delete-existing-roster` - 删除指定日期范围排班

### CSV导入接口
- **POST** `/api/import-schedule` - 上传CSV文件解析（返回预览）
- **POST** `/api/confirm-import-schedule` - 确认导入排班数据

### 钉钉推送接口
- **POST** `/api/send-dingtalk-message` - 手动推送排班信息
  ```json
  {
    "start_date": "2026-03-01",
    "end_date": "2026-03-02",
    "time_slots": ["8:00～9:00", "9:00～12:00"],
    "dingtalk_webhook": "加密后的webhook地址"
  }
  ```
- **GET** `/api/dingtalk-schedule-config` - 获取定时推送配置
- **POST** `/api/dingtalk-schedule-config` - 保存定时推送配置
- **DELETE** `/api/dingtalk-schedule-config/<id>` - 删除定时推送配置

### Vue前端兼容接口
- **GET** `/api/list?page=1&size=10` - 分页获取排班列表
- **POST** `/api/create` - 创建排班（预留）
- **PUT** `/api/<schedule_id>` - 更新排班（预留）

## 📊 排班示例

### 日常排班示例
```
日期: 2026-03-01 (周一)
8:00～9:00   - 林子旺 (轮换)
9:00～12:00  - 郑晨昊 (主班) + 曾婷婷、陈伟强、吴绍烨 (辅班)
13:30～18:00 - 郑晨昊、林子旺、曾婷婷、陈伟强、吴绍烨 (全员)
18:00～21:00 - 林子旺 (轮换)

日期: 2026-03-02 (周二) - 避让林子旺（前一天早班）
8:00～9:00   - 曾婷婷 (轮换，避让林子旺)
9:00～12:00  - 郑晨昊 (主班) + 林子旺、陈伟强、吴绍烨 (辅班，避让前一天上午班的郑晨昊)
13:30～18:00 - 郑晨昊、林子旺、曾婷婷、陈伟强、吴绍烨 (全员)
18:00～21:00 - 曾婷婷 (轮换)
```

### 节假日排班示例
```
日期: 2026-03-02 (周二，节假日) - 避让曾婷婷（前一天上午班）
8:00～12:00   - 林子旺 (轮换，避让曾婷婷)
13:30～17:30  - 林子旺 (轮换)
17:30～21:30  - 林子旺 (轮换)

日期: 2026-03-03 (周三，节假日) - 避让林子旺（前一天早班）
8:00～12:00   - 陈伟强 (轮换，避让林子旺)
13:30～17:30  - 陈伟强 (轮换)
17:30～21:30  - 陈伟强 (轮换)
```

## 🛡️ 异常处理

### 数据完整性保障
- 请假冲突检测
- 人员重复安排检查
- 数据库事务回滚机制

### 错误处理
- 数据库连接失败处理
- SQL执行异常捕获
- 参数验证和边界检查

## 🚀 使用说明

### 1. 环境准备

#### 数据库初始化
```bash
# 创建数据库和表结构
mysql -u root -p < routes/排班/sch.sql
```

#### 环境变量配置
```env
# .env 文件
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=schedule
WEBHOOK_ENCRYPTION_KEY=auto_generated_or_custom_key
```

### 2. 启动服务

#### 后端服务
```bash
# 启动 Flask 应用
python app.py
# 或使用开发模式
./start_all_dev.sh
```

#### 前端服务
```bash
cd frontend
npm install
npm run dev
```

### 3. 初始配置

#### 配置人员
访问前端页面 → 人员配置标签页：
- 设置核心人员（默认：郑晨昊）
- 添加测试人员（默认：林子旺、曾婷婷、陈伟强、吴绍烨）
- 点击"保存人员配置"

#### 配置节假日
在 `holiday_config` 表中插入节假日数据：
```sql
-- 示例：2026年春节
INSERT INTO holiday_config (holiday_date, is_working_day, description) VALUES
('2026-02-17', 0, '春节'),
('2026-02-18', 0, '春节'),
('2026-02-19', 0, '春节');
```

### 4. 生成排班

#### 方法1: 通过前端界面
1. 访问排班配置页面
2. 切换到"生成排班"标签页
3. 选择开始日期和结束日期
4. 点击"生成排班"按钮

#### 方法2: 通过API调用
```bash
curl -X POST http://localhost:5000/schedule-config/api/generate-schedule \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2026-03-01", "end_date": "2026-03-31"}'
```

### 5. 管理请假

#### 添加请假
```bash
curl -X POST http://localhost:5000/schedule-config/api/leave-records \
  -H "Content-Type: application/json" \
  -d '{
    "staff_name": "林子旺",
    "start_date": "2026-03-15",
    "end_date": "2026-03-15",
    "is_full_day": true
  }'
```

#### 时段请假
```json
{
  "staff_name": "曾婷婷",
  "start_date": "2026-03-16",
  "end_date": "2026-03-16",
  "is_full_day": false,
  "start_time": "09:00",
  "end_time": "12:00"
}
```

### 6. 导出与推送

#### 导出排班表
前端页面 → 排班查询 → 点击"导出"按钮，下载CSV文件

#### 钉钉推送
1. 配置钉钉机器人 Webhook（前端→钉钉推送配置）
2. 设置推送时段（如 08:00, 09:00, 18:00）
3. 系统自动定时推送，或手动点击"钉钉推送"按钮

### 7. CSV导入

#### 导入格式
```csv
日期,星期,时段,人员,备注
2026-03-01,周一,8:00～9:00,林子旺,
2026-03-01,周一,9:00～12:00,郑晨昊、林子旺、曾婷婷、陈伟强,
```

#### 导入步骤
1. 前端页面 → 排班查询 → 点击"导入CSV"
2. 上传CSV文件，系统解析并显示预览
3. 确认无误后点击"确认导入"

## 📈 扩展性考虑

### 可扩展功能
1. **多班组支持**: 支持多个独立班组
2. **技能匹配**: 根据人员技能分配岗位
3. **自动通知**: 排班生成后自动通知相关人员
4. **统计报表**: 生成排班统计和考勤报表
5. **移动端支持**: 开发移动端查看和申请请假
6. **智能避让**: 基于历史排班数据的智能避让优化
7. **连续工作限制**: 设置人员连续工作天数上限
8. **避让规则可视化**: 图形化展示避让规则执行情况
9. **违规预警**: 实时检测和预警避让规则 violations
10. **自定义避让策略**: 支持配置不同的避让规则策略

### 性能优化建议
1. 数据库索引优化
2. 批量数据处理
3. 缓存常用配置数据
4. 异步任务处理大量排班生成