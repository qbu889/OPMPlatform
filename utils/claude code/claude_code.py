# LM Studio API 桥接服务
# 将 Claude Code 的请求转发到本地运行的 LM Studio

from flask import Flask, request, jsonify, Response
import requests
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

# 配置日志 - 同时输出到文件和控制台
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 按日期生成日志文件名
log_file = os.path.join(log_dir, f'lmstudio_bridge_{datetime.now().strftime("%Y%m%d")}.log')

# 创建 logger
logger = logging.getLogger('lmstudio_bridge')
logger.setLevel(logging.INFO)

# 文件处理器 - 详细日志
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(file_formatter)

# 控制台处理器 - 简洁日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

app = Flask(__name__)

# 从环境变量读取配置，提供默认值
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "sk-lm-6DRaG7rN:ZXtTmkXmVj9DBFzYGsLB")
# DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3.5-35b-a3b")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3-coder-30b-a3b-instruct-mlx")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8081"))


@app.before_request
def log_request():
    """记录每个请求的详细信息"""
    request.start_time = datetime.now()
    logger.info(f"\n{'='*60}")
    logger.info(f"收到请求: {request.method} {request.path}")
    logger.info(f"来源 IP: {request.remote_addr}")
    logger.info(f"User-Agent: {request.headers.get('User-Agent', 'Unknown')[:100]}")
    
    # 记录请求体大小
    content_length = request.content_length
    if content_length:
        logger.info(f"请求体大小: {content_length} bytes")


@app.after_request
def log_response(response):
    """记录响应信息"""
    if hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        logger.info(f"响应状态: {response.status_code}")
        logger.info(f"处理耗时: {duration:.3f}s")
        logger.info(f"{'='*60}\n")
    return response


def forward_request(endpoint: str, method: str = "POST", **kwargs) -> Response:
    """
    通用请求转发函数

    Args:
        endpoint: LM Studio API 端点路径（如 /v1/chat/completions）
        method: HTTP 方法
        **kwargs: 传递给 requests 的其他参数

    Returns:
        Flask Response 对象
    """
    url = f"{LMSTUDIO_BASE_URL}{endpoint}"
    
    logger.info(f"准备转发请求:")
    logger.info(f"  - 目标 URL: {url}")
    logger.info(f"  - 请求方法: {method}")

    headers = {
        "Authorization": f"Bearer {LMSTUDIO_API_KEY}",
        "Content-Type": "application/json"
    }

    # 合并自定义 headers
    if 'headers' in kwargs:
        headers.update(kwargs.pop('headers'))

    try:
        logger.info(f"发送请求到 LM Studio...")
        request_start = datetime.now()

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=int(os.getenv("REQUEST_TIMEOUT", "120")),
            **kwargs
        )
        
        request_duration = (datetime.now() - request_start).total_seconds()
        logger.info(f"LM Studio 响应:")
        logger.info(f"  - 状态码: {response.status_code}")
        logger.info(f"  - 响应时间: {request_duration:.3f}s")
        logger.info(f"  - 响应大小: {len(response.content)} bytes")

        # 返回原始响应
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )

    except requests.exceptions.Timeout:
        logger.error(f"请求超时: {url}")
        return jsonify({
            "error": {
                "message": "请求 LM Studio 超时，请检查 LM Studio 是否正常运行",
                "type": "timeout_error"
            }
        }), 504

    except requests.exceptions.ConnectionError:
        logger.error(f"连接失败: {url}，请确认 LM Studio 正在运行")
        return jsonify({
            "error": {
                "message": "无法连接到 LM Studio，请确认它正在运行并监听正确的端口",
                "type": "connection_error"
            }
        }), 502

    except Exception as e:
        logger.error(f"转发请求时发生错误: {str(e)}")
        return jsonify({
            "error": {
                "message": f"内部服务器错误: {str(e)}",
                "type": "internal_error"
            }
        }), 500


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    聊天补全接口 - 将 Claude Code 的请求转发到 LM Studio
    """
    try:
        payload = request.get_json(force=True)
        
        # 记录关键请求信息（不记录完整消息内容，避免日志过大）
        model_name = payload.get('model', '未指定')
        messages_count = len(payload.get('messages', []))
        has_stream = payload.get('stream', False)
        
        logger.info(f"聊天请求详情:")
        logger.info(f"  - 模型: {model_name}")
        logger.info(f"  - 消息数量: {messages_count}")
        logger.info(f"  - 流式输出: {has_stream}")
        
        # 如果有 system message，记录其长度
        messages = payload.get('messages', [])
        if messages and messages[0].get('role') == 'system':
            system_msg_len = len(messages[0].get('content', ''))
            logger.info(f"  - System 消息长度: {system_msg_len} 字符")

        # 如果没有指定模型，使用默认模型
        if "model" not in payload or not payload["model"]:
            payload["model"] = DEFAULT_MODEL
            logger.info(f"使用默认模型: {DEFAULT_MODEL}")

        logger.info(f"转发请求到 LM Studio...")

        return forward_request('/v1/chat/completions', json=payload)

    except json.JSONDecodeError:
        return jsonify({
            "error": {
                "message": "无效的 JSON 格式",
                "type": "invalid_request_error"
            }
        }), 400

    except Exception as e:
        logger.error(f"处理聊天请求时出错: {str(e)}")
        return jsonify({
            "error": {
                "message": f"处理请求时出错: {str(e)}",
                "type": "internal_error"
            }
        }), 500


@app.route('/v1/completions', methods=['POST'])
def completions():
    """
    文本补全接口
    """
    try:
        payload = request.get_json(force=True)

        if "model" not in payload or not payload["model"]:
            payload["model"] = DEFAULT_MODEL

        return forward_request('/v1/completions', json=payload)

    except Exception as e:
        logger.error(f"处理补全请求时出错: {str(e)}")
        return jsonify({
            "error": {
                "message": f"处理请求时出错: {str(e)}",
                "type": "internal_error"
            }
        }), 500


@app.route('/v1/models/<model_id>', methods=['GET'])
def get_model(model_id: str):
    """
    获取特定模型信息
    """
    return forward_request(f'/v1/models/{model_id}', method='GET')


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    """
    try:
        # 尝试连接 LM Studio
        response = requests.get(
            f"{LMSTUDIO_BASE_URL}/v1/models",
            headers={"Authorization": f"Bearer {LMSTUDIO_API_KEY}"},
            timeout=5
        )

        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "lmstudio": "connected",
                "timestamp": datetime.now().isoformat(),
                "lmstudio_url": LMSTUDIO_BASE_URL
            }), 200
        else:
            return jsonify({
                "status": "degraded",
                "lmstudio": f"unreachable (status: {response.status_code})",
                "timestamp": datetime.now().isoformat()
            }), 503

    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "lmstudio": f"error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 503


