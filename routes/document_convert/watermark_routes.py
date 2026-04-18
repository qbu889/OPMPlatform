"""
图片水印清除系统 - 后端路由模块
=========================================
提供图片上传、水印清除、结果下载等功能
"""
import os
import uuid
import time
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

# 创建蓝图
watermark_bp = Blueprint('watermark', __name__, url_prefix='/api/watermark')

# 配置
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'watermark')
RESULT_FOLDER = os.path.join(UPLOAD_FOLDER, 'results')

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename):
    """生成唯一的文件名"""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    unique_id = str(uuid.uuid4())
    return f"{unique_id}.{ext}"


@watermark_bp.route('/upload', methods=['POST'])
def upload_image():
    """
    上传图片
    
    Returns:
        JSON响应，包含上传后的文件名和信息
    """
    try:
        # 检查是否有文件
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传文件'
            }), 400
        
        file = request.files['image']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '文件名为空'
            }), 400
        
        # 验证文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式，仅支持: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 读取文件内容并检查大小
        file_content = file.read()
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'文件大小超过限制（最大{MAX_FILE_SIZE // (1024*1024)}MB）'
            }), 400
        
        # 生成唯一文件名
        original_filename = secure_filename(file.filename)
        unique_filename = generate_unique_filename(original_filename)
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # 保存文件
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"图片上传成功: {unique_filename}")
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_name': original_filename,
            'size': len(file_content),
            'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'message': '上传成功'
        }), 200
        
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'上传失败: {str(e)}'
        }), 500


