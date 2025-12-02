import atexit
import os
import shutil

from app import app, logger


def cleanup_temp_files():
    """清理临时文件"""
    temp_files = [
        os.path.join(app.config['UPLOAD_FOLDER'], 'source_doc.docx'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'converted_demo.docx'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'temp_demo.docx'),
        os.path.join(app.config['UPLOAD_FOLDER'], 'temp_check.docx')
    ]

    for file_path in temp_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"已清理临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"清理临时文件失败 {file_path}: {str(e)}")


# 在应用关闭时清理临时文件
atexit.register(cleanup_temp_files)
