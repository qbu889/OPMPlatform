# models/__init__.py
"""
数据模型包
"""
# 从 fpa_category_rules 导入统一的 db 实例，避免创建多个 SQLAlchemy 实例
from models.fpa_category_rules import db

# 延迟导入，避免循环依赖
__all__ = ['db']

# 注意：具体模型类请在各模块中直接使用 db 导入
