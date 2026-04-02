#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端新的预处理逻辑（包含换行符处理）
"""

import re
import json

def fix_field_invalid_escapes(json_string, field_name):
    """修复指定 JSON 字段值中的非法转义字符（包含换行处理）"""
    print(f"  - 检查字段：{field_name}")
    
    field_pattern = rf'("{field_name}"\s*:\s*")(.+?)("\s*[,}}])'
    
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
    
    # 【新增】将字段值中的真实换行转换为 \n 转义
    fixed_value = fixed_value.replace('\n', '\\n')
    fixed_value = fixed_value.replace('\r', '')
    
    print(f"    ✓ 字段 {field_name} 修复完成")
    
    before_fix = match.group(0)
    after_fix = match.group(1) + fixed_value + match.group(3)
    
    return json_string.replace(before_fix, after_fix)


def preprocess_es_data(raw_data):
    """模拟前端新的 preprocessEsData 函数（只在字段层面处理换行）"""
    processed = raw_data
    
    # 1. 先修复特定字段的非法转义（包含换行处理）
    print("\n第一步：修复特定字段的非法转义字符...")
    processed = fix_field_invalid_escapes(processed, 'EVENT_REASON')
    processed = fix_field_invalid_escapes(processed, 'SRC_ORG_ALARM_TEXT')
    processed = fix_field_invalid_escapes(processed, 'EVENT_EFFECT')
    
    # 2. 处理三重引号
    processed = processed.replace('"""', '"')
    
    # 3. HTML 实体
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
    
    # 4. 尾随逗号
    processed = re.sub(r',\s*([\}\]])', r'\1', processed)
    
    # 5. 控制字符
    processed = re.sub(r'[\x00-\x1F\x7F]', '', processed)
    
    # 6. 特殊 Unicode
    processed = processed.replace('\u003c', '<').replace('\u003e', '>')
    
    # 不再全局处理换行符，因为已经在字段层面处理了
    
    return processed


def test_with_real_data():
    """使用真实的 es_data.txt 测试"""
    
    # 从文件读取 curl 命令
    with open('test/kafka/前端展示Kafka 消息.txt', 'r', encoding='utf-8') as f:
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
        
        # 尝试验证原始 es_source_raw
        print("\n[测试 1] 尝试验证原始 es_source_raw...")
        try:
            json.loads(es_source_raw)
            print("✅ 意外成功！原始数据可以直接解析")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ 预期失败：{e}")
            
            # 进行预处理
            print("\n[测试 2] 使用新的前端逻辑进行预处理...")
            fixed_es_source = preprocess_es_data(es_source_raw)
            
            print(f"\n处理后长度：{len(fixed_es_source)}")
            print(f"前 500 字符预览:")
            print(fixed_es_source[:500])
            print("...\n")
            
            print("[测试 3] 尝试验证处理后的 es_source_raw...")
            try:
                parsed = json.loads(fixed_es_source)
                print(f"✅ 成功！解析出 {len(parsed.keys())} 个字段")
                
                # 验证关键字段
                print("\n验证关键字段:")
                print(f"  - EVENT_REASON: {len(parsed.get('EVENT_REASON', ''))} 字符")
                print(f"  - SRC_ORG_ALARM_TEXT: {len(parsed.get('SRC_ORG_ALARM_TEXT', ''))} 字符")
                print(f"  - EVENT_EFFECT: {len(parsed.get('EVENT_EFFECT', ''))} 字符")
                
                # 检查是否包含换行符
                event_reason = parsed.get('EVENT_REASON', '')
                if '\n' in event_reason:
                    actual_newlines = event_reason.count('\n')
                    escaped_newlines = event_reason.count('\\n') if '\\n' in event_reason else 0
                    print(f"\nEVENT_REASON 中的换行符:")
                    print(f"  - 实际换行：{actual_newlines} 个")
                    print(f"  - 转义\\n: {escaped_newlines} 个")
                
                return True
                
            except json.JSONDecodeError as e2:
                print(f"❌ 预处理后仍然失败：{e2}")
                
                # 显示错误位置
                error_pos = e2.pos
                start = max(0, error_pos - 100)
                end = min(len(fixed_es_source), error_pos + 100)
                print(f"\n错误位置附近:\n...{repr(fixed_es_source[start:end])}...")
                return False
        
    except Exception as e:
        print(f"❌ 测试异常：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*80)
    print("测试前端新的预处理逻辑（包含换行符智能处理）")
    print("="*80)
    
    success = test_with_real_data()
    
    if success:
        print("\n" + "="*80)
        print("✅ 测试通过！新逻辑可以正确处理换行符和非法转义")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ 测试失败！需要进一步调试")
        print("="*80)
