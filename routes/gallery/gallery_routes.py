"""
画作与诗集展示 - 后端路由
提供画作和诗集的 CRUD 及浏览接口
"""
from flask import Blueprint, jsonify, request, send_file
import os
import json
from datetime import datetime

gallery_bp = Blueprint('gallery', __name__, url_prefix='/api/gallery')

# ==================== 数据存储路径 ====================
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'gallery')
os.makedirs(DATA_DIR, exist_ok=True)

PAINTINGS_FILE = os.path.join(DATA_DIR, 'paintings.json')
POETRY_FILE = os.path.join(DATA_DIR, 'poetry.json')

# ==================== 示例数据（首次启动时初始化）====================
DEFAULT_PAINTINGS = [
    {
        "id": 1,
        "title": "星空",
        "artist": "梵高",
        "year": 1889,
        "category": "后印象派",
        "image_url": "/static/gallery/starry_night.jpg",
        "description": "夜晚的天空中，星星闪烁着光芒，月亮像金色的镰刀悬挂在天边。",
        "tags": ["油画", "夜景", "经典"],
        "created_at": "2026-01-01"
    },
    {
        "id": 2,
        "title": "睡莲",
        "artist": "莫奈",
        "year": 1899,
        "category": "印象派",
        "image_url": "/static/gallery/water_lilies.jpg",
        "description": "池塘中睡莲静静绽放，水面倒映着天空的色彩。",
        "tags": ["油画", "花卉", "印象派"],
        "created_at": "2026-01-01"
    },
    {
        "id": 3,
        "title": "清明上河图",
        "artist": "张择端",
        "year": 1120,
        "category": "古代绘画",
        "image_url": "/static/gallery/qingming_scroll.jpg",
        "description": "描绘了北宋都城汴京的繁华景象，人物众多，场景丰富。",
        "tags": ["国画", "长卷", "历史"],
        "created_at": "2026-01-01"
    },
    {
        "id": 4,
        "title": "蒙娜丽莎",
        "artist": "达芬奇",
        "year": 1503,
        "category": "文艺复兴",
        "image_url": "/static/gallery/mona_lisa.jpg",
        "description": "神秘的微笑穿越时空，成为艺术史上最著名的肖像画。",
        "tags": ["油画", "肖像", "经典"],
        "created_at": "2026-01-01"
    },
    {
        "id": 5,
        "title": "富春山居图",
        "artist": "黄公望",
        "year": 1347,
        "category": "古代绘画",
        "image_url": "/static/gallery/fuchun_mountains.jpg",
        "description": "以富春江一带秋景为题材，笔墨简远，意境苍茫。",
        "tags": ["国画", "山水", "经典"],
        "created_at": "2026-01-01"
    },
    {
        "id": 6,
        "title": "呐喊",
        "artist": "蒙克",
        "year": 1893,
        "category": "表现主义",
        "image_url": "/static/gallery/the_scream.jpg",
        "description": "扭曲的天空下，一个人捂住耳朵发出无声的呐喊。",
        "tags": ["油画", "表现主义", "现代"],
        "created_at": "2026-01-01"
    }
]

DEFAULT_POETRY = [
    {
        "id": 1,
        "title": "静夜思",
        "author": "李白",
        "dynasty": "唐",
        "content": "床前明月光，疑是地上霜。\n举头望明月，低头思故乡。",
        "category": "思乡",
        "description": "诗人旅居外地，在寂静的夜晚望月思乡，表达了深切的思乡之情。",
        "tags": ["唐诗", "思乡", "月亮"],
        "created_at": "2026-01-01"
    },
    {
        "id": 2,
        "title": "春晓",
        "author": "孟浩然",
        "dynasty": "唐",
        "content": "春眠不觉晓，处处闻啼鸟。\n夜来风雨声，花落知多少。",
        "category": "山水田园",
        "description": "描写春天早晨的美好景象，表达了对自然美景的喜爱与珍惜。",
        "tags": ["唐诗", "春天", "田园"],
        "created_at": "2026-01-01"
    },
    {
        "id": 3,
        "title": "水调歌头·明月几时有",
        "author": "苏轼",
        "dynasty": "宋",
        "content": "明月几时有？把酒问青天。\n不知天上宫阙，今夕是何年。\n我欲乘风归去，又恐琼楼玉宇，高处不胜寒。\n起舞弄清影，何似在人间。",
        "category": "抒情",
        "description": "中秋望月怀人，以明月为线索，表达了对弟弟苏辙的思念之情。",
        "tags": ["宋词", "抒情", "月亮"],
        "created_at": "2026-01-01"
    },
    {
        "id": 4,
        "title": "登高",
        "author": "杜甫",
        "dynasty": "唐",
        "content": "风急天高猿啸哀，渚清沙白鸟飞回。\n无边落木萧萧下，不尽长江滚滚来。\n万里悲秋常作客，百年多病独登台。\n艰难苦恨繁霜鬓，潦倒新停浊酒杯。",
        "category": "抒情",
        "description": "诗人登高望远，触景生情，抒发了漂泊异乡、年老多病的悲凉心境。",
        "tags": ["唐诗", "抒情", "秋天"],
        "created_at": "2026-01-01"
    },
    {
        "id": 5,
        "title": "念奴娇·赤壁怀古",
        "author": "苏轼",
        "dynasty": "宋",
        "content": "大江东去，浪淘尽，千古风流人物。\n故垒西边，人道是，三国周郎赤壁。\n乱石穿空，惊涛拍岸，卷起千堆雪。",
        "category": "怀古",
        "description": "游览赤壁，追念周瑜的英雄业绩，抒发了对历史英雄的仰慕和自己壮志未酬的感慨。",
        "tags": ["宋词", "怀古", "豪放"],
        "created_at": "2026-01-01"
    },
    {
        "id": 6,
        "title": "江雪",
        "author": "柳宗元",
        "dynasty": "唐",
        "content": "千山鸟飞绝，万径人踪灭。\n孤舟蓑笠翁，独钓寒江雪。",
        "category": "山水田园",
        "description": "描绘了一幅寒江独钓图，表现了诗人清高孤傲、不与世俗同流合污的情怀。",
        "tags": ["唐诗", "山水", "孤独"],
        "created_at": "2026-01-01"
    }
]


