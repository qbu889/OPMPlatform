# routes/markdown_upload_routes.py
import os
import logging
from flask import Blueprint, request, render_template, send_file
from werkzeug.utils import secure_filename
import markdown
from docx import Document
from datetime import datetime
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH
from bs4 import BeautifulSoup


# 创建 Blueprint 实例
markdown_upload_bp = Blueprint('markdown', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'md'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 设置日志
logging.basicConfig(level=logging.INFO)

TEMPLATE_DOCX = "templates/template.docx"
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@markdown_upload_bp.route('/markdown-upload', methods=['GET', 'POST'])
def markdown_upload():
    """Markdown文件上传和转换页面"""
    try:
        if request.method == 'POST':
            if 'markdown_file' not in request.files:
                return render_template('markdown_upload.html', error='没有选择文件')

            file = request.files['markdown_file']
            if file.filename == '' or not allowed_file(file.filename):
                return render_template('markdown_upload.html', error='没有选择有效的 Markdown 文件')

            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # 防止路径穿越攻击
            real_path = os.path.realpath(filepath)
            if not real_path.startswith(os.path.realpath(UPLOAD_FOLDER)):
                raise ValueError("非法路径访问尝试")

            file.save(real_path)

            word_filename = filename.replace('.md', '.docx')
            word_filepath = os.path.join(UPLOAD_FOLDER, word_filename)

            convert_md_to_docx(real_path, word_filepath)

            response = send_file(word_filepath, as_attachment=True)

            # 删除临时文件
            @response.call_on_close
            def cleanup():
                try:
                    os.remove(real_path)
                    os.remove(word_filepath)
                except Exception as e:
                    logging.warning(f"Cleanup failed: {e}")

            return response

        return render_template('markdown_upload.html')
    except Exception as e:
        logging.error(f"Error processing upload: {str(e)}")
        return render_template('markdown_upload.html', error="处理过程中发生错误，请稍后再试")


def set_font(run, name='宋体', size=None, bold=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    if size:
        run.font.size = Pt(size)
    if bold:
        run.bold = True


def create_style_mapping():
    return {
        ('h1', '5.', '功能需求'): (18, True),
        ('h1', 'FPA', None): (16, True),
        ('h2', '一级分类', None): (16, True),
        ('h2', '二级分类', None): (15, True),
        ('h3', '三级分类', None): (14, True),
        ('h4', '功能点名称', None): (12, True),
    }


def apply_heading_style(doc, text, level, style_map):
    key_match = next(
        ((k, v) for k, v in style_map.items()
         if k[0] == f'h{level}' and
            (not k[1] or text.startswith(k[1])) and
            (not k[2] or k[2] in text)), None)

    if key_match:
        _, (size, bold) = key_match
        heading = doc.add_heading(text, level=min(level, 9))  # docx 最大支持到9级标题
        set_font(heading.runs[0], size=size, bold=bold)
    else:
        default_sizes = [None, 16, 15, 14, 12, 10.5, 12]
        size = default_sizes[level] if level < len(default_sizes) else 12
        heading = doc.add_heading(text, level=min(level, 9))
        set_font(heading.runs[0], size=size, bold=True)


def add_special_label_paragraph(doc, text, in_h6_section, special_labels):
    if in_h6_section:
        paragraph = doc.add_paragraph(style='List Bullet')
        matched = False
        for label in special_labels:
            if text.startswith(label):
                bold_run = paragraph.add_run(label)
                set_font(bold_run, size=12, bold=True)
                remaining = text[len(label):]
                if remaining:
                    normal_run = paragraph.add_run(remaining)
                    set_font(normal_run, size=12)
                matched = True
                break
        if not matched:
            run = paragraph.add_run(text)
            set_font(run, size=12)
    else:
        add_custom_paragraph(doc, text, bold=True, size=12)


def add_data_file_paragraphs(doc, text):
    keywords = [
        '本期新增/变更的内部逻辑文件：',
        '本期涉及原有但没修改的内部逻辑文件：',
        '本期新增/变更的外部逻辑文件：',
        '本期涉及原有但没修改的外部逻辑文件：'
    ]
    processed_text = text
    for kw in keywords[1:]:
        processed_text = processed_text.replace(kw, '\n' + kw)
    parts = processed_text.split('\n')
    for part in parts:
        stripped_part = part.strip()
        if stripped_part:
            p = doc.add_paragraph(stripped_part, style='List Bullet')
            set_font(p.runs[0], size=12)


def add_custom_paragraph(doc, text, bold=False, size=None):
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(text)
    set_font(run, size=size, bold=bold)
    return paragraph

def find_style(doc, targets):
    """
    在模板中查找一个匹配名称的样式（支持中英文、部分匹配）
    targets: ['Normal', '正文', ...]
    """
    for style in doc.styles:
        name = style.name.strip()
        for t in targets:
            if t.lower() in name.lower():
                return name
    return None

def load_template_styles(doc):
    """
    自动读取模板中的 常规段落、标题、列表 样式
    """
    styles = {}

    # Normal / 正文
    styles["p"] = (
        find_style(doc, ["Normal", "正文", "Body", "Normal Text"])
        or doc.styles[0].name  # 兜底
    )

    # 标题样式
    styles["h1"] = find_style(doc, ["Heading 1", "标题 1"]) or styles["p"]
    styles["h2"] = find_style(doc, ["Heading 2", "标题 2"]) or styles["p"]
    styles["h3"] = find_style(doc, ["Heading 3", "标题 3"]) or styles["p"]
    styles["h4"] = find_style(doc, ["Heading 4", "标题 4"]) or styles["p"]
    styles["h5"] = find_style(doc, ["Heading 5", "标题 5"]) or styles["p"]
    styles["h6"] = find_style(doc, ["Heading 6", "标题 6"]) or styles["p"]

    # 列表样式
    styles["ul"] = (
        find_style(doc, ["List Bullet", "项目符号"])
        or styles["p"]
    )
    styles["ol"] = (
        find_style(doc, ["List Number", "编号"])
        or styles["p"]
    )

    return styles


def convert_md_to_docx(md_path, docx_path):

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html = markdown.markdown(md_content, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')

    # 加载模板
    doc = Document(TEMPLATE_DOCX)

    # 自动加载模板中的样式
    style_map = load_template_styles(doc)

    processed = set()

    for element in soup.find_all(['h1','h2','h3','h4','h5','h6','p','ul','ol','li']):
        text = element.get_text().strip()
        if not text or text in processed:
            continue
        processed.add(text)

        # 标题
        if element.name in ['h1','h2','h3','h4','h5','h6']:
            p = doc.add_paragraph(text, style=style_map[element.name])
            continue

        # 段落
        if element.name == 'p':
            doc.add_paragraph(text, style=style_map["p"])
            continue

        # 列表
        if element.name in ['ul', 'ol']:
            list_style = style_map[element.name]
            for li in element.find_all('li'):
                li_text = li.get_text().strip()
                if not li_text or li_text in processed:
                    continue
                processed.add(li_text)
                doc.add_paragraph(li_text, style=list_style)

    doc.save(docx_path)