@watermark_bp.route('/remove', methods=['POST'])
def remove_watermark():
    """
    手动框选去除水印
    
    Request Body:
        {
            "filename": "unique_id.jpg",
            "bbox": [x, y, width, height],  // 可选，单个区域
            "bboxes": [[x1, y1, w1, h1], ...],  // 可选，多个区域
            "algorithm": "telea|ns",  // 修复算法
            "radius": 3  // 修复半径
        }
    
    Returns:
        JSON响应，包含处理结果
    """
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: filename'
            }), 400
        
        filename = data['filename']
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 获取边界框（支持单个或多个）
        bboxes = []
        if 'bboxes' in data:
            bboxes = data['bboxes']
        elif 'bbox' in data:
            bboxes = [data['bbox']]
        
        if not bboxes:
            return jsonify({
                'success': False,
                'error': '请提供水印区域的边界框'
            }), 400
        
        # 获取算法参数
        algorithm = data.get('algorithm', 'telea')
        radius = int(data.get('radius', 3))
        
        # 开始处理
        start_time = time.time()
        
        # 读取图片
        img = cv2.imread(filepath)
        if img is None:
            return jsonify({
                'success': False,
                'error': '无法读取图片'
            }), 400
        
        logger.info(f"图片原始尺寸: {img.shape[1]}x{img.shape[0]}")
        
        # 创建掩码
        mask = np.zeros(img.shape[:2], np.uint8)
        
        # 在掩码上标记水印区域（前端已按原始尺寸换算坐标）
        for bbox in bboxes:
            x, y, w, h = [int(val) for val in bbox]
            # 确保坐标在有效范围内
            x = max(0, min(x, img.shape[1] - 1))
            y = max(0, min(y, img.shape[0] - 1))
            w = max(1, min(w, img.shape[1] - x))
            h = max(1, min(h, img.shape[0] - y))
            mask[y:y+h, x:x+w] = 255
            logger.info(f"标记水印区域: x={x}, y={y}, w={w}, h={h}")
        
        # 选择修复算法
        if algorithm == 'ns':
            # Navier-Stokes 方法
            result = cv2.inpaint(img, mask, radius, cv2.INPAINT_NS)
        else:
            # Telea 方法（默认）
            result = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
        
        # 生成输出文件名
        output_filename = f"result_{filename}"
        output_path = os.path.join(RESULT_FOLDER, output_filename)
        
        # 保存结果
        cv2.imwrite(output_path, result)
        
        processing_time = time.time() - start_time
        logger.info(f"水印清除完成: {filename}, 耗时: {processing_time:.2f}秒")
        
        # 返回base64编码的图片数据用于预览
        _, buffer = cv2.imencode('.jpg', result)
        import base64
        image_data = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'image_data': f"data:image/jpeg;base64,{image_data}",
            'processing_time': round(processing_time, 2),
            'message': '水印清除成功'
        }), 200
        
    except Exception as e:
        logger.error(f"水印清除失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500


@watermark_bp.route('/ai-remove', methods=['POST'])
def ai_remove_watermark():
    """
    使用IOPaint AI模型去除水印
    
    Request Body:
        {
            "filename": "unique_id.jpg",
            "bboxes": [[x, y, w, h], ...]
        }
    
    Returns:
        JSON响应，包含处理结果
    """
    try:
        import requests as req_lib
        import tempfile
        
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: filename'
            }), 400
        
        filename = data['filename']
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 获取边界框
        bboxes = data.get('bboxes', [])
        
        if not bboxes:
            return jsonify({
                'success': False,
                'error': '请提供水印区域的边界框'
            }), 400
        
        # 创建mask图片
        img = cv2.imread(filepath)
        if img is None:
            return jsonify({
                'success': False,
                'error': '无法读取图片'
            }), 400
        
        mask = np.zeros(img.shape[:2], np.uint8)
        for bbox in bboxes:
            x, y, w, h = [int(val) for val in bbox]
            x = max(0, min(x, img.shape[1] - 1))
            y = max(0, min(y, img.shape[0] - 1))
            w = max(1, min(w, img.shape[1] - x))
            h = max(1, min(h, img.shape[0] - y))
            mask[y:y+h, x:x+w] = 255
        
        # 保存mask到临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as mask_file:
            mask_path = mask_file.name
            cv2.imwrite(mask_path, mask)
        
        try:
            # 调用IOPaint API
            iopaint_url = 'http://localhost:8080/api'
            
            # 准备文件
            files = {
                'image': (filename, open(filepath, 'rb'), 'image/jpeg'),
                'mask': ('mask.png', open(mask_path, 'rb'), 'image/png')
            }
            
            # 发送请求到IOPaint
            response = req_lib.post(
                f'{iopaint_url}/infer',
                files=files,
                data={'model': 'lama'},
                timeout=60
            )
            
            if response.status_code == 200:
                # 保存结果
                output_filename = f"result_ai_{filename}"
                output_path = os.path.join(RESULT_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # 返回base64编码的图片数据
                _, buffer = cv2.imencode('.jpg', cv2.imread(output_path))
                import base64
                image_data = base64.b64encode(buffer).decode('utf-8')
                
                logger.info(f"AI水印清除完成: {filename}")
                
                return jsonify({
                    'success': True,
                    'output_filename': output_filename,
                    'image_data': f"data:image/jpeg;base64,{image_data}",
                    'message': 'AI水印清除成功'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': f'IOPaint服务返回错误: {response.status_code}'
                }), 500
                
        except req_lib.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': '无法连接到IOPaint服务，请确保服务正在运行 (端口8080)'
            }), 503
        finally:
            # 清理临时mask文件
            if os.path.exists(mask_path):
                os.remove(mask_path)
        
    except Exception as e:
        logger.error(f"AI水印清除失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500


@watermark_bp.route('/auto-remove', methods=['POST'])
def auto_remove_watermark():
    """
    自动识别并去除水印
    
    Request Body:
        {
            "filename": "unique_id.jpg",
            "algorithm": "telea|ns",
            "radius": 3
        }
    
    Returns:
        JSON响应，包含处理结果
    """
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({
                'success': False,
                'error': '缺少必要参数: filename'
            }), 400
        
        filename = data['filename']
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        # 获取算法参数
        algorithm = data.get('algorithm', 'telea')
        radius = int(data.get('radius', 3))
        
        # 开始处理
        start_time = time.time()
        
        # 读取图片
        img = cv2.imread(filepath)
        if img is None:
            return jsonify({
                'success': False,
                'error': '无法读取图片'
            }), 400
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 使用阈值检测可能的白色水印区域
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        
        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 创建掩码
        mask = np.zeros(img.shape[:2], np.uint8)
        
        # 筛选可能的水印区域（面积较小的区域）
        img_area = img.shape[0] * img.shape[1]
        for contour in contours:
            area = cv2.contourArea(contour)
            # 假设水印区域面积小于图片的5%
            if area < img_area * 0.05 and area > 100:
                cv2.drawContours(mask, [contour], -1, 255, -1)
        
        # 如果没有检测到水印区域，尝试检测底部和角落
        if np.sum(mask) == 0:
            h, w = img.shape[:2]
            # 检测底部区域（常见水印位置）
            bottom_region = gray[int(h*0.9):, :]
            _, bottom_thresh = cv2.threshold(bottom_region, 240, 255, cv2.THRESH_BINARY)
            if np.sum(bottom_thresh) > 0:
                mask[int(h*0.9):, :] = bottom_thresh
            
            # 检测右下角
            corner_region = gray[int(h*0.85):, int(w*0.7):]
            _, corner_thresh = cv2.threshold(corner_region, 240, 255, cv2.THRESH_BINARY)
            if np.sum(corner_thresh) > 0:
                mask[int(h*0.85):, int(w*0.7):] = corner_thresh
        
        # 如果仍然没有检测到，返回原图
        if np.sum(mask) == 0:
            logger.warning(f"未检测到水印区域: {filename}")
            return jsonify({
                'success': True,
                'output_filename': filename,
                'message': '未检测到水印区域，返回原图',
                'detected_regions': 0
            }), 200
        
        # 执行修复
        if algorithm == 'ns':
            result = cv2.inpaint(img, mask, radius, cv2.INPAINT_NS)
        else:
            result = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
        
        # 生成输出文件名
        output_filename = f"result_auto_{filename}"
        output_path = os.path.join(RESULT_FOLDER, output_filename)
        
        # 保存结果
        cv2.imwrite(output_path, result)
        
        processing_time = time.time() - start_time
        logger.info(f"自动水印清除完成: {filename}, 耗时: {processing_time:.2f}秒")
        
        # 返回base64编码的图片数据用于预览
        _, buffer = cv2.imencode('.jpg', result)
        import base64
        image_data = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'image_data': f"data:image/jpeg;base64,{image_data}",
            'processing_time': round(processing_time, 2),
            'message': '自动水印清除完成'
        }), 200
        
    except Exception as e:
        logger.error(f"自动水印清除失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'处理失败: {str(e)}'
        }), 500


