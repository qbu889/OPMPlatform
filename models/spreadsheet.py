# models/spreadsheet.py
"""
在线表格数据模型
=================
支持存储和管理电子表格数据
"""
from datetime import datetime
from models import db


class Spreadsheet(db.Model):
    """表格定义表"""
    __tablename__ = 'spreadsheet'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, comment='表格名称')
    description = db.Column(db.String(500), comment='表格描述')
    created_by = db.Column(db.String(100), comment='创建人')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_template = db.Column(db.Boolean, default=False, comment='是否为模板')
    
    # 元数据
    row_count = db.Column(db.Integer, default=0, comment='总行数')
    col_count = db.Column(db.Integer, default=0, comment='总列数')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'row_count': self.row_count,
            'col_count': self.col_count
        }


class SpreadsheetColumn(db.Model):
    """表格列定义表"""
    __tablename__ = 'spreadsheet_column'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spreadsheet_id = db.Column(db.Integer, db.ForeignKey('spreadsheet.id'), nullable=False, comment='表格 ID')
    column_index = db.Column(db.Integer, nullable=False, comment='列索引 (从 0 开始)')
    column_name = db.Column(db.String(100), nullable=False, comment='列名')
    column_type = db.Column(db.String(50), default='text', comment='列类型：text, number, date, select')
    width = db.Column(db.Integer, default=100, comment='列宽 (像素)')
    is_required = db.Column(db.Boolean, default=False, comment='是否必填')
    default_value = db.Column(db.String(500), comment='默认值')
    options = db.Column(db.Text, comment='选项值 (JSON 格式，用于 select 类型)')
    
    # 样式配置
    background_color = db.Column(db.String(20), comment='背景色')
    text_color = db.Column(db.String(20), comment='文字颜色')
    font_weight = db.Column(db.String(20), default='normal', comment='字体粗细')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'spreadsheet_id': self.spreadsheet_id,
            'column_index': self.column_index,
            'column_name': self.column_name,
            'column_type': self.column_type,
            'width': self.width,
            'is_required': self.is_required,
            'default_value': self.default_value,
            'options': json.loads(self.options) if self.options else None,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'font_weight': self.font_weight
        }


class SpreadsheetRow(db.Model):
    """表格行数据表"""
    __tablename__ = 'spreadsheet_row'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spreadsheet_id = db.Column(db.Integer, db.ForeignKey('spreadsheet.id'), nullable=False, comment='表格 ID')
    row_index = db.Column(db.Integer, nullable=False, comment='行索引 (从 0 开始)')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        return {
            'id': self.id,
            'spreadsheet_id': self.spreadsheet_id,
            'row_index': self.row_index,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }


class SpreadsheetCell(db.Model):
    """单元格数据表"""
    __tablename__ = 'spreadsheet_cell'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    row_id = db.Column(db.Integer, db.ForeignKey('spreadsheet_row.id'), nullable=False, comment='行 ID')
    column_id = db.Column(db.Integer, db.ForeignKey('spreadsheet_column.id'), nullable=False, comment='列 ID')
    value = db.Column(db.Text, comment='单元格值')
    
    # 单元格样式（可覆盖列样式）
    background_color = db.Column(db.String(20), comment='背景色')
    text_color = db.Column(db.String(20), comment='文字颜色')
    font_weight = db.Column(db.String(20), comment='字体粗细')
    text_align = db.Column(db.String(20), default='left', comment='对齐方式')
    
    # 数据验证
    is_validated = db.Column(db.Boolean, default=True, comment='是否通过验证')
    validation_message = db.Column(db.String(500), comment='验证提示信息')
    
    __table_args__ = (
        db.UniqueConstraint('row_id', 'column_id', name='unique_row_column'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'row_id': self.row_id,
            'column_id': self.column_id,
            'value': self.value,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'font_weight': self.font_weight,
            'text_align': self.text_align,
            'is_validated': self.is_validated,
            'validation_message': self.validation_message
        }


class SpreadsheetHistory(db.Model):
    """表格操作历史表"""
    __tablename__ = 'spreadsheet_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spreadsheet_id = db.Column(db.Integer, db.ForeignKey('spreadsheet.id'), nullable=False, comment='表格 ID')
    operation_type = db.Column(db.String(50), nullable=False, comment='操作类型：add_row, delete_row, update_cell, etc.')
    operation_data = db.Column(db.Text, comment='操作数据 (JSON 格式)')
    operated_by = db.Column(db.String(100), comment='操作人')
    operated_at = db.Column(db.DateTime, default=datetime.now, comment='操作时间')
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'spreadsheet_id': self.spreadsheet_id,
            'operation_type': self.operation_type,
            'operation_data': json.loads(self.operation_data) if self.operation_data else None,
            'operated_by': self.operated_by,
            'operated_at': self.operated_at.strftime('%Y-%m-%d %H:%M:%S') if self.operated_at else None
        }
