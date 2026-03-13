#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAQ 提取 JSON 解析测试用例
用于测试和改进 JSON 解析成功率
"""
import json
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.ollama_client import OllamaClient


def test_json_parse_issue_1():
    """测试用例 1：AI 返回了 Markdown 格式包裹的 JSON"""
    print("\n=== 测试用例 1：Markdown 包裹的 JSON ===")
    
    # 模拟 AI 返回的内容（包含 Markdown 代码块）
    ai_response = """```json
[
    {
        "question": "什么是事件工单？",
        "answer": "事件工单是集中故障管理系统中用于记录和处理故障事件的工单。"
    },
    {
        "question": "如何创建事件工单？",
        "answer": "可以通过以下步骤创建事件工单：\\n1. 登录系统\\n2. 点击创建工单\\n3. 填写信息"
    }
]
```"""
    
    print(f"AI 返回内容：\n{ai_response}\n")
    
    # 测试各种解析方法
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=1)
    print(f"解析结果：{len(faqs)} 条 FAQ")
    for faq in faqs:
        print(f"  - Q: {faq['question']}")
    
    return len(faqs) > 0


def test_json_parse_issue_2():
    """测试用例 2：AI 返回了包含解释文字的 JSON"""
    print("\n=== 测试用例 2：包含解释文字的 JSON ===")
    
    ai_response = """好的，我已经从文档中提取了以下 FAQ：

[
    {
        "question": "工单处理流程是什么？",
        "answer": "工单处理流程包括：受理、处理、回复、归档"
    },
    {
        "question": "工单超时如何处理？",
        "answer": "工单超时需要进行升级处理，并通知相关负责人"
    }
]

以上是提取的所有 FAQ，请查阅。"""
    
    print(f"AI 返回内容：\n{ai_response}\n")
    
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=2)
    print(f"解析结果：{len(faqs)} 条 FAQ")
    
    return len(faqs) > 0


def test_json_parse_issue_3():
    """测试用例 3：AI 返回了格式错误的 JSON（缺少引号等）"""
    print("\n=== 测试用例 3：格式不规范的 JSON ===")
    
    ai_response = """[
    {
        question: "工单优先级如何划分？",  // 键名缺少引号
        answer: "工单优先级分为：紧急、高、中、低"  // 注释
    },
    {
        "question": "如何处理紧急工单？",
        "answer": "紧急工单需要立即响应，并在 2 小时内处理完毕"
    }
]"""
    
    print(f"AI 返回内容：\n{ai_response}\n")
    
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=3)
    print(f"解析结果：{len(faqs)} 条 FAQ")
    
    return len(faqs) > 0


def test_json_parse_issue_4():
    """测试用例 4：空响应或无效响应"""
    print("\n=== 测试用例 4：空响应或无效响应 ===")
    
    test_cases = [
        ("空字符串", ""),
        ("只有空格", "   "),
        ("无法解析的内容", "这是一个普通的文本段落，没有任何 JSON 格式"),
        ("只有方括号", "[]"),
        ("JSON 对象而非数组", '{"question": "测试", "answer": "答案"}'),
    ]
    
    for name, response in test_cases:
        print(f"\n  测试：{name}")
        faqs = parse_json_with_multiple_methods(response, chunk_index=4)
        print(f"  结果：{len(faqs)} 条 FAQ")


def test_json_parse_issue_5():
    """测试用例 5：包含特殊字符的 JSON"""
    print("\n=== 测试用例 5：包含特殊字符的 JSON ===")
    
    ai_response = r"""[
    {
        "question": "如何处理包含特殊字符的工单？",
        "answer": "需要注意以下特殊字符：\n1. 反斜杠 \\ \n2. 双引号 \"\n3. 换行符 \n\nSQL 示例：SELECT * FROM table WHERE id = 1"
    },
    {
        "question": "图片如何显示？",
        "answer": "![流程图](http://example.com/flow.png)\n\n步骤说明..."
    }
]"""
    
    print(f"AI 返回内容：\n{ai_response}\n")
    
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=5)
    print(f"解析结果：{len(faqs)} 条 FAQ")
    for faq in faqs:
        print(f"  - Q: {faq['question']}")
        print(f"    A: {faq['answer'][:50]}...")
    
    return len(faqs) > 0


def parse_json_with_multiple_methods(response: str, chunk_index: int = 0):
    """
    使用多种方法尝试解析 JSON（增强版）
    
    Args:
        response: AI 返回的响应文本
        chunk_index: 文本段索引（用于日志）
        
    Returns:
        解析后的 FAQ 列表
    """
    import re
    
    if not response or not response.strip():
        print(f"[Chunk {chunk_index}] 空响应")
        return []
    
    response = response.strip()
    
    # 方法 1：直接解析（最优情况）
    try:
        faqs = json.loads(response)
        if isinstance(faqs, list):
            print(f"[Chunk {chunk_index}] 方法 1：直接解析成功")
            return faqs
    except json.JSONDecodeError as e:
        print(f"[Chunk {chunk_index}] 方法 1 失败：{e}")
    
    # 方法 2：移除 Markdown 代码块标记
    try:
        cleaned = response
        # 移除 ```json 或 ``` 开头和结尾
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        faqs = json.loads(cleaned)
        if isinstance(faqs, list):
            print(f"[Chunk {chunk_index}] 方法 2：移除 Markdown 标记成功")
            return faqs
    except Exception as e:
        print(f"[Chunk {chunk_index}] 方法 2 失败：{e}")
    
    # 方法 3：提取第一个 [ 到最后一个 ]
    try:
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            print(f"[Chunk {chunk_index}] 方法 3：提取 JSON 部分 [{start_idx}:{end_idx}]")
            
            # 清理特殊字符
            json_str = json_str.replace('\n', '\\n').replace('\r', '\\r')
            faqs = json.loads(json_str)
            if isinstance(faqs, list):
                print(f"[Chunk {chunk_index}] 方法 3 成功")
                return faqs
    except Exception as e:
        print(f"[Chunk {chunk_index}] 方法 3 失败：{e}")
    
    # 方法 4：尝试修复常见 JSON 错误
    try:
        fixed_json = fix_common_json_errors(response)
        if fixed_json:
            faqs = json.loads(fixed_json)
            if isinstance(faqs, list):
                print(f"[Chunk {chunk_index}] 方法 4：修复 JSON 错误成功")
                return faqs
    except Exception as e:
        print(f"[Chunk {chunk_index}] 方法 4 失败：{e}")
    
    # 方法 5：使用正则表达式提取 JSON 对象
    try:
        # 尝试匹配多个 JSON 对象
        pattern = r'\{\s*"question"\s*:\s*"[^"]+"\s*,\s*"answer"\s*:\s*"[^"]+"\s*\}'
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            print(f"[Chunk {chunk_index}] 方法 5：正则表达式匹配到 {len(matches)} 个对象")
            faqs = []
            for match in matches:
                try:
                    faq = json.loads(match)
                    faqs.append(faq)
                except:
                    pass
            return faqs
    except Exception as e:
        print(f"[Chunk {chunk_index}] 方法 5 失败：{e}")
    
    # 所有方法都失败
    print(f"[Chunk {chunk_index}] 所有方法都失败")
    return []


def fix_common_json_errors(text: str) -> str:
    """
    修复常见的 JSON 格式错误
    
    Args:
        text: 可能包含 JSON 的文本
        
    Returns:
        修复后的 JSON 字符串，如果无法修复则返回 None
    """
    import re
    
    # 提取 JSON 部分
    start_idx = text.find('[')
    end_idx = text.rfind(']') + 1
    if start_idx < 0 or end_idx <= start_idx:
        return None
    
    json_str = text[start_idx:end_idx]
    
    # 1. 移除行内注释（// 开头的）
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    
    # 2. 移除多行注释（/* */）
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # 3. 修复键名缺少引号的情况
    # 将 { key: "value" } 改为 { "key": "value" }
    json_str = re.sub(r'(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1 "\2":', json_str)
    
    # 4. 修复字符串中未转义的双引号（简单版本）
    # 注意：这个修复可能不完美，但对于简单情况有效
    
    # 5. 清理控制字符
    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    
    # 6. 移除末尾多余的逗号
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    return json_str


def test_real_ai_response():
    """测试用例 6：使用真实的 AI 响应测试"""
    print("\n=== 测试用例 6：真实 AI 响应测试 ===")
    
    # 创建一个简单的测试文档
    test_content = """
