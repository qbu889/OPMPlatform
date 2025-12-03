from docx import Document
from flask import Flask, request, render_template, send_file, jsonify
import os
import logging
from utils.demo_generator import generate_demo_doc
import json
import re
from utils.document_formatter import analyze_template_format, apply_format_to_document, \
    enhanced_apply_format_to_document
# 导入所有需要的模块
from utils.document_parser import parse_source_doc
from utils.demo_validator import validate_demo_format
from utils.format_matcher import match_document_format

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用实例
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['JSON_AS_ASCII'] = False
app.config['DEMO_TEMPLATE_PATH'] = os.path.join(app.config['UPLOAD_FOLDER'], 'valid_demo.docx')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==================== 文档转换系统路由 ====================
# 添加新的路由处理文档格式化
@app.route('/format-document', methods=['POST'])
def format_document():
    """处理文档格式化请求"""
    logger.info("开始处理文档格式化请求")

    try:
        # 检查模板是否存在
        template_path = 'templates/功能需求_Demo模板.docx'
        if not os.path.exists(template_path):
            logger.warning("Demo模板不存在")
            return render_template('document_formatter.html',
                                   format_result={'success': False, 'msg': '格式模板不存在'})

        # 处理上传文件
        if 'source_file' not in request.files:
            logger.warning("未选择待格式化文件")
            return render_template('document_formatter.html',
                                   format_result={'success': False, 'msg': '未选择待格式化文件'})

        source_file = request.files['source_file']
        if source_file.filename == '':
            logger.warning("待格式化文件名为空")
            return render_template('document_formatter.html',
                                   format_result={'success': False, 'msg': '文件名不能为空'})

        # 保存上传文件
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], 'source_to_format.docx')
        source_file.save(source_path)
        logger.info(f"待格式化文件已保存至: {source_path}")

        # 分析模板格式
        logger.info("开始分析模板格式")
        template_format = analyze_template_format(template_path)

        # 应用格式到文档（使用增强版）
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'formatted_document.docx')
        logger.info("开始应用格式到文档")

        success, error = enhanced_apply_format_to_document(source_path, template_format, output_path)

        if not success:
            logger.error(f"文档格式化失败: {error}")
            return render_template('document_formatter.html',
                                   format_result={'success': False, 'msg': f'文档格式化失败：{error}'})

        logger.info("文档格式化成功")
        return render_template('document_formatter.html',
                               format_result={'success': True, 'msg': '文档格式化成功',
                                              'download_url': '/download-formatted-doc'})

    except Exception as e:
        logger.error(f"文档格式化过程中发生未预期错误: {str(e)}", exc_info=True)
        return render_template('document_formatter.html',
                               format_result={'success': False, 'msg': f'系统错误：{str(e)}'})


@app.route('/download-formatted-doc')
def download_formatted_doc():
    """下载格式化后的文档"""
    logger.info("开始处理格式化文档下载请求")
    formatted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'formatted_document.docx')
    if not os.path.exists(formatted_path):
        logger.error(f"格式化后的文档不存在: {formatted_path}")
        return jsonify({'success': False, 'msg': '格式化后的文档不存在'}), 404

    logger.info(f"成功找到格式化后的文档: {formatted_path}")
    return send_file(formatted_path, as_attachment=True,
                     download_name='格式化后的文档.docx')


# 添加格式化页面路由
@app.route('/document-formatter')
def document_formatter():
    """文档格式化页面"""
    logger.info("访问文档格式化页面")
    template_exists = os.path.exists('templates/功能需求_Demo模板.docx')
    logger.info(f"模板存在状态: {template_exists}")
    return render_template('document_formatter.html',
                           template_exists=template_exists,
                           format_result=None)
# 在 app.py 中添加文档预检函数
def inspect_document(doc_path):
    """检查文档基本信息"""
    try:
        doc = Document(doc_path)
        inspection_result = {
            'paragraph_count': len(doc.paragraphs),
            'table_count': len(doc.tables),
            'sample_paragraphs': [],
            'sample_tables': []
        }

        # 提取前几个段落样本
        for i, paragraph in enumerate(doc.paragraphs[:5]):
            inspection_result['sample_paragraphs'].append({
                'index': i,
                'text': paragraph.text[:100] + ('...' if len(paragraph.text) > 100 else '')
            })

        # 提取前几个表格样本
        for i, table in enumerate(doc.tables[:2]):
            table_info = {
                'index': i,
                'rows': len(table.rows),
                'cols': len(table.columns) if table.rows else 0,
                'sample_cells': []
            }
            if table.rows and len(table.rows) > 0 and len(table.rows[0].cells) > 0:
                for j, cell in enumerate(table.rows[0].cells[:3]):
                    table_info['sample_cells'].append({
                        'col_index': j,
                        'text': cell.text[:50] + ('...' if len(cell.text) > 50 else '')
                    })
            inspection_result['sample_tables'].append(table_info)

        return inspection_result
    except Exception as e:
        logger.error(f"文档检查失败: {str(e)}")
        return None
