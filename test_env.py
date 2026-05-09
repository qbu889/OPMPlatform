#!/usr/bin/env python3
import os
from dotenv import load_dotenv

print(f'当前目录: {os.getcwd()}')
print(f'加载前 WEBHOOK_ENCRYPTION_KEY: {os.environ.get("WEBHOOK_ENCRYPTION_KEY", "未设置")}')

# 测试 load_dotenv
result = load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
print(f'load_dotenv() 返回值: {result}')
print(f'加载后 WEBHOOK_ENCRYPTION_KEY: {os.environ.get("WEBHOOK_ENCRYPTION_KEY", "未设置")}')

# 测试解密
if os.environ.get('WEBHOOK_ENCRYPTION_KEY'):
    from cryptography.fernet import Fernet
    fernet = Fernet(os.environ.get('WEBHOOK_ENCRYPTION_KEY').encode())
    encrypted = 'gAAAAABp6XdqtMoDWt0oYKgIncjYYZcmdpjSAX6vf4eZ5i8qFC6kgVVCY3ikfqakrAml_m2HAAhQVknV2u4u_YUMWVpeE1OO9HLDeAntV4-7FDqbUCdK3kI5NeBnL5ZBwPB3GCnFJLqHvRmMS4oWe8zgodGSH3kSZ7eBYlQ_vyNfkv8aEh3tFKh7OKPJq1Xa7kEsQuRE3OM97clRHcvtJlCbUnGN5oYa197b6XB9zWcqmS_8uiI9bco='
    try:
        decrypted = fernet.decrypt(encrypted.encode())
        print(f'解密成功: {decrypted.decode()[:60]}...')
    except Exception as e:
        print(f'解密失败: {e}')
else:
    print('WEBHOOK_ENCRYPTION_KEY 仍然未设置')
