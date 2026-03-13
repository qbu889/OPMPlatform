#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试完整的 ES 数据处理"""

import sys
sys.path.append('/')

import json
import re

# 导入修复函数
from routes.kafka_generator_routes import preprocess_json_data

# 真实的 ES 数据片段（包含问题的 \\:）
es_data = '''{
  "SRC_ORG_ALARM_TEXT": """{"addInfo":"Remark:RRU 上次重启原因\\:POWERON, 光口 1 对应的上联光口\\:未接收到光信号\\; 单板序列号\\: 219990953029"}"""
}'''

print("=" * 80)
print("原始数据:")
print(es_data)
print("\n")

# 预处理
processed = preprocess_json_data(es_data)

print("=" * 80)
print("处理后数据:")
print(processed)
print("\n")

# 尝试解析
try:
    result = json.loads(processed)
    print("✅ JSON 解析成功！")
    print("解析结果:", result)
except Exception as e:
    print("❌ JSON 解析失败:", e)
    import traceback
    traceback.print_exc()
