# routes/markdown_upload_routes.py
import os
import logging
import re

from flask import Blueprint, request, render_template, send_file, json
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
KEYWORDS_FILE = os.path.join('config', 'keywords.json')
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


def remove_extra_blank_lines(text):
    """
    去除文本中多余的空行，连续空行只保留一行空行，
    并且去除开头和结尾的空行，使文本紧凑。
    """
    lines = text.split('\n')
    new_lines = []
    blank_line = False

    for line in lines:
        if line.strip() == '':
            # 遇到空行，如果之前没空行则保留，否则跳过
            if not blank_line:
                new_lines.append('')
                blank_line = True
        else:
            new_lines.append(line)
            blank_line = False

    # 去除开头和结尾的空行
    while new_lines and new_lines[0].strip() == '':
        new_lines.pop(0)
    while new_lines and new_lines[-1].strip() == '':
        new_lines.pop()

    return '\n'.join(new_lines)


def fix_header_and_remove_footer(content):
    """
    替换文档开头指定标题内容，
    并删除尾部多余说明文字。
    """

    lines = content.split('\n')

    # --- 处理开头 ---
    # 找到“5.功能需求”所在行，替换下一行为指定描述
    for i, line in enumerate(lines):
        if line.strip().startswith('5.功能需求'):
            # 保证下一行存在且是“5.1 按照FPA”，替换为新描述
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('5.1 按照FPA'):
                lines[i + 1] = '按照FPA中列出的本需求需改造的功能逐级（即按一级分类、二级分类、三级分类、功能点名称、功能点计数项结构）描述功能需求。'
            break

    # --- 处理尾部 ---
    # 删除尾部包含“按照FPA《集中故障管理系统”或“仅保留EI/EO/EQ类功能点”等关键字的行及之后的所有行
    footer_start_keywords = [
        '按照FPA《集中故障管理系统',
        '仅保留EI/EO/EQ类功能点',
        '剔除ILF/EIF类',
        '按照FPA中列出的本需求需改造的功能逐级'
    ]

    # 找到尾部起始行
    footer_start_index = None
    for i in range(len(lines) - 1, -1, -1):
        if any(keyword in lines[i] for keyword in footer_start_keywords):
            footer_start_index = i
        # 如果已经找到尾部起始行，继续向上找第一行不属于尾部内容的行
        elif footer_start_index is not None:
            break

    if footer_start_index is not None:
        # 删除尾部多余内容，从footer_start_index开始到文件结尾
        lines = lines[:footer_start_index]

    return '\n'.join(lines)


