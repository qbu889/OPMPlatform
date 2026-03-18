# routes/fpa_category_rules_routes.py
"""
FPA 类别判断规则管理路由
"""
from flask import Blueprint, render_template, request, jsonify
from models.fpa_category_rules import FPACategoryRule, db
from sqlalchemy import or_

fpa_rules_bp = Blueprint('fpa_rules', __name__, url_prefix='/fpa-rules')

@fpa_rules_bp.route('/management')
def rules_management_page():
    """规则管理页面"""
    return render_template('fpa_category_rules.html')

@fpa_rules_bp.route('/api/rules')
def get_rules():
    """获取所有规则（支持筛选和分页）"""
    try:
        from flask import current_app
        # 获取查询参数
        category = request.args.get('category', None)
        is_active = request.args.get('is_active', None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        current_app.logger.info(f"查询参数：category={category}, is_active={is_active}, page={page}, per_page={per_page}")
        
        # 构建查询
        query = FPACategoryRule.query
        
        if category:
            query = query.filter_by(category=category)
        
        if is_active is not None and is_active != '':
            is_active_bool = is_active.lower() == 'true'
            query = query.filter_by(is_active=is_active_bool)
        
        # 按优先级和 ID 排序
        query = query.order_by(FPACategoryRule.priority.asc(), FPACategoryRule.id.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        rules = pagination.items
        
        current_app.logger.info(f"查询结果：total={pagination.total}, rules_count={len(rules)}")
        
        # 转换为字典列表
        result = {
            'rules': [rule.to_dict() for rule in rules],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"查询失败：{str(e)}")
        return jsonify({'error': str(e)}), 500

@fpa_rules_bp.route('/api/rules/<int:rule_id>', methods=['GET'])
def get_rule(rule_id):
    """获取单个规则详情"""
    try:
        rule = FPACategoryRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': '规则不存在'}), 404
        
        return jsonify(rule.to_dict())
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fpa_rules_bp.route('/api/rules', methods=['POST'])
def create_rule():
    """创建新规则"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['category', 'priority', 'rule_type', 'keyword', 'ufp_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段：{field}'}), 400
        
        # 验证类别
        valid_categories = ['EI', 'EO', 'EQ', 'ILF', 'EIF']
        if data['category'] not in valid_categories:
            return jsonify({'error': f'无效的类别，必须是：{", ".join(valid_categories)}'}), 400
        
        # 验证规则类型
        valid_rule_types = ['endswith', 'contains', 'startswith', 'special']
        if data['rule_type'] not in valid_rule_types:
            return jsonify({'error': f'无效的规则类型，必须是：{", ".join(valid_rule_types)}'}), 400
        
        # 创建规则
        rule = FPACategoryRule(
            category=data['category'],
            priority=data['priority'],
            rule_type=data['rule_type'],
            keyword=data['keyword'],
            description=data.get('description', ''),
            ufp_value=data['ufp_value'],
            is_active=data.get('is_active', True)
        )
        
        db.session.add(rule)
        db.session.commit()
        
        return jsonify({
            'message': '规则创建成功',
            'rule': rule.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fpa_rules_bp.route('/api/rules/<int:rule_id>', methods=['PUT'])
def update_rule(rule_id):
    """更新规则"""
    try:
        rule = FPACategoryRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': '规则不存在'}), 404
        
        data = request.get_json()
        
        # 更新字段
        if 'category' in data:
            valid_categories = ['EI', 'EO', 'EQ', 'ILF', 'EIF']
            if data['category'] not in valid_categories:
                return jsonify({'error': f'无效的类别，必须是：{", ".join(valid_categories)}'}), 400
            rule.category = data['category']
        
        if 'priority' in data:
            rule.priority = data['priority']
        
        if 'rule_type' in data:
            valid_rule_types = ['endswith', 'contains', 'startswith', 'special']
            if data['rule_type'] not in valid_rule_types:
                return jsonify({'error': f'无效的规则类型，必须是：{", ".join(valid_rule_types)}'}), 400
            rule.rule_type = data['rule_type']
        
        if 'keyword' in data:
            rule.keyword = data['keyword']
        
        if 'description' in data:
            rule.description = data['description']
        
        if 'ufp_value' in data:
            rule.ufp_value = data['ufp_value']
        
        if 'is_active' in data:
            rule.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': '规则更新成功',
            'rule': rule.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fpa_rules_bp.route('/api/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule(rule_id):
    """删除规则"""
    try:
        rule = FPACategoryRule.query.get(rule_id)
        if not rule:
            return jsonify({'error': '规则不存在'}), 404
        
        db.session.delete(rule)
        db.session.commit()
        
        return jsonify({'message': '规则删除成功'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@fpa_rules_bp.route('/api/rules/batch', methods=['POST'])
def batch_update_rules():
    """批量更新规则（用于前端表格编辑）"""
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        updated_count = 0
        for update_data in updates:
            rule_id = update_data.get('id')
            if not rule_id:
                continue
            
            rule = FPACategoryRule.query.get(rule_id)
            if not rule:
                continue
            
            # 更新字段
            if 'category' in update_data:
                rule.category = update_data['category']
            if 'priority' in update_data:
                rule.priority = update_data['priority']
            if 'rule_type' in update_data:
                rule.rule_type = update_data['rule_type']
            if 'keyword' in update_data:
                rule.keyword = update_data['keyword']
            if 'description' in update_data:
                rule.description = update_data['description']
            if 'ufp_value' in update_data:
                rule.ufp_value = update_data['ufp_value']
            if 'is_active' in update_data:
                rule.is_active = update_data['is_active']
            
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'批量更新成功，共更新 {updated_count} 条规则'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
