# utils/document_parser.py
from docx import Document


def parse_source_doc(file_path):
    """
    解析源文档，提取功能需求信息
    """
    # 延迟导入，避免循环依赖
    from app import logger
    try:
        logger.info(f"[DOC_PARSE] Starting document parsing: {file_path}")
        doc = Document(file_path)
        parsed_data = []

        # 确保正确遍历所有段落
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:  # 跳过空段落
                continue

            # 检查段落样式和内容
            style_name = para.style.name
            logger.debug(f"[DOC_PARSE] Paragraph: '{text}' | Style: '{style_name}'")

            # 根据实际文档结构调整解析逻辑
            # 可能需要调整样式识别条件
            if style_name.startswith('Heading'):
                # 处理标题段落
                pass
            else:
                # 处理正文段落
                pass

        logger.info(f"[DOC_PARSE] Parsing completed, extracted {len(parsed_data)} items")
        return parsed_data, None
    except Exception as e:
        error_msg = f"[DOC_PARSE] Parsing error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return None, error_msg
