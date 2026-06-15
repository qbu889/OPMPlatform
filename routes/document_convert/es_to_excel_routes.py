"""
ES 查询结果转 Excel 路由
支持：
  1. 文件上传（txt 竖线分隔 / JSON / ES SQL 表格）
  2. 文本粘贴（直接粘贴 ES SQL 查询结果）
  3. 字段中英文映射（基于 MySQL 数据库配置）
"""
import os
import re
import time
import sys
import csv
import json
import mysql.connector
import pandas as pd
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import logging

from utils.ES结果导Excel.EsToExcel import parse_es_result, export_to_excel

logger = logging.getLogger(__name__)

# 创建蓝图
es_to_excel_bp = Blueprint('es_to_excel', __name__, url_prefix='/api/es-to-excel')

# 配置上传和输出目录
UPLOAD_FOLDER = Path('uploads/es_to_excel')
OUTPUT_FOLDER = Path('downloads/es_to_excel')
ALLOWED_EXTENSIONS = {'txt', 'json'}

# 确保目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


def _parse_json_with_control_char_fix(raw_data):
    """安全解析 JSON，自动清理非法控制字符。

    当请求体包含未转义的控制字符（如 \\x01-\\x1f 中除 \\n, \\t, \\r 外的字符）时，
    Flask 的 request.json 会抛出 JSONDecodeError。此函数先清理控制字符再解析。

    修复内容：
    - 预处理三引号（\"\"\"），将其替换为合法的 JSON 转义序列（\\\"）
    - 正则表达式添加 re.DOTALL 标志，确保能匹配跨行字符串值
    - 将字符串内的字面控制字符（\\n, \\r, \\t 字节）转换为 JSON 转义序列（\\\\n, \\\\r, \\\\t）
    - 同时清理 JSON 结构部分（字符串之外）的字面控制字符
    """
    try:
        return json.loads(raw_data)
    except (json.JSONDecodeError, TypeError):
        pass

    try:
        raw_bytes = raw_data if isinstance(raw_data, bytes) else raw_data.encode('utf-8')
    except Exception:
        raise ValueError("无法解析请求体数据")

    try:
        raw_str = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        try:
            raw_str = raw_bytes.decode('latin-1')
        except Exception:
            raise ValueError("无法解码请求体数据")

    # 预处理：移除三引号（\"\"\"）作为 ES SQL 响应格式的分隔符
    # ES SQL 响应中，字符串值可能包含 \"\"\" 包裹多行文本（如定界结果），
    # 这不是合法的 JSON。策略：直接移除所有 \"\"\"（它们只是 ES SQL 的分隔符，
    # 内容本身才是有用的），然后继续清理控制字符。
    raw_str = raw_str.replace('"""', '')

    # 清理 JSON 字符串值中的非法控制字符
    # 策略：匹配 JSON 字符串值（引号内的内容），将字面控制字符转换为
    # JSON 转义序列（\\n, \\r, \\t），移除其他非法控制字符（\\x01-\\x1f）和 DEL (0x7f)
    def clean_json_string_value(match):
        full = match.group(0)
        start_q = full.find('"')
        end_q = full.rfind('"')
        if start_q == end_q:
            return full

        prefix = full[:start_q + 1]
        inner = full[start_q + 1:end_q]
        suffix = full[end_q:]

        # 将字面控制字符转换为 JSON 转义序列
        cleaned = inner.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        # 移除其他非法控制字符（\\x01-\\x1f，排除 \\n, \\t, \\r 已转换）
        cleaned = ''.join(
            ch if 0x20 <= ord(ch) or ord(ch) == 0 else ''
            for ch in cleaned
        )
        # 同时移除 DEL (0x7f)
        cleaned = cleaned.replace('\x7f', '')

        return prefix + cleaned + suffix

    # 匹配 JSON 字符串值（处理转义引号）
    # 使用 re.DOTALL 确保 . 匹配换行符，从而正确处理跨行字符串值
    cleaned_str = re.sub(
        r'"(?:[^"\\]|\\.)*"',
        clean_json_string_value,
        raw_str,
        flags=re.DOTALL
    )

    # 清理 JSON 结构部分（字符串之外）的字面控制字符
    def clean_json_structure(match):
        text = match.group(0)
        # 将字面控制字符转换为 JSON 转义序列
        text = text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        # 移除其他非法控制字符（\\x01-\\x1f，排除 \\n, \\t, \\r 已转换）
        text = ''.join(
            ch if 0x20 <= ord(ch) or ord(ch) == 0 else ''
            for ch in text
        )
        # 移除 DEL (0x7f)
        return text.replace('\x7f', '')

    # 匹配非字符串部分（JSON 结构：括号、逗号、冒号、键名等）
    cleaned_str = re.sub(
        r'(?:"(?:[^"\\]|\\.)*"|[^"\\])',
        clean_json_structure,
        raw_str,  # 使用原始字符串清理结构部分
        flags=re.DOTALL
    )

    try:
        return json.loads(cleaned_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 格式错误：{e.msg} at line {e.lineno}, column {e.colno}")


def _clean_string_value(match_str):
    """清理 JSON 字符串值中的字面控制字符，转换为合法的 JSON 转义序列。

    Args:
        match_str: 正则匹配到的完整字符串（包含首尾双引号）

    Returns:
        清理后的字符串值，控制字符已转换为 \\n, \\r, \\t 等转义序列
    """
    start_q = match_str.find('"')
    end_q = match_str.rfind('"')
    if start_q == end_q:
        return match_str

    prefix = match_str[:start_q + 1]
    inner = match_str[start_q + 1:end_q]
    suffix = match_str[end_q:]

    # 将字面控制字符转换为 JSON 转义序列
    cleaned = inner.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    # 移除其他非法控制字符（\\x01-\\x1f，排除 \\n, \\t, \\r 已转换）
    cleaned = ''.join(
        ch if 0x20 <= ord(ch) or ord(ch) == 0 else ''
        for ch in cleaned
    )
    # 同时移除 DEL (0x7f)
    cleaned = cleaned.replace('\x7f', '')

    return prefix + cleaned + suffix


def _get_field_mapping():
    """获取最新的字段映射（实时从数据库查询）"""
    try:
        conn = mysql.connector.connect(
            host=current_app.config.get('MYSQL_HOST', 'localhost'),
            port=current_app.config.get('MYSQL_PORT', 3306),
            user=current_app.config.get('MYSQL_USER', 'root'),
            password=current_app.config.get('MYSQL_PASSWORD', '12345678'),
            charset=current_app.config.get('MYSQL_CHARSET', 'utf8mb4'),
            database=current_app.config.get('KNOWLEDGE_BASE_DB', 'knowledge_base')
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT english_name, chinese_name 
            FROM es_field_mapping 
            WHERE is_active = TRUE
            ORDER BY sort_order ASC, id ASC
        """)
        rows = cursor.fetchall()
        
        mapping = {row['english_name']: row['chinese_name'] for row in rows}
        
        cursor.close()
        conn.close()
        
        return mapping
    except Exception as e:
        logger.error(f"⚠️  从数据库获取字段映射失败: {e}")
        # 返回内存中的缓存作为后备
        return FIELD_MAPPING

# 初始化时加载一次作为缓存
FIELD_MAPPING = {}

def init_field_mapping(app):
    """初始化字段映射（需要在 Flask app 上下文中调用）"""
    global FIELD_MAPPING
    with app.app_context():
        try:
            FIELD_MAPPING = _get_field_mapping()
            logger.info(f"✅ ES 字段映射初始化完成，共 {len(FIELD_MAPPING)} 条")
        except Exception as e:
            logger.error(f"⚠️  ES 字段映射初始化失败: {e}")


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _apply_chinese_mapping(df, use_chinese_names):
    """
    应用中文映射到 DataFrame 的列名
    
    Args:
        df: pandas DataFrame
        use_chinese_names: 是否使用中文字段名
    
    Returns:
        处理后的 DataFrame
    """
    if not use_chinese_names:
        return df
    
    # 实时从数据库获取最新映射
    current_mapping = _get_field_mapping()
    if not current_mapping:
        return df
    
    original_columns = list(df.columns)
    new_columns = []
    mapped_count = 0
    
    for col in original_columns:
        # 尝试直接匹配
        if col in current_mapping:
            new_columns.append(current_mapping[col])
            mapped_count += 1
        else:
            # 如果包含点号，尝试匹配点号后面的部分
            if '.' in col:
                simple_name = col.split('.')[-1]  # 取最后一部分
                if simple_name in current_mapping:
                    new_columns.append(current_mapping[simple_name])
                    mapped_count += 1
                else:
                    new_columns.append(col)  # 保持原名
            else:
                new_columns.append(col)  # 保持原名
    
    df.columns = new_columns
    logger.info(f"已应用中文字段名映射，共 {mapped_count} 个字段被映射")
    
    return df


@es_to_excel_bp.route('/upload', methods=['POST'])
def upload_file():
    """上传 ES 查询结果文件（支持单个或多个文件）"""
    try:
        if 'file' not in request.files and 'files' not in request.files:
            return jsonify({'success': False, 'message': '没有上传文件'}), 400

        # 支持单个文件或多个文件
        files = request.files.getlist('files') if 'files' in request.files else [request.files['file']]
        
        uploaded_files = []
        for file in files:
            if file.filename == '':
                continue

            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': f'不支持的文件格式：{file.filename}'}), 400

            # 生成唯一文件名
            timestamp = int(time.time() * 1000)
            original_filename = secure_filename(file.filename)
            unique_filename = f"{Path(original_filename).stem}_{timestamp}{Path(original_filename).suffix}"

            # 保存文件
            file_path = UPLOAD_FOLDER / unique_filename
            file.save(file_path)
            
            uploaded_files.append({
                'filename': unique_filename,
                'original_name': original_filename
            })

        logger.info(f"文件上传成功：{len(uploaded_files)} 个文件")

        return jsonify({
            'success': True,
            'message': f'成功上传 {len(uploaded_files)} 个文件',
            'files': uploaded_files
        })

    except Exception as e:
        logger.error(f"文件上传失败：{e}", exc_info=True)
        return jsonify({'success': False, 'message': f'上传失败：{str(e)}'}), 500


@es_to_excel_bp.route('/convert', methods=['POST'])
def convert_to_excel():
    """将 ES 查询结果转换为 Excel（支持单个或多个文件）"""
    try:
        data = request.json
        filenames = data.get('filenames') or ([data.get('filename')] if data.get('filename') else [])
        excel_format = data.get('format', 'xlsx')  # 默认 xlsx，可选 xls
        use_chinese_names = data.get('use_chinese_names', False)  # 是否使用中文字段名

        if not filenames:
            return jsonify({'success': False, 'message': '缺少文件名参数'}), 400

        # 验证所有文件是否存在
        input_paths = []
        for filename in filenames:
            input_path = UPLOAD_FOLDER / filename
            if not input_path.exists():
                return jsonify({'success': False, 'message': f'文件不存在：{filename}'}), 404
            input_paths.append(input_path)
        
        logger.info(f"开始解析 {len(input_paths)} 个文件")
        
        # 解析所有文件
        all_dfs = []
        reference_columns = None
        
        for i, input_path in enumerate(input_paths):
            logger.info(f"解析第 {i+1}/{len(input_paths)} 个文件：{input_path.name}")
            df_result = parse_es_result(str(input_path))
            
            if len(df_result) == 0:
                logger.warning(f"文件 {input_path.name} 未解析到数据，跳过")
                continue
            
            # 检查字段是否一致
            current_columns = list(df_result.columns)
            if reference_columns is None:
                reference_columns = current_columns
                logger.info(f"参考字段：{reference_columns}")
            elif set(current_columns) != set(reference_columns):
                logger.warning(f"文件 {input_path.name} 字段不一致，跳过")
                logger.warning(f"  期望：{reference_columns}")
                logger.warning(f"  实际：{current_columns}")
                continue
            
            all_dfs.append(df_result)
        
        if not all_dfs:
            return jsonify({'success': False, 'message': '没有有效数据可转换'}), 400
        
        # 合并所有 DataFrame
        if len(all_dfs) == 1:
            merged_df = all_dfs[0]
            logger.info(f"单个文件，共 {len(merged_df)} 条数据")
        else:
            merged_df = pd.concat(all_dfs, ignore_index=True)
            logger.info(f"合并 {len(all_dfs)} 个文件，共 {len(merged_df)} 条数据")

        # 如果启用中文字段名映射，则重命名列
        merged_df = _apply_chinese_mapping(merged_df, use_chinese_names)

        # 生成输出文件名
        file_ext = '.xls' if excel_format == 'xls' else '.xlsx'
        if len(filenames) == 1:
            output_filename = f"{Path(filenames[0]).stem}{file_ext}"
        else:
            output_filename = f"merged_{int(time.time())}{file_ext}"
        
        output_path = OUTPUT_FOLDER / output_filename

        # 导出 Excel（根据格式选择）
        logger.info(f"开始导出 Excel：{output_filename} (格式: {excel_format})")
        use_xlsx = (excel_format != 'xls')
        actual_output_path = export_to_excel(merged_df, str(output_path), use_xlsx=use_xlsx)
        
        # 如果实际输出路径与预期不同（例如 xls 降级为 xlsx），更新文件名
        if actual_output_path != str(output_path):
            output_filename = Path(actual_output_path).name
            logger.info(f"⚠️  文件格式已调整：{output_filename}")

        logger.info(f"转换完成：{output_filename}")

        return jsonify({
            'success': True,
            'message': f'转换成功，合并了 {len(all_dfs)} 个文件',
            'output_filename': output_filename,
            'data_count': len(merged_df),
            'column_count': len(merged_df.columns),
            'file_count': len(all_dfs),
            'format': excel_format
        })

    except Exception as e:
        logger.error(f"转换失败：{e}", exc_info=True)
        return jsonify({'success': False, 'message': f'转换失败：{str(e)}'}), 500


@es_to_excel_bp.route('/download/<filename>', methods=['GET'])
def download_excel(filename):
    """下载生成的 Excel 文件"""
    try:
        excel_path = OUTPUT_FOLDER / filename
        if not excel_path.exists():
            return jsonify({'success': False, 'message': '文件不存在'}), 404

        return send_file(
            str(excel_path),
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"下载失败：{e}", exc_info=True)
        return jsonify({'success': False, 'message': f'下载失败：{str(e)}'}), 500


@es_to_excel_bp.route('/preview', methods=['POST'])
def preview_data():
    """预览数据（返回前几条记录）"""
    try:
        data = request.json
        filename = data.get('filename')
        limit = data.get('limit', 5)  # 默认预览 5 条

        if not filename:
            return jsonify({'success': False, 'message': '缺少文件名参数'}), 400

        input_path = UPLOAD_FOLDER / filename
        if not input_path.exists():
            return jsonify({'success': False, 'message': '文件不存在'}), 404
        
        # 解析 ES 查询结果
        logger.info(f"开始预览文件：{filename}")
        df_result = parse_es_result(str(input_path))
        
        if len(df_result) == 0:
            return jsonify({'success': False, 'message': '未解析到任何数据'}), 400

        # 返回前 N 条数据
        preview_df = df_result.head(limit)
        preview_data = preview_df.to_dict('records')

        return jsonify({
            'success': True,
            'message': '预览成功',
            'total_count': len(df_result),
            'preview_count': len(preview_data),
            'columns': list(df_result.columns),
            'data': preview_data
        })

    except Exception as e:
        logger.error(f"预览失败：{e}", exc_info=True)
        return jsonify({'success': False, 'message': f'预览失败：{str(e)}'}), 500


@es_to_excel_bp.route('/paste', methods=['POST'])
def paste_text():
    """直接粘贴文本进行处理（支持 ES SQL 表格、JSON、竖线分隔格式）"""
    try:
        # 使用安全解析，自动处理非法控制字符
        data = _parse_json_with_control_char_fix(request.get_data())
        text = data.get('text', '').strip()
        excel_format = data.get('format', 'xlsx')
        use_chinese_names = data.get('use_chinese_names', False)  # 是否使用中文字段名
        preview_only = data.get('preview_only', False)  # 是否仅预览

        if not text:
            return jsonify({'success': False, 'message': '未提供文本内容'}), 400

        # 将文本保存到临时文件
        timestamp = int(time.time() * 1000)
        temp_filename = f"paste_{timestamp}.txt"
        temp_path = UPLOAD_FOLDER / temp_filename
        temp_path.write_text(text, encoding='utf-8')

        logger.info(f"文本已保存：{temp_filename}")

        # 解析文本
        df_result = parse_es_result(str(temp_path))

        if len(df_result) == 0:
            return jsonify({'success': False, 'message': '未解析到任何数据，请检查文本格式'}), 400

        # 如果启用中文字段名映射，则重命名列
        df_result = _apply_chinese_mapping(df_result, use_chinese_names)

        # 如果仅预览，返回数据但不生成文件
        if preview_only:
            preview_data = df_result.head(10).to_dict('records')
            return jsonify({
                'success': True,
                'message': f'预览成功，共 {len(df_result)} 条数据',
                'total_count': len(df_result),
                'columns': list(df_result.columns),
                'data': preview_data
            })

        # 生成输出文件名
        file_ext = '.xls' if excel_format == 'xls' else '.xlsx'
        output_filename = f"paste_result_{timestamp}{file_ext}"
        output_path = OUTPUT_FOLDER / output_filename

        # 导出 Excel
        use_xlsx = (excel_format != 'xls')
        export_to_excel(df_result, str(output_path), use_xlsx=use_xlsx)

        logger.info(f"粘贴文本转换完成：{output_filename}")

        return jsonify({
            'success': True,
            'message': f'处理成功，共 {len(df_result)} 条数据，{len(df_result.columns)} 个字段',
            'output_filename': output_filename,
            'data_count': len(df_result),
            'column_count': len(df_result.columns),
            'columns': list(df_result.columns)
        })

    except ValueError as e:
        # 数据格式错误，返回 400
        logger.warning(f"粘贴文本格式错误：{e}")
        return jsonify({'success': False, 'message': f'格式错误：{str(e)}'}), 400
    except Exception as e:
        logger.error(f"粘贴文本处理失败：{e}", exc_info=True)
        return jsonify({'success': False, 'message': f'处理失败：{str(e)}'}), 500
