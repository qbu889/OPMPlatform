import os
from flask import Blueprint, request, render_template, send_file, abort
from werkzeug.utils import secure_filename
from docx import Document
from markdownify import markdownify as md
import io

word_to_md_bp = Blueprint('word_to_md', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'docx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_to_md(run):
    text = run.text
    if run.bold:
        text = f"**{text}**"
    if run.italic:
        text = f"*{text}*"
    return text

def para_to_md(paragraph):
    style = paragraph.style.name.lower()
    text = ''.join(run_to_md(run) for run in paragraph.runs).strip()
    if not text:
        return ''

    if 'heading 1' in style:
        return f"# {text}"
    elif 'heading 2' in style:
        return f"## {text}"
    elif 'heading 3' in style:
        return f"### {text}"
    elif 'heading 4' in style:
        return f"#### {text}"
    elif 'heading 5' in style:
        return f"##### {text}"
    elif 'heading 6' in style:
        return f"###### {text}"
    else:
        return text

def docx_to_markdown(docx_path):
    doc = Document(docx_path)
    md_lines = []
    for para in doc.paragraphs:
        md_line = para_to_md(para)
        if md_line:
            md_lines.append(md_line)
    return '\n\n'.join(md_lines)

@word_to_md_bp.route('/word-to-md', methods=['GET', 'POST'])
def word_to_md():
    if request.method == 'POST':
        if 'word_file' not in request.files:
            return render_template('word_to_md.html', error='没有选择文件')
        file = request.files['word_file']
        if file.filename == '' or not allowed_file(file.filename):
            return render_template('word_to_md.html', error='请选择有效的 Word 文件（.docx）')

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            markdown_text = docx_to_markdown(filepath)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('word_to_md.html', error=f'转换失败: {str(e)}')

        # 删除上传的文件
        if os.path.exists(filepath):
            os.remove(filepath)

        # 将markdown文本写入内存文件，返回下载
        md_filename = os.path.splitext(filename)[0] + '.md'
        md_bytes = markdown_text.encode('utf-8')
        md_file = io.BytesIO(md_bytes)
        md_file.seek(0)

        return send_file(
            md_file,
            as_attachment=True,
            download_name=md_filename,
            mimetype='text/markdown'
        )

    return render_template('word_to_md.html')
