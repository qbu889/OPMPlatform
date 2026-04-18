"""
图片水印清除功能测试脚本
用于验证后端API是否正常工作
"""
import os
import sys
import requests
from PIL import Image
import io

# 配置
BASE_URL = 'http://127.0.0.1:5001/api/watermark'
TEST_IMAGE_PATH = 'test_uploads/test_watermark.jpg'


def create_test_image():
    """创建测试图片"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (800, 600), color='white')
    
    # 添加一些内容
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # 绘制文字（模拟水印）
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()
    
    # 在右下角添加水印文字
    draw.text((600, 550), "WATERMARK", fill=(200, 200, 200), font=font)
    
    # 保存图片
    os.makedirs(os.path.dirname(TEST_IMAGE_PATH), exist_ok=True)
    img.save(TEST_IMAGE_PATH)
    print(f"✓ 测试图片已创建: {TEST_IMAGE_PATH}")
    
    return TEST_IMAGE_PATH


def test_upload(image_path):
    """测试上传接口"""
    print("\n=== 测试图片上传 ===")
    
    with open(image_path, 'rb') as f:
        files = {'image': ('test.jpg', f, 'image/jpeg')}
        response = requests.post(f'{BASE_URL}/upload', files=files)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200 and response.json()['success']:
        filename = response.json()['filename']
        print(f"✓ 上传成功，文件名: {filename}")
        return filename
    else:
        print("✗ 上传失败")
        return None


def test_remove_watermark(filename):
    """测试手动去除水印"""
    print("\n=== 测试手动去除水印 ===")
    
    # 定义一个测试区域（右下角）
    data = {
        'filename': filename,
        'bboxes': [[600, 540, 180, 50]],  # x, y, w, h
        'algorithm': 'telea',
        'radius': 3
    }
    
    response = requests.post(f'{BASE_URL}/remove', json=data)
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"处理耗时: {result.get('processing_time', 'N/A')}秒")
    
    if response.status_code == 200 and result['success']:
        output_filename = result['output_filename']
        print(f"✓ 水印去除成功，输出文件: {output_filename}")
        return output_filename
    else:
        print(f"✗ 水印去除失败: {result.get('error', '未知错误')}")
        return None


def test_auto_remove(filename):
    """测试自动去除水印"""
    print("\n=== 测试自动去除水印 ===")
    
    data = {
        'filename': filename,
        'algorithm': 'telea',
        'radius': 3
    }
    
    response = requests.post(f'{BASE_URL}/auto-remove', json=data)
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200 and result['success']:
        print(f"✓ 自动去除成功")
        print(f"消息: {result.get('message', '')}")
        return True
    else:
        print(f"✗ 自动去除失败: {result.get('error', '未知错误')}")
        return False


def test_download(filename):
    """测试下载接口"""
    print("\n=== 测试图片下载 ===")
    
    response = requests.get(f'{BASE_URL}/download/{filename}')
    
    if response.status_code == 200:
        download_path = f'test_uploads/downloaded_{filename}'
        with open(download_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ 下载成功，保存到: {download_path}")
        return True
    else:
        print(f"✗ 下载失败，状态码: {response.status_code}")
        return False


def test_cleanup(filename):
    """测试清理接口"""
    print("\n=== 测试临时文件清理 ===")
    
    response = requests.post(f'{BASE_URL}/cleanup', json={'filename': filename})
    
    if response.status_code == 200 and response.json()['success']:
        cleaned_count = response.json()['cleaned_count']
        print(f"✓ 清理成功，删除了 {cleaned_count} 个文件")
        return True
    else:
        print(f"✗ 清理失败")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("图片水印清除功能测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get('http://127.0.0.1:5001/')
        print("✓ 服务器正在运行")
    except:
        print("✗ 服务器未运行，请先启动 Flask 应用")
        print("  运行命令: python app.py")
        sys.exit(1)
    
    # 创建测试图片
    image_path = create_test_image()
    
    # 测试上传
    filename = test_upload(image_path)
    if not filename:
        print("\n✗ 测试中止：上传失败")
        return
    
    # 测试手动去除
    output_filename = test_remove_watermark(filename)
    
    # 测试自动去除
    test_auto_remove(filename)
    
    # 测试下载
    if output_filename:
        test_download(output_filename)
    
    # 测试清理
    test_cleanup(filename)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
