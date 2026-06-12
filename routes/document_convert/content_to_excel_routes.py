#!/usr/bin/env python3
"""
内容转 Excel 工具 - Flask 路由模块
========================================
提供文件上传、解析、Excel生成和关键字库管理的API接口。

路由列表:
  POST /api/content-to-excel/generate     - 上传文件并生成Excel
  GET  /api/content-to-excel/software-ip-list   - 获取软件-IP映射列表
  POST /api/content-to-excel/software-ip        - 新增软件-IP映射
  PUT  /api/content-to-excel/software-ip/<id>   - 更新软件-IP映射
  DELETE /api/content-to-excel/software-ip/<id> - 删除软件-IP映射
  GET  /api/content-to-excel/initial-version-list - 获取初始版本号列表
  POST /api/content-to-excel/initial-version    - 新增初始版本号
  PUT  /api/content-to-excel/initial-version/<id> - 更新初始版本号
  DELETE /api/content-to-excel/initial-version/<id> - 删除初始版本号

作者: Claude Code
日期: 2026-05-29
"""

from flask import (
    Blueprint,
    request,
    jsonify,
    send_file,
)
import os
import uuid
import pymysql
from werkzeug.utils import secure_filename

from routes.document_convert.content_to_excel import (
    generate_excel,
    parse_upgrade_records,
    match_softwares,
    calculate_standard_version,
    BUILTIN_SOFTWARE_MAP,
    BUILTIN_INITIAL_VERSIONS,
)


def _get_db_config():
    """从 Flask 配置中获取数据库连接参数"""
    from flask import current_app
    return {
        'host': current_app.config.get('MYSQL_HOST', 'localhost'),
        'port': current_app.config.get('MYSQL_PORT', 3306),
        'user': current_app.config.get('MYSQL_USER', 'root'),
        'password': current_app.config.get('MYSQL_PASSWORD', '12345678'),
        'charset': current_app.config.get('MYSQL_CHARSET', 'utf8mb4'),
    }


def _get_db_connection(database=None):
    """获取 MySQL 数据库连接"""
    config = _get_db_config()
    if database:
        from flask import current_app
        config['database'] = current_app.config.get(database, 'schedule_system')
    else:
        from flask import current_app
        config['database'] = current_app.config.get('KNOWLEDGE_BASE_DB', 'knowledge_base')
    return pymysql.connect(**config)


def _ensure_tables(app):
    """确保数据库表存在（首次使用时自动创建）"""
    with app.app_context():
        try:
            conn = _get_db_connection()
            cursor = conn.cursor()

            # 软件-IP映射表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_to_excel_software_ip (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    software_name VARCHAR(255) NOT NULL UNIQUE COMMENT '软件名称',
                    target_ip VARCHAR(255) DEFAULT '' COMMENT '目标IP',
                    operator VARCHAR(100) DEFAULT '' COMMENT '操作员',
                    verifier VARCHAR(100) DEFAULT '' COMMENT '验证员',
                    initial_version VARCHAR(100) DEFAULT '' COMMENT '初始版本号',
                    is_builtin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否内置软件：1=内置不可删除，0=外部配置可删除',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_software_name (software_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容转Excel-软件IP映射表'
            """)

            # 初始版本号表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS content_to_excel_initial_version (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    software_name VARCHAR(255) NOT NULL UNIQUE COMMENT '软件名称',
                    initial_version VARCHAR(100) DEFAULT '' COMMENT '初始版本号',
                    is_builtin TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否内置软件：1=内置不可删除，0=外部配置可删除',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_software_name (software_name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='内容转Excel-初始版本号表'
            """)

            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"⚠️ 创建数据库表失败（不影响其他功能）: {e}")


# ============================================================================
# 蓝图定义
# ============================================================================

content_to_excel_bp = Blueprint(
    'content_to_excel',
    __name__,
    url_prefix='/api/content-to-excel',
)


def init_content_to_excel(app):
    """初始化内容转Excel模块（在 Flask app 创建后调用）"""
    _ensure_tables(app)


# ============================================================================
# 数据库辅助函数：软件-IP映射
# ============================================================================

def _get_software_ip_from_db() -> dict:
    """从数据库获取软件-IP映射列表（回退到内置）"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT software_name, target_ip, operator, verifier, initial_version
            FROM content_to_excel_software_ip
            ORDER BY software_name ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if rows:
            return {row['software_name']: row for row in rows}
    except Exception as e:
        print(f"⚠️ 从数据库获取软件-IP映射失败: {e}")

    # 回退到内置映射
    return None


def _get_initial_version_from_db() -> dict:
    """从数据库获取初始版本号（回退到内置）"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            SELECT software_name, initial_version
            FROM content_to_excel_initial_version
            ORDER BY software_name ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if rows:
            return {row['software_name']: row['initial_version'] for row in rows}
    except Exception as e:
        print(f"⚠️ 从数据库获取初始版本号失败: {e}")

    # 回退到内置
    return None