# 事件工单运维手册

## 1. 什么是事件工单？

事件工单是集中故障管理系统中用于记录和处理故障事件的工单。事件工单帮助运维团队跟踪和管理故障处理过程。

## 2. 如何创建事件工单？

创建事件工单的步骤如下：

1. 登录集中故障管理系统
2. 点击导航栏的"工单管理"
3. 点击"创建工单"按钮
4. 填写工单信息：
   - 工单标题
   - 工单描述
   - 优先级
   - 负责人
5. 点击"提交"按钮

## 3. 工单优先级如何划分？

工单优先级分为四个级别：

- **紧急**：系统完全不可用，需要立即响应
- **高**：系统功能严重受影响，需要 2 小时内响应
- **中**：系统功能部分受影响，需要 4 小时内响应
- **低**：轻微问题，需要 24 小时内响应
"""
    
    print(f"测试文档内容长度：{len(test_content)} 字符")
    
    # 使用增强的解析函数测试（不需要实际调用 AI）
    from utils.document_processor import parse_json_with_multiple_methods
    
    # 模拟几种 AI 可能返回的内容
    test_responses = [
        # 正常 JSON
        '[{"question": "什么是事件工单？", "answer": "事件工单是..."}]',
        
        # Markdown 包裹
        '```json\n[{"question": "如何创建工单？", "answer": "步骤如下..."}]\n```',
        
        # 包含解释
        '根据文档，我提取了以下 FAQ：\n\n[{"question": "工单优先级？", "answer": "分为四个级别..."}]\n\n请查阅。',
    ]
    
    total_extracted = 0
    for idx, response in enumerate(test_responses, 1):
        print(f"\n  测试响应 {idx}:")
        faqs = parse_json_with_multiple_methods(response, chunk_index=idx)
        print(f"  解析结果：{len(faqs)} 条")
        total_extracted += len(faqs)
    
    print(f"\n总计解析：{total_extracted} 条 FAQ")
    return total_extracted > 0


def run_all_tests():
    """运行所有测试用例"""
    print("=" * 60)
    print("FAQ JSON 解析测试套件")
    print("=" * 60)
    
    results = []
    
    # 运行各个测试用例
    results.append(("测试 1：Markdown 包裹", test_json_parse_issue_1()))
    results.append(("测试 2：包含解释文字", test_json_parse_issue_2()))
    results.append(("测试 3：格式不规范", test_json_parse_issue_3()))
    results.append(("测试 4：空响应", test_json_parse_issue_4()))
    results.append(("测试 5：特殊字符", test_json_parse_issue_5()))
    results.append(("测试 6：真实 AI 响应", test_real_ai_response()))
    
    # 输出测试报告
    print("\n" + "=" * 60)
    print("测试报告")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
