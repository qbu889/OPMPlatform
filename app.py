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
from flask_cors import CORS
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
from routes.document_convert.cosmic_routes import cosmic_bp
from routes.document_convert.es_to_excel_routes import es_to_excel_bp
from routes.document_convert.clean_event_routes import clean_event_bp

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

# Word 转 Excel 模块
from routes.word_to_excel.word_to_excel_routes import word_to_excel_bp

# 在线表格模块
from routes.spreadsheet.spreadsheet_routes import spreadsheet_bp

# 工具类
from utils.ollama_client import init_ollama_service, check_omlx_connectivity
from utils.cleanup_thread import CleanupThread
from models.fpa_category_rules import db as fpa_db
from models.visit_log import VisitLog


# ============================================================================
# 日志配置
# ============================================================================
def setup_logging():
    """
    配置日志系统（支持按等级输出）
    
    日志级别控制（通过 LOG_LEVEL 环境变量或 .env 文件配置）：
    - ERROR: 只输出 ERROR 级别日志
    - WARNING: 输出 ERROR 和 WARNING 级别日志
    - INFO: 输出 ERROR、WARNING 和 INFO 级别日志
    - DEBUG: 输出所有级别日志（包括 DEBUG）
    
    可选配置：
    - LOG_TO_CONSOLE: 是否输出到控制台（默认：True）
    - LOG_TO_FILE: 是否输出到文件（默认：True）
    - LOG_FORMAT: 日志格式（默认：详细格式）
    """
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建 logger
    logger = logging.getLogger()
    
    # 清除已有的 handler（避免重复）
    if logger.handlers:
        logger.handlers.clear()
    
    # 从环境变量获取日志级别（默认 INFO）
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)
    
    # 是否输出到控制台
    log_to_console = os.getenv('LOG_TO_CONSOLE', 'True').lower() in ('true', '1', 'yes')
    
    # 是否输出到文件
    log_to_file = os.getenv('LOG_TO_FILE', 'True').lower() in ('true', '1', 'yes')
    
    # 日志格式
    log_format = os.getenv(
        'LOG_FORMAT',
        '%(asctime)s | %(levelname)-8s | %(name)-40s | %(message)s'
    )
    date_format = os.getenv('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S')
    
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # 控制台处理器
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        app_logger_temp = logging.getLogger(__name__)
        app_logger_temp.info(f"日志已配置：输出到控制台，级别={log_level_str}")
    
    # 文件处理器
    if log_to_file:
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log'),
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        app_logger_temp = logging.getLogger(__name__)
        app_logger_temp.info(f"日志已配置：输出到文件，级别={log_level_str}")
    
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
    
    # 启用 CORS（允许跨域请求）
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 设置 secret key
    app.config['SECRET_KEY'] = 'your-temporary-secret-key-for-development'
    
    # 设置最大上传文件大小（100MB）
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
    
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
        document_bp,  # 文档转换主路由（包含 excel-to-cosmic）
        excel2word_bp,
        markdown_upload_bp,
        word_to_md_bp,
        cosmic_bp,  # 表格转 COSMIC
        es_to_excel_bp,  # ES 查询结果转 Excel
        clean_event_bp,  # 事件数据清洗
            
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
        
        # Word 转 Excel 模块（蓝图已定义前缀）
        word_to_excel_bp,
        
        # 在线表格模块（蓝图已定义前缀）
        spreadsheet_bp,
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
    # 模板上下文处理器 - 注入全局变量
    # ==========================================================================
    @app.context_processor
    def inject_user():
        """向所有模板注入 user 对象，用于导航栏显示用户信息"""
        from flask import session
        return {
            'user': {
                'logged_in': 'user_id' in session,
                'username': session.get('username', ''),
                'role': session.get('role', 'user'),
                'email': session.get('email', '')
            }
        }
    
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
# Vue 应用路由 - Catch-all for SPA
# ============================================================================
@app.route('/vue')
@app.route('/vue/<path:path>')
def vue_app(path=None):
    """
    Vue 应用入口（SPA）
    """
    return render_template('vue-app.html')


# ============================================================================
# 静态文件路由 - 上传的文件
# ============================================================================
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    from flask import send_from_directory
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(upload_dir, filename)


# ============================================================================
# 应用主入口
# ============================================================================
if __name__ == '__main__':
    import webbrowser
    import threading
    import subprocess
    
    port = int(os.environ.get("PORT", 5002))  # 优先使用环境变量,否则默认 5002
    app_logger.info(f"启动 Flask 应用，端口：{port}")
    
    # 启动 cloudflared tunnel
    def start_cloudflared_tunnel():
        """在后台线程中启动 cloudflared tunnel"""
        try:
            app_logger.info("=" * 80)
            app_logger.info(" 正在启动 Cloudflare Tunnel...")
            app_logger.info("=" * 80)
            
            # cloudflared tunnel 命令
            tunnel_command = [
                'cloudflared',
                'tunnel',
                'run',
                '--token',
                'eyJhIjoiYWM0NmFmMGQzZTViYjIyMGM4YWMyZWYxNzdlMjQxNmMiLCJ0IjoiNDRhMGJiZDQtYjhiZC00YzM4LTk2OTQtOTY4NTNmMzExZjMwIiwicyI6Ik9HUm1PRGswTmpVdFpERTVNaTAwTnpFM0xUZ3dOV0V0TmpSaFkySmlaVFExTmpoaiJ9'
            ]
            
            # 启动子进程
            process = subprocess.Popen(
                tunnel_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 读取输出
            for line in process.stderr:
                app_logger.info(f"cloudflared: {line.strip()}")
            
        except FileNotFoundError:
            app_logger.error("❌ 未找到 cloudflared 命令，请先安装 cloudflared")
            app_logger.error("   安装方法：brew install cloudflared (macOS)")
        except Exception as e:
            app_logger.error(f"❌ Cloudflare Tunnel 启动失败：{e}")
    
    # 在后台线程中启动 cloudflared tunnel
    tunnel_thread = threading.Thread(target=start_cloudflared_tunnel, daemon=True)
    tunnel_thread.start()
    app_logger.info("🔗 Cloudflare Tunnel 启动线程已启动（后台运行）")
    
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