def convert_md_to_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    # # 先去除多余空行
    # md_content = remove_extra_blank_lines(md_content)
    # 剔除场景说明
    md_content = remove_scenario_description_lines(md_content)
    # 处理其他逻辑，如统计、功能描述等
    md_content = update_file_statistics(md_content)
    md_content = process_function_description(md_content)
    import re
    md_content = re.sub(r'^(#{7,})', '######', md_content, flags=re.MULTILINE)

    html = markdown.markdown(md_content, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')

    doc = Document()

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li']):
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            heading = doc.add_heading(level=min(level, 9))
            text = element.get_text().strip()
            if text:
                run = heading.add_run(text)
                set_font(run, size=get_heading_size(level), bold=True)
            continue

        if element.name == 'p':
            text = element.get_text().strip()
            if not text:
                # 跳过空段落
                continue
            paragraph = doc.add_paragraph()
            add_formatted_text(paragraph, element)
            continue

        if element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                li_text = li.get_text().strip()
                if not li_text:
                    continue
                paragraph = doc.add_paragraph(style='List Bullet')
                add_formatted_text(paragraph, li)

    add_fixed_function_requirements(doc)
    doc.save(docx_path)


def remove_scenario_description_lines(content):
    """
    删除文本中所有包含“场景说明”的行
    """
    lines = content.split('\n')
    filtered_lines = [line for line in lines if '场景说明' not in line]
    return '\n'.join(filtered_lines)


def remove_numbering_from_process_line(line):
    """
    去除“处理过程”字段中数字序号，支持带加粗的Markdown格式。
    """
    prefix_match = re.match(r'^\**处理过程[:：]\**\s*(.*)$', line)
    if not prefix_match:
        return line

    content = prefix_match.group(1)

    # 按分号分割内容，去掉每部分开头的数字序号
    parts = re.split(r'[；;]', content)
    cleaned_parts = []
    for part in parts:
        cleaned = re.sub(r'^\s*\d+\.\s*', '', part).strip()
        if cleaned:
            cleaned_parts.append(cleaned)

    new_content = '；'.join(cleaned_parts)

    # 返回时保留原加粗格式的“处理过程：”
    # 这里用 '**处理过程：**' 固定返回，如果你需要动态保留原格式可进一步处理
    return f'**处理过程：**{new_content}'

def process_function_description(content):
    """
    处理功能描述字段，将"处理xxx相关业务"修改为"进行xxx"
    同时处理输入字段，当标题包含特定关键词时修改输入值
    并去除处理过程字段中的数字序号
    """
    import re

    keywords_config = load_keywords_config()
    person_keywords = keywords_config.get('person_keywords', [])
    system_keywords = keywords_config.get('system_keywords', [])

    pattern_title = r'^(#{5,})\s*\*\*\s*([\d\.]+)\s*(.+?)\s*\*\*$'

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # 新增：处理“处理过程”字段去除序号
        if re.match(r'^\**处理过程[:：]\**', line):
            lines[i] = remove_numbering_from_process_line(line)
            line = lines[i]  # 更新当前行内容

        match = re.match(pattern_title, line)
        title_processed = False

        if match and not title_processed:
            func_name = match.group(3).strip()
            contains_keyword = any(keyword in func_name for keyword in person_keywords)
            contains_keyword2 = any(keyword in func_name for keyword in system_keywords)

            j = i + 1
            desc_processed = False
            input_processed = False

            while j < len(lines):
                desc_line = lines[j]
                if re.match(r'^#{1,5}\s*', desc_line) and title_processed:
                    break

                if not desc_processed:
                    desc_pattern = r'^(\**功能描述[:：]\**)\s*(.*)$'
                    desc_match = re.match(desc_pattern, desc_line)
                    if desc_match:
                        prefix = desc_match.group(1)
                        new_desc = '进行' + func_name
                        lines[j] = f"{prefix} {new_desc}"
                        desc_processed = True

                if contains_keyword and not input_processed:
                    input_pattern = r'^(\**输入[:：]\**)\s*(.*)$'
                    input_match = re.match(input_pattern, desc_line)
                    if input_match:
                        prefix = input_match.group(1)
                        new_input = '用户触发' + func_name
                        lines[j] = f"{prefix} {new_input}"
                        input_processed = True

                if contains_keyword2 and not input_processed:
                    input_pattern = r'^(\**输入[:：]\**)\s*(.*)$'
                    input_match = re.match(input_pattern, desc_line)
                    if input_match:
                        prefix = input_match.group(1)
                        new_input = '系统判定' + func_name
                        lines[j] = f"{prefix} {new_input}"
                        input_processed = True

                j += 1

            title_processed = True

        i += 1

    return '\n'.join(lines)


def add_fixed_function_requirements(doc):
    """添加固定的功能需求描述"""

    # 检查文档中是否已包含相关功能需求描述，避免重复添加
    existing_content = ""
    for paragraph in doc.paragraphs:
        existing_content += paragraph.text + "\n"

    if "按照FPA中列出的本需求需改造的功能逐级" in existing_content:
        return

    # 添加标题
    heading = doc.add_heading('5.功能需求', level=1)
    set_font(heading.runs[0], size=16, bold=True)

    # 添加正文内容（只添加一段，替换之前多余的两段）
    paragraph = doc.add_paragraph()
    run1 = paragraph.add_run(
        '按照FPA中列出的本需求需改造的功能逐级（即按一级分类、二级分类、三级分类、功能点名称、功能点计数项结构）描述功能需求。')
    set_font(run1, size=12)
    run1.bold = False  # 这里不加粗，如果需要加粗可以设置 True


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
    """
    根据分隔符统计文件数量。
    分隔符可能有：逗号，分号，空格，换行等。
    如果内容为“无”或空，返回0。
    """
    if not text or text == '无':
        return 0
    # 用逗号、分号、空格、换行分割
    import re
    parts = re.split(r'[，,；;\s]+', text.strip())
    # 过滤空字符串
    parts = [p for p in parts if p]
    return len(parts)

def count_files_by_separators(text):
    if not text or text == '无':
        return 0
    parts = re.split(r'[，,；;\s]+', text.strip())
    parts = [p for p in parts if p]
    return len(parts)

def update_file_statistics(content):
    """更新本事务功能预计涉及到的数据文件（即 FTR/RET）内容"""

    # 格式化：去掉数字与“个”之间的空格，比如“涉及到 2 个” -> “涉及到2个”
    cleaned_content = re.sub(r'(\d+)\s+个', r'\1个', content)

    # 格式化：去掉“新增 / 变更”中多余空格，变成“新增/变更”
    cleaned_content = re.sub(r'新增\s*/\s*变更', '新增/变更', cleaned_content)

    # 格式化：去掉冒号前后的多余空格，但不影响换行
    cleaned_content = re.sub(r'[ \t]*：[ \t]*', '：', cleaned_content)

    # 匹配"本事务功能预计涉及到 2 个内部逻辑文件，0 个外部逻辑文件"这样的模式
    pattern = r'本事务功能预计涉及到\s*(\d+)\s*个内部逻辑文件\s*，?\s*(\d+)\s*个外部逻辑文件'
    match = re.search(pattern, cleaned_content)

    if match:
        # 统计内部逻辑文件数量
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

        # 统计外部逻辑文件数量
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

        # 替换原来的统计数字，只替换第一个匹配
        updated_content = re.sub(
            pattern,
            f'本事务功能预计涉及到{actual_internal_count}个内部逻辑文件，{actual_external_count}个外部逻辑文件',
            cleaned_content,
            count=1
        )

        return updated_content

    # 即使没有匹配到统计模式，也要返回清理后的文本
    return cleaned_content


# 初始化关键词配置文件
def init_keywords_config():
    if not os.path.exists('config'):
        os.makedirs('config')

    if not os.path.exists(KEYWORDS_FILE):
        default_config = {
            "person_keywords": [
                "增加",
                "删除",
                "修改",
                "查询",
                "呈现",
                "列表",
                "渲染",
                "导出",
                "页面",
                "自定义",
                "点击",
                "看板",
                "录入",
                "编辑",
                "查看",
                "搜索",
                "筛选",
                "排序",
                "下载",
                "上传",
                "选择",
                "勾选",
                "取消",
                "确认",
                "提交",
                "保存",
                "刷新",
                "切换",
                "拖拽",
                "复制",
                "粘贴",
                "撤销",
                "重做",
                "下钻",
                "钻取",
                "展开",
                "收缩",
                "过滤",
                "钻探",
                "跳转",
                "关联",
                "流转",
                "设置",
                "控制"
            ],
            "system_keywords": [
                "判断",
                "自动",
                "定时",
                "轮询",
                "监听",
                "检测",
                "校验",
                "验证",
                "同步",
                "异步",
                "回调",
                "触发",
                "推送",
                "通知",
                "告警",
                "计算",
                "统计",
                "分析",
                "识别",
                "匹配",
                "对比",
                "评估",
                "鉴权",
                "认证",
                "授权",
                "加密",
                "解密",
                "签名",
                "验签",
                "审计",
                "监控",
                "日志",
                "备份",
                "恢复",
                "缓存",
                "对接",
                "调用",
                "判定",
                "记录"
            ]
        }
        with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)


