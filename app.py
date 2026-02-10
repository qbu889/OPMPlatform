# app.py
from datetime import datetime
from http import client

import uuid

import json
from flask import send_file
import markdown
from docx import Document
from flask import Flask, render_template, request, jsonify
import os
import logging

from openai import chat
from werkzeug.utils import secure_filename
from flask import send_from_directory
from config import config
from routes.document_routes import document_bp
from routes.excel2word_routes import excel2word_bp
from routes.kafka_routes import kafka_bp, generate_unique_fp, BASE_KAFKA_MSG
from routes.markdown_upload_routes import markdown_upload_bp
from routes.schedule_config_routes import schedule_config_bp
from routes.sql_routes import sql_bp
from routes.event_routes import event_bp
from routes.word_to_md_routes import word_to_md_bp
from utils.cleanup_thread import CleanupThread  # 导入清理线程类

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static')  # 明确指定静态文件目录
    app.config.from_object(config[config_name])
    # 确保设置了 secret key
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'your-temporary-secret-key-for-development'

    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 注册蓝图
    app.register_blueprint(document_bp)
    app.register_blueprint(sql_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(excel2word_bp)
    app.register_blueprint(markdown_upload_bp)
    app.register_blueprint(word_to_md_bp)
    app.register_blueprint(kafka_bp)  # 给Kafka蓝图添加前缀
    app.register_blueprint(schedule_config_bp)
    # 初始化并启动清理线程
    cleanup_thread = CleanupThread(app)  # 传递 Flask 应用实例
    cleanup_thread.start()

    return app


app = create_app()



@app.route('/favicon.ico')
def favicon():
 return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    """系统首页：提供步骤导航"""
    logger.info("访问系统首页")
    demo_exists = os.path.exists(app.config['DEMO_TEMPLATE_PATH'])
    logger.info(f"Demo模板存在状态: {demo_exists}")
    return render_template('index.html', demo_exists=demo_exists)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))  # 优先使用环境变量，否则默认 5004
    logger.info(f"启动Flask应用，端口: {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
