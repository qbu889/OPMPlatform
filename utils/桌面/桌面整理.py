import os
import shutil
from datetime import datetime

# 目标目录
# download_dir = '/Users/linziwang/Downloads/'
download_dir = '/Users/linziwang/Documents/'

# 分类规则：扩展名对应的文件夹名
file_types = {
    '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
    '文档': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.csv'],
    '视频': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
    '音频': ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
    '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    '代码': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.sh', '.php'],
    '安装包': ['.exe', '.msi', '.dmg', '.iso'],
}

# 需要跳过的系统文件
skip_files = ['.DS_Store', '.Spotlight-V100', '.Trashes', '._.DS_Store']

def get_category(filename):
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in file_types.items():
        if ext in extensions:
            return category
    return '其他'  # 未分类文件

def get_unique_path(target_path):
    """如果目标路径已存在，生成带时间戳的唯一文件名"""
    if not os.path.exists(target_path):
        return target_path
    
    directory = os.path.dirname(target_path)
    filename = os.path.basename(target_path)
    name, ext = os.path.splitext(filename)
    
    # 添加时间戳避免重名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{name}_{timestamp}{ext}"
    return os.path.join(directory, new_filename)

def organize_files():
    moved_count = 0
    skipped_count = 0
    failed_count = 0
    
    for item in os.listdir(download_dir):
        item_path = os.path.join(download_dir, item)
        
        # 跳过目录
        if os.path.isdir(item_path):
            continue
            
        # 跳过系统文件
        if item in skip_files or item.startswith('._'):
            print(f'跳过系统文件：{item}')
            skipped_count += 1
            continue
        
        category = get_category(item)
        target_dir = os.path.join(download_dir, category)
        
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        target_path = get_unique_path(os.path.join(target_dir, item))
        
        try:
            shutil.move(item_path, target_path)
            if target_path != os.path.join(target_dir, item):
                print(f'已移动 (重命名): {item} -> {category}/{os.path.basename(target_path)}')
            else:
                print(f'已移动：{item} -> {category}/')
            moved_count += 1
        except Exception as e:
            print(f'移动失败：{item}，原因：{e}')
            failed_count += 1
    
    print(f'\n整理完成！')
    print(f'成功移动：{moved_count} 个文件')
    print(f'跳过：{skipped_count} 个文件')
    print(f'失败：{failed_count} 个文件')

if __name__ == '__main__':
    organize_files()
