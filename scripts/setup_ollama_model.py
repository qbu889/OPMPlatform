#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置 Ollama 模型配置
"""
import os

def set_ollama_model(model_name: str):
    """设置 Ollama 模型配置"""
    
    # 方法 1: 创建 .env 文件
    env_content = f"""# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL={model_name}

# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ 已创建 .env 文件，配置模型为：{model_name}")
    print(f"\n使用方法:")
    print(f"1. 重启应用：python app.py")
    print(f"2. 或在代码中导入：from dotenv import load_dotenv; load_dotenv()")
    
    # 方法 2: 直接修改 ollama_client.py 的默认值
    print(f"\n或者，你可以直接设置环境变量:")
    print(f"   export OLLAMA_MODEL={model_name}")
    print(f"   python app.py")

if __name__ == '__main__':
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "deepseek-r1:7b"
    set_ollama_model(model)
