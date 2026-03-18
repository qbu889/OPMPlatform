 # app.py
from datetime import datetime
from http import client
import uuid
import json
from flask import send_file
import markdown
from docx import Document
from flask import Flask, render_template, request, jsonify, session
import os
import logging
from dotenv import load_dotenv

 # 加载 .env 文件
load_dotenv()

# from openai import chat
from werkzeug.utils import secure_filename
from flask import send_from_directory
from config import config

# 导入路由蓝图
from routes.document_convert.document_routes import document_bp
from routes.document_convert.excel2word_routes import excel2word_bp
from routes.document_convert.markdown_upload_routes import markdown_upload_bp
from routes.document_convert.word_to_md_routes import word_to_md_bp
from routes.schedule.schedule_config_routes import schedule_config_bp
from routes.kafka.kafka_routes import kafka_bp
from routes.kafka.kafka_generator_routes import kafka_generator_bp
from routes.fpa.sql_routes import sql_bp
from routes.fpa.event_routes import event_bp
from routes.auth.auth_routes import auth_bp
from routes.chat.chatbot_routes import chatbot_bp
from routes.fpa.category_routes import category_bp
from routes.fpa.fpa_generator_routes import fpa_generator_bp
from routes.fpa.adjustment_routes import adjustment_bp
from routes.fpa.adjustment_calc_routes import adjustment_calc_bp
from routes.fpa.fpa_category_rules_routes import fpa_rules_bp
from utils.ollama_client import init_ollama_service, check_omlx_connectivity  # 导入 OMLX 服务初始化工具
from utils.cleanup_thread import CleanupThread  # 导入清理线程类
from models.fpa_category_rules import db as fpa_db  # 导入 FPA 规则数据库实例
from models.visit_log import VisitLog  # 导入访问日志模型（暂时不使用）


# 配置日志 - 统一日志格式（同时输出到控制台和文件）
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

# 获取应用 logger
app_logger = logging.getLogger(__name__)

