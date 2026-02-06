# roster 表：存储每日排班信息
CREATE TABLE roster (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    date DATE NOT NULL COMMENT '排班日期',
    time_slot VARCHAR(20) NOT NULL COMMENT '时间段',
    staff_name VARCHAR(50) NOT NULL COMMENT '员工姓名'
) COMMENT='存储每日排班信息';

# holiday_config 表：存储法定节假日配置（包括是否上班）
CREATE TABLE holiday_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    holiday_date DATE NOT NULL COMMENT '节假日日期',
    is_working_day BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为工作日',
    description VARCHAR(100) COMMENT '节假日描述',
    wage INT DEFAULT 1 COMMENT '薪资倍数',
    after BOOLEAN DEFAULT FALSE COMMENT '是否为补班日',
    target VARCHAR(100) COMMENT '关联的节假日名称',
    rest INT COMMENT '距离下一个假期的天数'
) COMMENT='存储法定节假日配置';

# leave_record 表：记录人员请假信息（支持时间段或整天）
CREATE TABLE leave_record (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    staff_name VARCHAR(50) NOT NULL COMMENT '员工姓名',
    leave_date DATE NOT NULL COMMENT '请假日期',
    start_time TIME COMMENT '请假开始时间',
    end_time TIME COMMENT '请假结束时间',
    is_full_day BOOLEAN NOT NULL DEFAULT FALSE COMMENT '是否为全天请假'
) COMMENT='记录人员请假信息';


SHOW CREATE TABLE holiday_config;
