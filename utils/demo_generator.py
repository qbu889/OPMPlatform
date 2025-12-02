# utils/demo_generator.py
from docx import Document
import logging

logger = logging.getLogger(__name__)


def generate_demo_doc(demo_template_path, parsed_data, output_path):
    """
    按Demo模板生成转换后的文档
    """
    try:
        logger.info(f"开始生成文档，模板路径: {demo_template_path}, 输出路径: {output_path}")
        logger.debug(f"待处理数据条数: {len(parsed_data)}")

        # 创建新文档（不基于模板以避免格式问题）
        doc = Document()

        # 添加标题
        doc.add_heading('5.功能需求', 1)

        # 跟踪当前层级状态
        current_levels = {
            '一级分类': None,
            '二级分类': None,
            '三级分类': None,
            '功能点名称': None
        }

        for item in parsed_data:
            # 生成一级分类（Heading 1）
            if item.get('一级分类') and item['一级分类'] != current_levels['一级分类']:
                current_levels['一级分类'] = item['一级分类']
                para = doc.add_paragraph(current_levels['一级分类'])
                para.style = doc.styles['Heading 1']
                logger.debug(f"生成一级分类: {current_levels['一级分类']}")

            # 生成二级分类（Heading 2）
            if item.get('二级分类') and item['二级分类'] != current_levels['二级分类']:
                current_levels['二级分类'] = item['二级分类']
                para = doc.add_paragraph(current_levels['二级分类'])
                para.style = doc.styles['Heading 2']
                logger.debug(f"生成二级分类: {current_levels['二级分类']}")

            # 生成三级分类（Heading 3）
            if item.get('三级分类') and item['三级分类'] != current_levels['三级分类']:
                current_levels['三级分类'] = item['三级分类']
                para = doc.add_paragraph(current_levels['三级分类'])
                para.style = doc.styles['Heading 3']
                logger.debug(f"生成三级分类: {current_levels['三级分类']}")

            # 生成功能点名称（Heading 4）
            if item.get('功能点名称') and item['功能点名称'] != current_levels['功能点名称']:
                current_levels['功能点名称'] = item['功能点名称']
                para = doc.add_paragraph(current_levels['功能点名称'])
                para.style = doc.styles['Heading 4']
                logger.debug(f"生成功能点名称: {current_levels['功能点名称']}")

            # 生成功能点计数项（Heading 5）
            if item.get('功能点计数项'):
                para = doc.add_paragraph(item['功能点计数项'])
                para.style = doc.styles['Heading 5']
                logger.debug(f"生成功能点计数项: {item['功能点计数项']}")

            # 生成计数项子字段
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

            # 每个计数项后添加空行分隔
            doc.add_paragraph()

        # 保存生成的文档
        doc.save(output_path)
        logger.info(f"文档生成完成，文件已保存至: {output_path}")
        return True, None
    except Exception as e:
        error_msg = f"文档生成过程中发生错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
