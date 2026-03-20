#!/usr/bin/env python3
import re
import json

with open('/Users/linziwang/PycharmProjects/wordToWord/test/kafka/es数据.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 es_source_raw
match = re.search(r'"es_source_raw":"(.+?)","custom_fields":\{\}\}', content, re.DOTALL)
if not match:
    print("未找到")
    exit(1)

raw = match.group(1)
print(f"原始长度：{len(raw)}")

# 查找 ProbableCauseTxt 附近的 \\\\
pos = raw.find('ProbableCauseTxt')
if pos > 0:
    snippet = raw[pos:pos+400]
    print("\nProbableCauseTxt 附近 (原始):")
    print(repr(snippet))
    
    # 找反斜杠序列
    bs_pos = snippet.find('\\\\中')
    if bs_pos >= 0:
        print(f"\n在位置{bs_pos}找到\\\\中 (4 个反斜杠)")
    else:
        # 找单个\\中
        bs_pos = snippet.find('\\中')
        if bs_pos >= 0:
            print(f"\n在位置{bs_pos}找到\\中 (2 个反斜杠)")
            # 数前面有多少个反斜杠
            count = 0
            for i in range(bs_pos-1, -1, -1):
                if snippet[i] == '\\':
                    count += 1
                else:
                    break
            print(f"前面有{count}个反斜杠")
