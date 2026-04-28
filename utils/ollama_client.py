#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama AI 客户端工具类
封装本地 Ollama AI 模型的 API 调用
"""
import os
import requests
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Generator
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama AI 客户端"""
    
    def __init__(self, base_url: str = None, model: str = None, use_omlx: bool = False):
        """
        初始化 Ollama 客户端
        
        Args:
            base_url: Ollama API 基础 URL
            model: 默认使用的模型名称（如果为 None 则从.env 读取）
            use_omlx: 是否使用 OMLX 模型（Qwen3.5-4B-OptiQ-4bit）
        """
        # 显式加载 .env 文件
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv()
            logger.debug(f"[OLLAMA_ENV] 已加载 .env 文件：{env_path.absolute()}")
        
        # 根据 use_omlx 参数选择配置源
        if use_omlx:
            # 使用 OMLX 模型配置
            self.base_url = (base_url or os.getenv("OMLX_BASE_URL", "https://omlx.cn")).rstrip('/')
            self.model = (model or os.getenv("OMLX_MODEL", "Qwen3.5-4B-OptiQ-4bit"))
            logger.info(f"[OLLAMA_INIT] 使用 OMLX 配置 - URL: {self.base_url}, Model: {self.model}")
        else:
            # 使用本地 Ollama 配置
            self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL"))
            if not self.base_url:
                # 如果环境变量未设置，使用默认值
                self.base_url = "http://localhost:11434"
            self.model = (model or os.getenv("OLLAMA_MODEL", "qwen3:4b"))
            logger.info(f"[OLLAMA_INIT] 使用本地 Ollama 配置 - URL: {self.base_url}, Model: {self.model}")
        
        # 移除末尾的斜杠
        self.base_url = self.base_url.rstrip('/')
        
        # 先保存 use_omlx 参数
        self.use_omlx = use_omlx
        
        # 根据 use_omlx 选择 API 端点
        if self.use_omlx:
            # OMLX 使用 OpenAI 兼容接口
            self.api_endpoint = f"{self.base_url}/chat/completions"
            self.chat_endpoint = f"{self.base_url}/chat/completions"
            logger.info(f"[OLLAMA_INIT] OMLX 模式 - 使用 OpenAI 兼容接口：{self.api_endpoint}")
        else:
            # 本地 Ollama 使用原生接口
            self.api_endpoint = f"{self.base_url}/api/generate"
            self.chat_endpoint = f"{self.base_url}/api/chat"
            logger.info(f"[OLLAMA_INIT] 本地 Ollama 模式 - 使用原生接口：{self.api_endpoint}")
        
        # 创建 requests session，复用连接
        self.session = requests.Session()
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Ollama-Client/1.0'
        })
        
        logger.info(f"[OLLAMA_INIT] 初始化 - URL: {self.base_url}, Model: {self.model}, OMLX: {self.use_omlx}")
        
        # 快速检查服务是否可用（不阻塞）
        if not self._quick_check():
            logger.warning(f"[OLLAMA_INIT] 服务可能不可用，将在首次请求时报错")
    
    def _quick_check(self) -> bool:
        """快速检查服务是否可用（超时 2 秒）"""
        try:
            if self.use_omlx:
                # OMLX 使用 OpenAI 兼容接口，检查 /v1/models
                response = requests.get(f"{self.base_url}/models", timeout=2, headers={"Authorization": "Bearer 666666"})
                return response.status_code == 200
            else:
                # 本地 Ollama 使用原生接口，检查 /api/tags
                response = requests.get(f"{self.base_url}/api/tags", timeout=2)
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"[OLLAMA_CHECK] 服务检查失败：{e}")
            return False
    
    def _validate_model(self):
        """验证模型是否存在，如果不存在则尝试切换到可用模型"""
        try:
            available_models = self.list_models()
            if not available_models:
                logger.warning(f"[OLLAMA_INIT] 无法获取模型列表，使用默认模型：{self.model}")
                return
            
            if self.model not in available_models:
                # 模型不存在，尝试找最接近的
                logger.warning(f"[OLLAMA_INIT] 模型 '{self.model}' 不存在！")
                logger.info(f"[OLLAMA_INIT] 可用模型：{', '.join(available_models)}")
                
                # 优先选择 qwen3 系列或 qwen:1.8b
                for fallback in ['qwen:1.8b', 'qwen3:4b', 'qwen3:8b', 'qwen3:14b', 'qwen3']:
                    if fallback in available_models:
                        logger.info(f"[OLLAMA_INIT] 自动切换到可用模型：{fallback}")
                        self.model = fallback
                        return
                
                # 如果都没有，使用第一个可用模型
                if available_models:
                    self.model = available_models[0]
                    logger.warning(f"[OLLAMA_INIT] 使用第一个可用模型：{self.model}")
            else:
                logger.info(f"[OLLAMA_INIT] 模型验证成功：{self.model}")
        except Exception as e:
            logger.error(f"[OLLAMA_INIT] 模型验证失败：{e}")
        
    def generate(self, 
                 prompt: str, 
                 model: Optional[str] = None,
                 system: Optional[str] = None,
                 stream: bool = False,
                 options: Optional[Dict] = None,
                 retry: int = None) -> str:
        """
        生成文本回复（支持 Ollama 和 OMLX 两种 API）
        
        Args:
            prompt: 输入提示词
            model: 模型名称（可选，默认使用实例的 model）
            system: 系统提示
            stream: 是否流式输出
            options: 其他配置选项
            retry: 重试次数（默认从环境变量 OLLAMA_MAX_RETRIES 读取，默认 3 次）
            
        Returns:
            生成的文本内容
        """
        # 从环境变量读取重试次数，如果未传入
        if retry is None:
            retry = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
        
        attempt = 0
        last_error = None
        
        while attempt <= retry:
            try:
                # 根据 use_omlx 选择不同的 API 格式
                if self.use_omlx:
                    # OMLX 使用 OpenAI 兼容接口
                    payload = {
                        "model": model or self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "stream": stream
                    }
                    if system:
                        payload["messages"].insert(0, {"role": "system", "content": system})
                    if options:
                        payload.update(options)
                else:
                    # 本地 Ollama 使用原生接口
                    payload = {
                        "model": model or self.model,
                        "prompt": prompt,
                        "stream": stream
                    }
                    if system:
                        payload["system"] = system
                    if options:
                        payload["options"] = options
                
                # 添加详细日志，诊断问题
                logger.info(f"[OLLAMA_REQUEST] URL: {self.api_endpoint}")
                logger.info(f"[OLLAMA_REQUEST] Model: {model or self.model}")
                logger.info(f"[OLLAMA_REQUEST] Prompt length: {len(prompt)} chars")
                logger.info(f"[OLLAMA_REQUEST] Attempt: {attempt + 1}/{retry + 1}")
                
                # 如果使用的是 OMLX，特别标注
                if self.use_omlx:
                    logger.info(f"[OMLX_REQUEST] 🌐 正在请求 OMLX 在线模型...")
                    logger.info(f"[OMLX_REQUEST]    - Base URL: {self.base_url}")
                    logger.info(f"[OMLX_REQUEST]    - Model: {self.model}")
                    logger.info(f"[OMLX_REQUEST]    - Endpoint: /v1/chat/completions (OpenAI compatible)")
                else:
                    logger.info(f"[OLLAMA_LOCAL] 💻 正在请求本地 Ollama 模型...")
                    logger.info(f"[OLLAMA_LOCAL]    - Endpoint: /api/generate (Ollama native)")
                
                # 生成对应的 CURL 命令用于调试
                import json as json_module
                curl_cmd = f'curl -X POST "{self.api_endpoint}" \\'
                curl_cmd += f'\n  -H "Content-Type: application/json" \\'
                if self.use_omlx:
                    curl_cmd += f'\n  -H "Authorization: Bearer 666666" \\'
                json_payload = json_module.dumps(payload, ensure_ascii=False)
                curl_cmd += f'\n  -d \'{json_payload}\''
                logger.info(f"[OLLAMA_CURL]\n{curl_cmd}")
                
                # 实际请求时也要添加 API Key（仅 OMLX）
                headers = {}
                if self.use_omlx:
                    headers['Authorization'] = 'Bearer 666666'
                
                response = self.session.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers,
                    stream=stream,
                    timeout=1200  # 增加到 20 分钟超时，避免大文档处理超时
                )
                
                # 如果是 404，记录详细信息
                if response.status_code == 404:
                    logger.error(f"[OLLAMA_404] Endpoint not found: {self.api_endpoint}")
                    logger.error(f"[OLLAMA_404] Payload: {payload}")
                    logger.error(f"[OLLAMA_404] Response headers: {dict(response.headers)}")
                
                response.raise_for_status()
                
                if stream:
                    return self._parse_stream_response(response)
                else:
                    result = response.json()
                    # 根据 API 类型解析不同的响应格式
                    if self.use_omlx:
                        # OpenAI 兼容格式
                        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    else:
                        # Ollama 原生格式
                        return result.get("response", "")
                        
            except requests.exceptions.ConnectionError as e:
                last_error = e
                attempt += 1
                if attempt <= retry:
                    wait_time = 2 ** attempt * 3  # 指数退避：6, 12, 24, 48, 96 秒
                    logger.warning(f"[OLLAMA_CONNECTION_ERROR] 连接失败，{wait_time}秒后重试 (Attempt {attempt}/{retry + 1}): {e}")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"[OLLAMA_GENERATE] 连接失败，已达最大重试次数：{e}")
                    raise Exception(f"AI 服务连接失败：{str(e)}")
            except requests.exceptions.HTTPError as e:
                # 处理 HTTP 错误（包括 502、503、504、400 等服务器错误）
                last_error = e
                attempt += 1
                
                # 详细记录错误响应，帮助诊断问题
                logger.error(f"[OLLAMA_HTTP_ERROR] ❌ HTTP 错误 {response.status_code}")
                logger.error(f"[OLLAMA_HTTP_ERROR]    URL: {self.api_endpoint}")
                logger.error(f"[OLLAMA_HTTP_ERROR]    Method: POST")
                logger.error(f"[OLLAMA_HTTP_ERROR]    Status: {response.status_code} {response.reason}")
                
                # 尝试读取响应内容
                try:
                    error_response = response.json()
                    logger.error(f"[OLLAMA_HTTP_ERROR]    Error Response: {json.dumps(error_response, ensure_ascii=False, indent=2)}")
                except:
                    error_text = response.text[:500]
                    logger.error(f"[OLLAMA_HTTP_ERROR]    Error Text: {error_text}")
                
                # 记录请求的 payload（前 1000 字符）
                logger.error(f"[OLLAMA_HTTP_ERROR]    Request Payload (preview): {str(payload)[:1000]}...")
                
                if attempt <= retry:
                    wait_time = 2 ** attempt * 3  # 指数退避：6, 12, 24, 48, 96 秒
                    logger.warning(f"[OLLAMA_HTTP_ERROR] {wait_time}秒后重试 (Attempt {attempt}/{retry + 1})")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"[OLLAMA_GENERATE] HTTP 错误，已达最大重试次数：{e}")
                    raise Exception(f"AI 服务不可用：{str(e)}")
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.error(f"[OLLAMA_GENERATE] Failed: {e}")
                raise Exception(f"AI 服务不可用：{str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"[OLLAMA_JSON] Parse error: {e}")
                raise Exception("AI 响应格式错误")
        
        # 不应该到这里，但为了类型安全
        raise Exception(f"AI 服务不可用：{str(last_error)}")
    
    def chat(self,
             messages: List[Dict[str, str]],
             model: Optional[str] = None,
             stream: bool = False,
             options: Optional[Dict] = None,
             retry: int = None) -> str:
        """
        聊天对话（支持多轮对话）
        
        Args:
            messages: 消息列表，每条消息包含 role 和 content
                     role 可以是 'system', 'user', 'assistant'
            model: 模型名称
            stream: 是否流式输出
            options: 其他配置选项
            retry: 重试次数（默认从环境变量 OLLAMA_MAX_RETRIES 读取，默认 3 次）
            
        Returns:
            AI 助手的回复内容
        """
        # 从环境变量读取重试次数，如果未传入
        if retry is None:
            retry = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
        
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": stream
        }
        
        if options:
            payload["options"] = options
        
        attempt = 0
        last_error = None
        
        while attempt <= retry:
            try:
                logger.info(f"[OLLAMA_CHAT] URL: {self.chat_endpoint}")
                logger.info(f"[OLLAMA_CHAT] Model: {model or self.model}")
                logger.info(f"[OLLAMA_CHAT] Messages: {len(messages)}条")
                logger.info(f"[OLLAMA_CHAT] Attempt: {attempt + 1}/{retry + 1}")
                
                response = self.session.post(
                    self.chat_endpoint,
                    json=payload,
                    stream=stream,
                    timeout=300  # 增加到 5 分钟
                )
                
                # 如果是 404 错误，尝试切换到 generate API
                if response.status_code == 404 and 'messages' in payload:
                    logger.warning(f"[OLLAMA_CHAT_404] /api/chat not found, trying /api/generate")
                    return self._chat_via_generate(messages, model)
                
                response.raise_for_status()
                
                if stream:
                    return self._parse_stream_response(response)
                else:
                    result = response.json()
                    return result.get("message", {}).get("content", "")
                    
            except requests.exceptions.ConnectionError as e:
                last_error = e
                attempt += 1
                if attempt <= retry:
                    wait_time = 2 ** attempt  # 指数退避
                    logger.warning(f"[OLLAMA_CHAT_CONNECTION_ERROR] 连接失败，{wait_time}秒后重试 (Attempt {attempt}/{retry + 1}): {e}")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"[OLLAMA_CHAT_FAILED] 连接失败，已达最大重试次数：{e}")
                    raise Exception(f"AI 服务连接失败：{str(e)}")
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.warning(f"[OLLAMA_CHAT_RETRY] Attempt {attempt + 1}/{retry + 1} failed: {e}")
                attempt += 1
                if attempt <= retry:
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                continue
            except json.JSONDecodeError as e:
                logger.error(f"[OLLAMA_CHAT_JSON] Parse error: {e}")
                raise Exception("AI 响应格式错误")
        
        logger.error(f"[OLLAMA_CHAT_FAILED] Max retries ({retry}) exceeded: {last_error}")
        raise Exception(f"AI 服务不可用：{str(last_error)}")
    
    def _chat_via_generate(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """
        通过 generate API 实现 chat 功能（备用方案）
        """
        # 将 messages 转换为单个 prompt
        prompt_parts = []
        system_prompt = ""
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                system_prompt = content
            elif role == 'user':
                prompt_parts.append(f"User: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        full_prompt = '\n'.join(prompt_parts)
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{full_prompt}"
        
        return self.generate(full_prompt, model=model)
    
    def _parse_stream_response(self, response) -> str:
        """解析流式响应"""
        full_content = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    content = data.get("response", "") or data.get("message", {}).get("content", "")
                    full_content += content
                except json.JSONDecodeError:
                    continue
        return full_content
    
    def list_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            if self.use_omlx:
                # OMLX 使用 OpenAI 兼容接口，获取 /v1/models
                response = requests.get(f"{self.base_url}/models", timeout=10, headers={"Authorization": "Bearer 666666"})
                response.raise_for_status()
                data = response.json()
                # OpenAI 格式：{"data": [{"id": "model1"}, ...]}
                models = [model.get("id") for model in data.get("data", [])]
                logger.info(f"[OLLAMA_MODELS] OMLX 模型列表：{models}")
                return models
            else:
                # 本地 Ollama 使用原生接口，获取 /api/tags
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                response.raise_for_status()
                data = response.json()
                # Ollama 格式：{"models": [{"name": "model1"}, ...]}
                models = [model.get("name") for model in data.get("models", [])]
                logger.info(f"[OLLAMA_MODELS] Ollama 模型列表：{models}")
                return models
        except Exception as e:
            logger.error(f"[OLLAMA_MODELS] Failed to get model list: {e}")
            return []
    
    def is_available(self) -> bool:
        """检查 Ollama 服务是否可用"""
        try:
            if self.use_omlx:
                # OMLX 使用 OpenAI 兼容接口，检查 /v1/models
                response = requests.get(f"{self.base_url}/models", timeout=5, headers={"Authorization": "Bearer 666666"})
                return response.status_code == 200
            else:
                # 本地 Ollama 使用原生接口，检查 /api/tags
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                return response.status_code == 200
        except Exception as e:
            logger.debug(f"[OLLAMA_AVAILABLE] 服务可用性检查失败：{e}")
            return False


# 全局客户端实例（延迟初始化）
_ollama_client = None
_omlx_client = None  # OMLX 专用客户端


def init_ollama_service(use_omlx: bool = None) -> OllamaClient:
    """
    初始化 OMLX/Ollama 服务（在应用启动时调用）
    
    Args:
        use_omlx: 是否使用 OMLX 模型（如果为 None，则从环境变量 USE_OMLX_FOR_CHATBOT 读取）
        
    Returns:
        OllamaClient 实例
    """
    global _omlx_client, _ollama_client
    
    # 如果没有显式传入参数，从环境变量读取
    if use_omlx is None:
        use_omlx = os.getenv("USE_OMLX_FOR_CHATBOT", "true").lower() == "true"
        logger.info(f"[OLLAMA_INIT_SERVICE] 从环境变量读取 USE_OMLX_FOR_CHATBOT={use_omlx}")
    
    try:
        if use_omlx:
            # 初始化 OMLX 客户端
            logger.info(f"[OLLAMA_INIT_SERVICE] 正在初始化 OMLX 客户端...")
            logger.info(f"   - 配置来源：环境变量")
            logger.info(f"   - OMLX_BASE_URL: {os.getenv('OMLX_BASE_URL', 'http://localhost:11434/v1')}")
            logger.info(f"   - OMLX_MODEL: {os.getenv('OMLX_MODEL', 'Qwen3.5-4B-OptiQ-4bit')}")
            
            _omlx_client = OllamaClient(use_omlx=True)
            
            logger.info(f"[OLLAMA_INIT_SERVICE] ✅ OMLX 服务初始化成功")
            logger.info(f"   - Base URL: {_omlx_client.base_url}")
            logger.info(f"   - Model: {_omlx_client.model}")
            logger.info(f"   - Endpoint: {_omlx_client.api_endpoint}")
            logger.info(f"   - Use OMLX: {_omlx_client.use_omlx}")
            return _omlx_client
        else:
            # 初始化本地 Ollama 客户端
            logger.info(f"[OLLAMA_INIT_SERVICE] 正在初始化本地 Ollama 客户端...")
            logger.info(f"   - 配置来源：环境变量")
            logger.info(f"   - OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
            logger.info(f"   - OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'qwen3:4b')}")
            
            _ollama_client = OllamaClient(use_omlx=False)
            
            logger.info(f"[OLLAMA_INIT_SERVICE] ✅ 本地 Ollama 服务初始化成功")
            logger.info(f"   - Base URL: {_ollama_client.base_url}")
            logger.info(f"   - Model: {_ollama_client.model}")
            logger.info(f"   - Endpoint: {_ollama_client.api_endpoint}")
            return _ollama_client
    except Exception as e:
        logger.error(f"[OLLAMA_INIT_SERVICE] ❌ 初始化失败：{e}")
        raise


def check_omlx_connectivity() -> bool:
    """
    检查 AI 服务是否连通（快速验证）
    根据环境变量配置检查对应的服务（OMLX 或本地 Ollama）
    
    Returns:
        bool: True 表示连通，False 表示不连通
    """
    global _omlx_client, _ollama_client
    
    # 从环境变量读取配置
    import os
    use_omlx = os.getenv("USE_OMLX_FOR_CHATBOT", "true").lower() == "true"
    
    try:
        if use_omlx:
            # 检查 OMLX 服务
            if _omlx_client is None:
                logger.warning("[AI_CONNECTIVITY] OMLX 客户端未初始化")
                return False
            
            test_prompt = "你只需要直接回复我：are you ok?"
            response = _omlx_client.generate(test_prompt, options={'timeout': 10})
            
            if response and len(response.strip()) > 0:
                logger.info(f"[AI_CONNECTIVITY] ✅ OMLX 服务连通性验证成功")
                return True
            else:
                logger.warning(f"[AI_CONNECTIVITY] ⚠️ OMLX 响应为空")
                return False
        else:
            # 检查本地 Ollama 服务
            if _ollama_client is None:
                logger.warning("[AI_CONNECTIVITY] 本地 Ollama 客户端未初始化")
                return False
            
            test_prompt = "你只需要直接回复我：are you ok?"
            response = _ollama_client.generate(test_prompt, options={'timeout': 10})
            
            if response and len(response.strip()) > 0:
                logger.info(f"[AI_CONNECTIVITY] ✅ 本地 Ollama 服务连通性验证成功")
                return True
            else:
                logger.warning(f"[AI_CONNECTIVITY] ⚠️ 本地 Ollama 响应为空")
                return False
            
    except Exception as e:
        logger.error(f"[AI_CONNECTIVITY] ❌ 连通性验证失败：{e}")
        return False


def get_ollama_client_for_fpa() -> Optional[OllamaClient]:
    """
    为 FPA 生成获取 Ollama 客户端（根据环境变量选择 OMLX 或本地 Ollama）
    
    Returns:
        OllamaClient 实例或 None（如果服务不可用）
    """
    global _omlx_client, _ollama_client
    
    try:
        # 从环境变量读取配置
        import os
        use_omlx = os.getenv("USE_OMLX_FOR_CHATBOT", "true").lower() == "true"
        
        if use_omlx:
            # 使用 OMLX 客户端
            if _omlx_client is None:
                logger.info("[FPA_AI] OMLX 客户端未初始化，正在初始化...")
                omlx_url = os.getenv("OMLX_BASE_URL", "http://localhost:11434/v1")
                omlx_model = os.getenv("OMLX_MODEL", "Qwen3.5-4B-OptiQ-4bit")
                _omlx_client = OllamaClient(base_url=omlx_url, model=omlx_model, use_omlx=True)
            
            logger.info(f"[FPA_AI] OMLX 客户端已就绪，模型：{_omlx_client.model}")
            return _omlx_client
        else:
            # 使用本地 Ollama 客户端
            if _ollama_client is None:
                logger.info("[FPA_AI] 本地 Ollama 客户端未初始化，正在初始化...")
                ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                ollama_model = os.getenv("OLLAMA_MODEL", "qwen3:4b")
                _ollama_client = OllamaClient(base_url=ollama_url, model=ollama_model, use_omlx=False)
            
            logger.info(f"[FPA_AI] 本地 Ollama 客户端已就绪，模型：{_ollama_client.model}")
            return _ollama_client
        
    except Exception as e:
        logger.error(f"[FPA_AI] 获取客户端失败：{e}")
        return None


def get_ollama_client(base_url: str = None, model: str = None, use_omlx: bool = None) -> OllamaClient:
    """
    获取 Ollama 客户端单例（支持 OMLX 和本地 Ollama）
    
    Args:
        base_url: Ollama API 地址
        model: 默认模型
        use_omlx: 是否使用 OMLX（如果为 None，则从环境变量读取）
        
    Returns:
        OllamaClient 实例
    """
    global _ollama_client, _omlx_client
    
    # 确定使用哪个服务
    if use_omlx is None:
        import os
        use_omlx = os.getenv("USE_OMLX_FOR_CHATBOT", "true").lower() == "true"
    
    try:
        if use_omlx:
            # 使用 OMLX 服务
            if _omlx_client is None:
                import os
                omlx_url = base_url or os.getenv("OMLX_BASE_URL", "http://localhost:11434/v1")
                omlx_model = model or os.getenv("OMLX_MODEL", "Qwen3.5-9B-MLX-4bit")
                
                _omlx_client = OllamaClient(base_url=omlx_url, model=omlx_model, use_omlx=True)
                logger.info(f"[OLLAMA_INIT] ✅ 使用 OMLX 服务 - URL: {omlx_url} | Model: {omlx_model}")
                logger.info(f"[OLLAMA_INIT]    OMLX 是本地部署的模型服务，不是远程 API")
            
            return _omlx_client
        else:
            # 使用本地 Ollama 服务
            if _ollama_client is None:
                import os
                ollama_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                ollama_model = model or os.getenv("OLLAMA_MODEL", "qwen3:4b")
                
                _ollama_client = OllamaClient(base_url=ollama_url, model=ollama_model, use_omlx=False)
                logger.info(f"[OLLAMA_INIT] 💻 使用本地 Ollama 服务 - URL: {ollama_url} | Model: {ollama_model}")
            
            return _ollama_client
    except Exception as e:
        logger.error(f"[OLLAMA_INIT] 初始化失败：{e}")
        raise


def reset_ollama_client():
    """重置客户端（用于重新配置）"""
    global _ollama_client
    _ollama_client = None
