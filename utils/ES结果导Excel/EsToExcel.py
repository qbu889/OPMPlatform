import pandas as pd
import re
import json
import sys
from pathlib import Path

# -------------------------- 配置项 --------------------------
# 输入文本路径（只需修改这里，输出文件名会自动生成）
INPUT_TXT = "查询结果_大批量.txt"

# 自动根据输入文件名生成输出文件名（将 .txt 替换为 .xlsx）
input_path = Path(INPUT_TXT)
OUTPUT_EXCEL = f"{input_path.stem}.xlsx"

# 你要求的标准字段（严格对应）
TARGET_COLUMNS = [
    "EVENT_NUMBER", "事件等级", "地市", "区县", "网元名称", "设备类型", "设备厂家",
    "定位信息", "派单时间", "维护组", "网络一级分类", "网络二级分类", "网络三级分类",
    "二级专业", "一级专业", "事件来源", "事件名称", "告警标题", "事件标准ID",
    "事件发生时间", "事件创建时间", "告警发现时间", "事件清除时间", "事件清除时间（转时间格式）",
    "工单号", "工单子单最后清除时间", "事件FP", "告警FP", "省内网管告警级别",
    "告警清除发现时间", "是否满足派单规则", "DISPATCH_REASON", "省内派单级别",
    "派单时延", "是否子事件", "是否根事件", "主事件FP", "机房信息",
    "通知单转处理单标识", "自研告警预警号", "是否夜间"
]


