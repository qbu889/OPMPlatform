#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能客服系统测试脚本
用于验证各个模块的功能是否正常
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ollama_client():
    """测试 Ollama 客户端"""
    print("\n=== 测试 Ollama 客户端 ===")
    
    try:
        from utils.ollama_client import get_ollama_client
        
        client = get_ollama_client()
        is_available = client.is_available()
        
        if is_available:
            print("✅ Ollama 服务可用")
            
            models = client.list_models()
            print(f"   可用模型：{len(models)} 个")
            for model in models[:5]:
                print(f"   - {model}")
            
            # 测试简单对话
            print("\n   测试对话...")
            response = client.generate("你好，请用一句话介绍你自己")
            print(f"   AI 回复：{response[:100]}...")
            
            return True
        else:
            print("❌ Ollama 服务不可用")
            print("   请确保已安装并启动 Ollama: ollama serve")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def test_document_processor():
    """测试文档处理器"""
    print("\n=== 测试文档处理器 ===")
    
    try:
        from utils.document_processor import DocumentProcessor
        
        processor = DocumentProcessor(upload_folder='test_uploads')
        
        print(f"✅ 文档处理器初始化成功")
        print(f"   支持格式：{processor.get_supported_formats()}")
        
        # 创建测试文件
        test_content = "这是一个测试文档。\n问题：什么是人工智能？\n答案：人工智能是模拟人类智能的技术。"
        test_file = os.path.join(processor.upload_folder, 'test.txt')
        
        os.makedirs(processor.upload_folder, exist_ok=True)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 测试处理文档
        result = processor.process_document(test_file)
        
        if result['success']:
            print(f"✅ 文档处理成功")
            print(f"   文件类型：{result['filetype']}")
            print(f"   内容长度：{len(result['content'])} 字符")
        else:
            print(f"❌ 文档处理失败：{result.get('error')}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return result['success']
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def test_knowledge_base():
    """测试知识库管理器"""
    print("\n=== 测试知识库管理器 ===")
    
    try:
        from models.knowledge_base import knowledge_base_manager
        
        # 测试添加文档
        doc_id = knowledge_base_manager.add_document(
            filename='test_doc.txt',
            original_filename='test.txt',
            file_type='text',
            metadata={'test': True}
        )
        
        if doc_id > 0:
            print(f"✅ 文档记录添加成功 (ID: {doc_id})")
            
            # 测试获取文档
            doc = knowledge_base_manager.get_document(doc_id)
            if doc:
                print(f"   文档名称：{doc['filename']}")
            
            # 测试添加 FAQ
            faq_id = knowledge_base_manager.add_faq(
                question="测试问题",
                answer="测试答案",
                document_id=doc_id,
                category="测试分类",
                tags=["测试", "demo"]
            )
            
            if faq_id > 0:
                print(f"✅ FAQ 添加成功 (ID: {faq_id})")
                
                # 测试搜索 FAQ
                faqs = knowledge_base_manager.search_faqs("测试", limit=5)
                print(f"   搜索结果：{len(faqs)} 条")
                
                # 测试获取所有 FAQ
                all_faqs = knowledge_base_manager.list_all_faqs()
                print(f"   总 FAQ 数：{len(all_faqs)} 条")
            
            # 清理测试数据（软删除）
            knowledge_base_manager.delete_document(doc_id)
            print(f"   ✅ 测试数据已清理")
            
            return True
        else:
            print(f"❌ 文档记录添加失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def test_chatbot_core():
    """测试客服核心处理器"""
    print("\n=== 测试客服核心处理器 ===")
    
    try:
        from utils.chatbot_core import get_chatbot_core
        
        chatbot = get_chatbot_core()
        print(f"✅ 客服核心初始化成功")
        
        # 测试问题解析
        print("\n   测试问题解析...")
        parsed = chatbot._parse_query("如何重置密码？")
        print(f"   解析结果：{parsed}")
        
        # 测试简单查询（不依赖知识库）
        print("\n   测试简单查询...")
        result = chatbot.process_query("你好")
        
        if result['success']:
            print(f"✅ 查询处理成功")
            print(f"   答案来源：{result['source']}")
            print(f"   答案预览：{result['answer'][:50]}...")
            return True
        else:
            print(f"❌ 查询处理失败：{result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def test_routes():
    """测试 Flask 路由"""
    print("\n=== 测试 Flask 路由 ===")
    
    try:
        from app import create_app
        
        app = create_app()
        app.config['TESTING'] = True
        
        with app.test_client() as client:
            # 测试首页
            response = client.get('/chatbot/')
            if response.status_code == 200:
                print(f"✅ 聊天页面访问成功")
            else:
                print(f"❌ 聊天页面访问失败：{response.status_code}")
                return False
            
            # 测试 Ollama 状态接口
            response = client.get('/chatbot/ollama/status')
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✅ Ollama 状态检查成功")
                    print(f"   服务可用：{data.get('available')}")
                else:
                    print(f"⚠️  Ollama 状态检查返回错误")
            else:
                print(f"❌ Ollama 状态接口错误：{response.status_code}")
            
            # 测试 FAQ 列表接口
            response = client.get('/chatbot/faqs')
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✅ FAQ 列表获取成功 ({len(data.get('faqs', []))} 条)")
                else:
                    print(f"⚠️  FAQ 列表获取失败")
            else:
                print(f"❌ FAQ 列表接口错误：{response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("智能客服系统功能测试")
    print("=" * 60)
    
    results = {
        'Ollama 客户端': test_ollama_client(),
        '文档处理器': test_document_processor(),
        '知识库管理器': test_knowledge_base(),
        '客服核心': test_chatbot_core(),
        'Flask 路由': test_routes()
    }
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n总计：{passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常使用。")
        return True
    else:
        print("\n⚠️  部分测试未通过，请检查相关配置。")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
