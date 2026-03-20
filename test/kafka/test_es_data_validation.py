#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试写入 ES 数据的 JSON 格式验证
模拟 POST /kafka-generator/generate 接口的真实请求
"""

import sys
import os
import json
import re

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def load_es_data():
    """从 kafka生成请求CURL.txt 文件加载真实的 curl 命令"""
    with open('test/kafka/kafka生成请求CURL.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 --data-raw 后面的 JSON 数据
    match = re.search(r"--data-raw \$'(.+?)'", content, re.DOTALL)
    if not match:
        raise Exception("无法从 kafka生成请求CURL.txt 中提取 JSON 数据")
    
    raw_json = match.group(1)
    print(f"✅ 成功提取原始 JSON 数据，长度：{len(raw_json)}")
    return raw_json

def extract_es_source(raw_json):
    """从请求 JSON 中提取 es_source_raw 字段"""
    try:
        # 先尝试直接解析
        request_data = json.loads(raw_json)
        es_source = request_data.get('es_source_raw', '')
        print(f"✅ 成功提取 es_source_raw，长度：{len(es_source)}")
        return es_source, request_data
    except json.JSONDecodeError as e:
        print(f"❌ 请求 JSON 解析失败：{e}")
        # 如果整个请求 JSON 都无法解析，尝试手动提取
        match = re.search(r'"es_source_raw":"(.+?)","custom_fields":', raw_json, re.DOTALL)
        if match:
            es_source = match.group(1)
            # 处理转义：这是从 bash $'...' 中提取的数据，需要还原转义
            # \" -> " (JSON 字符串内的双引号)
            # \\n -> \n (换行符)
            # \\t -> \t (制表符)
            # \\r -> \r (回车符)
            # \\\\ -> \\ (反斜杠)
            es_source = es_source.replace('\\"', '"')
            es_source = es_source.replace('\\\n', '\n')  # bash 中的字面换行
            es_source = es_source.replace('\\\\n', '\\n')  # JSON 的\n
            es_source = es_source.replace('\\\\t', '\\t')  # JSON 的\t
            es_source = es_source.replace('\\\\r', '\\r')  # JSON 的\r
            es_source = es_source.replace('\\\\\\\\', '\\\\')  # JSON 的\\
            print(f"✅ 手动提取 es_source_raw，长度：{len(es_source)}")
            return es_source, None
        raise

def fix_invalid_escapes(text):
    r"""修复非法的转义序列
    
    JSON 只允许以下转义序列：
    \\, \", \/, \b, \f, \n, \r, \t, \uXXXX
    
    其他如 \:, \(, \), \中等都是非法的
    """
    print("🔧 开始修复非法转义序列...")
    
    # 策略：先保护合法的转义，然后修复非法的
    
    # 第一步：临时替换合法的转义序列
    placeholders = {}
    valid_escapes = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']
    
    for i, escape_seq in enumerate(valid_escapes):
        placeholder = f'__VALID_ESCAPE_{i}__'
        placeholders[placeholder] = escape_seq
        text = text.replace(escape_seq, placeholder)
    
    # 第二步：处理 \uXXXX 格式
    def protect_unicode(match):
        return f'__UNICODE_{match.group(0)[1:]}__'
    
    text = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, text)
    
    # 第三步：保护字符串内容
    string_placeholders = {}
    counter = [0]
    
    def save_string(match):
        key = f'__STRING_{counter[0]}__'
        string_placeholders[key] = match.group(0)
        counter[0] += 1
        return key
    
    # 匹配 JSON 字符串（包括引号）
    text = re.sub(r'"(?:[^"\\]|\\.)*"', save_string, text)
    
    # 第四步：现在剩下的 \ 后跟字符都是非法的，双写反斜杠
    text = re.sub(r'\\(.)', r'\\\\\1', text)
    
    # 第五步：恢复字符串内容
    for key, value in string_placeholders.items():
        text = text.replace(key, value)
    
    # 第六步：恢复合法转义和 Unicode
    for placeholder, escape_seq in placeholders.items():
        text = text.replace(placeholder, escape_seq)
    
    text = re.sub(r'__UNICODE_([0-9a-fA-F]{4})__', r'\\u\1', text)
    
    print(f"✅ 转义序列修复完成")
    return text

def process_json_strings(text):
    """处理 JSON 字符串中的双重转义"""
    print("🔧 处理双重转义字符...")
    
    pattern = r'"((?:[^"\\]|\\.)*)"'
    
    def replace_string_content(match):
        content = match.group(1)
        # 修复双重转义
        content = content.replace('\\\\"', '\\"')
        content = content.replace('\\\\n', '\\n')
        content = content.replace('\\\\r', '\\r')
        content = content.replace('\\\\t', '\\t')
        content = content.replace('\\\\\\\\', '\\\\')
        return f'"{content}"'
    
    result = re.sub(pattern, replace_string_content, text)
    print("✅ 双重转义处理完成")
    return result

def validate_and_fix(json_string, description=""):
    """验证并修复 JSON"""
    print(f"\n{'='*80}")
    print(f"验证：{description}")
    print(f"{'='*80}")
    
    try:
        # 尝试直接解析
        json.loads(json_string)
        print("✅ JSON 格式正确，无需修复")
        return json_string, True
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误：{e}")
        
        # 尝试修复
        fixed = fix_invalid_escapes(json_string)
        fixed = process_json_strings(fixed)
        
        try:
            json.loads(fixed)
            print("✅ 修复成功！")
            return fixed, True
        except json.JSONDecodeError as e2:
            print(f"❌ 修复后仍然失败：{e2}")
            return fixed, False

def test_es_data():
    """测试 ES 数据的完整流程"""
    print("\n" + "="*80)
    print("开始测试写入 ES 数据的 JSON 格式验证")
    print("="*80)
    
    # 1. 加载数据
    print("\n[步骤 1] 加载 kafka生成请求CURL.txt")
    raw_request = load_es_data()
    
    # 2. 提取 es_source_raw
    print("\n[步骤 2] 提取 es_source_raw 字段")
    es_source, request_data = extract_es_source(raw_request)
    
    # 3. 验证并修复 es_source_raw
    print("\n[步骤 3] 验证 es_source_raw 的 JSON 格式")
    fixed_es_source, success = validate_and_fix(es_source, "es_source_raw 字段")
    
    if not success:
        print("\n⚠️  警告：es_source_raw 修复后仍然无法解析")
        # 显示错误位置附近的内容
        try:
            json.loads(fixed_es_source)
        except json.JSONDecodeError as e:
            error_pos = e.pos
            start = max(0, error_pos - 100)
            end = min(len(fixed_es_source), error_pos + 100)
            print(f"\n错误位置附近的内容:")
            print(f"...{fixed_es_source[start:end]}...")
    else:
        print("\n✅ es_source_raw 验证通过")
    
    # 4. 如果 request_data 存在，验证整个请求
    if request_data:
        print("\n[步骤 4] 验证完整的请求 JSON")
        try:
            json.dumps(request_data)
            print("✅ 完整请求 JSON 格式正确")
        except json.JSONDecodeError as e:
            print(f"❌ 完整请求 JSON 格式错误：{e}")
            
            # 尝试修复整个请求
            fixed_request, success = validate_and_fix(raw_request, "完整请求 JSON")
            if success:
                print("✅ 完整请求修复成功")
    
    # 5. 显示统计信息
    print("\n" + "="*80)
    print("测试统计")
    print("="*80)
    print(f"原始请求长度：{len(raw_request)}")
    print(f"es_source_raw 长度：{len(es_source)}")
    print(f"修复后 es_source_raw 长度：{len(fixed_es_source)}")
    print(f"长度变化：{len(fixed_es_source) - len(es_source)}")
    
    # 6. 尝试实际调用接口（可选）
    print("\n" + "="*80)
    print("是否实际调用接口测试？(y/n)")
    print("="*80)
    print("提示：如需实际测试，请使用以下 curl 命令:")
    print(f"\ncurl 'http://127.0.0.1:5001/kafka-generator/generate' \\")
    print(f"  -X POST \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{json.dumps({'es_source_raw': fixed_es_source, 'custom_fields': {}})[:200]}...'")
    
    return success

if __name__ == "__main__":
    try:
        success = test_es_data()
        if success:
            print("\n✅ 测试通过！JSON 格式验证成功")
            sys.exit(0)
        else:
            print("\n❌ 测试失败！JSON 格式验证未通过")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
