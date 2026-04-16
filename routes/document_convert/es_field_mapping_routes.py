"""
ES 字段映射管理路由
提供字段映射的增删改查功能
"""
import mysql.connector
from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
es_field_mapping_bp = Blueprint('es_field_mapping', __name__, url_prefix='/api/es-field-mapping')


def get_db_connection():
    """获取数据库连接"""
    return mysql.connector.connect(
        host=current_app.config['MYSQL_HOST'],
        port=current_app.config['MYSQL_PORT'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        charset=current_app.config['MYSQL_CHARSET'],
        database=current_app.config['KNOWLEDGE_BASE_DB']
    )


@es_field_mapping_bp.route('/list', methods=['GET'])
def get_mapping_list():
    """获取所有字段映射列表（支持分页和搜索）"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        search = request.args.get('search', '', type=str)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询条件
        where_clause = "WHERE is_active = TRUE"
        params = []
        
        if search:
            where_clause += " AND (english_name LIKE %s OR chinese_name LIKE %s)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM es_field_mapping {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据（分页）
        offset = (page - 1) * page_size
        data_sql = f"""
            SELECT id, english_name, chinese_name, description, is_active, sort_order, 
                   created_at, updated_at
            FROM es_field_mapping 
            {where_clause}
            ORDER BY sort_order ASC, id ASC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        cursor.execute(data_sql, params)
        mappings = cursor.fetchall()
        
        # 转换 datetime 为字符串
        for item in mappings:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            if item.get('updated_at'):
                item['updated_at'] = item['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': mappings,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
        
    except Exception as e:
        logger.error(f"获取字段映射列表失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@es_field_mapping_bp.route('/all', methods=['GET'])
def get_all_mappings():
    """获取所有启用的字段映射（用于前端下拉选择等）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT english_name, chinese_name 
            FROM es_field_mapping 
            WHERE is_active = TRUE
            ORDER BY sort_order ASC, id ASC
        """)
        mappings = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 转换为字典格式 {english: chinese}
        mapping_dict = {item['english_name']: item['chinese_name'] for item in mappings}
        
        return jsonify({
            'success': True,
            'data': mapping_dict,
            'count': len(mappings)
        })
        
    except Exception as e:
        logger.error(f"获取所有字段映射失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@es_field_mapping_bp.route('/add', methods=['POST'])
def add_mapping():
    """添加新的字段映射"""
    try:
        data = request.get_json()
        english_name = data.get('english_name', '').strip()
        chinese_name = data.get('chinese_name', '').strip()
        description = data.get('description', '').strip()
        sort_order = data.get('sort_order', 0)
        
        if not english_name or not chinese_name:
            return jsonify({'success': False, 'message': '英文字段名和中文字段名不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_sql = """
            INSERT INTO es_field_mapping (english_name, chinese_name, description, sort_order)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (english_name, chinese_name, description, sort_order))
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        logger.info(f"新增字段映射: {english_name} -> {chinese_name}")
        
        return jsonify({
            'success': True,
            'message': '添加成功',
            'id': new_id
        })
        
    except mysql.connector.IntegrityError:
        return jsonify({'success': False, 'message': '该英文字段名已存在'}), 400
    except Exception as e:
        logger.error(f"添加字段映射失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@es_field_mapping_bp.route('/update/<int:mapping_id>', methods=['PUT'])
def update_mapping(mapping_id):
    """更新字段映射"""
    try:
        data = request.get_json()
        chinese_name = data.get('chinese_name', '').strip()
        description = data.get('description', '').strip()
        sort_order = data.get('sort_order')
        is_active = data.get('is_active')
        
        if not chinese_name:
            return jsonify({'success': False, 'message': '中文字段名不能为空'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 构建更新语句
        update_fields = []
        params = []
        
        update_fields.append("chinese_name = %s")
        params.append(chinese_name)
        
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        
        if sort_order is not None:
            update_fields.append("sort_order = %s")
            params.append(sort_order)
        
        if is_active is not None:
            update_fields.append("is_active = %s")
            params.append(is_active)
        
        params.append(mapping_id)
        
        update_sql = f"UPDATE es_field_mapping SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(update_sql, params)
        conn.commit()
        
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        
        if affected_rows == 0:
            return jsonify({'success': False, 'message': '记录不存在'}), 404
        
        logger.info(f"更新字段映射 ID: {mapping_id}")
        
        return jsonify({
            'success': True,
            'message': '更新成功'
        })
        
    except Exception as e:
        logger.error(f"更新字段映射失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@es_field_mapping_bp.route('/delete/<int:mapping_id>', methods=['DELETE'])
def delete_mapping(mapping_id):
    """删除字段映射（软删除，设置为非激活状态）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE es_field_mapping SET is_active = FALSE WHERE id = %s",
            (mapping_id,)
        )
        conn.commit()
        
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        
        if affected_rows == 0:
            return jsonify({'success': False, 'message': '记录不存在'}), 404
        
        logger.info(f"删除字段映射 ID: {mapping_id}")
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除字段映射失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500


@es_field_mapping_bp.route('/batch-import', methods=['POST'])
def batch_import():
    """批量导入字段映射（从 CSV 或 JSON）"""
    try:
        data = request.get_json()
        mappings = data.get('mappings', [])
        
        if not mappings:
            return jsonify({'success': False, 'message': '没有提供映射数据'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_sql = """
            INSERT INTO es_field_mapping (english_name, chinese_name, description, sort_order)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                chinese_name = VALUES(chinese_name),
                description = VALUES(description),
                updated_at = CURRENT_TIMESTAMP
        """
        
        values = []
        for i, item in enumerate(mappings):
            english_name = item.get('english_name', '').strip()
            chinese_name = item.get('chinese_name', '').strip()
            description = item.get('description', '').strip()
            sort_order = item.get('sort_order', i)
            
            if english_name and chinese_name:
                values.append((english_name, chinese_name, description, sort_order))
        
        if values:
            cursor.executemany(insert_sql, values)
            conn.commit()
        
        cursor.close()
        conn.close()
        
        logger.info(f"批量导入 {len(values)} 条字段映射")
        
        return jsonify({
            'success': True,
            'message': f'成功导入 {len(values)} 条映射',
            'count': len(values)
        })
        
    except Exception as e:
        logger.error(f"批量导入失败: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500
