# LM Studio API 桥接服务
# 将 Claude Code 的请求转发到本地运行的 LM Studio

from flask import Flask, request, jsonify, Response, stream_with_context
import requests
import json
import os
import logging
import re
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

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-ab5234cc03554de9b8a539b7bfbe1835")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")
USE_DEEPSEEK = os.getenv("USE_DEEPSEEK", "false").lower() == "true"


def parse_anthropic_tool_call(content: str) -> Dict[str, Any]:
    """
    尝试从 Anthropic 格式的响应中提取工具调用
    
    支持两种格式：
    1. JSON 格式:
    {
        "name": "tool_name",
        "arguments": {"param": "value"}
    }
    
    2. XML 格式 (LM Studio 模型可能输出):
    <tool_call>
    <function=B