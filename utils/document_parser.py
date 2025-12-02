# utils/document_parser.py
from docx import Document
import logging

logger = logging.getLogger(__name__)


def parse_source_doc(file_path):
    """
    解析源文档，提取功能需求信息
    """
    try:
        logger.info(f"开始解析文档: {file_path}")
        doc = Document(file_path)
        parsed_data = []

        current_item = {}
        processed_items = 0

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # 根据不同标题级别提取信息
            if para.style.name == 'Heading 1':
                current_item['一级分类'] = text
                logger.debug(f"提取一级分类: {text}")
            elif para.style.name == 'Heading 2':
                current_item['二级分类'] = text
                logger.debug(f"提取二级分类: {text}")
            elif para.style.name == 'Heading 3':
                current_item['三级分类'] = text
                logger.debug(f"提取三级分类: {text}")
            elif para.style.name == 'Heading 4':
                current_item['功能点名称'] = text
                logger.debug(f"提取功能点名称: {text}")
            elif para.style.name == 'Heading 5':
                current_item['功能点计数项'] = text
                logger.debug(f"提取功能点计数项: {text}")
            elif text.startswith('功能描述：'):
                current_item['功能描述'] = text.replace('功能描述：', '').strip()
                logger.debug(f"提取功能描述: {current_item['功能描述']}")
            elif text.startswith('输入：'):
                current_item['输入'] = text.replace('输入：', '').strip()
                logger.debug(f"提取输入: {current_item['输入']}")
            elif text.startswith('输出：'):
                current_item['输出'] = text.replace('输出：', '').strip()
                logger.debug(f"提取输出: {current_item['输出']}")
            elif text.startswith('处理过程：'):
                current_item['处理过程'] = text.replace('处理过程：', '').strip()
                logger.debug(f"提取处理过程: {current_item['处理过程']}")
            elif text.startswith('涉及数据文件：'):
                current_item['涉及数据文件'] = text.replace('涉及数据文件：', '').strip()
                logger.debug(f"提取涉及数据文件: {current_item['涉及数据文件']}")

                # 当收集完一个完整项时，添加到结果中
                if '功能点计数项' in current_item:
                    parsed_data.append(current_item.copy())
                    processed_items += 1
                    logger.debug(f"完成第 {processed_items} 项数据提取")
                    current_item = {}

        logger.info(f"文档解析完成，共提取 {len(parsed_data)} 条数据")
        return parsed_data, None
    except Exception as e:
        logger.error(f"文档解析过程中发生错误: {str(e)}", exc_info=True)
        return None, str(e)
