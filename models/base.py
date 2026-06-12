from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

# 初始化基础模型类
Base = declarative_base()

class BaseORM(Base):
    """所有业务数据库模型的基类。"""
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=date.today)
    updated_at = Column(DateTime, default=date.today)

# ---------------------------------------------------------
# 【模拟核心表结构 - 需要与数据库连接对接】
# ---------------------------------------------------------

class SoftwareIpMap(BaseORM):
    """对应 tbl_software_ip_map 表，用于存储软件、IP和人员信息。"""
    __tablename__ = 'tbl_software_ip_map'
    software_name = Column(String, primary_key=True) # 软件名称作为主键
    target_ips = Column(String)                     # 目标IP列表，逗号分隔
    operator = Column(String)                         # 操作人员
    validator = Column(String)                        # 验证人员

class InitialVersion(BaseORM):
    """对应 tbl_initial_version 表，用于存储软件的初始基准版本。"""
    __tablename__ = 'tbl_initial_version'
    software_name = Column(String, primary_key=True) # 软件名称作为主键
    initial_version = Column(String)                 # 例如: "1.4.6"

class ParsingHistory(BaseORM):
    """对应 tbl_parsing_history 表，用于审计和记录历史结果。"""
    __tablename__ = 'tbl_parsing_history'
    record_id = Column(String, primary_key=True)     # 唯一批次流水号
    software_name = Column(String)
    parse_date = Column(DateTime)                     # 解析完成的日期
    final_version = Column(String)
    status = Column(String)                             # 例如: 'SUCCESS', 'FAILED'

# TODO: 其他业务相关的模型 (如 Task, User 等...) 将在此处添加。
