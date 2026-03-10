#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专业领域管理路由
提供专业领域的增删改查功能
"""
from flask import Blueprint, request, jsonify, render_template
from models.knowledge_base import knowledge_base_manager

category_bp = Blueprint('category', __name__, url_prefix='/api/category')


@category_bp.route('/list', methods=['GET'])
def list_categories():
    """获取所有专业领域列表"""
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        categories = knowledge_base_manager.list_categories(active_only=active_only)
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@category_bp.route('/add', methods=['POST'])
def add_category():
    """添加专业领域"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        color = data.get('color', '#1890ff')
        
        if not name:
            return jsonify({
                'success': False,
                'error': '领域名称不能为空'
            }), 400
        
        # 检查是否已存在
        existing = knowledge_base_manager.list_categories(active_only=False)
        for cat in existing:
            if cat['name'].lower() == name.lower():
                return jsonify({
                    'success': False,
                    'error': f'领域 "{name}" 已存在'
                }), 400
        
        category_id = knowledge_base_manager.add_category(name, description, color)
        
        if category_id > 0:
            return jsonify({
                'success': True,
                'message': '添加成功',
                'category_id': category_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '添加失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@category_bp.route('/update', methods=['POST'])
def update_category():
    """更新专业领域"""
    try:
        data = request.get_json()
        category_id = data.get('id')
        name = data.get('name')
        description = data.get('description')
        color = data.get('color')
        is_active = data.get('is_active')
        
        if not category_id:
            return jsonify({
                'success': False,
                'error': '领域 ID 不能为空'
            }), 400
        
        success = knowledge_base_manager.update_category(
            category_id, 
            name=name,
            description=description,
            color=color,
            is_active=is_active
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '更新失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@category_bp.route('/delete', methods=['POST'])
def delete_category():
    """删除专业领域（软删除）"""
    try:
        data = request.get_json()
        category_id = data.get('id')
        
        if not category_id:
            return jsonify({
                'success': False,
                'error': '领域 ID 不能为空'
            }), 400
        
        success = knowledge_base_manager.delete_category(category_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '删除失败'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@category_bp.route('/page')
def category_management_page():
    """专业领域管理页面"""
    return render_template('category_management.html')
