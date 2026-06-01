# LM Studio API 桥接服务
# 将 Claude Code 的请求转发到本地运行的 LM Studio

from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Generator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

LMSTUDIO_BASE_URL = os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234")
LMSTUDIO_API_KEY = os.getenv("LMSTUDIO_API_KEY", "sk-lm-6DRaG7rN:ZXtTmkXmVj9DBFzYGsLB")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen3.5-35b-a3b")
PROXY_PORT = int(os.getenv("PROXY_PORT", "8081"))


def parse_anthropic_tool_call(content: str) -> Dict[str, Any]:
    """
    尝试从 Anthropic 格式的响应中提取工具调用
    
    Anthropic 工具调用格式示例:
    {
        "name": "tool_name",
        "arguments": {"param": "value"}
    }
    """
    try:
        if content.startswith("{") and "name" in content and "arguments" in content:
            parsed = json.loads(content)
            if isinstance(parsed, dict) and "name" in parsed:
                return parsed
    except json.JSONDecodeError:
        pass
    return None


def format_tool_response(tool_name: str, tool_result: Any) -> Dict[str, Any]:
    """
    格式化工具调用响应为 Claude Code 期望的格式
    """
    return {
        "role": "assistant",
        "content": [
            {
                "type": "tool_result",
                "tool_name": tool_name,
                "content": json.dumps(tool_result, ensure_ascii=False)
            }
        ]
    }


def handle_streaming_response(lmstudio_response, anthropic_format: bool = True) -> Generator[str, None, None]:
    """
    处理流式响应，转换为 Claude Code 期望的格式
    """
    buffer = ""
    for chunk in lmstudio_response.iter_content(chunk_size=1024):
        if chunk:
            buffer += chunk.decode('utf-8', errors='ignore')
            
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                
                if not line or line.startswith(":"):
                    continue
                
                if line.startswith("data: "):
                    data = line[5:]
                    
                    if data == "[DONE]":
                        if anthropic_format:
                            yield "data: {\"type\":\"message_stop\"}\n\n"
                        else:
                            yield "data: [DONE]\n\n"
                        return
                    
                    try:
                        parsed = json.loads(data)
                        
                        if anthropic_format:
                            content = parsed.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if content:
                                tool_call = parse_anthropic_tool_call(content)
                                if tool_call:
                                    yield f'data: {{"type":"content_block_delta","index":0,"delta":{{"type":"tool_use","id":"toolu_0","name":"{tool_call["name"]}","input":{json.dumps(tool_call.get("arguments", {}))}}}}}\n\n'
                                else:
                                    yield f'data: {{"type":"content_block_delta","index":0,"delta":{{"type":"text","text":"{content}"}}}}\n\n'
                        else:
                            yield f"data: {data}\n\n"
                            
                    except json.JSONDecodeError:
                        if anthropic_format:
                            yield f'data: {{"type":"content_block_delta","index":0,"delta":{{"type":"text","text":"{data}"}}}}\n\n'
                        else:
                            yield f"data: {data}\n\n"


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """
    聊天补全接口 - 将 Claude Code 的请求转发到 LM Studio
    支持工具调用转换
    """
    try:
        payload = request.get_json(force=True)
        
        if "model" not in payload or not payload["model"]:
            payload["model"] = DEFAULT_MODEL

        logger.info(f"收到聊天请求，模型: {payload.get('model')}")
        logger.info(f"消息数量: {len(payload.get('messages', []))}")
        
        anthropic_format = payload.pop('anthropic_format', True)
        
        messages = payload.get('messages', [])
        lmstudio_messages = []
        system_content = ""
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                if isinstance(content, list):
                    for part in content:
                        if part.get('type') == 'text':
                            system_content += part.get('text', '') + "\n"
                else:
                    system_content += content + "\n"
                continue
            
            if role not in ['user', 'assistant']:
                tool_result_text = ""
                
                if isinstance(content, list):
                    for part in content:
                        if part.get('type') == 'tool_result':
                            tool_result_text += f"工具调用结果[{part.get('tool_name', '')}]: {part.get('content', '')}\n"
                        elif part.get('type') == 'text':
                            tool_result_text += part.get('text', '') + "\n"
                        elif isinstance(part, dict) and 'content' in part:
                            tool_result_text += str(part.get('content', '')) + "\n"
                elif isinstance(content, dict):
                    if 'content' in content:
                        tool_result_text = str(content['content'])
                    elif content.get('type') == 'tool_result':
                        tool_result_text = f"工具调用结果: {content.get('content', '')}"
                elif isinstance(content, str):
                    tool_result_text = content
                
                if tool_result_text.strip() and len(lmstudio_messages) > 0:
                    lmstudio_messages.append({
                        "role": "assistant",
                        "content": tool_result_text.strip()
                    })
                continue
            
            if isinstance(content, list):
                text_content = ""
                tool_calls = []
                
                for part in content:
                    if part.get('type') == 'text':
                        text_content += part.get('text', '')
                    elif part.get('type') == 'tool_use':
                        tool_calls.append({
                            'name': part.get('name', ''),
                            'arguments': part.get('input', {})
                        })
                
                if system_content and role == 'user' and len(lmstudio_messages) == 0:
                    text_content = f"以下是系统提示，请按照要求执行：\n{system_content}\n\n{text_content}"
                    system_content = ""
                
                if text_content:
                    lmstudio_messages.append({"role": role, "content": text_content})
                
                for tc in tool_calls:
                    lmstudio_messages.append({
                        "role": "assistant",
                        "content": json.dumps(tc)
                    })
            else:
                if system_content and role == 'user' and len(lmstudio_messages) == 0:
                    content = f"以下是系统提示，请按照要求执行：\n{system_content}\n\n{content}"
                    system_content = ""
                
                lmstudio_messages.append({"role": role, "content": content})
        
        payload['messages'] = lmstudio_messages
        
        stream = payload.get('stream', False)
        
        headers = {
            "Authorization": f"Bearer {LMSTUDIO_API_KEY}",
            "Content-Type": "application/json"
        }

        url = f"{LMSTUDIO_BASE_URL}/v1/chat/completions"
        logger.info(f"转发请求到 LM Studio: POST {url}")

        if stream:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=int(os.getenv("REQUEST_TIMEOUT", "120"))
            )
            
            return Response(
                stream_with_context(handle_streaming_response(response, anthropic_format)),
                content_type='text/event-stream'
            )
        else:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=int(os.getenv("REQUEST_TIMEOUT", "120"))
            )
            
            if anthropic_format:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                tool_call = parse_anthropic_tool_call(content)
                
                if tool_call:
                    anthropic_response = {
                        "id": result.get("id", "chatcmpl-0"),
                        "type": "message",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_0",
                                "name": tool_call["name"],
                                "input": tool_call.get("arguments", {})
                            }
                        ],
                        "model": payload["model"],
                        "stop_reason": "tool_use",
                        "usage": result.get("usage", {})
                    }
                else:
                    anthropic_response = {
                        "id": result.get("id", "chatcmpl-0"),
                        "type": "message",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": content
                            }
                        ],
                        "model": payload["model"],
                        "stop_reason": "end_turn",
                        "usage": result.get("usage", {})
                    }
                
                return jsonify(anthropic_response)
            else:
                return Response(
                    response.content,
                    status=response.status_code,
                    content_type=response.headers.get('Content-Type', 'application/json')
                )

    except json.JSONDecodeError:
        return jsonify({
            "error": {
                "message": "无效的 JSON 格式",
                "type": "invalid_request_error"
            }
        }), 400

    except requests.exceptions.Timeout:
        logger.error("请求 LM Studio 超时")
        return jsonify({
            "error": {
                "message": "请求 LM Studio 超时，请检查 LM Studio 是否正常运行",
                "type": "timeout_error"
            }
        }), 504

    except requests.exceptions.ConnectionError:
        logger.error("无法连接到 LM Studio")
        return jsonify({
            "error": {
                "message": "无法连接到 LM Studio，请确认它正在运行并监听正确的端口",
                "type": "connection_error"
            }
        }), 502

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
    try:
        payload = request.get_json(force=True)

        if "model" not in payload or not payload["model"]:
            payload["model"] = DEFAULT_MODEL

        url = f"{LMSTUDIO_BASE_URL}/v1/completions"
        headers = {
            "Authorization": f"Bearer {LMSTUDIO_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=int(os.getenv("REQUEST_TIMEOUT", "120"))
        )

        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type', 'application/json')
        )

    except Exception as e:
        logger.error(f"处理补全请求时出错: {str(e)}")
        return jsonify({
            "error": {
                "message": f"处理请求时出错: {str(e)}",
                "type": "internal_error"
            }
        }), 500


