import pandas as pd
import re
from pathlib import Path

# -------------------------- 配置项 --------------------------
# 输入文本路径（只需修改这里，输出文件名会自动生成）
INPUT_TXT = "查询工单为空的数据.txt"

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
        # 解析文本
        df_result = parse_vertical_txt(INPUT_TXT)
        # 导出Excel
        export_to_excel(df_result, OUTPUT_EXCEL)
        print(f"✅ 转换成功！共处理 {len(df_result)} 条数据")
        print(f"📄 文件已保存：{OUTPUT_EXCEL}")
    except Exception as e:
        print(f"❌ 转换失败：{str(e)}")