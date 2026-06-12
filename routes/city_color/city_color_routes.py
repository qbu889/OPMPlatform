#!/usr/bin/env python3
"""
CityColor 颜色提取系统 - MySQL 持久化版本
==========================================
提供内容颜色提取、方案管理接口。数据全部存储于 MySQL。

路由列表:
  POST   /api/city-color/extract              - 从内容提取颜色
  GET    /api/city-color/schemes               - 获取方案列表（分页）
  POST   /api/city-color/schemes               - 保存颜色方案
  GET    /api/city-color/schemes/<scheme_id>   - 获取方案详情
  PUT    /api/city-color/schemes/<scheme_id>   - 更新方案
  DELETE /api/city-color/schemes/<scheme_id>   - 删除方案
  GET    /api/city-color/palette-types          - 获取配色类型列表
  POST   /api/city-color/export/png            - 导出PNG图片
  GET    /api/city-color/keyword-mappings       - 获取关键词-颜色映射列表
  POST   /api/city-color/keyword-mappings       - 新增关键词-颜色映射
  PUT    /api/city-color/keyword-mappings/<id>  - 更新关键词-颜色映射
  DELETE /api/city-color/keyword-mappings/<id>  - 删除关键词-颜色映射
  GET    /api/city-color/city-colors            - 获取城市色彩库列表
  POST   /api/city-color/city-colors            - 新增城市色彩
  PUT    /api/city-color/city-colors/<id>       - 更新城市色彩
  DELETE /api/city-color/city-colors/<id>       - 删除城市色彩

作者: Claude Code
日期: 2026-06-11
"""

import os
import re
import json
import hashlib
import random
import logging
import io
from datetime import datetime

from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
    current_app,
)

logger = logging.getLogger(__name__)

city_color_bp = Blueprint('city_color', __name__, url_prefix='/city-color')


# ============================================================================
# 数据库工具函数（遵循项目 pymysql 模式）
# ============================================================================

def _get_db_config():
    """从 Flask 配置中获取数据库连接参数"""
    return {
        'host': current_app.config.get('MYSQL_HOST', 'localhost'),
        'port': int(current_app.config.get('MYSQL_PORT', 3306)),
        'user': current_app.config.get('MYSQL_USER', 'root'),
        'password': current_app.config.get('MYSQL_PASSWORD', '12345678'),
        'charset': current_app.config.get('MYSQL_CHARSET', 'utf8mb4'),
    }


def _get_db_connection(database=None):
    """获取 MySQL 数据库连接"""
    config = _get_db_config()
    if database:
        config['database'] = current_app.config.get(database, 'knowledge_base')
    else:
        config['database'] = current_app.config.get('KNOWLEDGE_BASE_DB', 'knowledge_base')
    import pymysql
    return pymysql.connect(**config)


