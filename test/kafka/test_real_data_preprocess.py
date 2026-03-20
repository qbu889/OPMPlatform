#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实的 es_data.txt 文件测试前端预处理逻辑
"""

import re
import json
import sys

def fix_field_invalid_escapes(json_string, field_name):
    """修复指定 JSON 字段值中的非法转义字符"""
    print(f"  - 检查字段：{field_name}")
    
    field_pattern = rf'("{field_name}"\s*:\s*")(.+?)("\s*[,,}}])'
    
    match = re.search(field_pattern, json_string, re.DOTALL)
    if not match:
        print(f"    ✓ 字段 {field_name} 未找到或格式异常，跳过")
        return json_string
    
    field_value = match.group(2)
    print(f"    发现字段 {field_name}，值长度：{len(field_value)}")
    
    fixed_value = field_value
    
    # 合法转义序列列表
    valid_escapes = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']
    
    # 保护合法转义
    placeholders = {}
    for index, escape in enumerate(valid_escapes):
        placeholder = f'__VALID_ESCAPE_{index}__'
        placeholders[placeholder] = escape
        fixed_value = fixed_value.replace(escape, placeholder)
    
    # 处理 Unicode
    def protect_unicode(m):
        placeholder = f'__UNICODE_{m.group(0)[1:]}__'
        placeholders[placeholder] = m.group(0)
        return placeholder
    
    fixed_value = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, fixed_value)
    
    # 修复非法转义
    fixed_value = re.sub(r'\\([^\\])', r'\\\\\1', fixed_value)
    
    # 恢复合法转义
    for placeholder, escape in placeholders.items():
        fixed_value = fixed_value.replace(placeholder, escape)
    
    print(f"    ✓ 字段 {field_name} 修复完成")
    
    before_fix = match.group(0)
    after_fix = match.group(1) + fixed_value + match.group(3)
    
    return json_string.replace(before_fix, after_fix)


def preprocess_es_data(raw_data):
    """模拟前端的 preprocessEsData 函数"""
    processed = raw_data
    
    # 1. 处理三重引号
    processed = processed.replace('"""', '"')
    
    # 2. HTML 实体
    html_entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    for entity, replacement in html_entities.items():
        processed = processed.replace(entity, replacement)
    
    # 3. 尾随逗号
    processed = re.sub(r',\s*([\}\]])', r'\1', processed)
    
    # 4. 控制字符
    processed = re.sub(r'[\x00-\x1F\x7F]', '', processed)
    
    # 5. 特殊 Unicode
    processed = processed.replace('\u003c', '<').replace('\u003e', '>')
    
    # 6. 换行符
    processed = processed.replace('\r\n', '\n').replace('\r', '\n')
    
    # 7. 修复特定字段
    print("\n开始修复特定字段的非法转义字符...")
    processed = fix_field_invalid_escapes(processed, 'EVENT_REASON')
    processed = fix_field_invalid_escapes(processed, 'SRC_ORG_ALARM_TEXT')
    processed = fix_field_invalid_escapes(processed, 'EVENT_EFFECT')
    
    return processed


def test_real_es_data():
    """测试真实的 ES 数据"""
    
    # 从文件读取 curl 命令
    with open('test/kafka/kafka生成请求CURL.txt', 'r', encoding='utf-8') as f:
        curl_content = f.read()
    
    # 提取 --data-raw 部分
    match = re.search(r"--data-raw \$'(.+?)'$", curl_content, re.DOTALL)
    if not match:
        print("❌ 无法提取数据")
        return False
    
    raw_data = match.group(1)
    print(f"✅ 提取成功，原始长度：{len(raw_data)}")
    
    # 使用 bash 解析转义
    import subprocess
    cmd = ['bash', '-c', f'echo -n $\'{raw_data}\'']
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0:
        print(f"❌ Bash 解析失败")
        return False
    
    post_data_bytes = result.stdout
    
    try:
        post_data_str = post_data_bytes.decode('utf-8')
        
        # 解析外层的请求 JSON
        request_json = json.loads(post_data_str)
        es_source_raw = request_json.get('es_source_raw', '')
        
        print(f"✅ 成功提取 es_source_raw，长度：{len(es_source_raw)}")
        
        # 显示问题字段的内容
        print("\n📋 检查问题字段内容:")
        
        # 尝试查找 ProbableCauseTxt 字段
        probable_cause_match = re.search(r'"ProbableCauseTxt":"([^"]*)"', es_source_raw)
        if probable_cause_match:
            prob_txt = probable_cause_match.group(1)
            print(f"\nProbableCauseTxt 内容:")
            print(f"  {repr(prob_txt)}")
            
            # 检查是否有非法转义
            if '\\' in prob_txt:
                print(f"  ⚠️  发现反斜杠，可能存在非法转义")
                # 找出具体的转义序列
                escapes = re.findall(r'\\.', prob_txt)
                print(f"  转义序列：{escapes}")
        
        # 尝试验证整个 es_source_raw
        print("\n[测试 1] 尝试验证原始 es_source_raw...")
        try:
            json.loads(es_source_raw)
            print("✅ 意外成功！原始数据可以直接解析")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ 预期失败：{e}")
            
            # 显示错误位置
            error_pos = e.pos
            start = max(0, error_pos - 100)
            end = min(len(es_source_raw), error_pos + 100)
            print(f"\n错误位置附近：\n...{repr(es_source_raw[start:end])}...")
            
            # 进行预处理
            print("\n[测试 2] 使用前端逻辑进行预处理...")
            fixed_es_source = preprocess_es_data(es_source_raw)
            
            print("\n[测试 3] 尝试验证处理后的 es_source_raw...")
            try:
                parsed = json.loads(fixed_es_source)
                print(f"✅ 成功！解析出 {len(parsed.keys())} 个字段")
                
                # 验证修复后的 ProbableCauseTxt
                fixed_prob_match = re.search(r'"ProbableCauseTxt":"([^"]*)"', fixed_es_source)
                if fixed_prob_match:
                    fixed_prob_txt = fixed_prob_match.group(1)
                    print(f"\n修复后的 ProbableCauseTxt:")
                    print(f"  {repr(fixed_prob_txt)}")
                    
                    # 检查转义是否正确
                    if '\\\\' in fixed_prob_txt:
                        print(f"  ✅ 反斜杠已正确转义为 \\\\")
                
                return True
                
            except json.JSONDecodeError as e2:
                print(f"❌ 预处理后仍然失败：{e2}")
                return False
        
    except Exception as e:
        print(f"❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print("测试真实 ES 数据的前端预处理功能")
    print("="*80)
    
    success = test_real_es_data()
    
    if success:
        print("\n" + "="*80)
        print("✅ 测试通过！前端预处理可以修复真实数据的问题")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ 测试失败！需要进一步调试")
        print("="*80)
        sys.exit(1)