# -------------------------- 核心处理逻辑 --------------------------
def detect_file_format(file_path):
    """检测文件格式：ES SQL表格(txt) / 竖线分隔 / JSON"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                lines = []
                for line in f:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#!"):
                        lines.append(stripped)
                    if len(lines) >= 3:
                        break
                
                if not lines:
                    return "json"
                
                first_line = lines[0]
                
                # 检测 ES SQL 表格格式（包含 ───+─── 或 -+- 分隔线）
                if len(lines) >= 2:
                    second_line = lines[1]
                    if re.match(r'^[-+\s]+$', second_line) and '|' in first_line:
                        return "es_sql_table"
                
                # 检测 JSON 格式
                if first_line.startswith("{"):
                    return "json"
                
                # 默认为竖线分隔
                return "pipe_separated"
        except (UnicodeDecodeError, Exception):
            continue
    
    return "pipe_separated"


def parse_json_format(file_path):
    """解析JSON格式的ES查询结果"""
    # 尝试多种编码读取文件，优先尝试中文编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    content = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            used_encoding = encoding
            break
        except (UnicodeDecodeError, Exception):
            continue
    
    if content is None:
        # 最后使用 latin-1（不会失败）
        with open(file_path, "r", encoding="latin-1") as f:
            content = f.read()
        used_encoding = 'latin-1'
    
    print(f"📖 使用编码: {used_encoding}")
    
    # 移除可能的注释行（以#!开头）
    lines = [line for line in content.split('\n') if not line.strip().startswith('#!')]
    cleaned_content = '\n'.join(lines)
    
    # 尝试直接解析，如果失败则进行修复
    try:
        data = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON 解析失败，尝试自动修复...\n   错误: {e.msg} at line {e.lineno}")
        
        # 尝试使用预处理器修复
        fixed_file = _auto_fix_json_file(file_path)
        if fixed_file and fixed_file.exists():
            print(f"📖 读取修复后的文件: {fixed_file}")
            with open(fixed_file, 'r', encoding='utf-8') as f:
                fixed_content = f.read()
            try:
                data = json.loads(fixed_content)
                print("✅ JSON 修复成功")
                return _process_json_data(data)
            except json.JSONDecodeError as e2:
                print(f"❌ 修复后仍然失败: {e2}")
        
        # 如果预处理器失败，尝试内置修复
        print("🔧 尝试内置修复...")
        cleaned_content = _fix_json_quotes(cleaned_content)
        try:
            data = json.loads(cleaned_content)
            print("✅ 内置修复成功")
        except json.JSONDecodeError as e3:
            print(f"❌ 所有修复方法均失败")
            print(f"💡 建议：先运行 fix_json_format.py 预处理文件")
            raise
    
    return _process_json_data(data)
    
def _process_json_data(data):
    """处理已解析的 JSON 数据 - 支持多种格式"""
    # 验证数据结构
    if not isinstance(data, dict):
        raise ValueError(f"JSON 数据格式错误：期望字典类型，实际为 {type(data).__name__}")
    
    # 检测是否为 ES SQL 格式（columns + rows）
    if 'columns' in data and 'rows' in data:
        return _process_es_sql_json(data)
    
    # 检测是否为 ES _search 格式（hits.hits[]）
    if 'hits' in data and isinstance(data['hits'], dict) and 'hits' in data['hits']:
        return _process_es_search_json(data)
    
    # 其他格式报错
    available_keys = list(data.keys())
    error_msg = "不支持的 JSON 数据格式\n"
    error_msg += f"可用字段: {', '.join(available_keys)}\n\n"
    error_msg += "💡 支持的格式：\n"
    error_msg += "1. ES SQL 查询结果：{\"columns\": [...], \"rows\": [...]}\n"
    error_msg += "2. ES _search 查询结果：{\"hits\": {\"hits\": [{\"_source\": {...}}]}}\n\n"
    error_msg += "✅ 建议使用 POST /_sql?format=json 或 POST /_search 接口获取数据"
    raise ValueError(error_msg)


def _process_es_sql_json(data):
    """处理 ES SQL JSON 格式（columns + rows）"""
    # 提取列名和数据
    columns = [col['name'] for col in data['columns']]
    rows = data['rows']
    
    # 创建 DataFrame
    df_result = pd.DataFrame(rows, columns=columns)
    df_result = df_result.fillna("")
    
    # 格式化时间字段
    _format_time_columns(df_result)
    
    print(f"✅ [ES SQL JSON] 动态导出 {len(columns)} 个字段: {', '.join(columns)}")
    return df_result


def _process_es_search_json(data):
    """处理 ES _search JSON 格式（hits.hits[]）"""
    hits = data['hits']['hits']
    
    if not hits:
        raise ValueError("ES 查询结果为空，没有命中任何文档")
    
    # 从第一个命中的 _source 中提取所有字段
    first_source = hits[0].get('_source', {})
    if not first_source:
        raise ValueError("ES 查询结果中缺少 _source 字段")
    
    # 获取所有字段名（按第一个文档的字段顺序）
    columns = list(first_source.keys())
    
    # 提取数据
    rows = []
    for hit in hits:
        source = hit.get('_source', {})
        row = [source.get(col, '') for col in columns]
        rows.append(row)
    
    # 创建 DataFrame
    df_result = pd.DataFrame(rows, columns=columns)
    df_result = df_result.fillna("")
    
    # 格式化时间字段
    _format_time_columns(df_result)
    
    print(f"✅ [ES _search JSON] 共 {len(hits)} 条记录，{len(columns)} 个字段")
    print(f"   字段列表: {', '.join(columns[:10])}{'...' if len(columns) > 10 else ''}")
    return df_result


def _auto_fix_json_file(input_path):
    """自动调用修复脚本处理 JSON 文件"""
    import subprocess
    
    input_file = Path(input_path)
    output_file = input_file.with_name(f"{input_file.stem}_fixed{input_file.suffix}")
    
    # 如果修复后的文件已存在，直接使用
    if output_file.exists():
        print(f"✨ 发现已修复的文件: {output_file}")
        return output_file
    
    # 查找修复脚本
    script_dir = Path(__file__).parent
    fix_script = script_dir / "fix_json_format.py"
    
    if not fix_script.exists():
        print(f"⚠️  未找到修复脚本: {fix_script}")
        return None
    
    try:
        print(f"🔧 调用修复脚本处理文件...")
        result = subprocess.run(
            [sys.executable, str(fix_script), str(input_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0 and output_file.exists():
            return output_file
        else:
            print(f"⚠️  修复脚本执行失败: {result.stderr}")
            return None
    except Exception as e:
        print(f"⚠️  调用修复脚本异常: {e}")
        return None


def parse_es_sql_table(file_path):
    """解析 ES SQL 表格格式（POST /_sql?format=txt 返回的结果）
    示例格式：
      CREATION_EVENT_TIME   |     EVENT_FP     |  ORDER_ID  
    ------------------------+------------------+------------
    2026-04-16T10:04:21.000Z|2681494263_...    |FJ-076-...
    """
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    lines = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                lines = [line.rstrip('\n') for line in f if line.strip() and not line.startswith("#!")]
            used_encoding = encoding
            break
        except (UnicodeDecodeError, Exception):
            continue
    
    if lines is None:
        with open(file_path, "r", encoding="latin-1") as f:
            lines = [line.rstrip('\n') for line in f if line.strip() and not line.startswith("#!")]
        used_encoding = 'latin-1'
    
    print(f"📖 使用编码: {used_encoding}")
    
    # 找到分隔线位置（包含 ---+--- 的行）
    separator_idx = -1
    for i, line in enumerate(lines):
        if re.match(r'^[-+\s]+$', line) and '+' in line:
            separator_idx = i
            break
    
    if separator_idx == -1:
        raise ValueError("未找到表格分隔线，无法解析 ES SQL 表格格式")
    
    # 解析表头（分隔线上一行）
    header_line = lines[separator_idx - 1]
    # 按 | 分割表头，去除首尾空格
    columns = [col.strip() for col in header_line.split('|') if col.strip()]
    
    # 解析数据行（分隔线之后的所有行）
    data_rows = []
    for line in lines[separator_idx + 1:]:
        # 跳过空行和分隔线
        if not line.strip() or re.match(r'^[-+\s]+$', line):
            continue
        
        # 按 | 分割数据，注意处理尾部多余空格
        parts = line.split('|')
        row = []
        for i, col in enumerate(parts):
            if i < len(columns):
                row.append(col.strip())
        
        # 只保留列数匹配的行
        if len(row) == len(columns):
            data_rows.append(row)
    
    # 创建 DataFrame
    df = pd.DataFrame(data_rows, columns=columns)
    df = df.fillna("")
    
    # 格式化时间字段
    _format_time_columns(df)
    
    print(f"✅ [ES SQL 表格] 解析成功：{len(columns)} 个字段，{len(data_rows)} 条数据")
    return df


def _format_time_columns(df):
    """格式化 DataFrame 中的时间字段（ISO 8601 -> 标准格式）"""
    time_columns_count = 0
    for col in df.columns:
        col_dtype = str(df[col].dtype)
        if col_dtype in ['object', 'str']:
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if sample and isinstance(sample, str) and 'T' in sample and ('Z' in sample or '+' in sample):
                try:
                    def format_time(x):
                        if not x or x == '':
                            return x
                        time_str = str(x).replace('T', ' ').replace('Z', '')
                        if '.' in time_str:
                            time_str = time_str.split('.')[0]
                        return time_str
                    
                    df[col] = df[col].apply(format_time)
                    time_columns_count += 1
                except Exception:
                    pass
    
    if time_columns_count > 0:
        print(f"✅ 共处理 {time_columns_count} 个时间字段")


def parse_vertical_txt(file_path):
    """解析竖线|分隔的告警文本，返回清洗后的DataFrame"""
    data_rows = []
    header_skipped = False  # 标记是否已跳过表头
    
    # 尝试多种编码读取文件，优先尝试中文编码
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin-1']
    lines = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#!")]
            used_encoding = encoding
            break
        except (UnicodeDecodeError, Exception):
            continue
    
    if lines is None:
        # 最后使用 latin-1（不会失败）
        with open(file_path, "r", encoding="latin-1") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith("#!")]
        used_encoding = 'latin-1'
    
    print(f"📖 使用编码: {used_encoding}")

    # 跳过表头分隔线和表头行
    for line in lines:
        # 跳过分隔线（---------------+---------------...）
        if re.match(r"^-+\+-+", line):
            continue
        
        # 跳过表头行（包含字段名的行）
        if not header_skipped:
            # 如果第一行包含 EVENT_NUMBER 或其他目标字段名，则跳过
            if any(col in line for col in TARGET_COLUMNS[:5]):  # 检查前5个字段
                header_skipped = True
                continue
        
        # 按|分割，去除首尾空格，替换null为空
        row = [col.strip().replace("null", "") for col in line.split("|")]
        if len(row) == len(TARGET_COLUMNS):
            data_rows.append(row)

    # 构建标准表格
    df = pd.DataFrame(data_rows, columns=TARGET_COLUMNS)
    
    # 格式化时间字段：将 ISO 8601 格式转换为标准格式
    # 例如：2026-04-09T10:37:30.000Z -> 2026-04-09 10:37:30（去掉毫秒）
    time_columns_count = 0
    for col in df.columns:
        col_dtype = str(df[col].dtype)
        
        # 支持 object 和 str 类型
        if col_dtype in ['object', 'str']:
            # 检测是否为时间格式（包含 T 和 Z）
            sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if sample and isinstance(sample, str) and 'T' in sample and ('Z' in sample or '+' in sample):
                try:
                    print(f"⏰ 检测到时间列: {col}，示例值: {sample}")
                    
                    def format_time(x):
                        if not x or x == '':
                            return x
                        # 转换：2026-04-09T10:37:30.000Z -> 2026-04-09 10:37:30
                        time_str = str(x).replace('T', ' ').replace('Z', '')
                        # 去掉毫秒部分（如果有）
                        if '.' in time_str:
                            time_str = time_str.split('.')[0]
                        return time_str
                    
                    df[col] = df[col].apply(format_time)
                    time_columns_count += 1
                    print(f"✅ 时间列 {col} 已格式化，示例: {df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else 'N/A'}")
                except Exception as e:
                    print(f"❌ 时间列 {col} 格式化失败: {e}")
                    pass  # 如果转换失败，保持原样
    
    if time_columns_count > 0:
        print(f"✅ 共处理 {time_columns_count} 个时间字段")
    
    return df


def _fix_json_quotes(content):
    """修复 JSON 中未转义的双引号和控制字符问题"""
    import re
    
    # 策略：逐行处理，识别并修复字符串值中的问题
    lines = content.split('\n')
    fixed_lines = []
    in_string_value = False  # 标记是否在字符串值中
    
    for line_num, line in enumerate(lines, 1):
        # 跳过纯结构行
        stripped = line.strip()
        if not stripped or stripped in ['[', ']', '{', '}', '[', ']'] or re.match(r'^[\s]*[,\]:]+[\s]*$', stripped):
            fixed_lines.append(line)
            continue
        
        # 检测是否是多行字符串的一部分（以 """ 开头或结尾）
        if '"""' in line:
            # 替换连续的多个双引号为单个
            line = re.sub(r'"{3,}', '"', line)
        
        # 清理字符串值中的非法控制字符（保留 \t, \n, \r 的转义形式）
        # 匹配引号之间的内容
        def clean_string_content(match):
            full_match = match.group(0)
            # 提取引号内的内容
            start_quote = full_match.find('"')
            end_quote = full_match.rfind('"')
            if start_quote == end_quote:
                return full_match
            
            prefix = full_match[:start_quote + 1]
            content_part = full_match[start_quote + 1:end_quote]
            suffix = full_match[end_quote:]
            
            # 替换实际的控制字符为空格或转义序列
            # 保留已转义的字符 \n, \t, \r 等
            cleaned = re.sub(r'(?<!\\)\n', '\\n', content_part)  # 未转义的换行
            cleaned = re.sub(r'(?<!\\)\r', '\\r', cleaned)  # 未转义的回车
            cleaned = re.sub(r'(?<!\\)\t', '\\t', cleaned)  # 未转义的制表符
            
            return prefix + cleaned + suffix
        
        # 对整行应用清理（只处理字符串值部分）
        try:
            line = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', clean_string_content, line)
        except:
            pass  # 如果正则失败，保持原样
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def parse_es_result(file_path):
    """智能解析ES查询结果（自动检测格式）"""
    file_format = detect_file_format(file_path)
    print(f"📋 检测到文件格式：{file_format}")
    
    if file_format == "json":
        return parse_json_format(file_path)
    elif file_format == "es_sql_table":
        return parse_es_sql_table(file_path)
    else:
        return parse_vertical_txt(file_path)


