# models/visit_log.py
"""
访问日志数据模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class VisitLog(db.Model):
    """访问日志表"""
    
    __tablename__ = 'visit_log'
    
    # 字段定义
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_address = db.Column(db.String(50), nullable=False, index=True, comment='IP 地址')
    user_id = db.Column(db.Integer, nullable=True, index=True, comment='用户 ID（如果已登录）')
    username = db.Column(db.String(100), nullable=True, comment='用户名')
    endpoint = db.Column(db.String(200), nullable=True, comment='访问的接口路径')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理')
    response_time = db.Column(db.Float, nullable=True, comment='响应时间（秒）')
    status_code = db.Column(db.Integer, nullable=True, comment='HTTP 状态码')
    visit_time = db.Column(db.DateTime, default=datetime.now, index=True, comment='访问时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_id': self.user_id,
            'username': self.username,
            'endpoint': self.endpoint,
            'user_agent': self.user_agent,
            'response_time': self.response_time,
            'status_code': self.status_code,
            'visit_time': self.visit_time.strftime('%Y-%m-%d %H:%M:%S') if self.visit_time else None
        }
    
    def __repr__(self):
        return f'<VisitLog {self.id}: {self.ip_address} at {self.visit_time}>'
