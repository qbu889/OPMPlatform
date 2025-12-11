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
    elif size is None:  # 如果未指定大小，则默认使用5号字体(10.5pt)
        run.font.size = Pt(10.5)
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
        1: 18,  # 小二
        2: 16,  # 三号
        3: 15,  # 小三
        4: 12,  # 四号
        5: 11,  # 小四
        6: 10  # 五号
    }
    return sizes.get(level, 12)


def format_markdown_content(content):
    """对Markdown内容进行格式化处理"""
    import re

    # 1. 删除 cite 标记
    content = re.sub(r'\[cite_start\]', '', content)
    content = re.sub(r'\[cite:\s*\d+\]', '', content)

    # 2. 把 "* **字段名：** 内容" → "**字段名：** 内容"
    content = re.sub(r'^\*\s+(\*\*.+?\*\*.*)$', r'\1', content, flags=re.MULTILINE)

    # ======= 3. 处理你的新需求：字段值“无”取消加粗 =======
    # 例如:  **系统界面：** **无**  →  **系统界面：** 无
    content = re.sub(
        r'(\*\*[^\n：:]+[:：]\*\*)\s*\*\*无\*\*',
        r'\1 无',
        content
    )

    # ======= 4. 数据文件块：去掉项目符号 "*" =======
    # 仅处理「本事务功能涉及到的数据文件」后的列表
    pattern_files_block = (
        r'(\*\*本事务功能涉及到的数据文件（即\s*FTR/RET\s*）\*\*)'
        r'([\s\S]*?)(?=\n#{1,6}|\Z)'
    )

    def remove_stars_in_block(match):
        header = match.group(1)
        block = match.group(2)
        # 删除每行前面的 "* "
        block = re.sub(r'^\s*\*\s+', '', block, flags=re.MULTILINE)
        return header + block

    content = re.sub(pattern_files_block, remove_stars_in_block, content)

    # 5. 清理多余空行
    content = re.sub(r'\n{3,}', '\n\n', content)
    # 修复“本事务功能涉及到的数据文件（即 FTR/RET）”后缺少换行的问题
    content = re.sub(
        r'(\*\*本事务功能涉及到的数据文件（即\s*FTR/RET\s*）\*\*)(\S)',
        r'\1\n\2',
        content
    )

    return content


