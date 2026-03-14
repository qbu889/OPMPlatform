#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置 Ollama 模型配置（从.env 读取并更新）
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def set_ollama_model(model_name: str):
    """设置 Ollama 模型配置（从.env 读取并更新）"""
    
    # 加载现有的 .env 配置
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv()
        print(f"✅ 检测到现有 .env 文件")
        
        # 读取现有的 OLLAMA_BASE_URL（如果存在）
        existing_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        print(f"   当前 OLLAMA_BASE_URL: {existing_base_url}")
    else:
        existing_base_url = 'http://localhost:11434'
        print(f"⚠️  未找到 .env 文件，将创建新文件")
    
    # 构建新的 .env 内容（保留现有配置，只更新模型）
    env_content = f"""# Ollama 配置
# OLLAMA_BASE_URL={existing_base_url}
OLLAMA_BASE_URL={existing_base_url}
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
