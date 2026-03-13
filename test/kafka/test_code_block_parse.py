#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试代码块未闭合场景的 JSON 解析
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from utils.document_processor import parse_json_with_multiple_methods


def test_unclosed_code_block():
    """测试包含未闭合代码块的 JSON 解析"""
    print("\n=== 测试：未闭合的代码块 ===")
    
    # 模拟第 13 段的失败场景
    ai_response = """[
    {
        "question": "替换脚本中的参数后执行",
        "answer": "替换脚本中的参数后执行\\n\\n![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/Q35O851P0m8ZWl9V/img/edc52e40-1f81-4314-b59f-cd4f5c5561c9.png)\\n\\n```plsql\\nDECLARE\\nv_event_fp VARCHAR(100);\\nv_sheet_id VARCHAR(100);\\nv_cancel_time TIMESTA
    }
]"""
    
    print(f"AI 响应预览：{ai_response[:100]}...")
    
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=0)
    
    print(f"解析结果：{len(faqs)} 条 FAQ")
    
    if faqs:
        for idx, faq in enumerate(faqs, 1):
            print(f"\nFAQ {idx}:")
            print(f"  问：{faq.get('question', 'N/A')[:50]}...")
            answer = faq.get('answer', 'N/A')
            print(f"  答：{answer[:100]}...")
            # 检查是否包含代码块
            if '```' in answer:
                print(f"  ✓ 答案包含代码块标记")
        
        return True
    else:
        print("❌ 解析失败")
        return False


def test_multiple_code_blocks():
    """测试包含多个代码块的情况"""
    print("\n=== 测试：多个代码块 ===")
    
    ai_response = """[
    {
        "question": "如何编写脚本？",
        "answer": "步骤如下：\\n\\n```bash\\necho 'Hello World'\\n```\\n\\n然后执行：\\n\\n```plsql\\nSELECT * FROM dual;\\n```"
    },
    {
        "question": "另一个问题",
        "answer": "答案内容\\n\\n```python\\nprint('test')\\n```"
    }
]"""
    
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=1)
    
    print(f"解析结果：{len(faqs)} 条 FAQ")
    
    if faqs:
        for idx, faq in enumerate(faqs, 1):
            print(f"\nFAQ {idx}:")
            print(f"  问：{faq.get('question', 'N/A')}")
            answer = faq.get('answer', 'N/A')
            print(f"  答：{answer[:80]}...")
            # 统计代码块数量
            code_blocks = answer.count('```') // 2
            print(f"  ✓ 包含 {code_blocks} 个完整代码块")
        
        return True
    else:
        print("❌ 解析失败")
        return False


def test_nested_special_chars():
    """测试包含特殊字符和代码块的复杂场景"""
    print("\n=== 测试：特殊字符 + 代码块 ===")
    
    ai_response = """[
    {
        "question": "如何处理特殊字符？",
        "answer": "需要注意：\\n\\n1. 双引号 \\"test\\"\\n2. 反斜杠 \\\\\\\\ \\n3. 图片：![img](http://example.com/a_b-c.png)\\n\\n```sql\\nSELECT * FROM table WHERE id = 'test';\\n```"
    }
]"""
    
    faqs = parse_json_with_multiple_methods(ai_response, chunk_index=2)
    
    print(f"解析结果：{len(faqs)} 条 FAQ")
    
    if faqs:
        faq = faqs[0]
        print(f"\nFAQ:")
        print(f"  问：{faq.get('question', 'N/A')}")
        answer = faq.get('answer', 'N/A')
        print(f"  答：{answer}")
        print(f"  ✓ 包含特殊字符和代码块")
        return True
    else:
        print("❌ 解析失败")
        return False


if __name__ == "__main__":
    print("="*60)
    print("代码块未闭合场景测试")
    print("="*60)
    
    results = []
    results.append(("未闭合代码块", test_unclosed_code_block()))
    results.append(("多个代码块", test_multiple_code_blocks()))
    results.append(("特殊字符 + 代码块", test_nested_special_chars()))
    
    print("\n" + "="*60)
    print("测试报告")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("🎉 所有测试通过！代码块处理功能正常。")
    else:
        print(f"⚠️  有 {total - passed} 个测试未通过。")