# 确保models目录存在
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static')  # 明确指定静态文件目录
    app.config.from_object(config[config_name])
    # 确保设置了 secret key
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'your-temporary-secret-key-for-development'
    
    # 初始化 FPA 规则数据库
    fpa_db.init_app(app)
    
    # 访问日志功能暂时不启用（需要配置主数据库实例）

    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 创建数据库表（如果不存在）
    with app.app_context():
        try:
            logger.info("正在初始化 FPA 规则数据库表...")
            fpa_db.create_all()
            logger.info("FPA 规则数据库表初始化完成")
        except Exception as e:
            logger.error(f"创建数据库表失败：{e}")

    # 注册蓝图
    app.register_blueprint(document_bp)
    app.register_blueprint(sql_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(excel2word_bp)
    app.register_blueprint(markdown_upload_bp)
    app.register_blueprint(word_to_md_bp)
    # app.register_blueprint(kafka_bp)  # 给 Kafka 蓝图添加前缀
    app.register_blueprint(schedule_config_bp)
    app.register_blueprint(kafka_generator_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chatbot_bp)  # 注册智能客服蓝图
    app.register_blueprint(category_bp)  # 注册专业领域管理蓝图
    app.register_blueprint(fpa_generator_bp)  # 注册 FPA 预估表生成器蓝图
    app.register_blueprint(adjustment_bp)  # 注册调整因子管理蓝图
    app.register_blueprint(adjustment_calc_bp)  # 注册调整因子计算器蓝图
    app.register_blueprint(fpa_rules_bp)  # 注册 FPA 类别规则管理蓝图
        
    # 访问记录中间件（暂时禁用）
    # @app.after_request
    # def log_visit(response):
    #     """记录访问日志"""
    #     try:
    #         from flask import request
    #         import time
    #         
    #         # 计算响应时间
    #         start_time = getattr(request, 'start_time', time.time())
    #         response_time = time.time() - start_time
    #         
    #         # 获取客户端 IP
    #         ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    #         
    #         # 获取用户信息
    #         user_id = None
    #         username = None
    #         try:
    #             from flask import session
    #             if 'user_id' in session:
    #                 user_id = session.get('user_id')
    #                 username = session.get('username')
    #         except:
    #             pass
    #         
    #         # 创建访问记录
    #         visit = VisitLog(
    #             ip_address=ip_address,
    #             user_id=user_id,
    #             username=username,
    #             endpoint=request.endpoint,
    #             user_agent=request.headers.get('User-Agent', ''),
    #             response_time=response_time,
    #             status_code=response.status_code
    #         )
    #         
    #         visit_db.session.add(visit)
    #         visit_db.session.commit()
    #     except Exception as e:
    #         logger.error(f"记录访问日志失败：{e}")
    #         visit_db.session.rollback()
    #     
    #     return response
    
    # 记录请求开始时间
    @app.before_request
    def before_request():
        """记录请求开始时间"""
        from flask import request
        import time
        request.start_time = time.time()
        
    # 系统统计 API（暂时禁用）
    # @app.route('/api/statistics')
    # def get_statistics():
    #     """获取系统统计数据"""
    #     from flask import jsonify
    #     from sqlalchemy import func, distinct
    #     from datetime import datetime, timedelta
    #     
    #     try:
    #         # 获取今天的开始时间
    #         today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    #         # 获取本周的开始时间（周一）
    #         week_start = today_start - timedelta(days=today_start.weekday())
    #         
    #         # 今日处理量
    #         today_count = VisitLog.query.filter(
    #             VisitLog.visit_time >= today_start
    #         ).count()
    #         
    #         # 本周活跃用户数（去重）
    #         week_users = VisitLog.query.filter(
    #             VisitLog.visit_time >= week_start,
    #             VisitLog.user_id.isnot(None)
    #         ).with_entities(distinct(VisitLog.user_id)).count()
    #         
    #         # 平均响应时间（最近 100 次请求）
    #         recent_visits = VisitLog.query.order_by(
    #             VisitLog.visit_time.desc()
    #         ).limit(100).all()
    #         
    #         avg_response_time = 0
    #         if recent_visits:
    #             response_times = [v.response_time for v in recent_visits if v.response_time is not None]
    #             if response_times:
    #                 avg_response_time = sum(response_times) / len(response_times)
    #         
    #         return jsonify({
    #             'success': True,
    #             'data': {
    #                 'today_count': today_count,
    #                 'week_users': week_users,
    #                 'avg_response_time': round(avg_response_time, 2)
    #             }
    #         })
    #     except Exception as e:
    #         logger.error(f"获取统计数据失败：{e}")
    #         return jsonify({
    #             'success': False,
    #             'error': str(e)
    #         }), 500

    # 在后台异步初始化 OMLX 服务（不阻塞应用启动）
    def init_omlx_async():
        """异步初始化 AI 服务（在后台线程中执行）"""
        try:
            logger.info("=" * 80)
            logger.info("🚀 正在异步初始化 AI 服务...")
            logger.info("=" * 80)
                
            # 初始化 OLLAMA/OMLX 客户端（从环境变量读取配置）
            init_ollama_service()
                
            # 验证连通性（超时 10 秒）
            is_available = check_omlx_connectivity()
                
            if is_available:
                logger.info("✅ AI 服务验证成功！可以正常使用 AI 功能")
            else:
                logger.error("❌ AI 服务验证失败！请检查服务是否正常运行")
                logger.error("   虽然服务不可用，但应用将继续运行，AI 相关功能将受到影响")
        except Exception as e:
            logger.error(f"❌ AI 服务异步初始化异常：{e}")
            logger.error("   应用将继续运行，但 AI 功能可能不可用")
        finally:
            logger.info("=" * 80)
        
    # 启动后台线程进行异步初始化
    import threading
    omlx_init_thread = threading.Thread(target=init_omlx_async, daemon=True)
    omlx_init_thread.start()
    logger.info("📡 OMLX 服务初始化线程已启动（后台运行，不阻塞应用）")
    
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
    logger.info(f"Demo 模板存在状态：{demo_exists}")
    
    # 检查用户登录状态
    from flask import session
    user_info = {
        'logged_in': 'user_id' in session,
        'username': session.get('username', ''),
        'role': session.get('role', 'user')
    }
    
    return render_template('index.html', demo_exists=demo_exists, user=user_info)
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5001))  # 优先使用环境变量，否则默认 5002
    logger.info(f"启动 Flask 应用，端口：{port}")
    # 禁用 debug 模式以确保模块正确重新加载
    app.run(debug=False, host='0.0.0.0', port=port)
