#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能客服路由模块
提供聊天、文档上传、知识库管理等功能接口
"""
from flask import Blueprint, render_template, request, jsonify, session
import os
import uuid
import logging
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

# 创建蓝图
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


@chatbot_bp.route('/')
def chatbot_index():
    """智能客服首页"""
    return render_template('chat/chatbot.html')


@chatbot_bp.route('/faq_preview')
def faq_preview_page():
    """FAQ 预览页面"""
    return render_template('chat/faq_preview.html')


@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """
    聊天接口
    
    Request JSON:
        {
            "message": "用户问题",
            "session_id": "会话 ID（可选）"
        }
    
    Response JSON:
        {
            "success": true,
            "answer": "AI 回复",
            "source": "knowledge_base|ai_generated",
            "retrieved_faqs": [...],
            "timestamp": "时间戳"
        }
    """
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': '缺少消息内容'
            }), 400
        
        user_message = data['message']
        
        # 获取或创建会话 ID
        session_id = data.get('session_id') or session.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['chat_session_id'] = session_id
        
        # 获取对话上下文
        from utils.chatbot_core import get_chatbot_core
        chatbot = get_chatbot_core()
        
        context = chatbot.get_session_context(session_id)
        
        # 处理查询
        result = chatbot.process_query(
            query=user_message,
            session_id=session_id,
            context=context
        )
        
        return jsonify({
            'success': result['success'],
            'answer': result.get('answer', ''),
            'source': result.get('source', 'unknown'),
            'retrieved_faqs': result.get('retrieved_faqs', []),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"[CHATBOT_CHAT] Chat interface error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/upload_document/preview', methods=['POST'])
def upload_document_preview():
    """
    上传文档并预览 FAQ（不入库）
    
    Form Data:
        file: 文件对象
        domain_id: 专业领域 ID（可选）
    
    Response JSON:
        {
            "success": true,
            "preview_id": "uuid",
            "filename": "xxx.pdf",
            "faqs_preview": [
                {"question": "问题 1", "answer": "答案 1", "is_duplicate": false},
                ...
            ],
            "total_count": 50,
            "duplicate_count": 5
        }
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '未找到上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        # 获取领域 ID
        domain_id = request.form.get('domain_id')
        if domain_id:
            domain_id = int(domain_id)
        
        # 保存文件
        from utils.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        filepath = processor.save_file(file, file.filename)
        
        # 处理文档
        doc_result = processor.process_document(filepath)
        
        if not doc_result['success']:
            return jsonify({
                'success': False,
                'error': doc_result.get('error', '文档处理失败')
            }), 400
        
        # 提取 FAQ（暂不入库）
        from utils.ollama_client import get_ollama_client
        ollama_client = get_ollama_client()
        
        content_length = len(doc_result['content'])
        
        if content_length > 10000:
            from utils.document_processor import extract_faq_parallel
            faqs = extract_faq_parallel(
                doc_result['content'], 
                ollama_client,
                chunk_size=2000,
                max_workers=2,
                domain_id=domain_id
            )
        else:
            from utils.document_processor import extract_faq_from_content
            faqs = extract_faq_from_content(doc_result['content'], ollama_client, domain_id=domain_id)
        
        # 检测重复问题
        seen_questions = {}
        faqs_with_dup = []
        duplicate_count = 0
        
        for idx, faq in enumerate(faqs):
            question = faq.get('question', '').strip()
            # 简单去重判断（完全相同）
            is_duplicate = question in seen_questions
            if is_duplicate:
                duplicate_count += 1
            else:
                seen_questions[question] = idx
            
            faqs_with_dup.append({
                'index': idx + 1,
                'question': question,
                'answer': faq.get('answer', ''),
                'is_duplicate': is_duplicate,
                'domain_id': domain_id
            })
        
        # 生成预览 ID 并存储到数据库临时表
        import uuid
        import json
        preview_id = str(uuid.uuid4())
        
        # 存储到 MySQL 临时表
        from models.knowledge_base import knowledge_base_manager
        conn = knowledge_base_manager.get_connection()
        cursor = conn.cursor()
        
        # 创建临时表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faq_preview_cache (
                preview_id VARCHAR(100) PRIMARY KEY,
                filename VARCHAR(255),
                filepath VARCHAR(500),
                filetype VARCHAR(50),
                domain_id INT,
                faqs_data LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 设置过期时间为 24 小时后
        from datetime import timedelta
        expires_at = datetime.now() + timedelta(hours=24)
        
        # 插入数据
        cursor.execute('''
            INSERT INTO faq_preview_cache 
            (preview_id, filename, filepath, filetype, domain_id, faqs_data, created_at, expires_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            preview_id,
            file.filename,
            filepath,
            doc_result['filetype'],
            domain_id,
            json.dumps(faqs_with_dup, ensure_ascii=False),
            datetime.now(),
            expires_at
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"[PREVIEW] Generated preview {preview_id} with {len(faqs)} FAQs (saved to DB)")
        
        return jsonify({
            'success': True,
            'preview_id': preview_id,
            'filename': file.filename,
            'faqs_preview': faqs_with_dup,
            'total_count': len(faqs),
            'duplicate_count': duplicate_count,
            'expires_in': '24 小时'
        })
        
    except Exception as e:
        logger.error(f"预览文档失败：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/upload_document/confirm', methods=['POST'])
def upload_document_confirm():
    """
    确认导入 FAQ
    
    Request JSON:
        preview_id: 预览 ID
        selected_indices: 要导入的 FAQ 索引列表（可选，默认全部导入）
    
    Response JSON:
        {
            "success": true,
            "document_id": 123,
            "imported_count": 45
        }
    """
    try:
        data = request.get_json()
        preview_id = data.get('preview_id')
        selected_indices = data.get('selected_indices')  # 用户选择的索引
        
        if not preview_id:
            return jsonify({
                'success': False,
                'error': '预览 ID 不能为空'
            }), 400
        
        # 从数据库中获取预览数据
        from models.knowledge_base import knowledge_base_manager
        import json
        
        conn = knowledge_base_manager.get_connection()
        cursor = conn.cursor()
        
        # 查询预览数据
        cursor.execute('''
            SELECT filename, filepath, filetype, domain_id, faqs_data, created_at, expires_at
            FROM faq_preview_cache
            WHERE preview_id = %s
        ''', (preview_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'error': '预览不存在或已过期，请重新上传'
            }), 404
        
        # 检查是否过期
        if row[6] and row[6] < datetime.now():
            # 删除过期数据
            cursor.execute('DELETE FROM faq_preview_cache WHERE preview_id = %s', (preview_id,))
            conn.commit()
            conn.close()
            return jsonify({
                'success': False,
                'error': '预览已过期，请重新上传'
            }), 400
        
        # 解析数据
        preview_data = {
            'filename': row[0],
            'filepath': row[1],
            'filetype': row[2],
            'domain_id': row[3],
            'faqs': json.loads(row[4])
        }
        
        logger.info(f"[IMPORT] Retrieved preview {preview_id} from DB with {len(preview_data['faqs'])} FAQs")
        
        # 保存文档到数据库
        from models.knowledge_base import knowledge_base_manager
        
        doc_id = knowledge_base_manager.add_document(
            filename=os.path.basename(preview_data['filepath']),
            original_filename=preview_data['filename'],
            file_type=preview_data['filetype'],
            metadata={
                'content_length': 0,  # 可以计算
                'processed_at': datetime.now().isoformat(),
                'faq_status': 'imported',
                'domain_id': preview_data['domain_id']
            }
        )
        
        # 批量导入 FAQ
        faqs = preview_data['faqs']
        imported_count = 0
        
        for faq in faqs:
            # 如果用户指定了索引，只导入选中的
            if selected_indices is not None and faq['index'] not in selected_indices:
                continue
            
            # 跳过重复问题（除非用户明确选择）
            if faq['is_duplicate'] and (selected_indices is None or faq['index'] not in selected_indices):
                continue
            
            # 添加 FAQ（注意：add_faq 不需要 domain_id 参数）
            knowledge_base_manager.add_faq(
                question=faq['question'],
                answer=faq['answer'],
                document_id=doc_id,
                category=None,  # 暂时不设置分类
                tags=None  # 暂时不设置标签
            )
            imported_count += 1
        
        # 清理缓存数据
        cursor.execute('DELETE FROM faq_preview_cache WHERE preview_id = %s', (preview_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"[IMPORT] Imported {imported_count} FAQs from preview {preview_id}")
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'imported_count': imported_count,
            'message': f'成功导入 {imported_count} 条 FAQ'
        })
        
    except Exception as e:
        logger.error(f"确认导入失败：{e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/documents', methods=['GET'])
def list_documents():
    """获取文档列表"""
    try:
        logger.info(f"[CHATBOT_DOCUMENTS] ====== 开始处理文档列表请求 ======")
        logger.info(f"[CHATBOT_DOCUMENTS] 请求参数：{request.args.to_dict()}")
        
        from models.knowledge_base import knowledge_base_manager
        
        logger.info(f"[CHATBOT_DOCUMENTS] 调用 knowledge_base_manager.list_documents(status='active')")
        documents = knowledge_base_manager.list_documents(status='active')
        
        logger.info(f"[CHATBOT_DOCUMENTS] 查询到文档数量：{len(documents)}")
        if documents:
            logger.info(f"[CHATBOT_DOCUMENTS] 第一个文档：{documents[0] if len(documents) > 0 else 'N/A'}")
        
        result = {
            'success': True,
            'documents': documents
        }
        logger.info(f"[CHATBOT_DOCUMENTS] 返回结果：success=True, count={len(documents)}")
        logger.info(f"[CHATBOT_DOCUMENTS] ====== 文档列表请求处理完成 ======")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[CHATBOT_DOCUMENTS] 获取文档列表失败：{e}")
        logger.error(f"[CHATBOT_DOCUMENTS] 错误堆栈：{__import__('traceback').format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/faqs', methods=['GET'])
def list_faqs():
    """获取 FAQ 列表"""
    try:
        logger.info(f"[CHATBOT_FAQS] ====== 开始处理 FAQ 列表请求 ======")
        logger.info(f"[CHATBOT_FAQS] 请求参数：{request.args.to_dict()}")
        
        from models.knowledge_base import knowledge_base_manager
        
        logger.info(f"[CHATBOT_FAQS] 调用 knowledge_base_manager.list_all_faqs()")
        faqs = knowledge_base_manager.list_all_faqs()
        
        logger.info(f"[CHATBOT_FAQS] 查询到 FAQ 数量：{len(faqs)}")
        if faqs:
            logger.info(f"[CHATBOT_FAQS] 第一个 FAQ 问题：{faqs[0].get('question', 'N/A')[:50]}...")
        
        result = {
            'success': True,
            'faqs': faqs
        }
        logger.info(f"[CHATBOT_FAQS] 返回结果：success=True, count={len(faqs)}")
        logger.info(f"[CHATBOT_FAQS] ====== FAQ 列表请求处理完成 ======")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[CHATBOT_FAQS] 获取 FAQ 列表失败：{e}")
        logger.error(f"[CHATBOT_FAQS] 错误堆栈：{__import__('traceback').format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/search', methods=['GET'])
def search_faqs():
    """搜索 FAQ"""
    try:
        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 10))
        
        if not keyword:
            return jsonify({
                'success': False,
                'error': '请输入搜索关键词'
            }), 400
        
        from models.knowledge_base import knowledge_base_manager
        
        faqs = knowledge_base_manager.search_faqs(keyword, limit=limit)
        
        return jsonify({
            'success': True,
            'keyword': keyword,
            'count': len(faqs),
            'faqs': faqs
        })
    except Exception as e:
        logger.error(f"搜索 FAQ 失败：{e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/conversation/clear', methods=['POST'])
def clear_conversation():
    """清空对话历史"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        if not session_id:
            session_id = session.get('chat_session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '会话 ID 不存在'
            }), 400
        
        from utils.chatbot_core import get_chatbot_core
        chatbot = get_chatbot_core()
        
        success = chatbot.clear_session(session_id)
        
        return jsonify({
            'success': success,
            'message': '对话历史已清空' if success else '清空失败'
        })
    except Exception as e:
        logger.error(f"清空对话失败：{e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@chatbot_bp.route('/ollama/status', methods=['GET'])
def check_ollama_status():
    """检查 Ollama 服务状态"""
    try:
        logger.info(f"[CHATBOT_OLLAMA] ====== 开始检查 Ollama 服务状态 ======")
        
        from utils.ollama_client import get_ollama_client
        
        logger.info(f"[CHATBOT_OLLAMA] 获取 Ollama 客户端实例")
        client = get_ollama_client()
        
        logger.info(f"[CHATBOT_OLLAMA] Ollama base_url: {client.base_url}")
        logger.info(f"[CHATBOT_OLLAMA] 调用 client.is_available()")
        is_available = client.is_available()
        
        logger.info(f"[CHATBOT_OLLAMA] Ollama 可用性检查结果：{is_available}")
        
        models = []
        if is_available:
            logger.info(f"[CHATBOT_OLLAMA] 调用 client.list_models()")
            models = client.list_models()
            logger.info(f"[CHATBOT_OLLAMA] 获取到模型数量：{len(models)}")
            logger.info(f"[CHATBOT_OLLAMA] 模型列表：{models}")
        else:
            logger.warning(f"[CHATBOT_OLLAMA] Ollama 服务不可用，跳过模型列表获取")
        
        result = {
            'success': True,
            'available': is_available,
            'models': models,
            'endpoint': client.base_url
        }
        
        logger.info(f"[CHATBOT_OLLAMA] 返回结果：available={is_available}, models_count={len(models)}")
        logger.info(f"[CHATBOT_OLLAMA] ====== Ollama 状态检查完成 ======")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"[CHATBOT_OLLAMA] 检查 Ollama 状态失败：{e}")
        logger.error(f"[CHATBOT_OLLAMA] 错误堆栈：{__import__('traceback').format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e),
            'available': False
        }), 500


# 辅助函数：从文档内容提取 FAQ
def extract_faq_from_content(content: str, ollama_client=None) -> list:
    """从文档内容中提取 FAQ"""
    if not ollama_client:
        from utils.ollama_client import get_ollama_client
        ollama_client = get_ollama_client()
    
    prompt = f"""
请从以下文档内容中提取所有可能的问答对（FAQ）。
要求：
1. 识别文档中的所有问题和对应的答案
2. 如果没有明确的问题，根据内容总结可能的问题
3. 每个问答对应该完整、准确
4. 使用 JSON 格式返回，格式如下：
[
    {{"question": "问题 1", "answer": "答案 1"}},
    {{"question": "问题 2", "answer": "答案 2"}}
]

文档内容：
{content[:3000]}  # 限制长度避免超时

请提取 FAQ：
"""
    
    try:
        response = ollama_client.generate(prompt)
        # 尝试解析 JSON
        import json
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            faqs = json.loads(json_str)
            if isinstance(faqs, list):
                return faqs
        return []
    except Exception as e:
        logger.error(f"FAQ 提取失败：{e}")
        return []
