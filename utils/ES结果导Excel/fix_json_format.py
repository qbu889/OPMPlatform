#!/usr/bin/env python3
"""
预处理器：修复 ES 导出 JSON 文件中的格式问题
- 处理未转义的双引号
- 处理字符串中的真实换行符
- 处理其他控制字符
"""
import re
import sys
from pathlib import Path


def fix_json_file(input_path, output_path=None):
    """修复 JSON 文件格式问题"""
    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_fixed{input_path.suffix}")
    
    print(f"📖 读取文件: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 开始修复...")
    
    # 步骤1: 移除注释行
    lines = content.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith('#!')]
    content = '\n'.join(cleaned_lines)
    
    # 步骤2: 修复多行字符串问题
    # 策略：将 "rows" 数组中的每个元素视为独立单元处理
    fixed_content = _fix_multiline_strings(content)
    
    print(f"💾 保存修复后的文件: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ 修复完成！文件大小: {len(fixed_content)} 字符")
    return output_path


def _fix_multiline_strings(content):
    """修复多行字符串：将字符串内的真实换行符替换为 \\n"""
    
    # 找到 rows 数组的开始位置
    rows_start = content.find('"rows"')
    if rows_start == -1:
        return content
    
    # 找到 rows 数组的起始方括号
    bracket_start = content.find('[', rows_start)
    if bracket_start == -1:
        return content
    
    # 分离头部（columns 部分）和主体（rows 部分）
    header = content[:bracket_start]
    rows_part = content[bracket_start:]
    
    # 策略：直接替换所有三引号为单引号，然后处理换行符
    # 1. 先处理三引号包裹的字符串
    import re
    
    # 匹配 """...""" 模式（可能跨越多行）
    def replace_triple_quotes(match):
        text = match.group(1)
        # 将内部的换行符转义
        text = text.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return f'"{text}"'
    
    # 使用 DOTALL 让 . 匹配换行符
    fixed_rows = re.sub(r'"""(.*?)"""', replace_triple_quotes, rows_part, flags=re.DOTALL)
    
    return header + fixed_rows


def _is_unclosed_string(line):
    """检查行是否有未闭合的字符串"""
    # 简单启发式：计算引号数量（排除转义的）
    quote_count = 0
    i = 0
    while i < len(line):
        if line[i] == '\\' and i + 1 < len(line):
            i += 2  # 跳过转义字符
            continue
        if line[i] == '"':
            quote_count += 1
        i += 1
    
    # 奇数个引号表示未闭合
    return quote_count % 2 != 0


def _is_json_structure(line):
    """检查是否是标准 JSON 结构行"""
    stripped = line.strip()
    return (stripped in ['[', ']', '{', '}', '[', ']', ',', ''] or
            re.match(r'^[\s]*[,{}\[\]:]+[\s]*$', stripped) or
            re.match(r'^\s*\d+\s*,?\s*$', stripped) or  # 纯数字
            re.match(r'^\s*(true|false|null)\s*,?\s*$', stripped))  # 布尔值或null


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fix_json_format.py <输入文件> [输出文件]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    try:
        result = fix_json_file(input_file, output_file)
        print(f"\n✨ 成功！修复后的文件: {result}")
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
