# LM Studio API 桥接服务
# 将 Claude Code 的请求转发到本地运行的 LM Studio

from flask import Flask, request, jsonify, Response
import requests
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 从环境变量读取配置，提供默认值
LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "sk-lm-6DRaG7rN:ZXtTmkXmVj9DBFzYGsLB")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3.5-35b-a3b")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8081"))


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

    headers = {
        "Authorization": f"Bearer {LMSTUDIO_API_KEY}",
        "Content-Type": "application/json"
    }

    # 合并自定义 headers
    if 'headers' in kwargs:
        headers.update(kwargs.pop('headers'))

    try:
        logger.info(f"转发请求到 LM Studio: {method} {url}")

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            timeout=int(os.getenv("REQUEST_TIMEOUT", "120")),
            **kwargs
        )

        logger.info(f"LM Studio 响应状态码: {response.status_code}")

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

        # 如果没有指定模型，使用默认模型
        if "model" not in payload or not payload["model"]:
            payload["model"] = DEFAULT_MODEL

        logger.info(f"收到聊天请求，模型: {payload.get('model')}")
        logger.debug(f"消息数量: {len(payload.get('messages', []))}")

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
    print("=" * 60)
    print("\n可用接口:")
    print("  POST /v1/chat/completions - 聊天补全")
    print("  POST /v1/completions      - 文本补全")
    print("  GET  /v1/models           - 列出模型")
    print("  GET  /health              - 健康检查")
    print("\n按 Ctrl+C 停止服务\n")

    app.run(host="0.0.0.0", port=PROXY_PORT, debug=False)
