# config.py
import os


class Config:
    UPLOAD_FOLDER = 'uploads'
    DEMO_TEMPLATE_PATH = os.path.join(UPLOAD_FOLDER, 'valid_demo.docx')
    JSON_AS_ASCII = False


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
