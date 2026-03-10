#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能客服核心处理模块
包含问题解析、意图识别、答案生成等功能
"""
import logging
from typing import List, Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class ChatbotCore:
    """智能客服核心处理器"""
    
    def __init__(self, ollama_client=None, knowledge_base=None):
        """
        初始化客服核心
        
        Args:
            ollama_client: Ollama 客户端实例
            knowledge_base: 知识库管理器实例
        """
        self.ollama_client = ollama_client
        self.knowledge_base = knowledge_base
        
        # 如果没有提供客户端，延迟初始化
        if not ollama_client:
            from utils.ollama_client import get_ollama_client
            self.ollama_client = get_ollama_client()
        
        if not knowledge_base:
            from models.knowledge_base import knowledge_base_manager
            self.knowledge_base = knowledge_base_manager
    
    def process_query(self, query: str, session_id: str = None, 
                     context: List[Dict] = None, domain_id: int = None) -> Dict:
        """
        处理用户查询
        
        Args:
            query: 用户问题
            session_id: 会话 ID
            context: 对话上下文
            domain_id: 专业领域 ID（可选）
            
        Returns:
            回复结果字典
        """
        try:
            # 1. 问题解析与意图识别
            parsed_query = self._parse_query(query)
            
            # 2. 检索知识库（支持领域过滤）
            retrieved_faqs = self._retrieve_knowledge(query, top_k=5, domain_id=domain_id)
            
            # 3. 如果有高相似度匹配，直接使用
            if retrieved_faqs and retrieved_faqs[0].get('similarity_score', 0) > 0.8:
                best_faq = retrieved_faqs[0]
                answer = best_faq['answer']
                source = 'knowledge_base'
                
                # 更新浏览次数
                self.knowledge_base.increment_faq_view(best_faq['id'])
            else:
                # 4. 使用 AI 生成答案
                answer, used_context = self._generate_answer(
                    query=query,
                    retrieved_faqs=retrieved_faqs,
                    context=context or []
                )
                source = 'ai_generated'
            
            # 5. 保存对话历史
            if session_id:
                self._save_conversation(
                    session_id=session_id,
                    query=query,
                    answer=answer,
                    retrieved_faqs=retrieved_faqs,
                    source=source
                )
            
            return {
                'success': True,
                'answer': answer,
                'source': source,
                'retrieved_faqs': retrieved_faqs[:3],  # 返回最相关的 3 个
                'parsed_query': parsed_query,
                'domain_id': domain_id  # 返回使用的领域 ID
            }
            
        except Exception as e:
            logger.error(f"处理查询失败：{e}")
            return {
                'success': False,
                'error': str(e),
                'answer': "抱歉，处理您的请求时出现错误。"
            }
    
    def _parse_query(self, query: str) -> Dict:
        """
        解析用户问题
        
        Args:
            query: 用户问题
            
        Returns:
            解析结果
        """
        # 使用 AI 进行问题解析
        prompt = f"""
请分析以下用户问题，提取关键信息：
1. 问题的主题/领域
2. 关键词
3. 问题类型（是什么、为什么、怎么做等）
4. 情感倾向（中性、积极、消极）

用户问题：{query}

