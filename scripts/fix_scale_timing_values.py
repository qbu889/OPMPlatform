#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正规模计数时机的 score_value 值
根据 Excel 公式更新为正确的值
"""
import mysql.connector
from config import Config

# 连接数据库
conn = mysql.connector.connect(
    host=Config.MYSQL_HOST,
    port=Config.MYSQL_PORT,
    user=Config.MYSQL_USER,
    password=Config.MYSQL_PASSWORD,
    charset=Config.MYSQL_CHARSET,
    database=Config.KNOWLEDGE_BASE_DB
)

cursor = conn.cursor()

print("=" * 80)
print("修正规模计数时机的 score_value 值")
print("=" * 80)

# Excel 公式对应的正确值
# =IF('3. 调整因子'!C2='3. 调整因子'!B36,'3. 调整因子'!D36,...)
correct_values = {
    '估算早期': '1.39',  # D36 - 概算、预算阶段
    '估算中期': '1.21',  # D37 - 投标、项目计划阶段
    '估算晚期': '1.10',  # D38 - 需求分析阶段
    '项目完成': '1.00',  # D39 - 项目交付后及运维阶段
}

# 查询当前数据
cursor.execute("""
    SELECT id, option_name, score_value 
    FROM fpa_adjustment_factor
    WHERE factor_category = '规模变更调整系数'
    ORDER BY id
""")

rows = cursor.fetchall()
print("\n【当前数据】")
for row in rows:
    print(f"  ID:{row[0]:3d} | {row[1]:12s} | {row[2]}")

# 更新数据
print("\n【执行更新】")
total_updated = 0
for option_name, correct_value in correct_values.items():
    cursor.execute("""
        UPDATE fpa_adjustment_factor
        SET score_value = %s
        WHERE factor_category = '规模变更调整系数' 
        AND option_name = %s
    """, (correct_value, option_name))
    updated = cursor.rowcount
    if updated > 0:
        total_updated += updated
        print(f"  ✓ {option_name:10s} → {correct_value} (更新{updated}条)")

conn.commit()

# 验证更新结果
cursor.execute("""
    SELECT id, option_name, score_value 
    FROM fpa_adjustment_factor
    WHERE factor_category = '规模变更调整系数'
    ORDER BY id
""")

rows = cursor.fetchall()
print("\n【更新后数据】")
for row in rows:
    print(f"  ID:{row[0]:3d} | {row[1]:12s} | {row[2]}")

print(f"\n共更新 {total_updated} 条记录")
print("=" * 80)

cursor.close()
conn.close()

print("\n✅ 数据库更新完成！")