def export_to_excel(df, output_path, use_xlsx=True):
    """导出Excel并自动美化列宽
    
    Args:
        df: DataFrame 数据
        output_path: 输出文件路径
        use_xlsx: 是否使用 xlsx 格式（默认True）
                   False 则使用 xlwt 直接生成 xls 格式（兼容达梦数据库）
    """
    if use_xlsx:
        # 使用 openpyxl 引擎导出 xlsx 格式（推荐）
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="告警目标清单", index=False)
            # 自动调整列宽
            worksheet = writer.sheets["告警目标清单"]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                worksheet.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)
    else:
        # 使用 xlwt 直接生成 xls 格式（兼容达梦数据库迁移工具）
        import xlwt
        
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('告警目标清单')
        
        # 写入表头
        for col_idx, column_name in enumerate(df.columns):
            worksheet.write(0, col_idx, str(column_name))
        
        # 写入数据
        for row_idx, row in enumerate(df.itertuples(index=False), start=1):
            for col_idx, value in enumerate(row):
                # 处理各种数据类型
                if pd.isna(value):
                    worksheet.write(row_idx, col_idx, '')
                elif isinstance(value, (int, float)):
                    worksheet.write(row_idx, col_idx, value)
                else:
                    worksheet.write(row_idx, col_idx, str(value))
        
        # 自动调整列宽
        for col_idx, column_name in enumerate(df.columns):
            # 计算该列最大宽度
            max_width = len(str(column_name))
            for row_idx in range(len(df)):
                cell_value = df.iloc[row_idx, col_idx]
                if not pd.isna(cell_value):
                    cell_width = len(str(cell_value))
                    max_width = max(max_width, cell_width)
            # 设置列宽（xls 单位是 256 * 字符数）
            worksheet.col(col_idx).width = min(max_width + 2, 50) * 256
        
        # 保存文件
        workbook.save(output_path)
        print(f"✅ 已生成 XLS 格式文件：{output_path}")
    
    return output_path


# -------------------------- 执行转换 --------------------------
if __name__ == "__main__":
    try:
        # 智能解析文本（自动检测格式）
        df_result = parse_es_result(INPUT_TXT)
        # 导出Excel
        export_to_excel(df_result, OUTPUT_EXCEL)
        print(f"✅ 转换成功！共处理 {len(df_result)} 条数据")
        print(f"📄 文件已保存：{OUTPUT_EXCEL}")
    except Exception as e:
        print(f"❌ 转换失败：{str(e)}")
        import traceback
        traceback.print_exc()