#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 FAQ 并行提取功能
对比单线程 vs 多线程性能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from docx import Document
from utils.document_processor import extract_faq_from_content, extract_faq_parallel
from utils.ollama_client import get_ollama_client, reset_ollama_client
import time

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
print('='*60)

# 测试单线程版本（只处理前 3000 字符）
print('\n【测试 1】单线程模式 (前 3000 字符)...')
try:
    ollama_client = get_ollama_client()
    print(f'使用模型：{ollama_client.model}')
    
    start_time = time.time()
    faqs_single = extract_faq_from_content(content[:3000], ollama_client)
    elapsed_single = time.time() - start_time
    
    print(f'✅ 单线程耗时：{elapsed_single:.2f} 秒')
    print(f'✅ 提取 {len(faqs_single)} 条 FAQ')
    
except Exception as e:
    print(f'❌ 单线程失败：{e}')

# 测试并行版本（处理前 6000 字符，分成 3 段）
print('\n【测试 2】并行处理模式 (前 6000 字符，分 3 段)...')
try:
    start_time = time.time()
    faqs_parallel = extract_faq_parallel(
        content[:6000], 
        ollama_client,
        chunk_size=2000,
        max_workers=3
    )
    elapsed_parallel = time.time() - start_time
    
    print(f'✅ 并行处理耗时：{elapsed_parallel:.2f} 秒')
    print(f'✅ 提取 {len(faqs_parallel)} 条 FAQ')
    
    # 计算加速比
    if len(faqs_single) > 0 and len(faqs_parallel) > 0:
        # 注意：这里处理的文本长度不同，仅供参考
        print(f'\n📊 性能对比:')
        print(f'   单线程：{elapsed_single:.2f} 秒 / {len(faqs_single)} 条 = {elapsed_single/len(faqs_single):.2f} 秒/条')
        print(f'   并行处理：{elapsed_parallel:.2f} 秒 / {len(faqs_parallel)} 条 = {elapsed_parallel/len(faqs_parallel):.2f} 秒/条')
        
except Exception as e:
    print(f'❌ 并行处理失败：{e}')
    import traceback
    traceback.print_exc()

print('\n' + '='*60)
print('测试完成！')
