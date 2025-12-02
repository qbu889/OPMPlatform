# utils/document_parser.py
from docx import Document


def parse_source_doc(file_path):
    """
    解析源文档，提取功能需求信息
    """
    try:
        doc = Document(file_path)
        parsed_data = []

        current_item = {}

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # 根据不同标题级别提取信息
            if para.style.name == 'Heading 1':
                current_item['一级分类'] = text
            elif para.style.name == 'Heading 2':
                current_item['二级分类'] = text
            elif para.style.name == 'Heading 3':
                current_item['三级分类'] = text
            elif para.style.name == 'Heading 4':
                current_item['功能点名称'] = text
            elif para.style.name == 'Heading 5':
                current_item['功能点计数项'] = text
            elif text.startswith('功能描述：'):
                current_item['功能描述'] = text.replace('功能描述：', '').strip()
            elif text.startswith('输入：'):
                current_item['输入'] = text.replace('输入：', '').strip()
            elif text.startswith('输出：'):
                current_item['输出'] = text.replace('输出：', '').strip()
            elif text.startswith('处理过程：'):
                current_item['处理过程'] = text.replace('处理过程：', '').strip()
            elif text.startswith('涉及数据文件：'):
                current_item['涉及数据文件'] = text.replace('涉及数据文件：', '').strip()

                # 当收集完一个完整项时，添加到结果中
                if '功能点计数项' in current_item:
                    current_item.setdefault('功能描述', '暂无描述')
                    current_item.setdefault('输入', '暂无输入说明')
                    current_item.setdefault('输出', '暂无输出说明')
                    current_item.setdefault('处理过程', '暂无处理过程说明')
                    current_item.setdefault('涉及数据文件', '无')

                    parsed_data.append(current_item.copy())
                    current_item = {}

        return parsed_data, None
    except Exception as e:
        return None, str(e)
