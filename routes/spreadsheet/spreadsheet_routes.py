# routes/spreadsheet/spreadsheet_routes.py
"""
在线表格路由
=============
提供在线表格的 CRUD 操作、数据编辑、样式设置等功能
"""
from flask import Blueprint, render_template, request, jsonify, session
import json
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db
from models.spreadsheet import (
    Spreadsheet, SpreadsheetColumn, 
    SpreadsheetRow, SpreadsheetCell, SpreadsheetHistory
)

spreadsheet_bp = Blueprint('spreadsheet', __name__, url_prefix='/spreadsheet')


# ============================================================================
# 页面路由 (已废弃，使用 Vue 页面)
# ============================================================================

# @spreadsheet_bp.route('/')
# def spreadsheet_list():
#     """表格列表页面"""
#     return render_template('spreadsheet/spreadsheet_list.html')


# @spreadsheet_bp.route('/<int:spreadsheet_id>')
# def spreadsheet_detail(spreadsheet_id):
#     """表格详情页面"""
#     return render_template('spreadsheet/spreadsheet_detail.html', spreadsheet_id=spreadsheet_id)


# ============================================================================
# API 路由 - 表格管理
# ============================================================================

@spreadsheet_bp.route('/api/create', methods=['POST'])
def create_spreadsheet():
    """创建新表格"""
    data = request.get_json()
    
    name = data.get('name', '未命名表格')
    description = data.get('description', '')
    created_by = data.get('created_by', session.get('user', 'anonymous'))
    columns = data.get('columns', [])
    
    try:
        # 创建表格
        spreadsheet = Spreadsheet(
            name=name,
            description=description,
            created_by=created_by,
            row_count=0,
            col_count=len(columns)
        )
        db.session.add(spreadsheet)
        db.session.flush()  # 获取 ID
        
        # 创建列定义
        for idx, col_data in enumerate(columns):
            column = SpreadsheetColumn(
                spreadsheet_id=spreadsheet.id,
                column_index=idx,
                column_name=col_data.get('name', f'列{idx+1}'),
                column_type=col_data.get('type', 'text'),
                width=col_data.get('width', 100),
                is_required=col_data.get('required', False),
                default_value=col_data.get('default_value'),
                options=json.dumps(col_data.get('options')) if col_data.get('options') else None,
                background_color=col_data.get('background_color'),
                text_color=col_data.get('text_color'),
                font_weight=col_data.get('font_weight', 'normal')
            )
            db.session.add(column)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': spreadsheet.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/list', methods=['GET'])
