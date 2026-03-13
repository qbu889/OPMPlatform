#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FAQ JSON 解析改进验证脚本
快速验证 5 层解析防护机制的有效性
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.document_processor import parse_json_with_multiple_methods


def test_case(name, response, expected_count):
    """测试单个用例"""
    print(f"\n{'='*60}")
    print(f"测试：{name}")
    print(f"{'='*60}")
    
    faqs = parse_json_with_multiple_methods(response, chunk_index=0)
    
    success = len(faqs) == expected_count
    status = "✅ PASS" if success else f"❌ FAIL (期望{expected_count}条，实际{len(faqs)}条)"
    
    print(f"结果：{status}")
    if faqs:
        for idx, faq in enumerate(faqs, 1):
            q = faq.get('question', 'N/A')[:50]
            print(f"  {idx}. Q: {q}...")
    
    return success


def main():
    print("="*60)
    print("FAQ JSON 解析改进验证报告")
    print("="*60)
    
    tests = [
        # (测试名称，AI 响应内容，期望解析数量)
        (
            "1. 标准 JSON 数组",
            '[{"question": "问题 1", "answer": "答案 1"}]',
            1
        ),
        (
            "2. Markdown 代码块包裹",
            '```json\n[{"question": "问题 2", "answer": "答案 2"}]\n```',
            1
        ),
        (
            "3. 前后都有解释文字",
            '好的，我提取了以下 FAQ：\n\n[{"question": "问题 3", "answer": "答案 3"}]\n\n请查阅。',
            1
        ),
        (
            "4. 多条 FAQ（Markdown 包裹）",
            '''```json
[
    {"question": "问题 A", "answer": "答案 A"},
    {"question": "问题 B", "answer": "答案 B"}
]
```''',
            2
        ),
        (
            "5. 键名缺少引号（格式错误）",
            '[{question: "问题", answer: "答案"}]',
            1  # 方法 4 应该能修复
        ),
        (
            "6. JSON 对象而非数组",
            '{"question": "单个问题", "answer": "单个答案"}',
            1  # 正则能提取到 1 个
        ),
        (
            "7. 空响应",
            '',
            0
        ),
        (
            "8. 包含特殊字符和换行",
            r'''[{"question": "如何处理特殊字符？", "answer": "注意：\n1. 反斜杠 \\\n2. 引号 \""}]''',
            1
        ),
    ]
    
    results = []
    for name, response, expected in tests:
        try:
            result = test_case(name, response, expected)
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试异常：{name}\n错误：{e}")
            results.append((name, False))
    
    # 生成报告
    print("\n" + "="*60)
    print("测试报告汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("🎉 所有测试通过！JSON 解析增强功能运行正常。")
    else:
        print(f"⚠️  有 {total - passed} 个测试未通过，需要进一步优化。")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
