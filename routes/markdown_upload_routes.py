# routes/markdown_upload_routes.py
import os
import logging
from flask import Blueprint, request, render_template, send_file
from werkzeug.utils import secure_filename
import markdown
from docx import Document
from datetime import datetime
from docx.shared import Pt, RGBColor
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
FIELD_NAMES = [
    "场景说明：",
    "功能描述：",
    "系统界面：",
    "输入：",
    "输出：",
    "处理过程：",

    # 关键字段：把常见变体都列全（含空格、含/不含冒号、全角/半角）
    "本事务功能涉及到的数据文件（即FTR/RET）：",
    "本事务功能涉及到的数据文件（即 FTR/RET）：",
    "本事务功能涉及到的数据文件（即FTR/RET）:",
    "本事务功能涉及到的数据文件（即 FTR/RET）:",
    "本事务功能涉及到的数据文件（即FTR/RET）",
    "本事务功能涉及到的数据文件（即 FTR/RET）",
]

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

            word_filename = clean_filename(file.filename).replace('.md', '.docx').replace('.MD', '.docx')
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
    # 设置字体颜色为黑色
    run.font.color.rgb = RGBColor(0, 0, 0)  # 明确设置为黑色

def clean_filename(filename):
    """清理文件名，移除特殊字符"""
    # 移除或替换不合法的文件名字符
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip(' ._')  # 移除首尾的空格和点

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

def get_heading_size(level):
    """获取标题字体大小"""
    sizes = {
        1: 16,
        2: 15,
        3: 14,
        4: 12,
        5: 12,
        6: 12,
        7: 12  # 添加对7级标题的支持
    }
    return sizes.get(level, 12)


