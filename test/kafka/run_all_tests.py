#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量运行 Kafka 相关测试
"""

import subprocess
import sys
import os

# 测试文件列表
test_files = [
    'test/kafka/test_simple_fix.py',
    'test/kafka/test_preprocessing.py',
    'test/kafka/test_kafka_generator.py',
    'test/kafka/test_json_parse_improved.py',
    'test/kafka/test_full_es_data.py',
    'test/kafka/TestKafkaRoutes.py',
    'test/kafka/test_json_fix.py',
    'test/kafka/test_escape_fix.py',
    'test/kafka/test_faq_json_parse.py',
    'test/kafka/test_es_format.py',
    'test/kafka/test_code_block_parse.py',
    'test/kafka/test_es_to_kafka_conversion.py',
    'test/kafka/fix_json_keys.py',
    'test/kafka/final_validation.py',
    'test/kafka/key_name_debug.py',
    # 'test/kafka/deepseekapp.py',  # 注释掉，这是被注释的代码
    'test/kafka/debug_simple.py',
    'test/kafka/debug_json_issue.py',
]

def run_test(file_path):
    """运行单个测试文件"""
    print(f"\n{'='*80}")
    print(f"运行测试：{file_path}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=60  # 60 秒超时
        )
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"❌ 测试超时（>60 秒）")
        return False
    except Exception as e:
        print(f"❌ 运行失败：{e}")
        return False

def main():
    print("="*80)
    print("开始批量运行 Kafka 测试用例")
    print("="*80)
    
    results = []
    
    for test_file in test_files:
        success = run_test(test_file)
        results.append((test_file, success))
    
    # 汇总报告
    print("\n" + "="*80)
    print("测试报告汇总")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_file, success in results:
        status = "✅ 通过" if success else "❌ 失败/异常"
        print(f"{status} - {os.path.basename(test_file)}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print("="*80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
