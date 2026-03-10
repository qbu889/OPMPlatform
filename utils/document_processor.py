#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档处理模块
支持多种格式文档的上传、解析和文本提取
"""
import os
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器"""

    def __init__(self, upload_folder: str = "uploads"):
        """
        初始化文档处理器
        
        Args:
            upload_folder: 上传文件夹路径
        """
        self.upload_folder = upload_folder
        os.makedirs(upload_folder, exist_ok=True)

        # 支持的扩展名
        self.supported_extensions = {
            '.txt': 'text',
            '.md': 'markdown',
            '.py': 'text',  # Python 代码文件
            '.doc': 'word',
            '.docx': 'word',
            '.pdf': 'pdf',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.bmp': 'image'
        }

    def save_file(self, file, filename: str) -> str:
        """
        保存上传的文件
        
        Args:
            file: 文件对象
            filename: 文件名
            
        Returns:
            保存后的文件路径
        """
        from werkzeug.utils import secure_filename

        # 提取扩展名（在 secure_filename 之前）
        import uuid
        from pathlib import Path
        ext = Path(filename).suffix.lower()
        logger.info(f"[DOC_SAVE] Filename: {filename} | Ext: {ext}")

        # 使用 UUID 生成唯一文件名，避免中文文件名被 secure_filename 过滤
        safe_filename = f"{uuid.uuid4().hex}{ext}"

        if not ext:
            raise ValueError("无效的文件名或无扩展名")

        # 确保目录存在
        os.makedirs(self.upload_folder, exist_ok=True)

        filepath = os.path.join(self.upload_folder, safe_filename)

        # 保存文件
        file.save(filepath)
        logger.info(f"[DOC_SAVE] File saved: {filepath}")

        return filepath

    def process_document(self, filepath: str) -> Dict:
        """
        处理文档，提取文本内容
        
        Args:
            filepath: 文件路径
            
        Returns:
            包含提取内容的字典：
            {
                'success': bool,
                'content': str,
                'filename': str,
                'filetype': str,
                'error': str (可选)
            }
        """
        if not os.path.exists(filepath):
            return {
                'success': False,
                'error': '文件不存在'
            }

        ext = Path(filepath).suffix.lower()
        filetype = self.supported_extensions.get(ext, 'unknown')

        logger.info(f"[DOC_PROCESS] Processing file: {filepath}")
        logger.info(f"[DOC_PROCESS] Extension: {ext}, Type: {filetype}")

        try:
            if filetype == 'text' or filetype == 'markdown':
                content = self._read_text_file(filepath)
            elif filetype == 'word':
                content = self._read_word_file(filepath)
            elif filetype == 'pdf':
                content = self._read_pdf_file(filepath)
            elif filetype == 'image':
                content = self._read_image_file(filepath)
            else:
                return {
                    'success': False,
                    'error': f'不支持的文件类型：{ext}'
                }

            return {
                'success': True,
                'content': content,
                'filename': os.path.basename(filepath),
                'filetype': filetype
            }

        except Exception as e:
            logger.error(f"[DOC_PROCESS] Failed to process document: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _read_text_file(self, filepath: str) -> str:
        """读取文本文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def _read_word_file(self, filepath: str) -> str:
        """读取 Word 文件"""
        try:
            from docx import Document

            doc = Document(filepath)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return '\n'.join(paragraphs)
        except ImportError:
            raise Exception("需要安装 python-docx 库：pip install python-docx")
        except Exception as e:
            raise Exception(f"读取 Word 文件失败：{str(e)}")

    def _read_pdf_file(self, filepath: str) -> str:
        """读取 PDF 文件"""
        try:
            import pdfplumber

            text_content = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            return '\n'.join(text_content)
        except ImportError:
            raise Exception("需要安装 pdfplumber 库：pip install pdfplumber")
        except Exception as e:
            raise Exception(f"读取 PDF 文件失败：{str(e)}")

    def _read_image_file(self, filepath: str) -> str:
        """读取图片文件（OCR）"""
        try:
            import pytesseract
            from PIL import Image

            # 中文识别
            text = pytesseract.image_to_string(
                Image.open(filepath),
                lang='chi_sim+eng'
            )
            return text
        except ImportError:
            raise Exception("需要安装 pytesseract 和 Pillow：pip install pytesseract pillow")
        except Exception as e:
            raise Exception(f"OCR 识别失败：{str(e)}")

    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式列表"""
        return list(self.supported_extensions.keys())


def extract_faq_from_content(content: str, ollama_client=None, domain_id: int = None) -> List[Dict]:
    """
    从文档内容中抽取 FAQ 对（单线程版本）
    
    Args:
        content: 文档内容
        ollama_client: Ollama 客户端实例
        domain_id: 专业领域 ID（可选）
        
    Returns:
        FAQ 列表，每个元素为 {'question': str, 'answer': str}
    """
    import json
    import re

    if not ollama_client:
        from utils.ollama_client import get_ollama_client
        ollama_client = get_ollama_client()

    # 按章节分割内容（基于 Markdown 标题）
    sections = []
    current_section = []
    
    for line in content.split('\n'):
        # 检测标题（# 开头的为标题）
        if line.strip().startswith('#') and len(line.strip()) > 2:
            # 保存上一个章节
            if current_section:
                sections.append('\n'.join(current_section))
            # 开始新章节
            current_section = [line]
        else:
            current_section.append(line)
    
    # 添加最后一个章节
    if current_section:
        sections.append('\n'.join(current_section))
    
    logger.info(f"[FAQ_EXTRACT] Document split into {len(sections)} sections")
    
    all_faqs = []
    
    # 逐个处理章节
    for idx, section in enumerate(sections):
        if not section.strip():
            continue
            
        section_prompt = f"""请从以下文档片段中提取所有可能的问答对（FAQ）。
要求：
1. 识别文档中的所有问题和对应的答案
2. 如果没有明确的问题，根据内容总结可能的问题
3. 【重要】答案必须完整，包含所有步骤、子步骤、注意事项等详细信息
4. 【重要】保留原文中的图片链接（Markdown 格式：![描述](URL)）
5. 【重要】保留原文中的代码块、SQL 语句、命令等
6. 【重要】保留原文的格式，包括换行、列表、缩进等
7. 【重要】必须返回纯 JSON 数组，不要包含任何 Markdown 格式（如 ```json）
8. 【重要】不要有任何解释、说明或其他文字
9. JSON 格式示例：
[
    {{"question": "问题 1", "answer": "完整的答案（包含步骤、图片、代码等）"}},
    {{"question": "问题 2", "answer": "完整的答案"}}
]

文档片段：
{section[:4000]}  # 每个章节限制 4000 字符

请提取 FAQ（只返回纯 JSON 数组，不要任何其他内容，保留所有细节）：
"""
        
        try:
            response = ollama_client.generate(section_prompt)
            logger.info(f"[FAQ_EXTRACT] Section {idx + 1}/{len(sections)} AI response length: {len(response)}")
            
            # 使用增强的多方法解析 JSON
            faqs = parse_json_with_multiple_methods(response, chunk_index=idx + 1)
            
            if faqs:
                # 添加 domain_id 到每个 FAQ
                for faq in faqs:
                    if domain_id:
                        faq['domain_id'] = domain_id
                all_faqs.extend(faqs)
                logger.info(f"[FAQ_EXTRACT] Section {idx + 1}: extracted {len(faqs)} FAQs")
            else:
                logger.warning(f"[FAQ_EXTRACT] Section {idx + 1}: no FAQs extracted")
                
        except Exception as e:
            logger.error(f"[FAQ_EXTRACT] Section {idx + 1} processing failed: {e}")
            import traceback
            traceback.print_exc()
    
    logger.info(f"[FAQ_EXTRACT] Total FAQs extracted: {len(all_faqs)}")
    return all_faqs


def parse_json_with_multiple_methods(response: str, chunk_index: int = 0):
    """
    使用多种方法尝试解析 JSON（增强版）
    
    Args:
        response: AI 返回的响应文本
        chunk_index: 文本段索引（用于日志）
        
    Returns:
        解析后的 FAQ 列表
    """
    import json
    import re
    
    if not response or not response.strip():
        logger.warning(f"[Chunk {chunk_index}] 空响应")
        return []
    
    response = response.strip()
    
    # 方法 1：直接解析（最优情况）
    try:
        faqs = json.loads(response)
        if isinstance(faqs, list):
            logger.info(f"[Chunk {chunk_index}] 方法 1：直接解析成功，{len(faqs)} 条")
            return faqs
    except json.JSONDecodeError as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 1 失败：{e}")
    
    # 方法 2：移除 Markdown 代码块标记
    try:
        cleaned = response
        # 移除 ```json 或 ``` 开头和结尾
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        faqs = json.loads(cleaned)
        if isinstance(faqs, list):
            logger.info(f"[Chunk {chunk_index}] 方法 2：移除 Markdown 标记成功，{len(faqs)} 条")
            return faqs
    except Exception as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 2 失败：{e}")
    
    # 方法 3：提取第一个 [ 到最后一个 ]
    try:
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            logger.debug(f"[Chunk {chunk_index}] 方法 3：提取 JSON 部分 [{start_idx}:{end_idx}], 长度 {len(json_str)}")
            
            # 清理特殊字符
            json_str = json_str.replace('\n', '\\n').replace('\r', '\\r')
            faqs = json.loads(json_str)
            if isinstance(faqs, list):
                logger.info(f"[Chunk {chunk_index}] 方法 3 成功，{len(faqs)} 条")
                return faqs
    except Exception as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 3 失败：{e}")
    
    # 方法 4：尝试修复常见 JSON 错误
    try:
        fixed_json = fix_common_json_errors(response)
        if fixed_json:
            faqs = json.loads(fixed_json)
            if isinstance(faqs, list):
                logger.info(f"[Chunk {chunk_index}] 方法 4：修复 JSON 错误成功，{len(faqs)} 条")
                return faqs
    except Exception as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 4 失败：{e}")
    
    # 方法 5：使用正则表达式提取 JSON 对象
    try:
        # 尝试匹配多个 JSON 对象
        pattern = r'\{\s*"question"\s*:\s*"[^"]+"\s*,\s*"answer"\s*:\s*"[^"]+"\s*\}'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            logger.info(f"[Chunk {chunk_index}] 方法 5：正则表达式匹配到 {len(matches)} 个对象")
            faqs = []
            for match in matches:
                try:
                    faq = json.loads(match)
                    faqs.append(faq)
                except:
                    pass
            return faqs
    except Exception as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 5 失败：{e}")
    
    # 方法 6：尝试提取包含长 URL 的 JSON（更宽松的匹配）
    try:
        # 匹配包含图片链接的 JSON 对象
        pattern = r'\{[^{}]*"question"[^{}]*,[^{}]*"answer"[^{}]*\}'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            logger.info(f"[Chunk {chunk_index}] 方法 6：宽松匹配到 {len(matches)} 个对象")
            faqs = []
            for match in matches:
                try:
                    # 尝试修复这个 JSON
                    fixed = fix_common_json_errors('[' + match + ']')
                    if fixed:
                        parsed = json.loads(fixed)
                        if isinstance(parsed, list) and len(parsed) == 1:
                            faqs.append(parsed[0])
                except Exception as e2:
                    logger.debug(f"[Chunk {chunk_index}] 方法 6 解析单个对象失败：{e2}")
            if faqs:
                return faqs
    except Exception as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 6 失败：{e}")
    
    # 方法 7：处理包含代码块但未闭合的 JSON
    try:
        # 查找 ``` 开头但没有 ``` 结尾的情况
        if '```' in response:
            # 统计 ``` 的数量
            code_block_count = response.count('```')
            if code_block_count % 2 == 1:
                logger.info(f"[Chunk {chunk_index}] 方法 7：检测到未闭合的代码块标记")
                
                # 尝试在合适的位置添加 ``` 来闭合
                # 找到最后一个 ``` 的位置
                last_backtick = response.rfind('```')
                
                # 在最后一个 ``` 后面找第一个 " 的位置（JSON 字符串结束）
                next_quote = response.find('"', last_backtick + 3)
                
                if next_quote > last_backtick:
                    # 在 " 之前插入 ```
                    fixed_response = response[:next_quote] + '```\n' + response[next_quote:]
                    logger.debug(f"[Chunk {chunk_index}] 方法 7：添加代码块结束标记")
                    
                    # 尝试解析修复后的 JSON
                    faqs = parse_json_with_multiple_methods(fixed_response, chunk_index)
                    if faqs:
                        logger.info(f"[Chunk {chunk_index}] 方法 7 成功修复代码块，{len(faqs)} 条")
                        return faqs
                else:
                    # 如果找不到 "，可能在字符串末尾
                    # 尝试在 response 末尾添加 ```
                    fixed_response = response.rstrip() + '```\n]'
                    logger.debug(f"[Chunk {chunk_index}] 方法 7：在末尾添加代码块结束标记")
                    
                    # 尝试解析
                    faqs = parse_json_with_multiple_methods(fixed_response, chunk_index)
                    if faqs:
                        logger.info(f"[Chunk {chunk_index}] 方法 7 成功修复代码块（末尾），{len(faqs)} 条")
                        return faqs
    except Exception as e:
        logger.debug(f"[Chunk {chunk_index}] 方法 7 失败：{e}")
    
    # 所有方法都失败
    logger.warning(f"[Chunk {chunk_index}] 所有方法都失败，响应预览：{response[:300]}...")
    return []


def fix_common_json_errors(text: str) -> str:
    """
    修复常见的 JSON 格式错误
    
    Args:
        text: 可能包含 JSON 的文本
        
    Returns:
        修复后的 JSON 字符串，如果无法修复则返回 None
    """
    import re
    
    # 提取 JSON 部分
    start_idx = text.find('[')
    end_idx = text.rfind(']') + 1
    if start_idx < 0 or end_idx <= start_idx:
        return None
    
    json_str = text[start_idx:end_idx]
    
    # 1. 移除行内注释（// 开头的）
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    
    # 2. 移除多行注释（/* */）
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # 3. 修复键名缺少引号的情况
    # 将 { key: "value" } 改为 { "key": "value" }
    json_str = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', json_str)
    
    # 4. 修复未闭合的代码块标记
    # 统计 ``` 的数量，如果是奇数，补充缺失的 ```
    code_block_count = json_str.count('```')
    if code_block_count % 2 == 1:
        # 在末尾添加 ``` 来闭合代码块
        # 但要在最后一个 ``` 之后添加
        last_backtick = json_str.rfind('```')
        if last_backtick >= 0:
            # 在最后一个 ``` 后面找第一个 " 的位置
            next_quote = json_str.find('"', last_backtick + 3)
            if next_quote > last_backtick:
                # 在 " 之前插入 ```
                json_str = json_str[:next_quote] + '```\n' + json_str[next_quote:]
    
    # 5. 修复字符串中未转义的双引号
    # 这个比较复杂，需要智能判断哪些双引号需要转义
    # 简单策略：将字符串内部的双引号替换为 \"
    # 注意：这个修复可能不完美，但对于简单情况有效
    
    # 6. 清理控制字符
    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    # 7. 移除末尾多余的逗号
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    # 8. 修复 URL 中的特殊字符（如果 URL 没有被正确引号包裹）
    # 将未转义的双引号进行转义（在 http:// 或 https:// 之前）
    json_str = re.sub(r'(?<!\\)"(https?://)', r'\\"\1', json_str)
    
    # 9. 修复未闭合的括号和引号（尝试平衡括号）
    # 统计括号数量
    open_brackets = json_str.count('[') - json_str.count(']')
    open_braces = json_str.count('{') - json_str.count('}')
    
    # 补充缺失的闭合括号
    json_str += ']' * open_brackets + '}' * open_braces
    
    return json_str


def extract_faq_parallel(content: str, ollama_client=None, chunk_size: int = 2000, max_workers: int = 3, domain_id: int = None) -> List[Dict]:
    """
    从文档内容中抽取 FAQ 对（并行处理版本）
    
    Args:
        content: 文档内容
        ollama_client: Ollama 客户端实例
        chunk_size: 每段文本的长度（默认 2000 字符）
        max_workers: 最大并发线程数（默认 3 个）
        domain_id: 专业领域 ID（可选）
        
    Returns:
        FAQ 列表
    """
    import json
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if not ollama_client:
        from utils.ollama_client import get_ollama_client
        ollama_client = get_ollama_client()

    # 分割文本
    chunks = []
    total_length = len(content)

    for i in range(0, total_length, chunk_size):
        chunk = content[i:i + chunk_size]
        if chunk.strip():  # 跳过空段落
            chunks.append({
                'index': i // chunk_size,
                'content': chunk,
                'start': i,
                'end': min(i + chunk_size, total_length)
            })

    logger.info(f"[FAQ_PARALLEL] Document total length: {total_length}, split into {len(chunks)} chunks")

    def process_chunk(chunk_info, retry_count: int = 3):
        """处理单个文本段（带重试机制）"""
        chunk_index = chunk_info['index']
        chunk_content = chunk_info['content']

        prompt = f"""请从以下文档片段中提取所有可能的问答对（FAQ）。
要求：
1. 识别文档中的所有问题和对应的答案
2. 如果没有明确的问题，根据内容总结可能的问题
3. 每个问答对应该完整、准确
4. 【重要】答案必须完整，包含所有步骤、子步骤、注意事项等详细信息
5. 【重要】保留原文中的图片链接（Markdown 格式：![描述](URL)）
6. 【重要】保留原文中的代码块、SQL 语句、命令等
7. 【重要】保留原文的格式，包括换行、列表、缩进等
8. 【重要】必须返回纯 JSON 数组，不要包含任何 Markdown 格式（如 ```json）
9. 【重要】不要有任何解释、说明或其他文字
10. JSON 格式示例：
[
    {{"question": "问题 1", "answer": "完整的答案（包含步骤、图片、代码等）"}},
    {{"question": "问题 2", "answer": "完整的答案"}}
]

文档片段：
{chunk_content}

请提取 FAQ（只返回纯 JSON 数组，不要任何其他内容，保留所有细节）：
"""

        for attempt in range(retry_count + 1):
            try:
                response = ollama_client.generate(prompt)

                logger.debug(f"第 {chunk_index} 段 AI 响应预览：{response[:200]}...")

                # 解析 JSON
                try:
                    faqs = json.loads(response.strip())
                except json.JSONDecodeError:
                    # 方法 1: 提取 JSON 部分（查找第一个 [ 和最后一个 ]）
                    start_idx = response.find('[')
                    end_idx = response.rfind(']') + 1

                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = response[start_idx:end_idx]
                        logger.debug(f"第 {chunk_index} 段提取 JSON: {start_idx} 到 {end_idx}")
                        # 清理特殊字符
                        json_str = json_str.replace('\n', '\\n').replace('\r', '\\r')
                        try:
                            faqs = json.loads(json_str)
                        except json.JSONDecodeError as e:
                            logger.warning(f"第 {chunk_index} 段 JSON 解析失败：{e}")
                            logger.debug(f"JSON 字符串：{json_str[:300]}...")
                            if attempt < retry_count:
                                logger.info(f"第 {chunk_index} 段重试 ({attempt + 1}/{retry_count})")
                                import time
                                time.sleep(1)
                                continue
                            return []
                    else:
                        # 方法 2: 尝试移除 Markdown 代码块标记
                        cleaned = response.strip()
                        if cleaned.startswith('```'):
                            # 移除 ```json 或 ``` 标记
                            lines = cleaned.split('\n')
                            if lines[0].startswith('```'):
                                lines = lines[1:]
                            if lines and lines[-1].startswith('```'):
                                lines = lines[:-1]
                            cleaned = '\n'.join(lines)
                            logger.debug(f"第 {chunk_index} 段移除 Markdown 标记")

                            # 再次尝试提取 JSON
                            start_idx = cleaned.find('[')
                            end_idx = cleaned.rfind(']') + 1
                            if start_idx >= 0 and end_idx > start_idx:
                                json_str = cleaned[start_idx:end_idx]
                                json_str = json_str.replace('\n', '\\n').replace('\r', '\\r')
                                try:
                                    faqs = json.loads(json_str)
                                except json.JSONDecodeError as e:
                                    logger.warning(f"第 {chunk_index} 段 JSON 解析失败 (清理后): {e}")
                                    if attempt < retry_count:
                                        logger.info(f"第 {chunk_index} 段重试 ({attempt + 1}/{retry_count})")
                                        import time
                                        time.sleep(1)
                                        continue
                                    return []
                            else:
                                logger.warning(f"第 {chunk_index} 段无法解析 JSON")
                                if attempt < retry_count:
                                    logger.info(f"第 {chunk_index} 段重试 ({attempt + 1}/{retry_count})")
                                    import time
                                    time.sleep(1)
                                    continue
                                return []
                        else:
                            logger.warning(f"第 {chunk_index} 段无法解析 JSON")
                            if attempt < retry_count:
                                logger.info(f"第 {chunk_index} 段重试 ({attempt + 1}/{retry_count})")
                                import time
                                time.sleep(1)
                                continue
                            return []

                if isinstance(faqs, list):
                    # 添加 domain_id 到每个 FAQ
                    for faq in faqs:
                        if domain_id:
                            faq['domain_id'] = domain_id
                    # 验证格式
                    valid_faqs = [faq for faq in faqs if
                                  isinstance(faq, dict) and 'question' in faq and 'answer' in faq]
                    logger.info(f"第 {chunk_index} 段提取 {len(valid_faqs)} 条 FAQ")
                    return valid_faqs
                else:
                    logger.warning(f"第 {chunk_index} 段 AI 返回的不是列表")
                    if attempt < retry_count:
                        logger.info(f"第 {chunk_index} 段重试 ({attempt + 1}/{retry_count})")
                        import time
                        time.sleep(1)
                        continue
                    return []

            except Exception as e:
                logger.error(f"第 {chunk_index} 段处理失败：{e}")
                if attempt < retry_count:
                    logger.info(f"第 {chunk_index} 段重试 ({attempt + 1}/{retry_count})")
                    import time
                    time.sleep(1)
                    continue
                return []

        logger.error(f"第 {chunk_index} 段已放弃（重试 {retry_count} 次后仍失败）")
        return []

    # 使用线程池并行处理
    all_faqs = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_chunk = {
            executor.submit(process_chunk, chunk): chunk
            for chunk in chunks
        }

        # 收集结果
        for future in as_completed(future_to_chunk):
            try:
                faqs = future.result()
                all_faqs.extend(faqs)
            except Exception as e:
                logger.error(f"线程执行错误：{e}")

    logger.info(f"并行处理完成，总共提取 {len(all_faqs)} 条 FAQ")
    return all_faqs
