#!/usr/bin/env python3
"""修复Font Awesome CSS文件中的字体路径"""

import re

def fix_fontawesome_paths():
    css_file = '/static/vendor/fontawesome/all.min.css'
    
    # 读取原文件
    with open(css_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义需要替换的路径映射
    replacements = [
        (r'url\(\.\./webfonts/fa-regular-400\.woff2\)', r'url(/static/vendor/webfonts/fa-regular-400.woff2)'),
        (r'url\(\.\./webfonts/fa-regular-400\.ttf\)', r'url(/static/vendor/webfonts/fa-regular-400.ttf)'),
        (r'url\(\.\./webfonts/fa-v4compatibility\.woff2\)', r'url(/static/vendor/webfonts/fa-v4compatibility.woff2)'),
        (r'url\(\.\./webfonts/fa-v4compatibility\.ttf\)', r'url(/static/vendor/webfonts/fa-v4compatibility.ttf)')
    ]
    
    # 执行替换
    modified_content = content
    for pattern, replacement in replacements:
        modified_content = re.sub(pattern, replacement, modified_content)
    
    # 写回文件
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print("Font Awesome CSS路径修复完成！")

if __name__ == '__main__':
    fix_fontawesome_paths()