@app.route('/', methods=['GET'])
def index():
    """
    服务信息页面
    """
    return jsonify({
        "service": "LM Studio Bridge",
        "version": "1.0.0",
        "description": "将 Claude Code 请求转发到 LM Studio 的桥接服务",
        "endpoints": [
            "POST /v1/chat/completions - 聊天补全",
            "POST /v1/completions - 文本补全",
            "GET /v1/models - 列出模型",
            "GET /v1/models/<model_id> - 获取模型信息",
            "GET /health - 健康检查"
        ],
        "config": {
            "lmstudio_url": LMSTUDIO_BASE_URL,
            "default_model": DEFAULT_MODEL,
            "port": PROXY_PORT
        }
    })


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 LM Studio Bridge Server")
    print("=" * 60)
    print(f"📡 代理地址: http://0.0.0.0:{PROXY_PORT}")
    print(f"🎯 LM Studio: {LMSTUDIO_BASE_URL}")
    print(f"🤖 默认模型: {DEFAULT_MODEL}")
    print(f"📝 日志文件: {log_file}")
    print("=" * 60)
    print("\n可用接口:")
    print("  POST /v1/chat/completions - 聊天补全")
    print("  POST /v1/completions      - 文本补全")
    print("  GET  /v1/models           - 列出模型")
    print("  GET  /health              - 健康检查")
    print("\n按 Ctrl+C 停止服务\n")
    
    logger.info("="*60)
    logger.info("LM Studio Bridge 服务启动")
    logger.info(f"监听地址: 0.0.0.0:{PROXY_PORT}")
    logger.info(f"LM Studio: {LMSTUDIO_BASE_URL}")
    logger.info(f"默认模型: {DEFAULT_MODEL}")
    logger.info(f"日志文件: {log_file}")
    logger.info("="*60)

    app.run(host="0.0.0.0", port=PROXY_PORT, debug=False)