# 加载关键词配置
def load_keywords_config():
    if not os.path.exists(KEYWORDS_FILE):
        init_keywords_config()

    with open(KEYWORDS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# 保存关键词配置
def save_keywords_config(config):
    with open(KEYWORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# 获取关键词API
@markdown_upload_bp.route('/api/keywords', methods=['GET'])
def get_keywords_api():
    """获取关键词配置API"""
    try:
        config = load_keywords_config()
        return config
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


# 更新关键词API
@markdown_upload_bp.route('/api/keywords', methods=['POST'])
def update_keywords_api():
    """更新关键词配置API"""
    try:
        data = request.json
        keyword_type = data.get('type')
        keyword = data.get('keyword')
        original = data.get('original')
        # 类型映射
        type_mapping = {
            'person': 'person_keywords',
            'system': 'system_keywords'
        }
        if keyword_type in type_mapping:
            keyword_type = type_mapping[keyword_type]

        if not keyword_type or not keyword:
            return {'status': 'error', 'message': '缺少必要参数'}, 400

        config = load_keywords_config()

        # if keyword_type not in config:
        #     return {'status': 'error', 'message': '无效的关键词类型'}, 400

        if original:
            # 编辑现有关键词
            if original in config[keyword_type]:
                config[keyword_type].remove(original)
            config[keyword_type].append(keyword)
        else:
            # 添加新关键词
            if keyword not in config[keyword_type]:
                config[keyword_type].append(keyword)

        save_keywords_config(config)
        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500


# 删除关键词API
@markdown_upload_bp.route('/api/keywords', methods=['DELETE'])
def delete_keywords_api():
    """删除关键词配置API"""
    try:
        data = request.json
        keyword_type = data.get('type')
        keyword = data.get('keyword')
        # 类型映射
        type_mapping = {
            'person': 'person_keywords',
            'system': 'system_keywords'
        }
        if keyword_type in type_mapping:
            keyword_type = type_mapping[keyword_type]
        if not keyword_type or not keyword:
            return {'status': 'error', 'message': '缺少必要参数'}, 400

        config = load_keywords_config()

        if keyword_type not in config:
            return {'status': 'error', 'message': '无效的关键词类型'}, 400

        if keyword in config[keyword_type]:
            config[keyword_type].remove(keyword)
            save_keywords_config(config)

        return {'status': 'success'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
