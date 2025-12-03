# app.py
from flask import Flask, render_template
import os
import logging
from config import config
from routes.document_routes import document_bp
from routes.sql_routes import sql_bp
from routes.event_routes import event_bp

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 注册蓝图
    app.register_blueprint(document_bp)
    app.register_blueprint(sql_bp)
    app.register_blueprint(event_bp)

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


if __name__ == '__main__':
    logger.info("启动Flask应用")
    app.run(debug=True, host='0.0.0.0', port=5001)
