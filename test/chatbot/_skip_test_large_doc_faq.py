#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 FAQ 提取功能 - 针对大型文档
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from docx import Document
from utils.document_processor import extract_faq_from_content
from utils.ollama_client import get_ollama_client, reset_ollama_client

# 重置客户端以加载最新配置
reset_ollama_client()

# 读取文档
doc_path = 'uploads/6e39180c2df7417f812830191e915cb1.docx'
doc = Document(doc_path)

# 提取所有文本
paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
content = '\n'.join(paragraphs)

print(f'文档总长度：{len(content)} 字符')
print(f'段落数量：{len(paragraphs)}')
print(f'\n内容预览 (前 500 字): ')
print(content[:500])
print('\n' + '='*60)

# 测试 FAQ 提取
print('\n正在调用 Ollama AI 提取 FAQ...')
try:
    ollama_client = get_ollama_client()
    print(f'使用模型：{ollama_client.model}')
    
    # 分段处理 - 每 3000 字符一段
    chunk_size = 3000
    all_faqs = []
    
    for i in range(0, min(len(content), 9000), chunk_size):  # 只测试前 9000 字符
        chunk = content[i:i+chunk_size]
        print(f'\n处理第 {i//chunk_size + 1} 段 ({len(chunk)} 字符)...')
        
        faqs = extract_faq_from_content(chunk, ollama_client)
        all_faqs.extend(faqs)
        print(f'本段提取 {len(faqs)} 条 FAQ')
    
    print(f'\n✅ 总共成功提取 {len(all_faqs)} 条 FAQ')
    
    for i, faq in enumerate(all_faqs, 1):
        print(f'\n{i}. 问：{faq.get("question")}')
        print(f'   答：{faq.get("answer")}')
        
except Exception as e:
    print(f'❌ 错误：{e}')
    import traceback
    traceback.print_exc()