def init_city_color(app):
    """初始化 CityColor 数据库表（首次使用时自动创建）"""
    with app.app_context():
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()

            # 颜色方案表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_color_schemes (
                    id VARCHAR(50) PRIMARY KEY COMMENT '方案唯一标识',
                    title VARCHAR(255) NOT NULL DEFAULT '' COMMENT '方案名称',
                    colors TEXT NOT NULL COMMENT '颜色数据(JSON数组)',
                    gradient VARCHAR(500) DEFAULT '' COMMENT '渐变CSS字符串',
                    palette_type VARCHAR(50) DEFAULT 'custom' COMMENT '配色类型',
                    source_text VARCHAR(1000) DEFAULT '' COMMENT '原始输入内容',
                    extract_mode VARCHAR(20) DEFAULT 'auto' COMMENT '提取模式: auto/city/brand/random',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_created_at (created_at),
                    INDEX idx_palette_type (palette_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CityColor-颜色方案表'
            """)

            # 关键词-颜色映射配置表（可管理扩展）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_color_keyword_mappings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    keyword VARCHAR(100) NOT NULL COMMENT '关键词',
                    hex_color VARCHAR(20) NOT NULL COMMENT 'HEX颜色值',
                    color_name VARCHAR(100) DEFAULT '' COMMENT '颜色中文名称',
                    category VARCHAR(50) DEFAULT '' COMMENT '分类: nature/city/emotion/brand',
                    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1=启用，0=禁用',
                    sort_order INT DEFAULT 0 COMMENT '排序权重',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_keyword (keyword),
                    INDEX idx_category (category)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CityColor-关键词颜色映射配置表'
            """)

            # 城市色彩库表（可管理扩展）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_color_city_db (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    city_name VARCHAR(100) NOT NULL UNIQUE COMMENT '城市名称',
                    colors TEXT NOT NULL COMMENT '颜色列表(JSON数组)',
                    description VARCHAR(500) DEFAULT '' COMMENT '城市色彩描述',
                    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否启用：1=启用，0=禁用',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_city_name (city_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='CityColor-城市色彩库表'
            """)

            # 插入默认关键词-颜色映射数据
            cursor.execute("""
                INSERT IGNORE INTO city_color_keyword_mappings 
                    (keyword, hex_color, color_name, category, sort_order) VALUES
                ('天空', '#87CEEB', '天蓝', 'nature', 1),
                ('蓝天', '#4A90D9', '天空蓝', 'nature', 2),
                ('海洋', '#1E90FF', '宝蓝', 'nature', 3),
                ('大海', '#006994', '深海蓝', 'nature', 4),
                ('水', '#5DADE2', '浅天蓝', 'nature', 5),
                ('河流', '#85C1E9', '浅蓝灰', 'nature', 6),
                ('森林', '#27AE60', '森林绿', 'nature', 7),
                ('绿色', '#2ECC71', '翠绿', 'nature', 8),
                ('草地', '#82E0AA', '薄荷绿', 'nature', 9),
                ('树叶', '#52BE80', '绿叶', 'nature', 10),
                ('树木', '#1ABC9C', '青绿', 'nature', 11),
                ('太阳', '#F39C12', '金色', 'nature', 12),
                ('阳光', '#F1C40F', '亮黄', 'nature', 13),
                ('金色', '#D4AC0D', '暗金', 'nature', 14),
                ('火焰', '#E74C3C', '珊瑚红', 'nature', 15),
                ('红色', '#C0392B', '深红', 'nature', 16),
                ('火', '#E67E22', '橙色', 'nature', 17),
                ('玫瑰', '#E91E63', '玫红', 'nature', 18),
                ('花', '#FF69B4', '粉色', 'nature', 19),
                ('樱花', '#FFB7C5', '樱花粉', 'nature', 20),
                ('紫色', '#8E44AD', '紫色', 'nature', 21),
                ('紫', '#9B59B6', '浅紫', 'nature', 22),
                ('白色', '#ECF0F1', '白色', 'nature', 23),
                ('雪', '#D5F5E3', '雪白', 'nature', 24),
                ('云', '#BDC3C7', '灰色', 'nature', 25),
                ('月亮', '#F9E79F', '月光黄', 'nature', 26),
                ('星星', '#F4D03F', '星黄', 'nature', 27),
                ('城市', '#7F8C8D', '石板灰', 'city', 28),
                ('建筑', '#95A5A6', '建筑灰', 'city', 29),
                ('钢铁', '#607D8B', '钢灰', 'city', 30),
                ('霓虹', '#FF00FF', '霓虹紫', 'city', 31),
                ('灯光', '#F39C12', '暖光黄', 'city', 32),
                ('夜景', '#2C3E50', '深蓝灰', 'city', 33),
                ('日落', '#E74C3C', '日落红', 'city', 34),
                ('黄昏', '#D35400', '深橙', 'city', 35),
                ('日出', '#F39C12', '日出金', 'city', 36),
                ('温暖', '#E67E22', '暖橙', 'emotion', 37),
                ('冷静', '#3498DB', '冷静蓝', 'emotion', 38),
                ('活力', '#E74C3C', '活力红', 'emotion', 39),
                ('宁静', '#AED6F1', '宁静蓝', 'emotion', 40),
                ('神秘', '#6C3483', '神秘紫', 'emotion', 41),
                ('浪漫', '#FD79A8', '浪漫粉', 'emotion', 42),
                ('复古', '#B8860B', '复古金', 'emotion', 43),
                ('未来', '#00CED1', '未来青', 'emotion', 44)
            """)

            # 插入默认城市色彩数据
            cursor.execute("""
                INSERT IGNORE INTO city_color_city_db 
                    (city_name, colors, description) VALUES
                ('巴黎', '["#8E44AD", "#F5B7B1", "#2C3E50", "#FDEBD0", "#FFFFFF"]', '紫/粉/灰——浪漫之都'),
                ('东京', '["#E74C3C", "#FFFFFF", "#2C3E50", "#F1C40F", "#27AE60"]', '红/白/黑——传统与现代'),
                ('纽约', '["#1A5276", "#F39C12", "#7F8C8D", "#ECF0F1", "#2C3E50"]', '蓝/金/灰——不夜城'),
                ('伦敦', '["#2C3E50", "#C0392B", "#FDEBD0", "#7D3C98", "#FFFFFF"]', '黑/红/米——古典英伦'),
                ('罗马', '["#E67E22", "#C0392B", "#F5B7B1", "#D4AC0D", "#ECF0F1"]', '橙/红/金——永恒之城'),
                ('北京', '["#C0392B", "#F1C40F", "#27AE60", "#ECF0F1", "#7D3C98"]', '红/金/绿——皇城色彩'),
                ('迪拜', '["#F1C40F", "#2C3E50", "#FFFFFF", "#E67E22", "#1ABC9C"]', '金/黑/白——沙漠明珠'),
                ('悉尼', '["#1E90FF", "#FFFFFF", "#27AE60", "#F39C12", "#ECF0F1"]', '蓝/白/绿——海港城市')
            """)

            conn.commit()
            cursor.close()
            conn.close()
            logger.info("✅ CityColor 数据库表初始化完成")
        except Exception as e:
            logger.error(f"⚠️  CityColor 数据库表初始化失败: {e}")


# ============================================================================
# 颜色提取核心引擎（与数据库无关）
# ============================================================================

def _hex_to_rgb(hex_color: str) -> dict:
    """HEX 转 RGB"""
    hex_color = hex_color.lstrip('#')
    return {
        'r': int(hex_color[0:2], 16),
        'g': int(hex_color[2:4], 16),
        'b': int(hex_color[4:6], 16)
    }


def _hsl_to_rgb(h: float, s: float, l: float) -> tuple:
    """HSL 转 RGB"""
    if s == 0:
        r = g = b = l
    else:
        def hue2rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1 / 3:
                return p + (q - p) * 6 * t
            if t < 1 / 2:
                return q
            if t < 2 / 3:
                return p + (q - p) * (2 / 3 - t) * 6
            return p

        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1 / 3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1 / 3)
    return r, g, b


def _generate_harmonious_colors(base_hue: int, count: int) -> list:
    """生成和谐配色（基于色相环）"""
    colors = []
    if count <= 3:
        angles = [0, 120, 240][:count] if count >= 3 else [0, 30][:count]
    elif count <= 6:
        angles = [0, 30, 150, 180, 210, 330][:count]
    else:
        angles = [i * (360 // count) for i in range(count)]

    for angle in angles:
        h = (base_hue + angle) % 360
        r, g, b = _hsl_to_rgb(h / 360, 0.7, 0.6)
        hex_color = f'#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}'
        colors.append(hex_color)
    return colors


def _generate_gradient(colors: list) -> str:
    """生成 CSS 渐变字符串"""
    hex_values = [c['hex'] if isinstance(c, dict) else c for c in colors]
    if len(hex_values) <= 1:
        return hex_values[0] if hex_values else '#FFFFFF'
    stops = ', '.join(
        f'{hex_values[i]} {(i / (len(hex_values) - 1)) * 100}%'
        for i in range(len(hex_values))
    )
    return f'linear-gradient(to right, {stops})'


def _build_color_objects(hex_colors: list, source_type: str) -> list:
    """构建颜色对象列表（含名称和比例）"""
    color_names = {
        '#E74C3C': '珊瑚红', '#C0392B': '深红', '#FF69B4': '粉色',
        '#3498DB': '天空蓝', '#1E90FF': '宝蓝', '#2C3E50': '深蓝灰',
        '#27AE60': '森林绿', '#2ECC71': '翠绿', '#82E0AA': '薄荷绿',
        '#F39C12': '金色', '#F1C40F': '亮黄', '#D4AC0D': '暗金',
        '#8E44AD': '紫色', '#9B59B6': '浅紫', '#E91E63': '玫红',
        '#ECF0F1': '白色', '#BDC3C7': '灰色', '#7F8C8D': '石板灰',
        '#E67E22': '橙色', '#D35400': '深橙', '#1ABC9C': '青绿',
        '#F5B7B1': '浅粉', '#FDEBD0': '米色', '#FFFFFF': '纯白',
        '#87CEEB': '天蓝', '#006994': '深海蓝', '#5DADE2': '浅天蓝',
        '#F9E79F': '月光黄', '#F4D03F': '星黄', '#FFB7C5': '樱花粉',
        '#607D8B': '钢灰', '#AED6F1': '宁静蓝', '#6C3483': '神秘紫',
        '#FD79A8': '浪漫粉', '#B8860B': '复古金', '#00CED1': '未来青',
        '#1A5276': '深蓝',
    }

    total = len(hex_colors)
    objects = []
    for i, hex_color in enumerate(hex_colors):
        name = color_names.get(hex_color, f'颜色{i + 1}')
        ratio = round(1.0 / total, 2)
        objects.append({
            'hex': hex_color,
            'name': name,
            'ratio': ratio,
            'rgb': _hex_to_rgb(hex_color)
        })
    return objects


def extract_colors_from_content(content: str, mode: str = 'auto', count: int = 5) -> dict:
    """从内容中提取颜色方案（从数据库读取映射规则）"""
    content_lower = content.lower()

    if mode == 'city':
        colors = _extract_city_colors_from_db(content, count)
        palette_type = 'custom'
    elif mode == 'brand':
        colors = _extract_brand_colors(content, count)
        palette_type = 'custom'
    elif mode == 'random':
        seed = hashlib.md5(content.encode()).hexdigest()[:8]
        colors = _generate_random_palette(seed, count)
        palette_type = 'custom'
    else:  # auto (默认模式)
        colors, palette_type = _extract_auto_colors_from_db(content, count)

    gradient = _generate_gradient(colors)
    return {
        'colors': colors,
        'gradient': gradient,
        'palette_type': palette_type,
        'source_text': content
    }


def _extract_city_colors_from_db(content: str, count: int) -> list:
    """城市模式：从数据库城市色彩库中提取"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT city_name, colors FROM city_color_city_db WHERE is_active = 1"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        for row in rows:
            if row['city_name'] in content:
                hex_list = json.loads(row['colors'])
                return _build_color_objects(hex_list[:count], f'city_{row["city_name"]}')

        # 未匹配到城市，返回默认色
        default_colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']
        return _build_color_objects(default_colors[:count], 'city_default')
    except Exception as e:
        logger.error(f"城市色彩提取失败: {e}")
        default_colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']
        return _build_color_objects(default_colors[:count], 'city_default')


