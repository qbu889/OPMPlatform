# app.py
from datetime import datetime
from http import client

from flask import send_file
import markdown
from docx import Document
from flask import Flask, render_template, request, jsonify
import os
import logging

from werkzeug.utils import secure_filename

from config import config
from routes.document_routes import document_bp
from routes.excel2word_routes import excel2word_bp
from routes.markdown_upload_routes import markdown_upload_bp
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

    # 初始化并启动清理线程
    cleanup_thread = CleanupThread(app)  # 传递 Flask 应用实例
    cleanup_thread.start()

    return app


app = create_app()


@app.route('/')
def index():
    """系统首页：提供步骤导航"""
    logger.info("访问系统首页")
    demo_exists = os.path.exists(app.config['DEMO_TEMPLATE_PATH'])
    logger.info(f"Demo模板存在状态: {demo_exists}")
    return render_template('index.html', demo_exists=demo_exists)


@app.route('/upload-demo-page')
def upload_demo_page():
    """跳转Demo上传页面"""
    logger.info("访问Demo上传页面")
    return render_template('demo_upload.html', success=False, msg='')

@app.route('/chat')
def chat_page():
    """提供聊天页面访问"""
    now = datetime.now()
    return render_template('chat.html', now=now)

if __name__ == '__main__':
    logger.info("启动Flask应用")
    app.run(debug=True, host='0.0.0.0', port=5002)