def _is_valid_file(filename: str) -> bool:
    """校验上传文件类型是否为 .md 或 .txt"""
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in ('.md', '.txt')


def _get_software_ip_store() -> dict:
    """获取软件-IP映射关键字库（优先使用数据库，回退到内置）"""
    db_store = _get_software_ip_from_db()
    return db_store if db_store else None


def _get_initial_version_store() -> dict:
    """获取初始版本号关键字库（优先使用数据库，回退到内置）"""
    db_store = _get_initial_version_from_db()
    return db_store if db_store else None


# ============================================================================
# API: 生成Excel（核心接口）
# ============================================================================

@content_to_excel_bp.route('/generate', methods=['POST'])
def generate():
    """
    上传 .md/.txt 文件并生成Excel表格。

    请求:
        multipart/form-data
          - file: 上传的文件（.md 或 .txt）

    响应:
        {
            "success": true,
            "file_path": "/path/to/generated.xlsx",
            "records_count": 6,
            "software_count": 2,
            "message": "Excel文件生成成功"
        }
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': '未找到上传文件',
        }), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({
            'success': False,
            'message': '未选择文件',
        }), 400

    # 校验文件类型
    if not _is_valid_file(file.filename):
        return jsonify({
            'success': False,
            'message': '仅支持 .md 或 .txt 格式的文件',
        }), 400

    # 读取文件内容
    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = file.read().decode('gbk')
        except UnicodeDecodeError:
            return jsonify({
                'success': False,
                'message': '文件编码不支持，请使用 UTF-8 或 GBK 编码',
            }), 400

    # 解析升级记录（用于返回预览信息）
    try:
        records = parse_upgrade_records(content)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'解析失败: {str(e)}',
        }), 400

    if not records:
        return jsonify({
            'success': False,
            'message': '未解析到任何升级申请记录，请检查文件格式是否符合规范。',
        }), 400

    # 生成Excel文件
    try:
        software_ip_map = _get_software_ip_store()
        output_file = generate_excel(
            content=content,
            software_ip_map=software_ip_map,
        )

        # 统计涉及的软件数量
        all_softwares = set()
        for record in records:
            softwares = match_softwares(record, software_ip_map)
            all_softwares.update(softwares)

        return jsonify({
            'success': True,
            'file_path': output_file,
            'records_count': len(records),
            'software_count': len(all_softwares),
            'message': f'Excel文件生成成功，包含 {len(records)} 条升级记录，涉及 {len(all_softwares)} 个软件',
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'生成失败: {str(e)}',
        }), 500


# ============================================================================
# API: 预览解析结果（不生成Excel，仅返回解析信息）
# ============================================================================

@content_to_excel_bp.route('/preview', methods=['POST'])
def preview():
    """
    预览文件解析结果（不生成Excel）。

    请求:
        multipart/form-data
          - file: 上传的文件（.md 或 .txt）

    响应:
        {
            "success": true,
            "records": [
                {
                    "year": 2026,
                    "month": 3,
                    "day": 11,
                    "date_str": "2026/3/11",
                    "type_desc": "功能升级",
                    "title": "监控综合应用平台2026年3月11日功能升级申请",
                    "matched_softwares": ["智能调服务"]
                }
            ]
        }
    """
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'message': '未找到上传文件',
        }), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({
            'success': False,
            'message': '未选择文件',
        }), 400

    if not _is_valid_file(file.filename):
        return jsonify({
            'success': False,
            'message': '仅支持 .md 或 .txt 格式的文件',
        }), 400

    try:
        content = file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            content = file.read().decode('gbk')
        except UnicodeDecodeError:
            return jsonify({
                'success': False,
                'message': '文件编码不支持',
            }), 400

    try:
        records = parse_upgrade_records(content)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'解析失败: {str(e)}',
        }), 400

    if not records:
        return jsonify({
            'success': False,
            'message': '未解析到任何升级申请记录',
        }), 400

    software_ip_map = _get_software_ip_store()

    # 为每条记录匹配软件
    for record in records:
        matched = match_softwares(record, software_ip_map)
        record['matched_softwares'] = matched

    return jsonify({
        'success': True,
        'records': records,
    })


# ============================================================================
# API: 下载生成的 Excel 文件
# ============================================================================

@content_to_excel_bp.route('/download/<path:filename>', methods=['GET'])
def download_file(filename: str):
    """
    下载已生成的 Excel 文件。

    参数:
        filename: 文件名，如 content_to_excel_666f100e.xlsx

    响应:
        文件下载流（application/vnd.openxmlformats-officedocument.spreadsheetml.sheet）
    """
    uploads_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'uploads', 'content_to_excel'
    )
    uploads_dir = os.path.normpath(os.path.join(uploads_dir))

    # 安全校验：防止路径遍历攻击
    filepath = os.path.normpath(os.path.join(uploads_dir, filename))
    if not filepath.startswith(uploads_dir):
        return jsonify({
            'success': False,
            'message': '非法文件路径',
        }), 403

    if not os.path.isfile(filepath):
        return jsonify({
            'success': False,
            'message': f'文件不存在: {filename}',
        }), 404

    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


# ============================================================================
# API: 软件-IP映射管理（增删改查 - MySQL持久化）
# ============================================================================

@content_to_excel_bp.route('/software-ip-list', methods=['GET'])
def get_software_ip_list():
    """获取软件-IP映射列表（优先返回数据库配置，回退到内置）"""
    db_store = _get_software_ip_from_db()

    if db_store:
        result = []
        for name, info in db_store.items():
            initial_ver = info.get('initial_version', '') or BUILTIN_INITIAL_VERSIONS.get(name, '')
            result.append({
                'id': name,
                'software_name': name,
                'target_ip': info.get('target_ip', ''),
                'operator': info.get('operator', ''),
                'verifier': info.get('verifier', ''),
                'initial_version': initial_ver,
            })
        return jsonify({'success': True, 'data': result})

    # 回退到内置映射
    result = []
    for name, info in BUILTIN_SOFTWARE_MAP.items():
        initial_ver = BUILTIN_INITIAL_VERSIONS.get(name, '')
        result.append({
            'id': name,
            'software_name': name,
            'target_ip': info.get('target_ip', ''),
            'operator': info.get('operator', ''),
            'verifier': info.get('verifier', ''),
            'initial_version': initial_ver,
        })

    return jsonify({'success': True, 'data': result})


@content_to_excel_bp.route('/software-ip', methods=['POST'])
def add_software_ip():
    """新增软件-IP映射（MySQL持久化）"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    software_name = data.get('software_name', '').strip()
    if not software_name:
        return jsonify({'success': False, 'message': '软件名称不能为空'}), 400

    target_ip = data.get('target_ip', '')
    operator = data.get('operator', '')
    verifier = data.get('verifier', '')
    initial_version = data.get('initial_version', '')

    # 判断是否为内置软件（is_builtin=1）
    is_builtin = 0
    if software_name in BUILTIN_SOFTWARE_MAP:
        is_builtin = 1

    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # 使用 INSERT ... ON DUPLICATE KEY UPDATE 实现 upsert
        cursor.execute("""
            INSERT INTO content_to_excel_software_ip
                (software_name, target_ip, operator, verifier, initial_version, is_builtin)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                target_ip = VALUES(target_ip),
                operator = VALUES(operator),
                verifier = VALUES(verifier),
                initial_version = VALUES(initial_version),
                is_builtin = VALUES(is_builtin)
        """, (software_name, target_ip, operator, verifier, initial_version, is_builtin))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'软件 [{software_name}] 添加成功',
    })