def convert_md_to_docx(md_path, docx_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    # 增加格式化处理
    md_content = format_markdown_content(md_content)

    # 更新文件统计数据
    md_content = update_file_statistics(md_content)

    # 处理功能描述和处理过程
    md_content = process_function_description(md_content)

    html = markdown.markdown(md_content, extensions=['tables'])
    soup = BeautifulSoup(html, 'html.parser')

    # 创建全新的空文档，而不是基于模板
    doc = Document()  # 不使用模板

    processed = set()

    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li']):
        text = element.get_text().strip()
        if not text or text in processed:
            continue
        processed.add(text)

        # 标题处理
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(element.name[1])
            heading = doc.add_heading(level=min(level, 9))
            # 处理标题文本，强制加粗，不使用斜体
            text = element.get_text().strip()
            if text:
                run = heading.add_run(text)
                set_font(run, size=get_heading_size(level), bold=True)  # 强制加粗
            continue

        # 段落处理
        if element.name == 'p':
            text = element.get_text().strip()
            #logging.info(f"Processing paragraph text: {text}")  # 添加调试日志

            # 检查是否包含多个字段，如果是则拆分处理
            field_matches = []
            for field_name in FIELD_NAMES:
                if field_name in text:
                    field_matches.append(field_name)

            #logging.info(f"Field matches found: {field_matches}")  # 添加调试日志

            if len(field_matches) > 1:
                # 包含多个字段，需要拆分处理
                split_and_add_multiple_fields(doc, text)
            elif any(text.startswith(f) for f in FIELD_NAMES):
                add_field_paragraph(doc, text)
            elif any(f in text for f in FIELD_NAMES):  # 添加这一条件来处理字段在段落中间的情况
                # 即使字段不在段落开头，只要包含字段也需要特殊处理
                split_and_add_multiple_fields(doc, text)
            else:
                # 保留你原有格式处理逻辑
                paragraph = doc.add_paragraph()
                add_formatted_text(paragraph, element)
            continue

        # 列表处理
        if element.name in ['ul', 'ol']:
            for li in element.find_all('li'):
                li_text = li.get_text().strip()
                if not li_text or li_text in processed:
                    continue
                processed.add(li_text)
                paragraph = doc.add_paragraph(style='List Bullet')
                add_formatted_text(paragraph, li)

    # 添加固定的功能需求描述
    add_fixed_function_requirements(doc)
    doc.save(docx_path)




def split_and_add_multiple_fields(doc, text):
    """
    将包含多个字段的文本拆分并分别添加到文档中
    """
    # 按 FIELD_NAMES 的顺序创建字段位置映射
    field_positions = []
    for field_name in FIELD_NAMES:
        start = 0
        while True:
            pos = text.find(field_name, start)
            if pos == -1:
                break
            field_positions.append((pos, field_name))
            start = pos + 1

    # 按位置排序
    field_positions.sort(key=lambda x: x[0])

    # 如果没有找到字段，按普通段落处理
    if not field_positions:
        paragraph = doc.add_paragraph()
        run = paragraph.add_run(text)
        set_font(run, size=12)
        return

    # 拆分并处理每个字段
    last_end = 0
    for i, (pos, field_name) in enumerate(field_positions):
        # 计算字段结束位置
        field_end = pos + len(field_name)

        # 找到下一个字段的开始位置，或者文本结尾
        next_pos = len(text)
        if i + 1 < len(field_positions):
            next_pos = field_positions[i + 1][0]

        # 提取完整的字段文本（字段名+字段值）
        field_text = text[pos:next_pos].strip()

        # 使用现有的 add_field_paragraph 处理单个字段
        add_field_paragraph(doc, field_text)


def extract_function_name_from_title(title):
    """从标题中提取功能名称"""
    import re
    # 匹配标题中的功能名称部分
    pattern = r'\d+(?:\.\d+)*\s+(.*?)(?:（注.*)?$'
    match = re.search(pattern, title.strip())
    if match and match.group(1):
        result = match.group(1).strip()
        # 移除可能的标点符号
        result = re.sub(r'[（\(].*?[）\)]$', '', result).strip()
        return result
    return title


def process_function_description(content):
    """处理功能描述、处理过程等字段，但不改变原有逻辑。
    仅满足两点额外要求：
    1. 删除所有 Markdown 加粗 **内容**；
    2. 删除“本事务功能涉及到的数据文件（即FTR/RET）**”中的 "**"。
    """
    import re

    # ==========================================================
    # 额外清理要求 (1)：删除所有 **加粗** → 内容
    # ==========================================================
    content = re.sub(r"\*\*(.*?)\*\*", r"\1", content)

    # ==========================================================
    # 额外清理要求 (2)：删除残留 "****" 或 "**"
    #（你明确说不要任何加粗符号）
    # ==========================================================
    content = content.replace("**", "")

    # ==========================================================
    # 以下部分为你原本的方法逻辑，完全保留！！
    # ==========================================================

    def extract_function_name_from_title(title):
        pattern = r'\d+(?:\.\d+)*\s+(.*?)(?:（注.*)?$'
        match = re.search(pattern, title.strip())
        if match and match.group(1):
            result = match.group(1).strip()
            result = re.sub(r'[（\(].*?[）\)]$', '', result).strip()
            return result
        return title

    def remove_bold_in_process_value(section_content):
        pattern = r'(处理过程[:：]\s*)(.*?)(?=\n|$)'
        match = re.search(pattern, section_content)
        if not match:
            return section_content
        prefix = match.group(1)
        value = match.group(2)
        # 这里原本是删除 value 的加粗，现在所有加粗已在上方统一去掉，无需重复逻辑
        return section_content[:match.start()] + prefix + value + section_content[match.end():]

    lines = content.split('\n')

    title_pattern = r'^#+\s*(\d+(?:\.\d+)*\s+.*?（注.*?FPA功能点计数项.*?）)'
    titles = []

    for line in lines:
        m = re.match(title_pattern, line.strip())
        if m:
            titles.append(m.group(1))

    if not titles:
        for line in lines:
            if 'FPA功能点计数项' in line:
                number_match = re.search(r'(\d+(?:\.\d+)*\s+.*)', line.strip())
                if number_match:
                    titles.append(number_match.group(1))

    for title in titles:
        title_start = content.find(title)
        if title_start == -1:
            continue

        next_title_start = len(content)
        for nt in titles:
            if nt != title:
                pos = content.find(nt, title_start + len(title))
                if pos != -1 and pos < next_title_start:
                    next_title_start = pos

        section = content[title_start: next_title_start]

        func_name = extract_function_name_from_title(title)
        processed_func_name = "进行" + func_name

        desc_pattern = r'[*]{0,2}功能描述[:：]\s*(.*?)(?=\n|$)'
        desc_match = re.search(desc_pattern, section)

        if desc_match:
            old_desc_value = desc_match.group(1).strip()

            section = re.sub(
                r'([*]{0,2}功能描述[:：]\s*)(.*?)(?=\n|$)',
                r'\1' + processed_func_name,
                section,
                count=1
            )

            section = re.sub(
                r'([*]{0,2}处理过程[:：]\s*)(.*?)(?=\n|$)',
                r'\1' + old_desc_value,
                section,
                count=1
            )

            section = remove_bold_in_process_value(section)

            content = content[:title_start] + section + content[next_title_start:]

    return content







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
        internal_new_added_pattern = r'本期新增\s*/\s*变更的内部逻辑文件[：:]\s*([^\n]*?)(?=\n|$)'
        internal_existing_pattern = r'本期涉及原有但没修改的内部逻辑文件[：:]\s*([^\n]*?)(?=\n|$)'

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
        external_new_added_pattern = r'本期新增\s*/\s*变更的外部逻辑文件[：:]\s*([^\n]*?)(?=\n|$)'
        external_existing_pattern = r'本期涉及原有但没修改的外部逻辑文件[：:]\s*([^\n]*?)(?=\n|$)'

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


def add_field_paragraph(doc, full_text):
    """
    字段名：四号（12pt）+ 加粗
    字段值：四号（12pt），不加粗
    """

    import re

    # 支持所有“即FTR/RET”变体（即FTR/RET / 即 FTR/RET / 即  FTR/RET）
    pattern_data_field = r"本事务功能涉及到的数据文件（即\s*FTR/RET\s*）"
    match = re.search(pattern_data_field, full_text)

    # 匹配统计数据
    stats_key = "本事务功能预计涉及到"

    # 如果字段和统计内容在同一段，则分行处理
    if match and stats_key in full_text:
        start = match.start()
        end = match.end()

        field_part = full_text[:end].strip()
        stats_part = full_text[end:].strip()

        # 1. 添加字段名（加粗）
        paragraph1 = doc.add_paragraph()
        run_name = paragraph1.add_run(field_part)
        set_font(run_name, size=12, bold=True)

        # 2. 添加统计信息（不加粗，自动换行了）
        paragraph2 = doc.add_paragraph()
        run_stats = paragraph2.add_run(stats_part)
        set_font(run_stats, size=12, bold=False)
        return

    # 原有的处理逻辑
    # 按 FIELD_NAMES 的顺序查找所有匹配的字段
    field_positions = []
    for field_name in FIELD_NAMES:
        start = 0
        while True:
            pos = full_text.find(field_name, start)
            if pos == -1:
                break
            field_positions.append((pos, field_name))
            start = pos + 1

    # 如果没有找到字段，按普通段落处理
    if not field_positions:
        paragraph = doc.add_paragraph()
        run = paragraph.add_run(full_text)
        set_font(run, size=12)
        return paragraph

    # 按位置排序
    field_positions.sort(key=lambda x: x[0])

    # 处理每个字段
    last_end = 0
    for i, (pos, field_name) in enumerate(field_positions):
        # 添加字段前的文本（如果有）
        if pos > last_end:
            prev_text = full_text[last_end:pos]
            if prev_text.strip():
                paragraph = doc.add_paragraph()
                run = paragraph.add_run(prev_text)
                set_font(run, size=12)

        # 计算字段值的结束位置
        field_start = pos + len(field_name)
        field_end = len(full_text)
        if i + 1 < len(field_positions):
            field_end = field_positions[i + 1][0]

        field_value = full_text[field_start:field_end].strip()

        # 添加字段名和字段值
        paragraph = doc.add_paragraph()
        run_name = paragraph.add_run(field_name)
        set_font(run_name, size=12, bold=True)

        if field_value:
            run_val = paragraph.add_run(" " + field_value)
            set_font(run_val, size=12, bold=False)

        last_end = field_end

    # 添加最后剩余的文本（如果有）
    if last_end < len(full_text):
        remaining_text = full_text[last_end:]
        if remaining_text.strip():
            paragraph = doc.add_paragraph()
            run = paragraph.add_run(remaining_text)
            set_font(run, size=12)




