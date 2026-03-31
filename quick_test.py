#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 Word 转 Excel 功能
"""
from utils.word_to_excel import WordDocumentParser, generate_excel
import os

# 使用 glob 找到测试文件
import glob

test_files = glob.glob("/Users/linziwang/PycharmProjects/wordToWord/test/wordToExcel/*.docx")

if not test_files:
    print("❌ 未找到测试文件")
    exit(1)

test_file = test_files[0]
print(f"📄 测试文件: {os.path.basename(test_file)}")

# 解析文档
print("\n 开始解析...")
parser = WordDocumentParser()
data_rows = parser.parse(test_file)

print(f"\n✅ 解析完成! 共提取 {len(data_rows)} 条功能点")

# 查找"阶段回复"
print("\n" + "="*60)
print("查找目标功能点（阶段回复）")
print("="*60)

found = False
for i, row in enumerate(data_rows, 1):
    if '阶段回复' in row.get('功能点名称', ''):
        found = True
        print(f"\n✅ 找到! 序号 #{i}")
        print(f"   名称: {row.get('功能点名称')}")
        print(f"   描述: {row.get('功能点描述', 'N/A')[:100]}")
        break

if not found:
    print("\n❌ 未找到'阶段回复'")

# 生成 Excel
print("\n📝 生成 Excel 文件...")
output_path = "/tmp/测试输出.xlsx"
generate_excel(data_rows, output_path)
print(f"✅ Excel 已生成: {output_path}")
print(f"\n💡 请打开 Excel 查看完整结果")