@content_to_excel_bp.route('/software-ip/<software_name>', methods=['PUT'])
def update_software_ip(software_name: str):
    """更新软件-IP映射（MySQL持久化）"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    target_ip = data.get('target_ip', '')
    operator = data.get('operator', '')
    verifier = data.get('verifier', '')
    initial_version = data.get('initial_version', '')

    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # 检查是否存在
        cursor.execute(
            "SELECT id FROM content_to_excel_software_ip WHERE software_name = %s",
            (software_name,)
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': f'软件 [{software_name}] 不存在'}), 404

        # 检查是否为内置软件（不可删除，但可更新）
        cursor.execute(
            "SELECT is_builtin FROM content_to_excel_software_ip WHERE software_name = %s",
            (software_name,)
        )
        is_builtin_row = cursor.fetchone()

        # 更新数据（内置软件也可以更新，只是不可删除）
        cursor.execute("""
            UPDATE content_to_excel_software_ip
            SET target_ip = %s, operator = %s, verifier = %s, initial_version = %s
            WHERE software_name = %s
        """, (target_ip, operator, verifier, initial_version, software_name))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'软件 [{software_name}] 更新成功',
    })


@content_to_excel_bp.route('/software-ip/<software_name>', methods=['DELETE'])
def delete_software_ip(software_name: str):
    """删除软件-IP映射（仅允许删除外部配置的，内置的不可删除）"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # 检查是否存在
        cursor.execute(
            "SELECT id, is_builtin FROM content_to_excel_software_ip WHERE software_name = %s",
            (software_name,)
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': f'软件 [{software_name}] 不存在'}), 404

        # 内置软件不可删除
        if row[1] == 1:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': f'内置软件 [{software_name}] 不可删除，可修改其配置',
            }), 403

        # 删除记录
        cursor.execute(
            "DELETE FROM content_to_excel_software_ip WHERE software_name = %s",
            (software_name,)
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'软件 [{software_name}] 已删除',
    })