# ==================== 工具函数 ====================
def _load_json(filepath, default=None):
    """安全读取 JSON 文件"""
    if default is None:
        return []
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    _save_json(filepath, default)
    return default


def _save_json(filepath, data):
    """安全写入 JSON 文件"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _init_data():
    """初始化数据（如果文件不存在）"""
    if not os.path.exists(PAINTINGS_FILE):
        _save_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)
    if not os.path.exists(POETRY_FILE):
        _save_json(POETRY_FILE, DEFAULT_POETRY)


# ==================== 画作接口 ====================
@gallery_bp.route('/paintings', methods=['GET'])
def get_paintings():
    """获取画作列表（支持筛选和搜索）"""
    _init_data()
    paintings = _load_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)

    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '').strip().lower()
    sort_by = request.args.get('sort', 'year')

    if category:
        paintings = [p for p in paintings if p.get('category') == category]

    if keyword:
        paintings = [p for p in paintings if (
            keyword in p.get('title', '').lower() or
            keyword in p.get('artist', '').lower() or
            keyword in p.get('description', '').lower() or
            any(keyword in tag.lower() for tag in p.get('tags', []))
        )]

    if sort_by == 'year':
        paintings.sort(key=lambda p: p.get('year', 0))
    elif sort_by == 'title':
        paintings.sort(key=lambda p: p.get('title', ''))

    return jsonify({
        'code': 200,
        'data': paintings,
        'total': len(paintings),
        'categories': list(set(p.get('category', '') for p in DEFAULT_PAINTINGS))
    })


@gallery_bp.route('/paintings/<int:painting_id>', methods=['GET'])
def get_painting(painting_id):
    """获取单幅画作详情"""
    _init_data()
    paintings = _load_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)
    painting = next((p for p in paintings if p['id'] == painting_id), None)
    if not painting:
        return jsonify({'code': 404, 'message': '画作不存在'}), 404
    return jsonify({'code': 200, 'data': painting})


@gallery_bp.route('/paintings', methods=['POST'])
def create_painting():
    """新增画作"""
    _init_data()
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '缺少数据'}), 400

    paintings = _load_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)
    max_id = max((p['id'] for p in paintings), default=0)

    painting = {
        'id': max_id + 1,
        'title': data.get('title', ''),
        'artist': data.get('artist', ''),
        'year': data.get('year', 0),
        'category': data.get('category', '其他'),
        'image_url': data.get('image_url', ''),
        'description': data.get('description', ''),
        'tags': data.get('tags', []),
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    paintings.append(painting)
    _save_json(PAINTINGS_FILE, paintings)

    return jsonify({'code': 200, 'message': '添加成功', 'data': painting})


@gallery_bp.route('/paintings/<int:painting_id>', methods=['PUT'])
def update_painting(painting_id):
    """更新画作"""
    _init_data()
    data = request.get_json()
    paintings = _load_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)

    for p in paintings:
        if p['id'] == painting_id:
            p.update({k: v for k, v in data.items() if k != 'id'})
            _save_json(PAINTINGS_FILE, paintings)
            return jsonify({'code': 200, 'message': '更新成功', 'data': p})

    return jsonify({'code': 404, 'message': '画作不存在'}), 404


@gallery_bp.route('/paintings/<int:painting_id>', methods=['DELETE'])
def delete_painting(painting_id):
    """删除画作"""
    _init_data()
    paintings = _load_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)
    paintings = [p for p in paintings if p['id'] != painting_id]
    _save_json(PAINTINGS_FILE, paintings)
    return jsonify({'code': 200, 'message': '删除成功'})


# ==================== 诗集接口 ====================
@gallery_bp.route('/poetry', methods=['GET'])
def get_poetry():
    """获取诗集列表（支持筛选和搜索）"""
    _init_data()
    poetry_list = _load_json(POETRY_FILE, DEFAULT_POETRY)

    category = request.args.get('category', '')
    keyword = request.args.get('keyword', '').strip().lower()
    dynasty = request.args.get('dynasty', '')

    if category:
        poetry_list = [p for p in poetry_list if p.get('category') == category]
    if dynasty:
        poetry_list = [p for p in poetry_list if p.get('dynasty') == dynasty]
    if keyword:
        poetry_list = [p for p in poetry_list if (
            keyword in p.get('title', '').lower() or
            keyword in p.get('author', '').lower() or
            keyword in p.get('content', '').lower() or
            any(keyword in tag.lower() for tag in p.get('tags', []))
        )]

    return jsonify({
        'code': 200,
        'data': poetry_list,
        'total': len(poetry_list),
        'categories': list(set(p.get('category', '') for p in DEFAULT_POETRY)),
        'dynasties': list(set(p.get('dynasty', '') for p in DEFAULT_POETRY))
    })


@gallery_bp.route('/poetry/<int:poetry_id>', methods=['GET'])
def get_poetry_detail(poetry_id):
    """获取单首诗详情"""
    _init_data()
    poetry_list = _load_json(POETRY_FILE, DEFAULT_POETRY)
    poem = next((p for p in poetry_list if p['id'] == poetry_id), None)
    if not poem:
        return jsonify({'code': 404, 'message': '诗歌不存在'}), 404
    return jsonify({'code': 200, 'data': poem})


@gallery_bp.route('/poetry', methods=['POST'])
def create_poetry():
    """新增诗歌"""
    _init_data()
    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '缺少数据'}), 400

    poetry_list = _load_json(POETRY_FILE, DEFAULT_POETRY)
    max_id = max((p['id'] for p in poetry_list), default=0)

    poem = {
        'id': max_id + 1,
        'title': data.get('title', ''),
        'author': data.get('author', ''),
        'dynasty': data.get('dynasty', ''),
        'content': data.get('content', ''),
        'category': data.get('category', '其他'),
        'description': data.get('description', ''),
        'tags': data.get('tags', []),
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    poetry_list.append(poem)
    _save_json(POETRY_FILE, poetry_list)

    return jsonify({'code': 200, 'message': '添加成功', 'data': poem})


@gallery_bp.route('/poetry/<int:poetry_id>', methods=['PUT'])
def update_poetry(poetry_id):
    """更新诗歌"""
    _init_data()
    data = request.get_json()
    poetry_list = _load_json(POETRY_FILE, DEFAULT_POETRY)

    for p in poetry_list:
        if p['id'] == poetry_id:
            p.update({k: v for k, v in data.items() if k != 'id'})
            _save_json(POETRY_FILE, poetry_list)
            return jsonify({'code': 200, 'message': '更新成功', 'data': p})

    return jsonify({'code': 404, 'message': '诗歌不存在'}), 404


@gallery_bp.route('/poetry/<int:poetry_id>', methods=['DELETE'])
def delete_poetry(poetry_id):
    """删除诗歌"""
    _init_data()
    poetry_list = _load_json(POETRY_FILE, DEFAULT_POETRY)
    poetry_list = [p for p in poetry_list if p['id'] != poetry_id]
    _save_json(POETRY_FILE, poetry_list)
    return jsonify({'code': 200, 'message': '删除成功'})


# ==================== 统计接口 ====================
@gallery_bp.route('/stats', methods=['GET'])
def get_stats():
    """获取画廊统计数据"""
    _init_data()
    paintings = _load_json(PAINTINGS_FILE, DEFAULT_PAINTINGS)
    poetry_list = _load_json(POETRY_FILE, DEFAULT_POETRY)

    return jsonify({
        'code': 200,
        'data': {
            'paintings_total': len(paintings),
            'poetry_total': len(poetry_list),
            'painting_categories': dict(
                (c, len([p for p in paintings if p.get('category') == c]))
                for c in set(p.get('category', '') for p in paintings)
            ),
            'poetry_categories': dict(
                (c, len([p for p in poetry_list if p.get('category') == c]))
                for c in set(p.get('category', '') for p in poetry_list)
            )
        }
    })
