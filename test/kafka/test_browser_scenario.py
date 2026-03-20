#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端新的预处理逻辑（模拟浏览器实际场景）
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
    
    # 【关键】第一步：先处理 \uXXXX（可能是三个或更多反斜杠的情况）
    # 将 \\\uXXXX 转换为 \\uXXXX（保留一个合法的反斜杠用于 Unicode）
    # 正则说明：匹配连续的反斜杠（至少 2 个），后面紧跟 uXXXX
    # 替换为单个反斜杠（这样加上后面的 u 就构成合法的 Unicode 转义）
    fixed_value = re.sub(r'\\{2,}(?=u[0-9a-fA-F]{4})', r'\\', fixed_value)
    
    # 合法转义序列列表
    valid_escapes = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']
    
    # 第二步：保护合法转义
    placeholders = {}
    for index, escape in enumerate(valid_escapes):
        placeholder = f'__VALID_ESCAPE_{index}__'
        placeholders[placeholder] = escape
        fixed_value = fixed_value.replace(escape, placeholder)
    
    # 第三步：处理 Unicode
    def protect_unicode(m):
        placeholder = f'__UNICODE_{m.group(0)[1:]}__'
        placeholders[placeholder] = m.group(0)
        return placeholder
    
    fixed_value = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, fixed_value)
    
    # 第四步：修复非法转义
    fixed_value = re.sub(r'\\([^\\])', r'\\\\\1', fixed_value)
    
    # 第五步：恢复合法转义
    for placeholder, escape in placeholders.items():
        fixed_value = fixed_value.replace(placeholder, escape)
    
    # 第六步：将字段值中的真实换行转换为 \n 转义
    fixed_value = fixed_value.replace('\n', '\\n')
    fixed_value = fixed_value.replace('\r', '')
    
    print(f"    ✓ 字段 {field_name} 修复完成")
    
    before_fix = match.group(0)
    after_fix = match.group(1) + fixed_value + match.group(3)
    
    return json_string.replace(before_fix, after_fix)


def preprocess_es_data(raw_data):
    """模拟前端新的 preprocessEsData 函数"""
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
    
    return processed


def simulate_browser_scenario():
    """模拟浏览器场景：用户从 curl 复制，粘贴到 textarea"""
    
    # 从文件读取 curl 命令
    with open('test/kafka/kafka生成请求CURL.txt', 'r', encoding='utf-8') as f:
        curl_content = f.read()
    
    # 提取 --data-raw 部分
    match = re.search(r"--data-raw \$'(.+?)'$", curl_content, re.DOTALL)
    if not match:
        print("❌ 无法提取数据")
        return False
    
    raw_escaped = match.group(1)
    print(f"✅ 提取成功，原始长度：{len(raw_escaped)}")
    
    # 使用 bash 解析 $'...' 中的转义
    import subprocess
    cmd = ['bash', '-c', f'echo -n $\'{raw_escaped}\'']
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
        
        # 【关键修复】从 bash 解析出来的 es_source_raw 中，\n 是字面的反斜杠+n
        # 但在原始 curl 中，这些 \n 代表的是真实换行符
        # 所以我们需要先把字面的 \n 转换成真实换行，让 JSON 恢复结构化
        print("\n[重要] 还原字面 \\n 为真实换行符...")
        es_source_restored = es_source_raw.replace('\\n', '\n')
        print(f"还原后长度：{len(es_source_restored)}")
        print(f"前 200 字符：{repr(es_source_restored[:200])}")
        
        # 这就是用户在浏览器 textarea 中看到的内容
        # 注意：经过上面的还原，现在的 \n 已经是真实换行符了
        print(f"\n模拟浏览器中的 es_source_raw 内容 (已还原):")
        
        # 现在模拟前端预处理
        print("\n" + "="*80)
        print("[预处理]")
        print("="*80)
        
        fixed_es_source = preprocess_es_data(es_source_restored)
        
        print(f"\n处理后长度：{len(fixed_es_source)}")
        print(f"前 300 字符预览:")
        print(fixed_es_source[:300])
        print("...\n")
        
        # 尝试验证
        print("[验证]")
        print("-"*80)
        try:
            parsed = json.loads(fixed_es_source)
            print(f"✅ 成功！解析出 {len(parsed.keys())} 个字段")
            
            # 验证关键字段
            print("\n验证关键字段:")
            event_reason = parsed.get('EVENT_REASON', '')
            src_org = parsed.get('SRC_ORG_ALARM_TEXT', '')
            event_effect = parsed.get('EVENT_EFFECT', '')
            
            print(f"  - EVENT_REASON: {len(event_reason)} 字符")
            print(f"  - SRC_ORG_ALARM_TEXT: {len(src_org)} 字符")
            print(f"  - EVENT_EFFECT: {len(event_effect)} 字符")
            
            # 检查换行符是否正确转义
            if '\\n' in event_reason:
                escaped_count = event_reason.count('\\n')
                print(f"\nEVENT_REASON 中包含 {escaped_count} 个 \\n 转义")
            elif '\n' in event_reason:
                actual_newlines = event_reason.count('\n')
                print(f"\nEVENT_REASON 中包含 {actual_newlines} 个实际换行符 (未转义)")
            
            # 打印一个字段示例
            print(f"\nEVENT_REASON 内容示例 (前 100 字符):")
            print(repr(event_reason[:100]))
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ 预处理后仍然失败：{e}")
            
            # 显示错误位置
            error_pos = e.pos
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
    print("测试前端新的预处理逻辑（模拟浏览器实际场景）")
    print("="*80)
    
    success = simulate_browser_scenario()
    
    if success:
        print("\n" + "="*80)
        print("✅ 测试通过！新逻辑可以正确处理")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ 测试失败！需要进一步调试")
        print("="*80)
