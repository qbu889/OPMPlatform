#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控综合应用平台功能升级申请文档解析工具

将 Markdown 格式的功能升级申请文档转换为结构化的 Excel 表格。
"""

import re
import os
from typing import List, Dict, Tuple, Optional

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    print("请安装 openpyxl: pip install openpyxl")
    exit(1)


class UpgradeRecord:
    """升级申请记录类"""
    
    def __init__(self):
        self.title: str = ""
        self.date: str = ""  # YYYY-MM-DD format
        self.contact_emails: List[str] = []
        self.contacts_with_phone: List[Tuple[str, str]] = []  # (name, phone)
        self.duty_phone: str = ""
        self.upgrade_description: str = ""
        self.time_window: str = ""  # e.g., "22 点至次日 5 点"
        self.impact_scope: str = ""
        self.features: List[str] = []  # Raw feature descriptions
    
    def to_dict(self, global_seq: int) -> List[Dict]:
        """转换为字典列表，每个功能点一条记录"""
        records = []
        
        # 提取联系人姓名和电话（去重）
        seen_names = {}
        for name, phone in self.contacts_with_phone:
            if name and name not in seen_names:
                seen_names[name] = phone
        contact_names = "; ".join(seen_names.keys())
        contact_phones = "; ".join(seen_names.values())
        
        # 如果没有功能点，创建一条空记录
        if not self.features:
            records.append({
                '序号': global_seq,
                '升级日期': self.date,
                '申请类型': self._get_application_type(),
                '升级时间窗口': self.time_window if self.time_window else "无",
                '影响范围': self.impact_scope,
                '值班电话': self.duty_phone,
                '联系人姓名': contact_names,
                '联系电话': contact_phones,
                '功能分类': "其他",
                '具体功能描述': "无"
            })
        else:
            for idx, feature in enumerate(self.features):
                category = self._categorize_feature(feature)
                records.append({
                    '序号': global_seq,
                    '升级日期': self.date,
                    '申请类型': self._get_application_type(),
                    '升级时间窗口': self.time_window if self.time_window else "无",
                    '影响范围': self.impact_scope,
                    '值班电话': self.duty_phone,
                    '联系人姓名': contact_names,
                    '联系电话': contact_phones,
                    '功能分类': category,
                    '具体功能描述': feature.strip()
                })
        
        return records
    
    def _get_application_type(self) -> str:
        """获取申请类型"""
        title_lower = self.title.lower()
        
        if "漏洞" in title_lower or "安全" in title_lower:
            return "安全加固/漏洞修复"
        elif "迁移" in title_lower:
            return "服务迁移"
        else:
            return "功能升级"
    
    def _categorize_feature(self, feature: str) -> str:
        """根据关键词对功能进行分类"""
        feature_lower = feature.lower()
        
        if "ivr" in feature_lower:
            return "IVR 督办"
        elif "审批" in feature_lower:
            return "审批流程优化"
        elif "pc 端" in feature_lower or "app 端" in feature_lower:
            return "界面优化"
        elif "接口" in feature_lower or "调用" in feature_lower:
            return "接口优化"
        elif "漏洞" in feature_lower or "安全" in feature_lower:
            return "安全加固"
        elif "迁移" in feature_lower and "服务" in feature_lower:
            return "服务迁移"
        elif "场景" in feature_lower or "适配" in feature_lower:
            return "场景适配"
        elif "质检" in feature_lower:
            return "质量检查"
        elif "任务" in feature_lower and ("合并" in feature_lower or "拆分" in feature_lower):
            return "任务管理"
        elif "字段" in feature_lower or "表"在 feature_lower:
            return "数据优化"
        elif "界面" in feature_lower or "隐藏" in feature_lower:
            return "界面优化"
        elif "bug" in feature_lower or "修复" in feature_lower:
            return "BUG 修复"
        else:
            return "其他功能"


def parse_markdown_to_records(markdown_content: str) -> List[Dict]:
    """将 Markdown 内容解析为字典列表"""
    
    # 分割多个升级申请记录 - 基于标题行分割（修正正则表达式）
    title_pattern = r'监控综合应用平台\d{4}年\d{1,2}月\d{1,2}日功能升级申请'
    sections = re.split(rf'(?={title_pattern})', markdown_content)
    
    all_records = []
    global_seq = 1
    
    for section in sections:
        if not section.strip():
            continue
        
        record = parse_single_upgrade(section)
        if record:
            records = record.to_dict(global_seq)
            for r in records:
                global_seq += 1
            all_records.extend(records)
    
    return all_records


def parse_single_upgrade(section: str) -> Optional[UpgradeRecord]:
    """解析单个升级申请记录"""
    
    record = UpgradeRecord()
    
    # 提取标题和日期（修正正则表达式 - 无空格）
    title_match = re.search(r'监控综合应用平台(\d{4}年\d{1,2}月\d{1,2}日) 功能升级申请', section)
    if not title_match:
        # 尝试没有空格的版本
        title_match = re.search(r'监控综合应用平台(\d{4}年\d{1,2}月\d{1,2}日) 功能升级申请', section)
    
    if title_match:
        date_str = title_match.group(1)
        record.date = convert_chinese_date_to_iso(date_str)
    
    # 提取联系人邮箱格式：姓名<邮箱> - 只提取第一组（非重复的）
    email_pattern = r'^([^\n<]+)<([^>]+)>'
    emails = re.findall(email_pattern, section, re.MULTILINE)
    # 过滤掉重复的邮箱（如 bo.2.tang<bo.2.tang@nokia-sbell.com>）
    unique_emails = []
    seen_emails = set()
    for name, email in emails:
        clean_name = name.strip()
        clean_email = email.strip()
        if clean_email and clean_email not in seen_emails:
            unique_emails.append(f"{clean_name}<{clean_email}>")
            seen_emails.add(clean_email)
    record.contact_emails = unique_emails
    
    # 提取联系人电话格式：姓名   电话 (多个空格分隔)
    phone_pattern = r'^([^\n]+)\s{2,}(\d{11})'
    phones = re.findall(phone_pattern, section, re.MULTILINE)
    # 过滤掉重复的联系人（唐波和何熙重复出现）
    seen_contacts = {}
    for name, phone in phones:
        clean_name = name.strip()
        clean_phone = phone.strip()
        if clean_name and clean_phone and clean_name not in seen_contacts:
            seen_contacts[clean_name] = clean_phone
    record.contacts_with_phone = list(seen_contacts.items())
    
    # 提取值班电话：监控综合应用值班 XXXXXXXXXXX
    duty_match = re.search(r'监控综合应用值班\s+(\d{11})', section)
    if duty_match:
        record.duty_phone = duty_match.group(1)
    
    # 提取升级说明和时间窗口 - 更精确的匹配
    upgrade_desc_pattern = r'监控综合应用平台申请 ([\d月日\s点至]+)(.*?)(?=监控综合应用值班|一、升级功能如下：|$)'
    upgrade_match = re.search(upgrade_desc_pattern, section, re.DOTALL)
    if upgrade_match:
        time_part = upgrade_match.group(1).strip()
        desc_part = upgrade_match.group(2).strip()
        
        # 提取时间窗口 "XX 点至 XX 点"
        time_window_match = re.search(r'(\d{1,2}点) 至 (\d{1,2}点)', time_part)
        if time_window_match:
            start_hour = int(time_window_match.group(1).replace('点', ''))
            end_hour = int(time_window_match.group(2).replace('点', ''))
            if start_hour >= 20 or end_hour <= 6:
                record.time_window = f"{start_hour}点至次日{end_hour}点"
            else:
                record.time_window = f"{start_hour}点至{end_hour}点"
        
        # 提取影响范围
        if "智能调度任务" in desc_part:
            record.impact_scope = "智能调度任务"
        elif "综合应用功能" in desc_part:
            record.impact_scope = "综合应用功能"
        elif "监件事件工单" in desc_part:
            record.impact_scope = "监件事件工单、智能调度"
        elif "系统不可用" in desc_part:
            record.impact_scope = "系统整体不可用"
        else:
            # 提取关键影响信息
            if desc_part:
                record.impact_scope = desc_part[:80]
            else:
                record.impact_scope = "无"
    
    # 提取功能列表：1、... 2、... 等 - 更精确的匹配
    # 先找到"一、升级功能如下："或类似标题后的内容
    feature_start_pattern = r'(?:一、|一，)[^\n]*\n((?:[\d]+[、.].*\n?)+)'
    feature_match = re.search(feature_start_pattern, section, re.DOTALL)
    
    if feature_match:
        features_text = feature_match.group(1)
        # 分割每个功能点
        feature_items = re.split(r'(?=[\d]+[、.])', features_text)
        for feature in feature_items:
            feature = feature.strip()
            if feature and len(feature) > 5:
                # 过滤掉非功能描述的行（如联系人信息）
                if not any(keyword in feature for keyword in ['监控综合应用值班', '郑晨昊', '唐波', '何熙', '叶芳彪', '林伟', '林菊兰', '保全']):
                    if not feature.endswith(',') and '<' not in feature:
                        record.features.append(feature)
    
    return record


def convert_chinese_date_to_iso(date_str: str) -> str:
    """将中文日期格式转换为 YYYY-MM-DD 格式"""
    match = re.match(r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日', date_str)
    if not match:
        # 尝试没有空格的版本
        match = re.match(r'(\d{4}) 年 (\d{1,2}) 月 (\d{1,2}) 日', date_str)
    if match:
        year, month, day = match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return ""


def create_excel(records: List[Dict], output_path: str):
    """创建 Excel 文件"""
    
    wb = Workbook()
    ws = wb.active
    ws.title = "功能升级记录"
    
    # 定义表头
    headers = ['序号', '升级日期', '申请类型', '升级时间窗口', 
               '影响范围', '值班电话', '联系人姓名', '联系电话', 
               '功能分类', '具体功能描述']
    
    # 设置表头样式
    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(name='微软雅黑', size=11, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # 写入表头
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
    
    # 设置边框
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # 写入数据行
    for row_idx, record in enumerate(records, 2):
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=record.get(header, ''))
            cell.border = thin_border
            cell.alignment = Alignment(vertical='center', wrap_text=True)
            
            # 奇偶行交替颜色
            if row_idx % 2 == 0:
                cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    
    # 调整列宽
    column_widths = [6, 12, 15, 18, 20, 14, 18, 18, 15, 60]
    for col_idx, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(col_idx)].width = width
    
    # 设置行高
    for row_idx in range(1, len(records) + 2):
        ws.row_dimensions[row_idx].height = 25 if row_idx == 1 else 20
    
    # 保存文件
    wb.save(output_path)
    print(f"Excel 文件已生成：{output_path}")


def main():
    """主函数"""
    
    # 文件路径
    input_file = "/Users/linziwang/PycharmProjects/wordToWord/docs/tools/contentToExcel/contentToChange.md"
    output_file = "/Users/linziwang/PycharmProjects/wordToWord/docs/tools/contentToExcel/shengchengbiaoge.xlsx"
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件不存在 - {input_file}")
        return
    
    # 读取 Markdown 内容
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    print(f"读取 Markdown 文件成功，共 {len(markdown_content)} 字符")
    
    # 解析为记录列表
    records = parse_markdown_to_records(markdown_content)
    
    print(f"解析完成，共生成 {len(records)} 条记录")
    
    # 创建 Excel 文件
    create_excel(records, output_file)
    
    print("\n处理完成!")


if __name__ == "__main__":
    main()
