import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

load_dotenv()
api_key = os.environ.get('DEEPSEEK_API_KEY') or 'sk-765106feffba484aa80e3bce504a1774'

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


@app.route('/call-deepseek', methods=['POST'])
def call_deepseek_api():
    """调用 DeepSeek API 的 Flask 接口"""
    try:
        # 获取请求数据
        data = request.get_json()
        model = data.get('model', 'deepseek-chat')
        messages = data.get('messages', [])
        stream = data.get('stream', False)

        # 记录请求日志
        logger.info(f"API Request - Model: {model}, Messages count: {len(messages)}")

        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=stream
        )

        # 获取响应内容
        content = response.choices[0].message.content
        role = response.choices[0].message.role

        # 记录响应日志
        logger.info(f"API Response - Role: {role}, Content length: {len(content)}")

        # 返回响应
        return jsonify({
            "choices": [{
                "message": {
                    "content": content,
                    "role": role
                }
            }]
        }), 200

    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return jsonify({"error": str(e)}), 500