def initialize_template():
    """初始化模板文件"""
    template_path = 'templates/功能需求_Demo模板.docx'
    if not os.path.exists(template_path):
        # 创建目录
        os.makedirs('templates', exist_ok=True)
        # 创建一个基本的Word文档作为模板
        from docx import Document
        doc = Document()
        doc.add_heading('5.功能需求Demo模板', 0)
        doc.save(template_path)
        logger.info(f"已创建默认模板文件: {template_path}")

# 1. 下载标准Demo模板
@app.route('/download-demo-template')
def download_demo_template():
    logger.info("开始处理下载Demo模板请求")
    # 修正路径为相对路径
    template_path = 'templates/功能需求_Demo模板.docx'
    if os.path.exists(template_path):
        logger.info(f"成功找到模板文件: {template_path}")
        return send_file(template_path, as_attachment=True, download_name='功能需求_Demo模板.docx')
    else:
        logger.error(f"模板文件不存在: {template_path}")
        return jsonify({'success': False, 'msg': '模板文件不存在'}), 404


# 2. 上传并验证Demo格式
@app.route('/upload-demo', methods=['POST'])
def upload_demo():
    logger.info("开始处理Demo模板上传请求")
    if 'demo_file' not in request.files:
        logger.warning("未选择文件")
        return render_template('demo_upload.html', success=False, msg='未选择文件')

    demo_file = request.files['demo_file']
    if demo_file.filename == '':
        logger.warning("文件名为空")
        return render_template('demo_upload.html', success=False, msg='文件名不能为空')

    # 保存临时文件
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_demo.docx')
    demo_file.save(temp_path)
    logger.info(f"临时文件已保存至: {temp_path}")

    # 验证Demo格式
    logger.info("开始验证Demo格式")
    validation_result, error_details = validate_demo_format(temp_path)
    logger.info(f"验证结果: {validation_result}, 错误数量: {len(error_details) if error_details else 0}")

    if not validation_result:
        logger.warning(f"Demo格式验证失败，错误详情: {error_details}")
        os.remove(temp_path)  # 删除无效文件
        return render_template('demo_upload.html', success=False, msg='Demo格式验证失败', error_details=error_details)

    # 验证通过：保存为正式模板
    os.rename(temp_path, app.config['DEMO_TEMPLATE_PATH'])
    logger.info(f"Demo模板验证通过，已保存为正式模板: {app.config['DEMO_TEMPLATE_PATH']}")
    return render_template('demo_upload.html', success=True, msg='Demo模板上传验证成功，可进行下一步文档转换')

# 3. 转换页面入口
@app.route('/convert-page')
def convert_page():
    logger.info("访问转换页面")
    demo_exists = os.path.exists(app.config['DEMO_TEMPLATE_PATH'])
    logger.info(f"Demo模板存在状态: {demo_exists}")
    return render_template('convert_upload.html', demo_exists=demo_exists, convert_result=None)

