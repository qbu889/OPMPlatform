#!/usr/bin/env python3
import re

# 测试字符串：模拟从 curl 命令接收到的数据
test_str = 'ProbableCauseTxt:\\u798f\\u5dde\\u4e2d\\中兴'

print(f"原始：{repr(test_str)}")

# 方法 1: r'\\\1'
result1 = re.sub(r'\\([^nrtbf\\"/])', r'\\\1', test_str)
print(f"方法 1 (r'\\\\\\1'): {repr(result1)}")

# 方法 2: r'\\\\\1'  
result2 = re.sub(r'\\([^nrtbf\\"/])', r'\\\\\1', test_str)
print(f"方法 2 (r'\\\\\\\\\\1'): {repr(result2)}")

# 方法 3: 直接使用函数
def replace_func(match):
    char = match.group(1)
    return '\\\\' + char  # 返回两个字面反斜杠 + 字符
    
result3 = re.sub(r'\\([^nrtbf\\"/])', replace_func, test_str)
print(f"方法 3 (函数): {repr(result3)}")

# 验证 JSON 是否合法
import json
test_json = f'{{"key": "value with \\中"}}'  # 非法
print(f"\n非法 JSON: {repr(test_json)}")
try:
    json.loads(test_json)
except Exception as e:
    print(f"解析失败：{e}")

test_json2 = f'{{"key": "value with \\\\中"}}'  # 合法
print(f"\n合法 JSON: {repr(test_json2)}")
try:
    data = json.loads(test_json2)
    print(f"解析成功：{data}")
except Exception as e:
    print(f"解析失败：{e}")
