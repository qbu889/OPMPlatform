#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文档处理器是否支持 .py 和 .md 文件
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from utils.document_processor import DocumentProcessor

def test_file_support():
    """测试文件类型支持"""
    print("=" * 60)
    print("测试文档处理器支持的文件类型")
    print("=" * 60)
    
    processor = DocumentProcessor(upload_folder='test_uploads')
    
    # 检查支持的格式
    supported = processor.get_supported_formats()
    print(f"\n✅ 支持的格式 ({len(supported)} 种):")
    for fmt in sorted(supported):
        print(f"   - {fmt}")
    
    # 测试 .md 文件
    print("\n" + "-" * 60)
    print("测试 .md 文件处理...")
    md_test_file = os.path.join(processor.upload_folder, 'test.md')
    
    try:
        with open(md_test_file, 'w', encoding='utf-8') as f:
            f.write("# 测试文档\n\n这是一个 Markdown 测试文件。")
        
        result = processor.process_document(md_test_file)
        if result['success']:
            print(f"✅ .md 文件处理成功")
            print(f"   文件类型：{result['filetype']}")
            print(f"   内容长度：{len(result['content'])} 字符")
        else:
            print(f"❌ .md 文件处理失败：{result.get('error')}")
    except Exception as e:
        print(f"❌ .md 文件测试异常：{e}")
    finally:
        if os.path.exists(md_test_file):
            os.remove(md_test_file)
    
    # 测试 .py 文件
    print("\n" + "-" * 60)
    print("测试 .py 文件处理...")
    py_test_file = os.path.join(processor.upload_folder, 'test.py')
    
    try:
        with open(py_test_file, 'w', encoding='utf-8') as f:
            f.write("#!/usr/bin/env python3\n# 测试 Python 文件\nprint('Hello World')\n")
        
        result = processor.process_document(py_test_file)
        if result['success']:
            print(f"✅ .py 文件处理成功")
            print(f"   文件类型：{result['filetype']}")
            print(f"   内容长度：{len(result['content'])} 字符")
        else:
            print(f"❌ .py 文件处理失败：{result.get('error')}")
    except Exception as e:
        print(f"❌ .py 文件测试异常：{e}")
    finally:
        if os.path.exists(py_test_file):
            os.remove(py_test_file)
    
    # 清理测试目录
    if os.path.exists(processor.upload_folder):
        import shutil
        shutil.rmtree(processor.upload_folder, ignore_errors=True)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_file_support()