def list_spreadsheets():
    """获取表格列表"""
    try:
        spreadsheets = Spreadsheet.query.order_by(Spreadsheet.updated_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [s.to_dict() for s in spreadsheets]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/<int:spreadsheet_id>', methods=['GET'])
def get_spreadsheet(spreadsheet_id):
    """获取表格详情"""
    try:
        spreadsheet = Spreadsheet.query.get_or_404(spreadsheet_id)
        return jsonify({
            'success': True,
            'data': spreadsheet.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/<int:spreadsheet_id>', methods=['DELETE'])
def delete_spreadsheet(spreadsheet_id):
    """删除表格"""
    try:
        spreadsheet = Spreadsheet.query.get_or_404(spreadsheet_id)
        db.session.delete(spreadsheet)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# API 路由 - 列管理
# ============================================================================

@spreadsheet_bp.route('/api/<int:spreadsheet_id>/columns', methods=['GET'])
def get_columns(spreadsheet_id):
    """获取表格的列定义"""
    try:
        columns = SpreadsheetColumn.query.filter_by(
            spreadsheet_id=spreadsheet_id
        ).order_by(SpreadsheetColumn.column_index).all()
        
        return jsonify({
            'success': True,
            'data': [col.to_dict() for col in columns]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/<int:spreadsheet_id>/columns', methods=['POST'])
def add_column(spreadsheet_id):
    """添加列"""
    data = request.get_json()
    
    try:
        # 获取最大列索引
        max_index = db.session.query(
            db.func.max(SpreadsheetColumn.column_index)
        ).filter_by(spreadsheet_id=spreadsheet_id).scalar() or -1
        
        column = SpreadsheetColumn(
            spreadsheet_id=spreadsheet_id,
            column_index=max_index + 1,
            column_name=data.get('name', f'列{max_index + 2}'),
            column_type=data.get('type', 'text'),
            width=data.get('width', 100),
            is_required=data.get('required', False),
            default_value=data.get('default_value'),
            options=json.dumps(data.get('options')) if data.get('options') else None,
            background_color=data.get('background_color'),
            text_color=data.get('text_color'),
            font_weight=data.get('font_weight', 'normal')
        )
        db.session.add(column)
        
        # 更新表格的列数
        spreadsheet = Spreadsheet.query.get(spreadsheet_id)
        spreadsheet.col_count += 1
        spreadsheet.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': column.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/columns/<int:column_id>', methods=['PUT'])
def update_column(column_id):
    """更新列"""
    data = request.get_json()
    
    try:
        column = SpreadsheetColumn.query.get_or_404(column_id)
        
        if 'name' in data:
            column.column_name = data['name']
        if 'type' in data:
            column.column_type = data['type']
        if 'width' in data:
            column.width = data['width']
        if 'required' in data:
            column.is_required = data['required']
        if 'default_value' in data:
            column.default_value = data['default_value']
        if 'options' in data:
            column.options = json.dumps(data['options'])
        if 'background_color' in data:
            column.background_color = data['background_color']
        if 'text_color' in data:
            column.text_color = data['text_color']
        if 'font_weight' in data:
            column.font_weight = data['font_weight']
        
        column.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': column.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/columns/<int:column_id>', methods=['DELETE'])
def delete_column(column_id):
    """删除列"""
    try:
        column = SpreadsheetColumn.query.get_or_404(column_id)
        spreadsheet_id = column.spreadsheet_id
        
        # 删除关联的单元格数据
        rows = SpreadsheetRow.query.filter_by(spreadsheet_id=spreadsheet_id).all()
        for row in rows:
            cell = SpreadsheetCell.query.filter_by(
                row_id=row.id,
                column_id=column_id
            ).first()
            if cell:
                db.session.delete(cell)
        
        db.session.delete(column)
        
        # 更新表格的列数
        spreadsheet = Spreadsheet.query.get(spreadsheet_id)
        spreadsheet.col_count -= 1
        spreadsheet.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# API 路由 - 行管理
# ============================================================================

@spreadsheet_bp.route('/api/<int:spreadsheet_id>/rows', methods=['GET'])
def get_rows(spreadsheet_id):
    """获取表格的所有行（包含单元格数据）"""
    try:
        rows = SpreadsheetRow.query.filter_by(
            spreadsheet_id=spreadsheet_id
        ).order_by(SpreadsheetRow.row_index).all()
        
        rows_data = []
        for row in rows:
            cells = SpreadsheetCell.query.filter_by(row_id=row.id).all()
            row_dict = row.to_dict()
            row_dict['cells'] = [cell.to_dict() for cell in cells]
            rows_data.append(row_dict)
        
        return jsonify({
            'success': True,
            'data': rows_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/<int:spreadsheet_id>/rows', methods=['POST'])
def add_row(spreadsheet_id):
    """添加行"""
    data = request.get_json()
    
    try:
        # 获取最大行索引
        max_index = db.session.query(
            db.func.max(SpreadsheetRow.row_index)
        ).filter_by(spreadsheet_id=spreadsheet_id).scalar() or -1
        
        row = SpreadsheetRow(
            spreadsheet_id=spreadsheet_id,
            row_index=max_index + 1
        )
        db.session.add(row)
        db.session.flush()
        
        # 创建默认单元格
        columns = SpreadsheetColumn.query.filter_by(
            spreadsheet_id=spreadsheet_id
        ).all()
        
        for column in columns:
            cell = SpreadsheetCell(
                row_id=row.id,
                column_id=column.id,
                value=column.default_value,
                background_color=column.background_color,
                text_color=column.text_color,
                font_weight=column.font_weight
            )
            db.session.add(cell)
        
        # 更新表格的行数
        spreadsheet = Spreadsheet.query.get(spreadsheet_id)
        spreadsheet.row_count += 1
        spreadsheet.updated_at = datetime.now()
        
        # 记录操作历史
        history = SpreadsheetHistory(
            spreadsheet_id=spreadsheet_id,
            operation_type='add_row',
            operation_data=json.dumps({'row_id': row.id, 'row_index': max_index + 1}),
            operated_by=session.get('user', 'anonymous')
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': row.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/rows/<int:row_id>', methods=['DELETE'])
def delete_row(row_id):
    """删除行"""
    try:
        row = SpreadsheetRow.query.get_or_404(row_id)
        spreadsheet_id = row.spreadsheet_id
        
        # 删除关联的单元格
        cells = SpreadsheetCell.query.filter_by(row_id=row_id).all()
        for cell in cells:
            db.session.delete(cell)
        
        db.session.delete(row)
        
        # 更新表格的行数
        spreadsheet = Spreadsheet.query.get(spreadsheet_id)
        spreadsheet.row_count -= 1
        spreadsheet.updated_at = datetime.now()
        
        # 记录操作历史
        history = SpreadsheetHistory(
            spreadsheet_id=spreadsheet_id,
            operation_type='delete_row',
            operation_data=json.dumps({'row_id': row.id}),
            operated_by=session.get('user', 'anonymous')
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# API 路由 - 单元格管理
# ============================================================================

@spreadsheet_bp.route('/api/cells/<int:cell_id>', methods=['GET'])
def get_cell(cell_id):
    """获取单元格数据"""
    try:
        cell = SpreadsheetCell.query.get_or_404(cell_id)
        return jsonify({
            'success': True,
            'data': cell.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/cells/<int:cell_id>', methods=['PUT'])
def update_cell(cell_id):
    """更新单元格"""
    data = request.get_json()
    
    try:
        cell = SpreadsheetCell.query.get_or_404(cell_id)
        
        if 'value' in data:
            cell.value = data['value']
        if 'background_color' in data:
            cell.background_color = data['background_color']
        if 'text_color' in data:
            cell.text_color = data['text_color']
        if 'font_weight' in data:
            cell.font_weight = data['font_weight']
        if 'text_align' in data:
            cell.text_align = data['text_align']
        
        cell.updated_at = datetime.now()
        
        # 记录操作历史
        row = SpreadsheetRow.query.get(cell.row_id)
        history = SpreadsheetHistory(
            spreadsheet_id=row.spreadsheet_id,
            operation_type='update_cell',
            operation_data=json.dumps({
                'cell_id': cell_id,
                'value': data.get('value')
            }),
            operated_by=session.get('user', 'anonymous')
        )
        db.session.add(history)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': cell.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@spreadsheet_bp.route('/api/batch-update', methods=['POST'])
def batch_update_cells():
    """批量更新单元格"""
    data = request.get_json()
    
    try:
        updates = data.get('updates', [])
        results = []
        
        for update in updates:
            cell_id = update.get('cell_id')
            cell = SpreadsheetCell.query.get(cell_id)
            
            if cell:
                if 'value' in update:
                    cell.value = update['value']
                if 'background_color' in update:
                    cell.background_color = update['background_color']
                if 'text_color' in update:
                    cell.text_color = update['text_color']
                
                db.session.add(cell)
                results.append({
                    'cell_id': cell_id,
                    'success': True
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# API 路由 - 历史记录
# ============================================================================

@spreadsheet_bp.route('/api/<int:spreadsheet_id>/history', methods=['GET'])
def get_history(spreadsheet_id):
    """获取操作历史"""
    try:
        history = SpreadsheetHistory.query.filter_by(
            spreadsheet_id=spreadsheet_id
        ).order_by(SpreadsheetHistory.operated_at.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'data': [h.to_dict() for h in history]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================================
# API 路由 - 文件上传
# ============================================================================

@spreadsheet_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """上传图片文件"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件'
            }), 400
        
        # 检查文件类型
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        if not file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            return jsonify({
                'success': False,
                'message': '不支持的文件类型，请上传图片文件 (png, jpg, jpeg, gif, bmp, webp)'
            }), 400
        
        # 生成安全的文件名
        original_filename = secure_filename(file.filename)
        if not original_filename:
            original_filename = 'unnamed'
        
        # 创建唯一文件名
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'png'
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'spreadsheet')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # 生成访问 URL
        file_url = f'/uploads/spreadsheet/{filename}'
        
        return jsonify({
            'success': True,
            'data': {
                'url': file_url,
                'filename': original_filename,
                'size': os.path.getsize(filepath)
            },
            'message': '上传成功'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'上传失败：{str(e)}'
        }), 500


# ============================================================================
# API 路由 - 单元格管理
# ============================================================================

@spreadsheet_bp.route('/api/rows/<int:row_id>/cells', methods=['POST'])
def create_cell(row_id):
    """创建单元格"""
    data = request.get_json()
    
    try:
        column_id = data.get('columnId')
        value = data.get('value', '')
        
        if not column_id:
            return jsonify({
                'success': False,
                'message': '缺少列 ID'
            }), 400
        
        # 检查是否已存在
        existing_cell = SpreadsheetCell.query.filter_by(
            row_id=row_id,
            column_id=column_id
        ).first()
        
        if existing_cell:
            # 已存在则更新
            existing_cell.value = value
            db.session.add(existing_cell)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': existing_cell.to_dict()
            })
        
        # 创建新单元格
        cell = SpreadsheetCell(
            row_id=row_id,
            column_id=column_id,
            value=value
        )
        db.session.add(cell)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': cell.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
