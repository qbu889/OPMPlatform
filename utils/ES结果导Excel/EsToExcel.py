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
    """检测文件格式：竖线分隔 或 JSON"""
    with open(file_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        # 跳过注释行
        while first_line.startswith("#!"):
            first_line = f.readline().strip()
        
        if first_line.startswith("{"):
            return "json"
        else:
            return "pipe_separated"


def parse_json_format(file_path):
    """解析JSON格式的ES查询结果"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
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
    """处理已解析的 JSON 数据"""
    # 提取列名和数据
    columns = [col['name'] for col in data['columns']]
    rows = data['rows']
    
    # 创建DataFrame并映射到目标字段
    df_raw = pd.DataFrame(rows, columns=columns)
    
    # 字段映射关系（ES字段 -> 目标中文字段）
    field_mapping = {
        "EVENT_ID": "EVENT_NUMBER",
        "EVENT_LEVEL_NAME": "事件等级",
        "CITY_NAME": "地市",
        "COUNTY_NAME": "区县",
        "EQUIPMENT_NAME": "网元名称",
        "OBJECT_CLASS_ID": "设备类型",
        "VENDOR_NAME": "设备厂家",
        "FAULT_LOCATION": "定位信息",
        "DISPATCH_INFO.ORDER_TIME": "派单时间",
        "MAINTAIN_TEAM": "维护组",
        "MAIN_NET_SORT_ONE": "网络一级分类",
        "MAIN_NET_SORT_TWO": "网络二级分类",
        "MAIN_NET_SORT_THREE": "网络三级分类",
        "NETWORK_SUB_TYPE_NAME": "二级专业",
        "NETWORK_TYPE_NAME": "一级专业",
        "ALARM_SOURCE": "事件来源",
        "EVENT_NAME": "事件名称",
        "ALARM_NAME": "告警标题",
        "EVENT_STANDARD_ID": "事件标准ID",
        "EVENT_TIME": "事件发生时间",
        "CREATION_EVENT_TIME": "事件创建时间",
        "EVENT_COLLECTION_TIME": "告警发现时间",
        "CANCEL_TIME": "事件清除时间",
        "ORDER_ID": "工单号",
        "EVENT_FP": "事件FP",
        "ORIG_ALARM_FP": "告警FP",
        "ALARM_LEVEL": "省内网管告警级别",
        "CANCEL_ARRIVAL_TIME": "告警清除发现时间",
        "CASE WHEN EVENT_TAG.IS_MATCH_DISPATCH_RULES = 1 THEN 1 ELSE 0 END": "是否满足派单规则",
        "DISPATCH_INFO.DISPATCH_REASON": "DISPATCH_REASON",
        "DISPATCH_INFO.DISPATCH_LEVEL": "省内派单级别",
        "DISPATCH_INFO.DELAY_TIME": "派单时延",
        "CASE WHEN EVENT_TAG.IS_ROOT = 0 THEN 1 ELSE 0 END": "是否子事件",
        "CASE WHEN EVENT_TAG.IS_ROOT = 1 THEN 1 ELSE 0 END": "是否根事件",
        "MASTER_EVENT_FP": "主事件FP",
        "NE_TAG.MACHINE_ROOM_INFO": "机房信息",
        "DISPATCH_INFO.ORDER_TYPE": "通知单转处理单标识",
        "ONE_WARNING_ID": "自研告警预警号",
        "SUPPRESS_NIGHT": "是否夜间"
    }
    
    # 重命名列
    df_renamed = df_raw.rename(columns=field_mapping)
    
    # 只保留目标字段，缺失的填充空值
    df_result = pd.DataFrame()
    for col in TARGET_COLUMNS:
        if col in df_renamed.columns:
            df_result[col] = df_renamed[col]
        else:
            df_result[col] = None
    
    # 替换null值为空字符串
    df_result = df_result.fillna("")
    
    # 添加计算字段：事件清除时间（转时间格式）
    if "事件清除时间" in df_result.columns:
        df_result["事件清除时间（转时间格式）"] = df_result["事件清除时间"].apply(
            lambda x: str(x).replace("T", " ").replace(".000Z", "") if x and x != "" else ""
        )
    
    # 添加工单子单最后清除时间（当前数据中没有，填充空值）
    if "工单子单最后清除时间" not in df_result.columns:
        df_result["工单子单最后清除时间"] = ""
    
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


def parse_vertical_txt(file_path):
    """解析竖线|分隔的告警文本，返回清洗后的DataFrame"""
    data_rows = []
    header_skipped = False  # 标记是否已跳过表头
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#!")]

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
    else:
        return parse_vertical_txt(file_path)


def export_to_excel(df, output_path):
    """导出Excel并自动美化列宽"""
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="告警目标清单", index=False)
        # 自动调整列宽
        worksheet = writer.sheets["告警目标清单"]
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            worksheet.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)


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