def _extract_auto_colors_from_db(content: str, count: int) -> tuple:
    """自动模式：从数据库关键词映射中提取颜色"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 先匹配城市库
        cursor.execute(
            "SELECT city_name, colors FROM city_color_city_db WHERE is_active = 1"
        )
        city_rows = cursor.fetchall()
        for row in city_rows:
            if row['city_name'] in content:
                hex_list = json.loads(row['colors'])[:count]
                cursor.close()
                conn.close()
                return _build_color_objects(hex_list, 'city'), 'custom'

        # 再匹配关键词库
        cursor.execute(
            "SELECT keyword, hex_color FROM city_color_keyword_mappings WHERE is_active = 1 ORDER BY sort_order"
        )
        keyword_rows = cursor.fetchall()

        found_colors = []
        seen_hex = set()
        for row in keyword_rows:
            if row['keyword'] in content_lower and row['hex_color'] not in seen_hex:
                found_colors.append(row['hex_color'])
                seen_hex.add(row['hex_color'])
            if len(found_colors) >= count:
                break

        # 如果关键词不够，补充随机色（基于内容哈希）
        if len(found_colors) < count:
            seed = hashlib.md5(content.encode()).hexdigest()[:8]
            random.seed(seed)
            while len(found_colors) < count:
                hex_color = f'#{random.randint(0x000000, 0xFFFFFF):06X}'
                if hex_color not in seen_hex:
                    found_colors.append(hex_color)
                    seen_hex.add(hex_color)

        cursor.close()
        conn.close()
        return _build_color_objects(found_colors[:count], 'auto'), 'custom'

    except Exception as e:
        logger.error(f"自动颜色提取失败: {e}")
        default_colors = ['#3498DB', '#2ECC71', '#E74C3C', '#F39C12', '#9B59B6']
        return _build_color_objects(default_colors[:count], 'auto'), 'custom'


def _extract_brand_colors(content: str, count: int) -> list:
    """品牌模式：基于品牌关键词生成色系"""
    brand_keywords = {
        '科技': ['#1A5276', '#2ECC71', '#ECF0F1'],
        '医疗': ['#27AE60', '#85C1E9', '#FFFFFF'],
        '教育': ['#2980B9', '#F39C12', '#E74C3C'],
        '餐饮': ['#E74C3C', '#F39C12', '#27AE60'],
        '金融': ['#1A5276', '#F1C40F', '#2C3E50'],
        '时尚': ['#2C3E50', '#E91E63', '#FFFFFF'],
    }

    found = []
    for keyword, colors in brand_keywords.items():
        if keyword in content.lower():
            found.extend(colors)

    if not found:
        seed = hashlib.md5(content.encode()).hexdigest()[:8]
        random.seed(seed)
        base_hue = int(seed, 16) % 360
        found = _generate_harmonious_colors(base_hue, count)

    return _build_color_objects(found[:count], 'brand')


def _generate_random_palette(seed: str, count: int) -> list:
    """基于种子生成随机和谐配色"""
    random.seed(seed)
    base_hue = int(seed, 16) % 360
    return _generate_harmonious_colors(base_hue, count)


# ============================================================================
# API 路由定义
# ============================================================================

@city_color_bp.route('/extract', methods=['POST'])
def extract_colors():
    """从输入内容中提取颜色方案"""
    try:
        body = request.get_json()
        if not body or 'content' not in body:
            return jsonify({'success': False, 'msg': '缺少 content 参数'}), 400

        content = body['content'].strip()
        if not content:
            return jsonify({'success': False, 'msg': '内容不能为空'}), 400

        mode = body.get('mode', 'auto')
        count = min(body.get('count', 5), 12)

        result = extract_colors_from_content(content, mode=mode, count=count)
        return jsonify({'success': True, 'data': result})

    except Exception as e:
        logger.error(f"颜色提取失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/schemes', methods=['GET'])
def get_schemes():
    """获取已保存的颜色方案列表（分页）"""
    try:
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        offset = (page - 1) * page_size

        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # 总数
        cursor.execute("SELECT COUNT(*) as total FROM city_color_schemes")
        total = cursor.fetchone()['total']

        # 分页查询
        cursor.execute(
            "SELECT id, title, colors, gradient, palette_type, source_text, extract_mode, created_at "
            "FROM city_color_schemes ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (page_size, offset)
        )
        schemes = cursor.fetchall()

        # 解析 colors JSON
        for scheme in schemes:
            if isinstance(scheme.get('colors'), str):
                scheme['colors'] = json.loads(scheme['colors'])

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'schemes': schemes
            }
        })

    except Exception as e:
        logger.error(f"获取方案列表失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/schemes', methods=['POST'])
def save_scheme():
    """保存颜色方案"""
    try:
        body = request.get_json()
        if not body or 'colors' not in body:
            return jsonify({'success': False, 'msg': '缺少 colors 数据'}), 400

        scheme_id = f"sc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(4).hex()}"

        # 将 colors 序列化为 JSON 字符串存储
        colors_json = json.dumps(body['colors'], ensure_ascii=False)

        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO city_color_schemes 
                (id, title, colors, gradient, palette_type, source_text, extract_mode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            scheme_id,
            body.get('title', f'方案 {datetime.now().strftime("%m%d%H%M")}'),
            colors_json,
            body.get('gradient', ''),
            body.get('palette_type', 'custom'),
            body.get('source_text', ''),
            body.get('extract_mode', 'auto')
        ))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {'id': scheme_id, 'message': '保存成功'}
        })

    except Exception as e:
        logger.error(f"保存方案失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/schemes/<scheme_id>', methods=['GET'])
def get_scheme(scheme_id):
    """获取单个颜色方案详情"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM city_color_schemes WHERE id = %s", (scheme_id,)
        )
        scheme = cursor.fetchone()
        cursor.close()
        conn.close()

        if not scheme:
            return jsonify({'success': False, 'msg': '方案不存在'}), 404

        # 解析 colors JSON
        if isinstance(scheme.get('colors'), str):
            scheme['colors'] = json.loads(scheme['colors'])

        return jsonify({'success': True, 'data': scheme})

    except Exception as e:
        logger.error(f"获取方案详情失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/schemes/<scheme_id>', methods=['PUT'])
def update_scheme(scheme_id):
    """更新颜色方案"""
    try:
        body = request.get_json()
        if not body or 'colors' not in body:
            return jsonify({'success': False, 'msg': '缺少 colors 数据'}), 400

        colors_json = json.dumps(body['colors'], ensure_ascii=False)

        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE city_color_schemes 
            SET title = %s, colors = %s, gradient = %s, 
                palette_type = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            body.get('title', ''),
            colors_json,
            body.get('gradient', ''),
            body.get('palette_type', 'custom'),
            scheme_id
        ))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'success': False, 'msg': '方案不存在'}), 404

        return jsonify({'success': True, 'data': {'message': '更新成功'}})

    except Exception as e:
        logger.error(f"更新方案失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/schemes/<scheme_id>', methods=['DELETE'])
def delete_scheme(scheme_id):
    """删除颜色方案"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM city_color_schemes WHERE id = %s", (scheme_id,))
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'success': False, 'msg': '方案不存在'}), 404

        return jsonify({'success': True, 'data': {'message': '删除成功'}})

    except Exception as e:
        logger.error(f"删除方案失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/palette-types', methods=['GET'])
def get_palette_types():
    """获取支持的配色类型列表"""
    palette_types = [
        {'value': 'complementary', 'label': '互补色'},
        {'value': 'analogous', 'label': '类似色'},
        {'value': 'triadic', 'label': '三角色'},
        {'value': 'split-complementary', 'label': '分裂互补色'},
        {'value': 'monochromatic', 'label': "单色系"},
        {'value': 'custom', 'label': '自定义'}
    ]
    return jsonify({'success': True, 'data': palette_types})


@city_color_bp.route('/export/png', methods=['POST'])
def export_as_png():
    """导出颜色方案为 PNG 图片"""
    try:
        from PIL import Image, ImageDraw

        body = request.get_json()
        if not body or 'colors' not in body:
            return jsonify({'success': False, 'msg': '缺少 colors 数据'}), 400

        colors = body['colors']
        width = body.get('width', 800)
        height = body.get('height', 600)
        title = body.get('title', 'CityColor Palette')

        img = Image.new('RGB', (width, height), '#FFFFFF')
        draw = ImageDraw.Draw(img)

        color_count = len(colors)
        bar_height = (height - 80) // max(color_count, 1)

        for i, color_info in enumerate(colors):
            hex_color = color_info.get('hex', '#000000')
            y_start = 60 + i * bar_height

            draw.rectangle(
                [(20, y_start), (width - 20, y_start + bar_height - 10)],
                fill=hex_color
            )

            label = color_info.get('name', hex_color)
            draw.text((30, y_start + bar_height // 2 - 10), label, fill='#333333')

        draw.text((20, 15), title, fill='#333333')

        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        return send_file(
            output,
            mimetype='image/png',
            as_attachment=True,
            download_name=f'{title}.png'
        )

    except ImportError:
        return jsonify({
            'success': False,
            'msg': 'Pillow 库未安装，请执行: pip install Pillow'
        }), 500
    except Exception as e:
        logger.error(f"导出PNG失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


# ============================================================================
# 关键词-颜色映射管理接口（配置化管理）
# ============================================================================

@city_color_bp.route('/keyword-mappings', methods=['GET'])
def get_keyword_mappings():
    """获取关键词-颜色映射列表（可管理）"""
    try:
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 50)), 100)
        offset = (page - 1) * page_size
        category = request.args.get('category', '')

        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if category:
            cursor.execute(
                "SELECT COUNT(*) as total FROM city_color_keyword_mappings WHERE category = %s",
                (category,)
            )
        else:
            cursor.execute("SELECT COUNT(*) as total FROM city_color_keyword_mappings")
        total = cursor.fetchone()['total']

        if category:
            cursor.execute(
                "SELECT * FROM city_color_keyword_mappings WHERE category = %s ORDER BY sort_order LIMIT %s OFFSET %s",
                (category, page_size, offset)
            )
        else:
            cursor.execute(
                "SELECT * FROM city_color_keyword_mappings ORDER BY sort_order LIMIT %s OFFSET %s",
                (page_size, offset)
            )
        mappings = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'mappings': mappings
            }
        })

    except Exception as e:
        logger.error(f"获取关键词映射失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/keyword-mappings', methods=['POST'])
def save_keyword_mapping():
    """新增关键词-颜色映射"""
    try:
        body = request.get_json()
        if not body or 'keyword' not in body or 'hex_color' not in body:
            return jsonify({'success': False, 'msg': '缺少 keyword 或 hex_color'}), 400

        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO city_color_keyword_mappings 
                (keyword, hex_color, color_name, category, sort_order)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            body['keyword'],
            body['hex_color'].lstrip('#'),
            body.get('color_name', ''),
            body.get('category', ''),
            body.get('sort_order', 0)
        ))
        conn.commit()
        mapping_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {'id': mapping_id, 'message': '保存成功'}
        })

    except Exception as e:
        logger.error(f"保存关键词映射失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/keyword-mappings/<int:mapping_id>', methods=['PUT'])
def update_keyword_mapping(mapping_id):
    """更新关键词-颜色映射"""
    try:
        body = request.get_json()

        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE city_color_keyword_mappings 
            SET keyword = %s, hex_color = %s, color_name = %s, 
                category = %s, is_active = %s, sort_order = %s
            WHERE id = %s
        """, (
            body.get('keyword'),
            body.get('hex_color', '').lstrip('#'),
            body.get('color_name'),
            body.get('category'),
            body.get('is_active', 1),
            body.get('sort_order', 0),
            mapping_id
        ))
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'success': False, 'msg': '映射不存在'}), 404

        return jsonify({'success': True, 'data': {'message': '更新成功'}})

    except Exception as e:
        logger.error(f"更新关键词映射失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/keyword-mappings/<int:mapping_id>', methods=['DELETE'])
def delete_keyword_mapping(mapping_id):
    """删除关键词-颜色映射（软删除：设置 is_active=0）"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE city_color_keyword_mappings SET is_active = 0 WHERE id = %s",
            (mapping_id,)
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'success': False, 'msg': '映射不存在'}), 404

        return jsonify({'success': True, 'data': {'message': '删除成功'}})

    except Exception as e:
        logger.error(f"删除关键词映射失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


# ============================================================================
# 城市色彩库管理接口（配置化管理）
# ============================================================================

@city_color_bp.route('/city-colors', methods=['GET'])
def get_city_colors():
    """获取城市色彩库列表"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM city_color_city_db ORDER BY city_name")
        cities = cursor.fetchall()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': cities})

    except Exception as e:
        logger.error(f"获取城市色彩库失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/city-colors', methods=['POST'])
def save_city_color():
    """新增城市色彩"""
    try:
        body = request.get_json()
        if not body or 'city_name' not in body or 'colors' not in body:
            return jsonify({'success': False, 'msg': '缺少 city_name 或 colors'}), 400

        # 确保 colors 是 JSON 字符串
        colors_value = body['colors']
        if isinstance(colors_value, list):
            colors_value = json.dumps(colors_value, ensure_ascii=False)

        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO city_color_city_db 
                (city_name, colors, description)
            VALUES (%s, %s, %s)
        """, (
            body['city_name'],
            colors_value,
            body.get('description', '')
        ))
        city_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {'id': city_id, 'message': '保存成功'}
        })

    except Exception as e:
        logger.error(f"保存城市色彩失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/city-colors/<int:city_id>', methods=['PUT'])
def update_city_color(city_id):
    """更新城市色彩"""
    try:
        body = request.get_json()

        colors_value = body.get('colors', '')
        if isinstance(colors_value, list):
            colors_value = json.dumps(colors_value, ensure_ascii=False)

        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE city_color_city_db 
            SET city_name = %s, colors = %s, description = %s, is_active = %s
            WHERE id = %s
        """, (
            body.get('city_name'),
            colors_value,
            body.get('description', ''),
            body.get('is_active', 1),
            city_id
        ))
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'success': False, 'msg': '城市色彩不存在'}), 404

        return jsonify({'success': True, 'data': {'message': '更新成功'}})

    except Exception as e:
        logger.error(f"更新城市色彩失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500


@city_color_bp.route('/city-colors/<int:city_id>', methods=['DELETE'])
def delete_city_color(city_id):
    """删除城市色彩（软删除：设置 is_active=0）"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE city_color_city_db SET is_active = 0 WHERE id = %s",
            (city_id,)
        )
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({'success': False, 'msg': '城市色彩不存在'}), 404

        return jsonify({'success': True, 'data': {'message': '删除成功'}})

    except Exception as e:
        logger.error(f"删除城市色彩失败: {e}")
        return jsonify({'success': False, 'msg': str(e)}), 500
