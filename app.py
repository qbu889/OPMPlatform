# app.py
"""
诺基亚 OPM 综合业务系统 - 主应用入口
=========================================
负责初始化 Flask 应用、注册蓝图、配置中间件等
"""
from datetime import datetime
import uuid
import json
import os
import sys
import logging
import threading
from http import client

from flask import Flask, render_template, request, jsonify, session, send_file, send_from_directory
from flask import redirect, url_for
import markdown
from docx import Document
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from config import config

# ============================================================================
# 导入路由蓝图（按功能模块分组）
# ============================================================================
# 文档转换模块
from routes.document_convert.document_routes import document_bp
from routes.document_convert.excel2word_routes import excel2word_bp
from routes.document_convert.markdown_upload_routes import markdown_upload_bp
from routes.document_convert.word_to_md_routes import word_to_md_bp

# 排班管理模块
from routes.schedule.schedule_config_routes import schedule_config_bp

# Kafka 模块
from routes.kafka.kafka_routes import kafka_bp
from routes.kafka.kafka_generator_routes import kafka_generator_bp

# FPA 功能点估算模块
from routes.fpa.sql_routes import sql_bp
from routes.fpa.event_routes import event_bp
from routes.fpa.fpa_generator_routes import fpa_generator_bp
# 导入异步路由模块（只注册路由，不导入函数，避免循环依赖）
from routes.fpa import fpa_async_routes
from routes.fpa.adjustment_routes import adjustment_bp
from routes.fpa.adjustment_calc_routes import adjustment_calc_bp
from routes.fpa.fpa_category_rules_routes import fpa_rules_bp
from routes.fpa.category_routes import category_bp

# 认证模块
from routes.auth.auth_routes import auth_bp

# 智能客服模块
from routes.chat.chatbot_routes import chatbot_bp

# 工具类
from utils.ollama_client import init_ollama_service, check_omlx_connectivity
from utils.cleanup_thread import CleanupThread
from models.fpa_category_rules import db as fpa_db
from models.visit_log import VisitLog


# ============================================================================
# 日志配置
# ============================================================================
def setup_logging():
    """配置日志系统（同时输出到控制台和文件）"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建 logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 清除已有的 handler（避免重复）
    if logger.handlers:
        logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)
# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 初始化日志系统
app_logger = setup_logging()


def create_app(config_name='development'):
    """
    应用工厂函数：创建并配置 Flask 应用
    
    Args:
        config_name: 配置名称 ('development', 'production', 'default')
    
    Returns:
        Flask 应用实例
    """
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 设置 secret key
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'your-temporary-secret-key-for-development'
    
    # ==========================================================================
    # 初始化数据库
    # ==========================================================================
    fpa_db.init_app(app)
    
    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 创建数据库表（如果不存在）
    with app.app_context():
        try:
            app_logger.info("正在初始化 FPA 规则数据库表...")
            fpa_db.create_all()
            app_logger.info("FPA 规则数据库表初始化完成")
        except Exception as e:
            app_logger.error(f"创建数据库表失败：{e}")
    
    # ==========================================================================
    # 注册蓝图（按功能模块分类）
    # ==========================================================================
    blueprints = [
        # 文档转换模块（蓝图已定义前缀）
        document_bp,
        excel2word_bp,
        markdown_upload_bp,
        word_to_md_bp,
            
        # 排班管理模块（蓝图已定义前缀）
        schedule_config_bp,
            
        # Kafka 模块（蓝图已定义前缀）
        # kafka_bp,  # 已注释，使用 kafka_generator_bp
        kafka_generator_bp,
            
        # FPA 模块（蓝图已定义前缀）
        sql_bp,
        event_bp,
        fpa_generator_bp,
        adjustment_bp,
        adjustment_calc_bp,
        fpa_rules_bp,
        category_bp,
            
        # 认证模块（蓝图已定义前缀）
        auth_bp,
            
        # 智能客服模块（蓝图已定义前缀）
        chatbot_bp,
    ]
        
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
    
    # ==========================================================================
    # 注册中间件
    # ==========================================================================
    @app.before_request
    def before_request():
        """记录请求开始时间"""
        import time
        request.start_time = time.time()
    
    # ==========================================================================
    # 异步初始化 AI 服务
    # ==========================================================================
    def init_omlx_async():
        """在后台线程中异步初始化 AI 服务"""
        try:
            app_logger.info("=" * 80)
            app_logger.info("🚀 正在异步初始化 AI 服务...")
            app_logger.info("=" * 80)
            
            # 初始化 OLLAMA/OMLX 客户端
            init_ollama_service()
            
            # 验证连通性（超时 10 秒）
            is_available = check_omlx_connectivity()
            
            if is_available:
                app_logger.info("✅ AI 服务验证成功！可以正常使用 AI 功能")
            else:
                app_logger.error("❌ AI 服务验证失败！请检查服务是否正常运行")
                app_logger.error("   虽然服务不可用，但应用将继续运行，AI 相关功能将受到影响")
        except Exception as e:
            app_logger.error(f"❌ AI 服务异步初始化异常：{e}")
            app_logger.error("   应用将继续运行，但 AI 功能可能不可用")
        finally:
            app_logger.info("=" * 80)
    
    # 启动后台线程进行异步初始化
    omlx_init_thread = threading.Thread(target=init_omlx_async, daemon=True)
    omlx_init_thread.start()
    app_logger.info("📡 OMLX 服务初始化线程已启动（后台运行，不阻塞应用）")
    
    # ==========================================================================
    # 启动清理线程
    # ==========================================================================
    cleanup_thread = CleanupThread(app)
    cleanup_thread.start()
    
    return app


# ============================================================================
# 创建应用实例
# ============================================================================
app = create_app('development')


# ============================================================================
# 主路由
# ============================================================================
@app.route('/')
def index():
    """
    系统首页：提供步骤导航
    """
    app_logger.info("访问系统首页")
    demo_exists = os.path.exists(app.config['DEMO_TEMPLATE_PATH'])
    app_logger.info(f"Demo 模板存在状态：{demo_exists}")
    
    # 检查用户登录状态
    user_info = {
        'logged_in': 'user_id' in session,
        'username': session.get('username', ''),
        'role': session.get('role', 'user')
    }
    
    return render_template('index.html', demo_exists=demo_exists, user=user_info)


# ============================================================================
# 应用主入口
# ============================================================================
if __name__ == '__main__':
    import webbrowser
    import threading
    
    port = int(os.environ.get("PORT", 5001))  # 优先使用环境变量，否则默认 5001
    app_logger.info(f"启动 Flask 应用，端口：{port}")
    
    # 延迟打开浏览器（等待服务器启动）
    def open_browser():
        """在服务器启动后自动打开浏览器"""
        import time
        time.sleep(2)  # 等待 2 秒确保服务器已启动
        try:
            webbrowser.open(f'http://127.0.0.1:{port}')
            app_logger.info(f"已在浏览器中打开 http://127.0.0.1:{port}")
        except Exception as e:
            app_logger.error(f"打开浏览器失败：{e}")
    
    # 在后台线程中打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    # 禁用 debug 模式以确保模块正确重新加载
    app.run(
        debug=False,
        host='0.0.0.0',
        port=port,
        threaded=True  # 启用多线程处理
    )
