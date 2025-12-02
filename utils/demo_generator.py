# utils/demo_generator.py
from docx import Document
from docx.shared import Pt
from docx.enum.style import WD_STYLE_TYPE
import logging

logger = logging.getLogger(__name__)


def create_styles(doc):
    """创建所需的样式"""
    # 创建标题样式
    for i in range(1, 6):
        style_name = f'Custom Heading {i}'
        if style_name not in [s.name for s in doc.styles]:
            style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)
            style.base_style = doc.styles['Heading ' + str(i)]
            font = style.font
            font.size = Pt(14 - i)  # 逐级减小字体


def generate_demo_doc(template_path, parsed_data, output_path):
    """
    按照标准格式生成功能需求文档
    """
    try:
        logger.info(f"开始生成文档: {output_path}")

        # 创建新文档
        doc = Document()
        create_styles(doc)

        # 添加主标题
        title_para = doc.add_paragraph('5.功能需求')
        title_para.style = doc.styles['Title']

        # 跟踪当前层级状态
        current_levels = {
            '一级分类': None,
            '二级分类': None,
            '三级分类': None,
            '功能点名称': None
        }

        # 用于编号的计数器
        counters = {
            '一级': 0,
            '二级': 0,
            '三级': 0,
            '功能点': 0,
            '计数项': 0
        }

        for item in parsed_data:
            # 一级分类处理
            if item.get('一级分类') and item['一级分类'] != current_levels['一级分类']:
                counters['一级'] += 1
                counters['二级'] = 0
                counters['三级'] = 0
                counters['功能点'] = 0
                counters['计数项'] = 0

                current_levels['一级分类'] = item['一级分类']
                current_levels['二级分类'] = None
                current_levels['三级分类'] = None
                current_levels['功能点名称'] = None

                # 添加一级分类（Heading 1）
                heading_text = f"{counters['一级']} {item['一级分类']}"
                para = doc.add_paragraph(heading_text)
                para.style = doc.styles['Heading 1']
                logger.debug(f"添加一级分类: {heading_text}")

            # 二级分类处理
            if item.get('二级分类') and item['二级分类'] != current_levels['二级分类']:
                counters['二级'] += 1
                counters['三级'] = 0
                counters['功能点'] = 0
                counters['计数项'] = 0

                current_levels['二级分类'] = item['二级分类']
                current_levels['三级分类'] = None
                current_levels['功能点名称'] = None

                # 添加二级分类（Heading 2）
                heading_text = f"{counters['一级']}.{counters['二级']} {item['二级分类']}"
                para = doc.add_paragraph(heading_text)
                para.style = doc.styles['Heading 2']
                logger.debug(f"添加二级分类: {heading_text}")

            # 三级分类处理
            if item.get('三级分类') and item['三级分类'] != current_levels['三级分类']:
                counters['三级'] += 1
                counters['功能点'] = 0
                counters['计数项'] = 0

                current_levels['三级分类'] = item['三级分类']
                current_levels['功能点名称'] = None

                # 添加三级分类（Heading 3）
                heading_text = f"{counters['一级']}.{counters['二级']}.{counters['三级']} {item['三级分类']}"
                para = doc.add_paragraph(heading_text)
                para.style = doc.styles['Heading 3']
                logger.debug(f"添加三级分类: {heading_text}")

            # 功能点名称处理
            if item.get('功能点名称') and item['功能点名称'] != current_levels['功能点名称']:
                counters['功能点'] += 1
                counters['计数项'] = 0

                current_levels['功能点名称'] = item['功能点名称']

                # 添加功能点名称（Heading 4）
                heading_text = f"{counters['一级']}.{counters['二级']}.{counters['三级']}.{counters['功能点']} {item['功能点名称']}"
                para = doc.add_paragraph(heading_text)
                para.style = doc.styles['Heading 4']
                logger.debug(f"添加功能点名称: {heading_text}")

            # 功能点计数项处理
            if item.get('功能点计数项'):
                counters['计数项'] += 1

                # 添加功能点计数项（Heading 5）
                heading_text = f"{counters['一级']}.{counters['二级']}.{counters['三级']}.{counters['功能点']}.{counters['计数项']} {item['功能点计数项']}"
                para = doc.add_paragraph(heading_text)
                para.style = doc.styles['Heading 5']
                logger.debug(f"添加功能点计数项: {heading_text}")

                # 添加详细信息
                if item.get('功能描述'):
                    doc.add_paragraph(f"功能描述：{item['功能描述']}")
                if item.get('输入'):
                    doc.add_paragraph(f"输入：{item['输入']}")
                if item.get('输出'):
                    doc.add_paragraph(f"输出：{item['输出']}")
                if item.get('处理过程'):
                    doc.add_paragraph(f"处理过程：{item['处理过程']}")
                if item.get('涉及数据文件'):
                    doc.add_paragraph(f"涉及数据文件：{item['涉及数据文件']}")

                # 添加空行分隔
                doc.add_paragraph("")

        # 保存文档
        doc.save(output_path)
        logger.info(f"文档生成完成: {output_path}")
        return True, None
    except Exception as e:
        error_msg = f"文档生成失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
