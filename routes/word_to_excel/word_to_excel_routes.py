#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word 转 Excel 路由模块
提供 Word 文档上传、解析和 Excel 下载功能
"""
import os
import uuid
import logging
from flask import Blueprint, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from pathlib import Path

logger = logging.getLogger(__name__)

# 创建蓝图
word_to_excel_bp = Blueprint('word_to_excel', __name__, url_prefix='/word-to-excel')

# 配置
UPLOAD_FOLDER = 'uploads/word_to_excel'
ALLOWED_EXTENSIONS = {'.docx'}  # 注意：这里需要带点
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    ext = Path(filename).suffix.lower()
    logger.debug(f"[WORD_TO_EXCEL] 文件扩展名检查：{filename} -> {ext}")
    return ext in ALLOWED_EXTENSIONS


@word_to_excel_bp.route('/', methods=['GET'])
def index():
    """显示 Word 转 Excel 页面"""
    logger.info("[WORD_TO_EXCEL] 访问首页")
    return render_template('word_to_excel.html')


@word_to_excel_bp.route('/upload', methods=['POST'])
def upload_document():
    """
    上传 Word 文档并转换为 Excel
    
    Request Form:
        - file: Word 文件对象
        
    Response JSON:
        {
            'success': bool,
            'message': str,
            'download_url': str (可选),
            'filename': str (可选),
            'stats': {
                'total_functions': int,
                'file_size': str
            } (可选)
        }
    """
    logger.info(f"[WORD_TO_EXCEL] ====== 收到上传请求 ======")
    
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            logger.warning(f"[WORD_TO_EXCEL] ❌ 没有文件上传")
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            logger.warning(f"[WORD_TO_EXCEL] ❌ 文件名为空")
            return jsonify({
                'success': False,
                'message': '文件名为空'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            logger.warning(f"[WORD_TO_EXCEL] ❌ 不支持的文件类型：{file.filename}")
            return jsonify({
                'success': False,
                'message': '不支持的文件类型，请上传 .docx 文件'
            }), 400
        
        # 检查文件大小（通过读取部分数据）
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到开头
        
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"[WORD_TO_EXCEL] ❌ 文件过大：{file_size} bytes")
            return jsonify({
                'success': False,
                'message': f'文件过大，最大支持 {MAX_FILE_SIZE // 1024 // 1024}MB'
            }), 400
        
        logger.info(f"[WORD_TO_EXCEL] 📄 上传文件：{file.filename}, 大小：{file_size} bytes")
        
        # 生成唯一文件名
        original_filename = Path(file.filename).stem
        ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        logger.info(f"[WORD_TO_EXCEL] 保存文件到：{filepath}")
        file.save(filepath)
        
        # 执行转换（带进度反馈）
        logger.info(f"[WORD_TO_EXCEL] 开始转换...")
        from utils.word_to_excel import parse_word_to_excel_with_progress
        
        # 使用带进度的转换函数
        result = parse_word_to_excel_with_progress(filepath)
        
        if not result or not result.get('success'):
            logger.error(f"[WORD_TO_EXCEL] ❌ 转换失败")
            return jsonify({
                'success': False,
                'message': result.get('message', '文档解析失败，请检查文档格式是否正确') if result else '文档解析失败，请检查文档格式是否正确'
            }), 500
        
        excel_path = result['excel_path']
        total_functions = result['total_functions']
        
        # 生成下载文件名
        download_filename = f"{original_filename}_软件资产清单.xlsx"
        
        # 生成下载 URL（使用临时文件 ID）
        download_id = uuid.uuid4().hex
        # 将文件路径映射到临时 ID（实际项目中可以使用 Redis 或数据库）
        # 这里简单处理：直接将文件复制到临时下载目录
        download_folder = 'downloads/word_to_excel'
        os.makedirs(download_folder, exist_ok=True)
        download_filepath = os.path.join(download_folder, f"{download_id}_{download_filename}")
        
        import shutil
        shutil.copy2(excel_path, download_filepath)
        
        download_url = f'/word-to-excel/download/{download_id}'
        
        logger.info(f"[WORD_TO_EXCEL] ✅ 转换成功，提取 {total_functions} 条功能点")
        logger.info(f"[WORD_TO_EXCEL] 下载 URL: {download_url}")
        
        return jsonify({
            'success': True,
            'message': f'转换成功，共提取 {total_functions} 条功能点',
            'download_url': download_url,
            'filename': download_filename,
            'stats': {
                'total_functions': total_functions,
                'file_size': f"{os.path.getsize(excel_path) // 1024} KB"
            }
        })
        
    except Exception as e:
        logger.error(f"[WORD_TO_EXCEL] ❌ 转换失败：{e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'转换失败：{str(e)}'
        }), 500


@word_to_excel_bp.route('/download/<download_id>', methods=['GET'])
def download_file(download_id: str):
    """
    下载转换后的 Excel 文件
    
    Args:
        download_id: 临时文件 ID
        
    Returns:
        Excel 文件
    """
    logger.info(f"[WORD_TO_EXCEL] 下载文件：{download_id}")
    
    try:
        # 查找文件
        download_folder = 'downloads/word_to_excel'
        
        # 查找匹配的文件
        matching_files = [f for f in os.listdir(download_folder) if f.startswith(f"{download_id}_")]
        
        if not matching_files:
            logger.warning(f"[WORD_TO_EXCEL] ❌ 文件不存在：{download_id}")
            return jsonify({
                'success': False,
                'message': '文件不存在或已过期'
            }), 404
        
        filename = matching_files[0]
        filepath = os.path.join(download_folder, filename)
        
        # 提取原始文件名
        original_filename = '_'.join(filename.split('_')[1:])
        
        logger.info(f"[WORD_TO_EXCEL] ✅ 发送文件：{filepath}")
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=original_filename
        )
        
    except Exception as e:
        logger.error(f"[WORD_TO_EXCEL] ❌ 下载失败：{e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'下载失败：{str(e)}'
        }), 500


@word_to_excel_bp.route('/help', methods=['GET'])
def help_page():
    """显示帮助页面"""
    help_content = """
    <h1>Word 转 Excel 功能说明</h1>
    
    <h2>功能描述</h2>
    <p>自动解析 Word 技术规范书，生成软件资产清单 Excel 文件。</p>
    
    <h2>支持的文档格式</h2>
    <ul>
        <li>文件格式：.docx</li>
        <li>文件大小：最大 50MB</li>
        <li>内容格式：包含层级编号的技术规范书</li>
    </ul>
    
    <h2>提取规则</h2>
    <p>根据 Word 文档中的层级编号自动识别：</p>
    <ul>
        <li><strong>一级分类</strong>：编号格式如 "3.1.1.2" → 提取："监控管理应用"</li>
        <li><strong>二级分类</strong>：编号格式如 "3.1.1.2.1" → 提取："分级调度管理"</li>
        <li><strong>功能模块</strong>：编号格式如 "3.1.1.2.1.1" → 提取："分级调度派发"</li>
        <li><strong>功能点名称</strong>：编号格式如 "3.1.1.2.1.1.1" → 提取："派发智能体自动修复"</li>
        <li><strong>功能点描述</strong>：功能点下方的详细描述文本（纯文本，不包含图片）</li>
    </ul>
    
    <h2>使用方法</h2>
    <ol>
        <li>点击"选择文件"按钮，选择要上传的 Word 文档</li>
        <li>点击"上传并转换"按钮</li>
        <li>等待转换完成</li>
        <li>点击"下载 Excel 文件"按钮下载结果</li>
    </ol>
    
    <h2>输出 Excel 格式</h2>
    <p>Excel 文件包含以下列：</p>
    <ul>
        <li>一级分类</li>
        <li>二级分类</li>
        <li>功能模块</li>
        <li>序号</li>
        <li>功能点名称</li>
        <li>功能点描述</li>
    </ul>
    
    <h2>注意事项</h2>
    <ul>
        <li>确保 Word 文档格式规范，包含清晰的层级编号</li>
        <li>功能点描述会自动过滤图片和特殊符号</li>
        <li>转换后的 Excel 文件会自动保存 7 天</li>
    </ul>
    """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>帮助 - Word 转 Excel</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            ul, ol {{ line-height: 1.8; }}
            li {{ margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        {help_content}
        <p><a href="/word-to-excel/">← 返回上传页面</a></p>
    </body>
    </html>
    """
