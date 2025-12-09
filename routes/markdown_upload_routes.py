# routes/markdown_upload_routes.py
import os

from flask import Blueprint, request, render_template
from werkzeug.utils import secure_filename
import markdown
from docx import Document
from datetime import datetime

# 创建 Blueprint 实例
markdown_upload_bp = Blueprint('markdown', __name__)

@markdown_upload_bp.route('/markdown-upload', methods=['GET', 'POST'])
def markdown_upload():
    """Markdown文件上传和转换页面"""
    if request.method == 'POST':
        if 'markdown_file' not in request.files:
            return render_template('markdown_upload.html', error='没有选择文件')

        file = request.files['markdown_file']
        if file.filename == '':
            return render_template('markdown_upload.html', error='没有选择文件')

        if file and file.filename.endswith('.md'):
            # 保存上传的 Markdown 文件
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', filename)
            file.save(filepath)

            # 转换为 Word 文档
            word_filename = filename.replace('.md', '.docx')
            word_filepath = os.path.join('uploads', word_filename)

            convert_md_to_docx(filepath, word_filepath)

            # 提供下载
            from flask import send_file
            return send_file(word_filepath, as_attachment=True)

    return render_template('markdown_upload.html')


def convert_md_to_docx(md_path, docx_path):
    """将 Markdown 文件转换为 Word 文档，并应用指定格式"""
    # 读取 Markdown 文件
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 转换 Markdown 为 HTML
    html = markdown.markdown(md_content)

    # 创建 Word 文档
    doc = Document()

    # 设置默认字体和大小（根据目标文档调整）
    from docx.shared import Pt
    style = doc.styles['Normal']
    font = style.font
    font.name = '宋体'
    font.size = Pt(10.5)

    # 简单处理 HTML 内容并添加到 Word 文档
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'ul', 'ol']):
        if element.name.startswith('h'):
            level = int(element.name[1])
            doc.add_heading(element.get_text(), level=level)
        elif element.name == 'p':
            p = doc.add_paragraph(element.get_text())
            p.style = 'Normal'
        elif element.name == 'ul':
            for li in element.find_all('li'):
                doc.add_paragraph(li.get_text(), style='List Bullet')
        elif element.name == 'ol':
            for li in element.find_all('li'):
                doc.add_paragraph(li.get_text(), style='List Number')

    # 保存 Word 文档
    doc.save(docx_path)