# ============================================================================
# API: 初始版本号管理（增删改查 - MySQL持久化）
# ============================================================================

@content_to_excel_bp.route('/initial-version-list', methods=['GET'])
def get_initial_version_list():
    """获取初始版本号列表（优先返回数据库配置，回退到内置）"""
    db_store = _get_initial_version_from_db()

    if db_store:
        result = []
        for name, version in db_store.items():
            result.append({
                'id': name,
                'software_name': name,
                'initial_version': version,
            })
        return jsonify({'success': True, 'data': result})

    # 回退到内置映射
    result = []
    for name, version in BUILTIN_INITIAL_VERSIONS.items():
        result.append({
            'id': name,
            'software_name': name,
            'initial_version': version,
        })

    return jsonify({'success': True, 'data': result})


@content_to_excel_bp.route('/initial-version', methods=['POST'])
def add_initial_version():
    """新增初始版本号（MySQL持久化）"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    software_name = data.get('software_name', '').strip()
    initial_version = data.get('initial_version', '').strip()

    if not software_name or not initial_version:
        return jsonify({
            'success': False,
            'message': '软件名称和版本号均不能为空',
        }), 400

    # 检查软件是否在软件-IP映射中存在
    if software_name not in BUILTIN_SOFTWARE_MAP:
        ip_store = _get_software_ip_from_db()
        if not ip_store or software_name not in ip_store:
            return jsonify({
                'success': False,
                'message': f'软件 [{software_name}] 不在软件-IP映射中，请先添加',
            }), 400

    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # 判断是否为内置软件
        is_builtin = 1 if software_name in BUILTIN_SOFTWARE_MAP else 0

        # upsert
        cursor.execute("""
            INSERT INTO content_to_excel_initial_version
                (software_name, initial_version, is_builtin)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                initial_version = VALUES(initial_version),
                is_builtin = VALUES(is_builtin)
        """, (software_name, initial_version, is_builtin))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'软件 [{software_name}] 初始版本号设置为 {initial_version}',
    })


@content_to_excel_bp.route('/initial-version/<software_name>', methods=['PUT'])
def update_initial_version(software_name: str):
    """更新初始版本号（MySQL持久化）"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '请求体不能为空'}), 400

    initial_version = data.get('initial_version', '').strip()
    if not initial_version:
        return jsonify({'success': False, 'message': '版本号不能为空'}), 400

    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # 检查是否存在
        cursor.execute(
            "SELECT id FROM content_to_excel_initial_version WHERE software_name = %s",
            (software_name,)
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': f'软件 [{software_name}] 不存在'}), 404

        # 更新数据
        cursor.execute("""
            UPDATE content_to_excel_initial_version
            SET initial_version = %s
            WHERE software_name = %s
        """, (initial_version, software_name))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'软件 [{software_name}] 初始版本号更新为 {initial_version}',
    })


@content_to_excel_bp.route('/initial-version/<software_name>', methods=['DELETE'])
def delete_initial_version(software_name: str):
    """删除初始版本号（仅允许删除外部配置的，内置的不可删除）"""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()

        # 检查是否存在
        cursor.execute(
            "SELECT id, is_builtin FROM content_to_excel_initial_version WHERE software_name = %s",
            (software_name,)
        )
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'message': f'软件 [{software_name}] 不存在'}), 404

        # 内置软件不可删除
        if row[1] == 1:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': f'内置软件 [{software_name}] 不可删除，可修改其配置',
            }), 403

        # 删除记录
        cursor.execute(
            "DELETE FROM content_to_excel_initial_version WHERE software_name = %s",
            (software_name,)
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': f'软件 [{software_name}] 初始版本号已删除',
    })


# ============================================================================
# API: 获取内置软件列表（只读，供前端展示）
# ============================================================================

@content_to_excel_bp.route('/builtin-software-list', methods=['GET'])
def get_builtin_software_list():
    """获取内置软件列表（只读，供前端展示参考）"""
    result = []
    for name in sorted(set(list(BUILTIN_SOFTWARE_MAP.keys()) + list(BUILTIN_INITIAL_VERSIONS.keys()))):
        info = BUILTIN_SOFTWARE_MAP.get(name, {})
        initial_ver = BUILTIN_INITIAL_VERSIONS.get(name, '')
        result.append({
            'software_name': name,
            'target_ip': info.get('target_ip', ''),
            'operator': info.get('operator', ''),
            'verifier': info.get('verifier', ''),
            'initial_version': initial_ver,
        })

    return jsonify({'success': True, 'data': result})
