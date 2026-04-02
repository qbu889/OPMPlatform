#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试 POST /kafka-generator/generate 接口
使用 requests 库模拟真实的 HTTP 请求
"""

import requests
import json
import sys

def test_es_data_api():
    """测试 ES 数据转 Kafka 的 API"""
    
    # API 地址（根据实际情况修改）
    url = "http://127.0.0.1:5001/kafka-generator/generate"
    
    # 从文件读取 curl 命令
    with open('test/kafka/前端展示Kafka 消息.txt', 'r', encoding='utf-8') as f:
        curl_content = f.read()
    
    print("="*80)
    print("测试写入 ES 数据的 JSON 格式验证")
    print("="*80)
    print(f"\n目标 URL: {url}")
    print(f"数据来源：test/kafka/前端展示Kafka 消息.txt")
    
    # 提取 curl 命令中的 --data-raw 部分
    import re
    match = re.search(r"--data-raw \$'(.+?)'$", curl_content, re.DOTALL)
    
    if not match:
        print("\n❌ 无法从 curl 命令中提取数据")
        return False
    
    raw_data = match.group(1)
    print(f"✅ 提取成功，原始数据长度：{len(raw_data)}")
    
    # 使用 bash 解析 $'...' 格式的转义字符
    import subprocess
    cmd = ['bash', '-c', f'echo -n $\'{raw_data}\'']
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode != 0:
        print(f"❌ Bash 解析失败：{result.stderr}")
        return False
    
    # 获取解析后的字节数据
    post_data_bytes = result.stdout
    
    print(f"✅ Bash 解析成功，字节长度：{len(post_data_bytes)}")
    
    # 尝试解码为字符串
    try:
        post_data_str = post_data_bytes.decode('utf-8')
        print(f"✅ UTF-8 解码成功，字符长度：{len(post_data_str)}")
        
        # 保存到临时文件用于调试
        with open('/tmp/test_post_data.json', 'wb') as f:
            f.write(post_data_bytes)
        print("✅ 已保存到 /tmp/test_post_data.json 用于调试")
        
    except UnicodeDecodeError as e:
        print(f"⚠️ UTF-8 解码失败，尝试 GBK: {e}")
        try:
            post_data_str = post_data_bytes.decode('gbk')
            print(f"✅ GBK 解码成功")
        except:
            print("❌ 无法解码为文本")
            return False
    
    # 显示前 500 个字符看看
    print(f"\n📋 请求数据预览 (前 500 字符):")
    print("-"*80)
    print(post_data_str[:500])
    print("-"*80)
    
    # 发送 POST 请求
    print(f"\n🚀 开始发送 POST 请求...")
    print(f"   Content-Length: {len(post_data_bytes)} bytes")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (compatible; Test Client)'
        }
        
        response = requests.post(url, data=post_data_bytes, headers=headers, timeout=30)
        
        print(f"\n📊 响应状态码：{response.status_code}")
        print(f"📊 响应头:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        # 尝试解析响应 JSON
        try:
            response_json = response.json()
            print(f"\n✅ 响应 JSON 解析成功！")
            
            # 美化输出
            print(f"\n📋 响应内容:")
            print(json.dumps(response_json, indent=2, ensure_ascii=False)[:2000])
            
            # 检查是否成功
            if response.status_code == 200:
                if response_json.get('success'):
                    print("\n✅ 测试通过！API 调用成功")
                    return True
                else:
                    print(f"\n❌ 测试失败：{response_json.get('message', '未知错误')}")
                    return False
            else:
                print(f"\n❌ HTTP 错误：{response.status_code}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"\n❌ 响应不是有效的 JSON: {e}")
            print(f"\n📋 原始响应 (前 1000 字符):")
            print(response.text[:1000])
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ 连接错误：无法连接到 {url}")
        print(f"   请确保 Flask 应用正在运行")
        print(f"   错误详情：{e}")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ 请求超时（>30 秒）")
        return False
    except Exception as e:
        print(f"\n❌ 请求失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("POST /kafka-generator/generate 接口测试")
    print("="*80)
    
    success = test_es_data_api()
    
    if success:
        print("\n" + "="*80)
        print("✅ 测试完成：SUCCESS")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ 测试完成：FAILED")
        print("="*80)
        sys.exit(1)