请以 JSON 格式返回：
{{
    "topic": "主题",
    "keywords": ["关键词 1", "关键词 2"],
    "question_type": "问题类型",
    "sentiment": "情感倾向"
}}
"""
        
        try:
            response = self.ollama_client.generate(prompt)
            # 尝试解析 JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
                return parsed
            else:
                return {'topic': 'unknown', 'keywords': [], 'question_type': 'general'}
        except Exception as e:
            logger.warning(f"问题解析失败：{e}")
            return {'topic': 'unknown', 'keywords': [], 'question_type': 'general'}
    
    def _retrieve_knowledge(self, query: str, top_k: int = 5, domain_id: int = None) -> List[Dict]:
        """
        从知识库中检索相关 FAQ
        
        Args:
            query: 查询文本
            top_k: 返回数量
            domain_id: 专业领域 ID（可选）
            
        Returns:
            相关 FAQ 列表
        """
        # 使用领域搜索
        faqs = self.knowledge_base.search_faqs_by_domain(query, domain_id=domain_id, limit=top_k * 2)
        
        # 计算简单的相似度分数
        query_keywords = set(query.lower().split())
        for faq in faqs:
            question_text = faq['question'].lower()
            answer_text = faq['answer'].lower()
            
            # 简单的词匹配分数
            match_count = sum(1 for kw in query_keywords if kw in question_text or kw in answer_text)
            faq['similarity_score'] = match_count / len(query_keywords) if query_keywords else 0
        
        # 按相似度排序
        faqs.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return faqs[:top_k]
    
    def _generate_answer(self, query: str, retrieved_faqs: List[Dict], 
                        context: List[Dict]) -> Tuple[str, List]:
        """
        使用 AI 生成答案
        
        Args:
            query: 用户问题
            retrieved_faqs: 检索到的 FAQ
            context: 对话上下文
            
        Returns:
            (答案，使用的上下文)
        """
        # 构建提示词
        system_prompt = """你是一个专业的企业智能客服助手。请根据提供的知识库内容和对话上下文，为用户问题生成准确、简洁、友好的回答。

要求：
1. 优先基于知识库内容回答
2. 如果知识库没有相关信息，使用你的通用知识
3. 保持回答专业且易于理解
4. 如果不确定，诚实地告知用户
5. 使用中文回答"""

        # 构建消息
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话上下文（最近 5 轮）
        if context:
            messages.extend(context[-10:])  # 保留最近 5 轮（10 条消息）
        
        # 构建知识库参考
        kb_context = ""
        if retrieved_faqs:
            kb_context = "\n\n参考知识库内容：\n"
            for i, faq in enumerate(retrieved_faqs, 1):
                kb_context += f"{i}. 问题：{faq['question']}\n   答案：{faq['answer']}\n\n"
        
        # 添加用户问题
        user_message = f"用户问题：{query}{kb_context}"
        messages.append({"role": "user", "content": user_message})
        
        try:
            # 调用 AI 生成答案
            answer = self.ollama_client.chat(messages)
            return answer.strip(), retrieved_faqs[:2]  # 返回使用的参考
        except Exception as e:
            logger.error(f"AI 生成答案失败：{e}")
            return "抱歉，我暂时无法回答这个问题。", []
    
    def _save_conversation(self, session_id: str, query: str, answer: str,
                          retrieved_faqs: List[Dict], source: str) -> None:
        """保存对话历史"""
        try:
            # 保存用户问题
            related_ids = [faq['id'] for faq in retrieved_faqs] if retrieved_faqs else None
            self.knowledge_base.add_conversation_message(
                session_id=session_id,
                message_role='user',
                message_content=query,
                related_faq_ids=None
            )
            
            # 保存 AI 回答
            self.knowledge_base.add_conversation_message(
                session_id=session_id,
                message_role='assistant',
                message_content=answer,
                related_faq_ids=related_ids
            )
        except Exception as e:
            logger.error(f"保存对话失败：{e}")
    
    def get_session_context(self, session_id: str, max_turns: int = 5) -> List[Dict]:
        """
        获取会话上下文
        
        Args:
            session_id: 会话 ID
            max_turns: 最大轮数
            
        Returns:
            格式化的对话历史
        """
        history = self.knowledge_base.get_conversation_history(session_id, limit=max_turns * 2)
        
        # 转换为 OpenAI 格式
        messages = []
        for msg in history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        return messages
    
    def clear_session(self, session_id: str) -> bool:
        """清空会话"""
        return self.knowledge_base.clear_conversation_history(session_id)


# 全局客服核心实例
_chatbot_core = None


def get_chatbot_core():
    """获取客服核心实例"""
    global _chatbot_core
    if _chatbot_core is None:
        from utils.ollama_client import get_ollama_client
        from models.knowledge_base import knowledge_base_manager
        
        ollama_client = get_ollama_client()
        _chatbot_core = ChatbotCore(ollama_client, knowledge_base_manager)
    
    return _chatbot_core
