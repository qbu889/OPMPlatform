# config.py
import os


class Config:
    UPLOAD_FOLDER = 'uploads'
    DEMO_TEMPLATE_PATH = os.path.join(UPLOAD_FOLDER, 'valid_demo.docx')
    JSON_AS_ASCII = False
    
    # MySQL 数据库配置（全局）
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '12345678')
    MYSQL_CHARSET = os.getenv('MYSQL_CHARSET', 'utf8mb4')
    
    # 各业务数据库名称
    KNOWLEDGE_BASE_DB = os.getenv('KNOWLEDGE_BASE_DB', 'knowledge_base')
    AUTH_DB = os.getenv('AUTH_DB', 'auth_system')
    SCHEDULE_DB = os.getenv('SCHEDULE_DB', 'schedule_system')


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
