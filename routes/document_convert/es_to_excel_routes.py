"""
ES 查询结果转 Excel 路由
支持 txt (竖线分隔) 和 json (ES SQL 查询结果) 格式
"""
import os
import time
import sys
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
ALLOWED_EXTENSIONS = {'txt'}

# 确保目录存在
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# 导入 EsToExcel 工具（需要添加路径）
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils' / 'ES结果导Excel'))


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        # 生成输出文件名
        if len(filenames) == 1:
            output_filename = f"{Path(filenames[0]).stem}.xlsx"
        else:
            output_filename = f"merged_{int(time.time())}.xlsx"
        
        output_path = OUTPUT_FOLDER / output_filename

        # 导出 Excel
        logger.info(f"开始导出 Excel：{output_filename}")
        export_to_excel(merged_df, str(output_path))

        logger.info(f"转换完成：{output_filename}")

        return jsonify({
            'success': True,
            'message': f'转换成功，合并了 {len(all_dfs)} 个文件',
            'output_filename': output_filename,
            'data_count': len(merged_df),
            'column_count': len(merged_df.columns),
            'file_count': len(all_dfs)
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
