# utils/demo_validator.py
from docx import Document
import logging

logger = logging.getLogger(__name__)

def validate_demo_format(doc_path):
    """
    验证文档是否符合5.功能需求Demo格式
    返回：(验证结果, 错误详情列表)
    """
    try:
        logger.info(f"开始验证文档格式: {doc_path}")
        doc = Document(doc_path)
        error_details = []
        current_level = {
            '一级分类': None,
            '二级分类': None,
            '三级分类': None,
            '功能点名称': None,
            '功能点计数项': None
        }

        # 将段落列表固定，避免重复访问时对象不一致
        paragraphs = list(doc.paragraphs)
        logger.debug(f"文档共包含 {len(paragraphs)} 个段落")

        # 遍历文档段落，检查层级结构（通过标题级别判断：Heading 1=一级，Heading 2=二级，以此类推）
        for i, para in enumerate(paragraphs):
            if para.style.name.startswith('Heading'):
                heading_level = int(para.style.name.replace('Heading ', ''))
                para_text = para.text.strip()
                logger.debug(f"处理第 {i+1} 个段落，标题级别: {heading_level}, 内容: {para_text}")

                # 一级分类（Heading 1）
                if heading_level == 1:
                    if not para_text:
                        error_msg = '一级分类名称不能为空'
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                    current_level['一级分类'] = para_text
                    # 重置下级层级
                    current_level['二级分类'] = None
                    current_level['三级分类'] = None
                    current_level['功能点名称'] = None
                    current_level['功能点计数项'] = None
                    logger.debug(f"设置一级分类: {para_text}")

                # 二级分类（Heading 2）
                elif heading_level == 2:
                    if not current_level['一级分类']:
                        error_msg = f'二级分类「{para_text}」前缺少一级分类'
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                    if not para_text:
                        error_msg = '二级分类名称不能为空'
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                    current_level['二级分类'] = para_text
                    current_level['三级分类'] = None
                    current_level['功能点名称'] = None
                    current_level['功能点计数项'] = None
                    logger.debug(f"设置二级分类: {para_text}")

                # 三级分类（Heading 3）
                elif heading_level == 3:
                    if not current_level['二级分类']:
                        error_msg = f'三级分类「{para_text}」前缺少二级分类'
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                    current_level['三级分类'] = para_text
                    current_level['功能点名称'] = None
                    current_level['功能点计数项'] = None
                    logger.debug(f"设置三级分类: {para_text}")

                # 功能点名称（Heading 4）
                elif heading_level == 4:
                    if not current_level['三级分类']:
                        error_msg = f'功能点名称「{para_text}」前缺少三级分类'
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                    current_level['功能点名称'] = para_text
                    current_level['功能点计数项'] = None
                    logger.debug(f"设置功能点名称: {para_text}")

                # 功能点计数项（Heading 5）
                elif heading_level == 5:
                    if not current_level['功能点名称']:
                        error_msg = f'功能点计数项「{para_text}」前缺少功能点名称'
                        error_details.append(error_msg)
                        logger.warning(error_msg)
                    current_level['功能点计数项'] = para_text
                    logger.debug(f"设置功能点计数项: {para_text}")

                    # 检查计数项是否包含必要子字段（功能描述、输入、输出等）
                    # （逻辑：遍历后续段落，直到下一个标题前，检查是否有指定关键词）
                    next_para_idx = i + 1
                    has_function_desc = False
                    has_input = False
                    has_output = False

                    while next_para_idx < len(paragraphs):
                        next_para = paragraphs[next_para_idx]
                        if next_para.style.name.startswith('Heading'):
                            break  # 遇到下一个标题，停止检查

                        next_para_text = next_para.text.strip()

                        if '功能描述：' in next_para_text:
                            has_function_desc = True
                        elif '输入：' in next_para_text:
                            has_input = True
                        elif '输出：' in next_para_text:
                            has_output = True

                        next_para_idx += 1

                    # 将强制性验证改为可选性检查
                    if not has_function_desc:
                        logger.warning(f'功能点计数项「{para_text}」缺少「功能描述」字段')
                        # 注释掉错误添加行，仅记录警告
                        error_details.append(f'功能点计数项「{para_text}」缺少「功能描述」字段')

                    if not has_input:
                        logger.warning(f'功能点计数项「{para_text}」缺少「输入」字段')
                        error_details.append(f'功能点计数项「{para_text}」缺少「输入」字段')

                    if not has_output:
                        logger.warning(f'功能点计数项「{para_text}」缺少「输出」字段')
                        error_details.append(f'功能点计数项「{para_text}」缺少「输出」字段')

        # 若有错误，返回失败；否则返回成功
        validation_result = len(error_details) == 0
        logger.info(f"文档格式验证完成，结果: {'通过' if validation_result else '不通过'}, 错误数量: {len(error_details)}")
        return validation_result, error_details
    except Exception as e:
        error_msg = f"验证过程出错: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, [error_msg]
