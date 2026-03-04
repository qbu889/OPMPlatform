import os
import shutil

# 目标目录
download_dir = '/Users/linziwang/Documents/'

# 分类规则：扩展名对应的文件夹名
file_types = {
    '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
    '文档': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md'],
    '视频': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'],
    '音频': ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
    '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    '代码': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.sh', '.php'],
}

def get_category(filename):
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in file_types.items():
        if ext in extensions:
            return category
    return '其他'  # 未分类文件

def organize_files():
    for item in os.listdir(download_dir):
        item_path = os.path.join(download_dir, item)
        if os.path.isfile(item_path):
            category = get_category(item)
            target_dir = os.path.join(download_dir, category)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            try:
                shutil.move(item_path, target_dir)
                print(f'已移动: {item} -> {category}/')
            except Exception as e:
                print(f'移动失败: {item}，原因: {e}')

if __name__ == '__main__':
    organize_files()
