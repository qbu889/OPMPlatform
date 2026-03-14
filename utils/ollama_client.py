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
    
    def __init__(self, base_url: str = None, model: str = None):
        """
        初始化 Ollama 客户端
        
        Args:
            base_url: Ollama API 基础 URL
            model: 默认使用的模型名称（如果为 None 则从.env 读取）
        """
        # 显式加载 .env 文件
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv()
            logger.debug(f"[OLLAMA_ENV] 已加载 .env 文件：{env_path.absolute()}")
        
        # 优先使用传入参数，否则从环境变量读取
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip('/')
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self.api_endpoint = f"{self.base_url}/api/generate"
        self.chat_endpoint = f"{self.base_url}/api/chat"
        
        # 创建 requests session，复用连接
        self.session = requests.Session()
        # 设置默认请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Ollama-Client/1.0'
        })
        
        logger.info(f"[OLLAMA_INIT] 初始化 - URL: {self.base_url}, Model: {self.model}")
        
        # 验证模型是否存在
        self._validate_model()
    
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
                 retry: int = 3) -> str:
        """
        生成文本回复（直接使用 generate API）
        
        Args:
            prompt: 输入提示词
            model: 模型名称（可选，默认使用实例的 model）
            system: 系统提示
            stream: 是否流式输出
            options: 其他配置选项
            retry: 重试次数（默认 3 次）
            
        Returns:
            生成的文本内容
        """
        # 直接使用 /api/generate 接口
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        if system:
            payload["system"] = system
        
        if options:
            payload["options"] = options
        
        attempt = 0
        last_error = None
        
        while attempt <= retry:
            try:
                # 添加详细日志，诊断 404 问题
                logger.info(f"[OLLAMA_REQUEST] URL: {self.api_endpoint}")
                logger.info(f"[OLLAMA_REQUEST] Model: {model or self.model}")
                logger.info(f"[OLLAMA_REQUEST] Prompt length: {len(prompt)} chars")
                logger.info(f"[OLLAMA_REQUEST] Attempt: {attempt + 1}/{retry + 1}")
                
                response = self.session.post(
                    self.api_endpoint,
                    json=payload,
                    stream=stream,
                    timeout=300  # 5 分钟
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
                    return result.get("response", "")
                    
            except requests.exceptions.ConnectionError as e:
                last_error = e
                attempt += 1
                if attempt <= retry:
                    wait_time = 2 ** attempt  # 指数退避：2, 4, 8 秒
                    logger.warning(f"[OLLAMA_CONNECTION_ERROR] 连接失败，{wait_time}秒后重试 (Attempt {attempt}/{retry + 1}): {e}")
                    import time
                    time.sleep(wait_time)
                else:
                    logger.error(f"[OLLAMA_GENERATE] 连接失败，已达最大重试次数：{e}")
                    raise Exception(f"AI 服务连接失败：{str(e)}")
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
             retry: int = 2) -> str:
        """
        聊天对话（支持多轮对话）
        
        Args:
            messages: 消息列表，每条消息包含 role 和 content
                     role 可以是 'system', 'user', 'assistant'
            model: 模型名称
            stream: 是否流式输出
            options: 其他配置选项
            retry: 重试次数
            
        Returns:
            AI 助手的回复内容
        """
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
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model.get("name") for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"[OLLAMA_MODELS] Failed to get model list: {e}")
            return []
    
    def is_available(self) -> bool:
        """检查 Ollama 服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


# 全局客户端实例（延迟初始化）
_ollama_client = None


def get_ollama_client(base_url: str = None, model: str = None) -> OllamaClient:
    """
    获取 Ollama 客户端单例
    
    Args:
        base_url: Ollama API 地址
        model: 默认模型
        
    Returns:
        OllamaClient 实例
    """
    global _ollama_client
    
    if _ollama_client is None:
        # 从环境变量或配置读取
        import os
        ollama_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        ollama_model = model or os.getenv("OLLAMA_MODEL", "qwen:1.8b")  # 改为 qwen:1.8b，更轻量

        _ollama_client = OllamaClient(base_url=ollama_url, model=ollama_model)
        logger.info(f"[OLLAMA_INIT] URL: {ollama_url} | Model: {ollama_model}")
    
    return _ollama_client


def reset_ollama_client():
    """重置客户端（用于重新配置）"""
    global _ollama_client
    _ollama_client = None
