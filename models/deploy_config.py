"""
部署配置模型
"""
from datetime import datetime
from models import db


class DeployConfig(db.Model):
    """部署配置表模型"""
    
    __tablename__ = 'deploy_config'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=False)
    config_type = db.Column(db.String(20), default='string')
    description = db.Column(db.String(500))
    category = db.Column(db.String(50), default='general', index=True)
    is_sensitive = db.Column(db.Boolean, default=False)
    updated_by = db.Column(db.Integer)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self, hide_sensitive=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value if not (hide_sensitive and self.is_sensitive) else '***',
            'config_type': self.config_type,
            'description': self.description,
            'category': self.category,
            'is_sensitive': self.is_sensitive,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
        }
        return data
    
    def get_typed_value(self):
        """获取类型化的配置值"""
        if self.config_type == 'number':
            try:
                return int(self.config_value)
            except ValueError:
                try:
                    return float(self.config_value)
                except ValueError:
                    return 0
        elif self.config_type == 'boolean':
            return self.config_value.lower() in ('true', '1', 'yes')
        elif self.config_type == 'json':
            import json
            try:
                return json.loads(self.config_value)
            except:
                return {}
        else:
            return self.config_value
    
    @staticmethod
    def get_config(key, default=None):
        """
        获取配置值（静态方法，方便调用）
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值（已转换为对应类型）
        """
        config = DeployConfig.query.filter_by(config_key=key).first()
        if config:
            return config.get_typed_value()
        return default
    
    @staticmethod
    def set_config(key, value, updated_by=None):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
            updated_by: 更新人ID
        """
        config = DeployConfig.query.filter_by(config_key=key).first()
        if config:
            config.config_value = str(value)
            if updated_by:
                config.updated_by = updated_by
            config.updated_at = datetime.utcnow()
            db.session.commit()
        else:
            new_config = DeployConfig(
                config_key=key,
                config_value=str(value),
                updated_by=updated_by
            )
            db.session.add(new_config)
            db.session.commit()
    
    @staticmethod
    def get_all_configs(category=None, hide_sensitive=True):
        """
        获取所有配置
        
        Args:
            category: 配置分类过滤
            hide_sensitive: 是否隐藏敏感信息
            
        Returns:
            配置列表
        """
        query = DeployConfig.query
        if category:
            query = query.filter_by(category=category)
        
        configs = query.order_by(DeployConfig.category, DeployConfig.config_key).all()
        return [config.to_dict(hide_sensitive=hide_sensitive) for config in configs]