def convert_md_to_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 更新文件统计数据
    md_content = update_file_statistics(md_content)

    # 预处理：规范化标题格式
    import re
    # 将过多的#符号规范化
    md_content = re.sub(r'^(#{7,})', '######', md_content, flags=re.MULTILINE)

    html = markdown.markdown(md_content, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')

    # 创建全新的空文档
    doc = Document()

    # 按顺序处理所有元素，不进行去重
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li']):
        # 标题处理
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            heading = doc.add_heading(level=min(level, 9))
            text = element.get_text().strip()
            if text:
                run = heading.add_run(text)
                set_font(run, size=get_heading_size(level), bold=True)
            continue

        # 段落处理
        if element.name == 'p':
            text = element.get_text().strip()
            if text:  # 只有非空段落才添加
                paragraph = doc.add_paragraph()
                add_formatted_text(paragraph, element)
            continue

        # 列表处理
        if element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                li_text = li.get_text().strip()
                if li_text:
                    paragraph = doc.add_paragraph(style='List Bullet')
                    add_formatted_text(paragraph, li)

    # 添加固定的功能需求描述
    add_fixed_function_requirements(doc)

    doc.save(docx_path)

def add_fixed_function_requirements(doc):
    """添加固定的功能需求描述"""
    # 检查文档中是否已包含相关功能需求描述
    existing_content = ""
    for paragraph in doc.paragraphs:
        existing_content += paragraph.text + "\n"

    # 如果已存在相关描述则不添加
    if "按照FPA《集中故障管理系统-监控综合应用" in existing_content:
        return

    # 添加标题
    heading = doc.add_heading('5. 功能需求', level=1)
    set_font(heading.runs[0], size=16, bold=True)

    # 添加第一段内容（FPA加粗）
    paragraph1 = doc.add_paragraph()
    run1 = paragraph1.add_run('按照FPA')
    run1.bold = True
    run2 = paragraph1.add_run(
        '《集中故障管理系统-监控综合应用-关于集团事件工单省部接口数据上报保障的开发需求-15400_20250318-FPA预估2025版V3_厂家版本.xlsx》"2. 规模估算"生成，仅保留EI/EO/EQ类功能点，剔除ILF/EIF类')
    set_font(run1, size=12)
    set_font(run2, size=12)

    # 添加第二段内容（写死的内容，FPA加粗）
    paragraph2 = doc.add_paragraph()
    run3 = paragraph2.add_run('按照FPA')
    run3.bold = True
    run4 = paragraph2.add_run(
        '中列出的本需求需改造的功能逐级（即按一级分类、二级分类、三级分类、功能点名称、功能点计数项结构）描述功能需求。')
    set_font(run3, size=12)
    set_font(run4, size=12)


def add_formatted_text(paragraph, element):
    """
    递归处理HTML元素，保留格式（如加粗）和换行，但去除斜体
    """
    if element.name is None:  # 文本节点
        text = str(element)
        if text.strip() or text.isspace():
            # 处理文本中的换行
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if line.strip():
                    run = paragraph.add_run(line)
                    set_font(run, size=12)
                # 如果不是最后一行且有换行符，则添加换行
                if i < len(lines) - 1:
                    paragraph.add_run('\n')
        return

    # 处理子元素
    for child in element.children:
        if hasattr(child, 'name'):
            if child.name in ['strong', 'b']:  # 加粗
                # 处理加粗文本中的换行
                text = child.get_text()
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        run = paragraph.add_run(line)
                        run.bold = True
                        set_font(run, size=12, bold=True)
                    if i < len(lines) - 1:
                        paragraph.add_run('\n')
            elif child.name in ['em', 'i']:  # 斜体 - 转换为普通文本
                # 处理斜体文本中的换行，但不应用斜体格式
                text = child.get_text()
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        run = paragraph.add_run(line)
                        set_font(run, size=12)  # 不应用斜体
                    if i < len(lines) - 1:
                        paragraph.add_run('\n')
            elif child.name == 'br':  # 换行标签
                paragraph.add_run('\n')
            else:  # 其他标签，递归处理
                add_formatted_text(paragraph, child)
        else:  # 文本内容
            text = str(child)
            if text.strip() or text.isspace():
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        run = paragraph.add_run(line)
                        set_font(run, size=12)
                    if i < len(lines) - 1:
                        paragraph.add_run('\n')


def count_files_by_separators(text):
    """根据分隔符数量统计文件个数，包含"（如适用）"的条目也计入统计"""
    if text.strip() == '无' or not text.strip():
        return 0

    # 分割文件列表并计数所有条目（包括包含"（如适用）"的）
    files = [f.strip() for f in text.split('、') if f.strip()]
    return len(files)


def update_file_statistics(content):
    """更新文件统计数据"""
    import re

    # 先清理"（如适用）"文本
    cleaned_content = content.replace('（如适用）', '')

    # 匹配"本事务功能预计涉及到 2 个内部逻辑文件，0 个外部逻辑文件"这样的模式
    pattern = r'本事务功能预计涉及到\s*(\d+)\s*个内部逻辑文件\s*，?\s*(\d+)\s*个外部逻辑文件'
    match = re.search(pattern, cleaned_content)

    if match:
        # 统计实际的内部逻辑文件数量
        internal_new_added_pattern = r'本期新增/变更的内部逻辑文件[：:]([^\n]*?)(?=\n|$)'
        internal_existing_pattern = r'本期涉及原有但没修改的内部逻辑文件[：:]([^\n]*?)(?=\n|$)'

        internal_new_added_match = re.search(internal_new_added_pattern, cleaned_content)
        internal_existing_match = re.search(internal_existing_pattern, cleaned_content)

        internal_new_count = 0
        internal_existing_count = 0

        if internal_new_added_match:
            internal_new_text = internal_new_added_match.group(1).strip()
            internal_new_count = count_files_by_separators(internal_new_text)

        if internal_existing_match:
            internal_existing_text = internal_existing_match.group(1).strip()
            internal_existing_count = count_files_by_separators(internal_existing_text)

        actual_internal_count = internal_new_count + internal_existing_count

        # 统计实际的外部逻辑文件数量
        external_new_added_pattern = r'本期新增/变更的外部逻辑文件[：:]([^\n]*?)(?=\n|$)'
        external_existing_pattern = r'本期涉及原有但没修改的外部逻辑文件[：:]([^\n]*?)(?=\n|$)'

        external_new_added_match = re.search(external_new_added_pattern, cleaned_content)
        external_existing_match = re.search(external_existing_pattern, cleaned_content)

        external_new_count = 0
        external_existing_count = 0

        if external_new_added_match:
            external_new_text = external_new_added_match.group(1).strip()
            external_new_count = count_files_by_separators(external_new_text)

        if external_existing_match:
            external_existing_text = external_existing_match.group(1).strip()
            external_existing_count = count_files_by_separators(external_existing_text)

        actual_external_count = external_new_count + external_existing_count

        # 替换原来的统计数字
        updated_content = re.sub(
            pattern,
            f'本事务功能预计涉及到{actual_internal_count}个内部逻辑文件，{actual_external_count}个外部逻辑文件',
            cleaned_content
        )

        return updated_content

    # 即使没有匹配到统计模式，也要返回清理后的文本
    return cleaned_content