@watermark_bp.route('/download/<filename>', methods=['GET'])
def download_image(filename):
    """
    下载处理后的图片
    
    Args:
        filename: 文件名
    
    Returns:
        文件流
    """
    try:
        # 安全检查：防止路径遍历攻击
        filename = secure_filename(filename)
        
        # 先在结果文件夹中查找
        result_path = os.path.join(RESULT_FOLDER, filename)
        if os.path.exists(result_path):
            return send_file(result_path, as_attachment=True, download_name=filename)
        
        # 再在上传文件夹中查找
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(upload_path):
            return send_file(upload_path, as_attachment=True, download_name=filename)
        
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404
        
    except Exception as e:
        logger.error(f"下载图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'下载失败: {str(e)}'
        }), 500


@watermark_bp.route('/cleanup', methods=['POST'])
def cleanup_temp_files():
    """
    清理临时文件
    
    Request Body:
        {
            "filename": "unique_id.jpg"  // 可选，指定清理特定文件
        }
    
    Returns:
        JSON响应
    """
    try:
        data = request.get_json() or {}
        filename = data.get('filename')
        
        cleaned_count = 0
        
        if filename:
            # 清理指定文件
            filename = secure_filename(filename)
            files_to_delete = [
                os.path.join(UPLOAD_FOLDER, filename),
                os.path.join(RESULT_FOLDER, f"result_{filename}"),
                os.path.join(RESULT_FOLDER, f"result_auto_{filename}")
            ]
            
            for filepath in files_to_delete:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    cleaned_count += 1
                    logger.info(f"已删除文件: {filepath}")
        else:
            # 清理所有超过24小时的文件
            now = datetime.now()
            cutoff_time = now - timedelta(hours=24)
            
            for folder in [UPLOAD_FOLDER, RESULT_FOLDER]:
                for filename in os.listdir(folder):
                    filepath = os.path.join(folder, filename)
                    if os.path.isfile(filepath):
                        file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                        if file_mtime < cutoff_time:
                            os.remove(filepath)
                            cleaned_count += 1
                            logger.info(f"已删除过期文件: {filepath}")
        
        logger.info(f"临时文件清理完成，共删除 {cleaned_count} 个文件")
        
        return jsonify({
            'success': True,
            'cleaned_count': cleaned_count,
            'message': f'成功清理 {cleaned_count} 个文件'
        }), 200
        
    except Exception as e:
        logger.error(f"清理临时文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'清理失败: {str(e)}'
        }), 500


@watermark_bp.route('/preview/<filename>', methods=['GET'])
def preview_image(filename):
    """
    预览图片（用于前端显示）
    
    Args:
        filename: 文件名
    
    Returns:
        图片文件
    """
    try:
        # 安全检查
        filename = secure_filename(filename)
        
        # 先在结果文件夹中查找
        result_path = os.path.join(RESULT_FOLDER, filename)
        if os.path.exists(result_path):
            return send_file(result_path)
        
        # 再在上传文件夹中查找
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(upload_path):
            return send_file(upload_path)
        
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404
        
    except Exception as e:
        logger.error(f"预览图片失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'预览失败: {str(e)}'
        }), 500
