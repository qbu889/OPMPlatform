#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 状态诊断脚本
"""
import requests
import sys

def check_ollama():
    """检查 Ollama 服务状态"""
    print("=" * 60)
    print("Ollama 状态诊断")
    print("=" * 60)
    
    base_url = "http://localhost:11434"
    
    # 1. 检查服务是否运行
    print("\n1. 检查 Ollama 服务...")
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print("   ✅ Ollama 服务正在运行")
        else:
            print(f"   ❌ Ollama 服务响应异常：{response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Ollama 服务未运行")
        print("   解决方案：执行 'ollama serve'")
        return False
    except Exception as e:
        print(f"   ❌ 连接失败：{e}")
        return False
    
    # 2. 获取可用模型列表
    print("\n2. 检查可用模型...")
    try:
        data = response.json()
        models = data.get('models', [])
        if models:
            print(f"   ✅ 已安装 {len(models)} 个模型:")
            for model in models:
                print(f"      - {model.get('name')}")
        else:
            print("   ⚠️  未安装任何模型")
            print("   解决方案：执行 'ollama pull deepseek-r1:7b'")
    except Exception as e:
        print(f"   ❌ 获取模型列表失败：{e}")
    
    # 3. 检查特定模型
    print("\n3. 检查 deepseek-r1:7b 模型...")
    model_name = "deepseek-r1:7b"
    model_found = any(m.get('name') == model_name for m in models)
    
    if model_found:
        print(f"   ✅ 模型 {model_name} 已安装")
    else:
        print(f"   ❌ 模型 {model_name} 未安装")
        print(f"   解决方案：执行 'ollama pull {model_name}'")
    
    # 4. 测试 generate API
    print("\n4. 测试 /api/generate 端点...")
    try:
        test_payload = {
            "model": model_name if model_found else (models[0].get('name') if models else "llama2"),
            "prompt": "Hello",
            "stream": False
        }
        response = requests.post(f"{base_url}/api/generate", json=test_payload, timeout=10)
        if response.status_code == 200:
            print("   ✅ /api/generate 端点正常")
        else:
            print(f"   ❌ /api/generate 端点异常：{response.status_code}")
    except Exception as e:
        print(f"   ❌ /api/generate 测试失败：{e}")
    
    # 5. 测试 chat API
    print("\n5. 测试 /api/chat 端点...")
    try:
        test_payload = {
            "model": model_name if model_found else (models[0].get('name') if models else "llama2"),
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        }
        response = requests.post(f"{base_url}/api/chat", json=test_payload, timeout=10)
        if response.status_code == 200:
            print("   ✅ /api/chat 端点正常")
        else:
            print(f"   ❌ /api/chat 端点异常：{response.status_code}")
            print(f"   响应内容：{response.text[:200]}")
    except Exception as e:
        print(f"   ❌ /api/chat 测试失败：{e}")
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = check_ollama()
    sys.exit(0 if success else 1)