# 4. 上传待转换文档并执行转换
# 在 app.py 中优化 upload_and_convert 函数
@app.route('/upload-and-convert', methods=['POST'])
def upload_and_convert():
    logger.info("开始处理文档转换请求")

    # 检查Demo模板是否存在
    if not os.path.exists(app.config['DEMO_TEMPLATE_PATH']):
        logger.warning("Demo模板不存在")
        # 添加格式化功能的提示
        return render_template('convert_upload.html', demo_exists=False,
                               convert_result=None, formatter_available=True)

    # 处理上传文件
    if 'convert_file' not in request.files:
        logger.warning("未选择待转换文件")
        return render_template('convert_upload.html', demo_exists=True,
                               convert_result={'success': False, 'msg': '未选择待转换文件'})

    convert_file = request.files['convert_file']
    if convert_file.filename == '':
        logger.warning("待转换文件名为空")
        return render_template('convert_upload.html', demo_exists=True,
                               convert_result={'success': False, 'msg': '文件名不能为空'})

    try:
        # 保存待转换文件
        source_path = os.path.join(app.config['UPLOAD_FOLDER'], 'source_doc.docx')
        convert_file.save(source_path)
        logger.info(f"待转换文件已保存至: {source_path}")

        # 文档预检
        inspection_result = inspect_document(source_path)
        if inspection_result:
            logger.info(
                f"文档检查结果: 段落数={inspection_result['paragraph_count']}, 表格数={inspection_result['table_count']}")

        # 步骤1：解析待转换文档，提取功能需求信息
        logger.info("开始解析待转换文档")
        parsed_data, parse_error = parse_source_doc(source_path)
        if parse_error:
            logger.error(f"文档解析失败: {parse_error}")
            return render_template('convert_upload.html', demo_exists=True,
                                   convert_result={'success': False, 'msg': f'文档解析失败：{parse_error}'})

        if not parsed_data or len(parsed_data) == 0:
            logger.warning("未解析到有效数据")
            # 提供更详细的错误信息帮助用户理解问题
            detailed_msg = ("文档中未找到有效的功能需求数据。请检查："
                           "1. 文档是否包含功能需求相关内容；"
                           "2. 文档格式是否符合要求；"
                           "3. 是否参考了标准模板格式")
            return render_template('convert_upload.html', demo_exists=True,
                                   convert_result={'success': False, 'msg': detailed_msg})

        logger.info(f"文档解析成功，共提取到 {len(parsed_data)} 条数据")

        # 步骤2：按Demo模板格式生成新文档
        output_doc_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_demo.docx')
        logger.info("开始生成转换后的文档")

        generate_success, generate_error = generate_demo_doc(
            demo_template_path=app.config['DEMO_TEMPLATE_PATH'],
            parsed_data=parsed_data,
            output_path=output_doc_path
        )

        if not generate_success:
            logger.error(f"文档转换失败: {generate_error}")
            return render_template('convert_upload.html', demo_exists=True,
                                   convert_result={'success': False, 'msg': f'文档转换失败：{generate_error}'})

        logger.info(f"文档转换成功，输出文件路径: {output_doc_path}")

        # 转换成功，返回下载链接
        return render_template('convert_upload.html', demo_exists=True, convert_result={
            'success': True,
            'msg': f'文档已成功转换为Demo格式，共处理 {len(parsed_data)} 条数据',
            'download_url': '/download-converted-doc'
        })

    except Exception as e:
        logger.error(f"文档转换过程中发生未预期错误: {str(e)}", exc_info=True)
        return render_template('convert_upload.html', demo_exists=True,
                               convert_result={'success': False, 'msg': f'系统错误：{str(e)}'})



# 5. 下载转换后的Demo文档
@app.route('/download-converted-doc')
def download_converted_doc():
    logger.info("开始处理转换后文档下载请求")
    converted_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_demo.docx')
    if not os.path.exists(converted_path):
        logger.error(f"转换后的文档不存在: {converted_path}")
        return jsonify({'success': False, 'msg': '转换后的文档不存在'}), 404

    logger.info(f"成功找到转换后的文档: {converted_path}")
    return send_file(converted_path, as_attachment=True, download_name='转换后_5_功能需求_Demo文档.docx')

# 文档格式检查路由
@app.route('/format-check', methods=['POST'])
def format_check():
    """
    检查上传文档与标准格式的匹配度
    """
    logger.info("开始文档格式检查")

    if 'document_file' not in request.files:
        logger.warning("未选择文件")
        return render_template('format_check.html',
                               result={"match_rate": 0, "errors": ["未选择文件"]})

    doc_file = request.files['document_file']
    if doc_file.filename == '':
        logger.warning("文件名为空")
        return render_template('format_check.html',
                               result={"match_rate": 0, "errors": ["文件名不能为空"]})

    # 保存临时文件
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_check.docx')
    doc_file.save(temp_path)
    logger.info(f"临时文件已保存至: {temp_path}")

    # 标准模板路径
    standard_template_path = 'templates/功能需求_Demo模板.docx'
    # 执行格式匹配
    match_result = match_document_format(temp_path, standard_template_path)

    # 清理临时文件
    os.remove(temp_path)

    logger.info(f"格式检查完成，匹配度: {match_result['match_rate']:.2f}")
    return render_template('format_check.html', result=match_result)

# ==================== SQL ID格式化工具路由 ====================

# SQL ID格式化工具主页面
@app.route('/sql-formatter')
def sql_formatter():
    """SQL ID格式化工具页面"""
    return render_template('sql_formatter.html')

# 处理ID格式化请求
@app.route('/format_ids', methods=['POST'])
def format_ids():
    """处理ID格式化请求"""
    # 获取前端传入的ID文本
    ids_text = request.form.get('ids', '')

    # 按行分割并清理空白字符
    ids_list = [id.strip() for id in ids_text.split('\n') if id.strip()]

    if not ids_list:
        return jsonify({
            'success': False,
            'error': '未输入任何ID'
        })

    # 格式化为SQL格式
    formatted_ids = [f"'{id}'" for id in ids_list]

    if len(ids_list) == 1:
        # 单个ID使用等号
        sql_result = f"'{ids_list[0]}'"
        sql_query = f"WHERE w1.sheet_id = '{ids_list[0]}'"
    else:
        # 多个ID使用IN语句
        sql_result = ',\n'.join(formatted_ids)
        sql_query = f"WHERE w1.sheet_id IN (\n{sql_result}\n)"

    return jsonify({
        'success': True,
        'formatted_ids': sql_result,
        'sql_query': sql_query,
        'count': len(ids_list)
    })


