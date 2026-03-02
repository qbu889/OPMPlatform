#!/usr/bin/env python3
"""
批量替换模板文件中的 CDN 链接为本地资源链接
"""

import os
import re

# 定义要替换的 CDN 链接映射
cdn_replacements = {
    # Bootstrap CSS
    r'https://cdn\.jsdelivr\.net/npm/bootstrap@5\.1\.3/dist/css/bootstrap\.min\.css': '/static/vendor/bootstrap/bootstrap.min.css',
    r'https://cdn\.jsdelivr\.net/npm/bootstrap@5\.3\.0/dist/css/bootstrap\.min\.css': '/static/vendor/bootstrap/bootstrap.min.css',
    
    # Bootstrap JS
    r'https://cdn\.jsdelivr\.net/npm/bootstrap@5\.1\.3/dist/js/bootstrap\.bundle\.min\.js': '/static/vendor/bootstrap/bootstrap.bundle.min.js',
    r'https://cdn\.jsdelivr\.net/npm/bootstrap@5\.3\.0/dist/js/bootstrap\.bundle\.min\.js': '/static/vendor/bootstrap/bootstrap.bundle.min.js',
    
    # Font Awesome
    r'https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.0\.0/css/all\.min\.css': '/static/vendor/fontawesome/all.min.css',
    r'https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/6\.4\.0/css/all\.min\.css': '/static/vendor/fontawesome/all.min.css',
    r'https://cdn\.bootcdn\.net/ajax/libs/font-awesome/6\.4\.0/css/all\.min\.css': '/static/vendor/fontawesome/all.min.css',
}

def replace_cdn_links_in_file(file_path):
    """替换单个文件中的 CDN 链接"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 执行替换
        for cdn_pattern, local_path in cdn_replacements.items():
            content = re.sub(cdn_pattern, local_path, content)
        
        # 如果内容有变化，则写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已更新: {file_path}")
            return True
        else:
            print(f"- 无需更改: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ 错误处理文件 {file_path}: {e}")
        return False

def main():
    """主函数"""
    template_dir = '../../templates'
    updated_count = 0
    error_count = 0
    
    print("开始批量替换 CDN 链接...")
    print("=" * 50)
    
    # 遍历所有 HTML 模板文件
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if replace_cdn_links_in_file(file_path):
                    updated_count += 1
    
    print("=" * 50)
    print(f"完成! 成功更新 {updated_count} 个文件")
    
    # 验证关键文件
    key_files = [
        'templates/base.html',
        'templates/chat.html', 
        'templates/es_to_kafka.html',
        'templates/json_fixer.html'
    ]
    
    print("\n验证关键文件:")
    for file_path in key_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    has_cdn = any(re.search(pattern, content) for pattern in cdn_replacements.keys())
                    status = "✗ 仍有CDN链接" if has_cdn else "✓ 已替换为本地链接"
                    print(f"{status}: {file_path}")
            except Exception as e:
                print(f"✗ 无法读取 {file_path}: {e}")

if __name__ == '__main__':
    main()