@app.route('/v1/models', methods=['GET'])
def list_models():
    try:
        url = f"{LMSTUDIO_BASE_URL}/v1/models"
        headers = {"Authorization": f"Bearer {LMSTUDIO_API_KEY}"}
        
        response = requests.get(url, headers=headers, timeout=30)
        
        result = response.json()
        
        anthropic_models = []
        for model in result.get('data', []):
            anthropic_models.append({
                "id": model.get('id', model.get('name', '')),
                "name": model.get('name', model.get('id', '')),
                "description": model.get('description', ''),
                "created": model.get('created', datetime.now().isoformat()),
                "model": model.get('id', model.get('name', '')),
                "max_tokens": model.get('max_tokens', 4096),
                "context_window": model.get('context_window', 8192),
                "type": "text_completion"
            })
        
        return jsonify({
            "data": anthropic_models,
            "object": "list"
        })
    
    except Exception as e:
        logger.error(f"获取模型列表时出错: {str(e)}")
        return jsonify({
            "error": {
                "message": f"获取模型列表失败: {str(e)}",
                "type": "internal_error"
            }
        }), 500


@app.route('/v1/models/<model_id>', methods=['GET'])
def get_model(model_id: str):
    return jsonify({
        "id": model_id,
        "name": model_id,
        "description": "Local LM Studio model",
        "created": datetime.now().isoformat(),
        "model": model_id,
        "max_tokens": 4096,
        "context_window": 8192,
        "type": "text_completion"
    })


@app.route('/health', methods=['GET'])
def health_check():
    try:
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
    return jsonify({
        "service": "LM Studio Bridge",
        "version": "1.1.0",
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
    logger.info("=" * 60)
    logger.info("🚀 LM Studio Bridge Server")
    logger.info("=" * 60)
    logger.info(f"📡 代理地址: http://0.0.0.0:{PROXY_PORT}")
    logger.info(f"🎯 LM Studio: {LMSTUDIO_BASE_URL}")
    logger.info(f"🤖 默认模型: {DEFAULT_MODEL}")
    logger.info("=" * 60)
    logger.info("\n可用接口:")
    logger.info("  POST /v1/chat/completions - 聊天补全")
    logger.info("  POST /v1/completions      - 文本补全")
    logger.info("  GET  /v1/models           - 列出模型")
    logger.info("  GET  /health              - 健康检查")
    logger.info("\n按 Ctrl+C 停止服务\n")

    app.run(host="0.0.0.0", port=PROXY_PORT, debug=False)