@app.route('/clean-event-page')
def clean_event_page():
    """事件数据清洗页面"""
    return render_template('clean_event.html')


@app.route('/clean-event', methods=['POST'])
def clean_event():
    """处理事件数据清洗请求"""
    try:
        data = request.get_json()
        fp_value = data.get('fp_value')
        event_time = data.get('event_time')

        if not fp_value or not event_time:
            return jsonify({'error': '缺少必需参数'}), 400

        # 修改FP值验证：只要求非空且长度不超过1000
        if not fp_value.strip() or len(fp_value) > 1000:
            return jsonify({'error': 'FP值不能为空且长度不能超过1000个字符'}), 400

        # 时间格式验证，支持多种格式
        time_pattern1 = r'^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}$'  # YYYY/MM/DD HH:MM
        time_pattern2 = r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}$'   # YYYY-MM-DD HH:MM
        time_pattern3 = r'^\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}$'  # YYYY-MM-DD HH:MM:SS

        if not (re.match(time_pattern1, event_time) or
                re.match(time_pattern2, event_time) or
                re.match(time_pattern3, event_time)):
            return jsonify({'error': '时间格式不正确，支持格式: YYYY/MM/DD HH:MM 或 YYYY-MM-DD HH:MM'}), 400

        # 处理数据
        result = clean_event_data(fp_value, event_time)
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': f'处理数据时发生错误: {str(e)}'}), 500



# 修改 clean_event_data 函数以支持多种时间格式
def clean_event_data(fp_value, event_time):
    """清洗事件数据"""
    active_status = "3"  # 保持不变

    # 统一处理日期分隔符，将"/"替换为"-"
    cleaned_time = event_time.replace("/", "-")

    # 分割日期和时间部分
    if " " in cleaned_time:
        date_part, time_part = cleaned_time.split(" ", 1)
    else:
        # 如果只有日期部分，默认时间为00:00
        date_part = cleaned_time
        time_part = "00:00:00"

    # 处理日期部分
    if "-" in date_part:
        date_components = date_part.split("-")
        if len(date_components) >= 3:
            year, month, day = date_components[0], date_components[1], date_components[2]
        else:
            raise ValueError("日期格式不正确")
    else:
        raise ValueError("日期格式不正确")

    # 处理时间部分
    if ":" in time_part:
        time_components = time_part.split(":")
        if len(time_components) >= 2:
            hour, minute = time_components[0], time_components[1]
            # 如果有秒部分则保留，否则设为00
            second = time_components[2] if len(time_components) >= 3 else "00"
        else:
            hour, minute, second = time_components[0], "00", "00"
    else:
        hour, minute, second = "00", "00", "00"

    # 确保各部分为两位数
    formatted_hour = hour.zfill(2)
    formatted_minute = minute.zfill(2)
    formatted_second = second.zfill(2)

    # 确保年月日为正确格式
    cleaned_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    cleaned_event_time = f"{cleaned_date} {formatted_hour}:{formatted_minute}:{formatted_second}"

    # 构建目标格式数据
    result = {
        "ACTIVE_STATUS": active_status,
        "EVENT_TIME": cleaned_event_time,
        "FP0_FP1_FP2_FP3": fp_value,
        "CFP0_CFP1_CFP2_CFP3": fp_value
    }

    return result


# ==================== 主页路由 ====================

# 首页路由
@app.route('/')
def index():
    """系统首页：提供步骤导航"""
    logger.info("访问系统首页")
    demo_exists = os.path.exists(app.config['DEMO_TEMPLATE_PATH'])
    logger.info(f"Demo模板存在状态: {demo_exists}")
    return render_template('index.html', demo_exists=demo_exists)

# 跳转Demo上传页面
@app.route('/upload-demo-page')
def upload_demo_page():
    """跳转Demo上传页面"""
    logger.info("访问Demo上传页面")
    return render_template('demo_upload.html', success=False, msg='')

# ==================== 应用启动 ====================

if __name__ == '__main__':
    logger.info("启动Flask应用")
    # 启动应用，端口5000用于文档转换系统，端口5002用于SQL工具
    app.run(debug=True, host='0.0.0.0', port=5001)
