# models/fpa_category_rules.py
"""
FPA 类别规则数据模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例（与其他模型共享）
db = SQLAlchemy()


class FPACategoryRule(db.Model):
    """FPA 功能点类别判断规则表"""
    
    __tablename__ = 'fpa_category_rules'
    
    # 字段定义
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(10), nullable=False, comment='功能点类型（EI/EO/EQ/ILF/EIF）')
    priority = db.Column(db.Integer, default=1, comment='优先级（数字越小优先级越高）')
    rule_type = db.Column(db.String(20), nullable=False, comment='规则类型（endswith/contains/startswith/special）')
    keyword = db.Column(db.String(100), nullable=False, comment='关键词')
    description = db.Column(db.Text, default='', comment='规则描述')
    ufp_value = db.Column(db.Integer, default=7, comment='默认 UFP 值')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'category': self.category,
            'priority': self.priority,
            'rule_type': self.rule_type,
            'keyword': self.keyword,
            'description': self.description,
            'ufp_value': self.ufp_value,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FPACategoryRule {self.id}: {self.category} - {self.keyword}>'
    
    @staticmethod
    def apply_rules(item_text: str):
        """
        根据功能点名称应用类别规则
        
        Args:
            item_text: 功能点名称
            
        Returns:
            tuple: (类别，UFP 值)
        """
        from flask import current_app
        
        try:
            # 从数据库获取所有启用的规则
            rules = FPACategoryRule.query.filter_by(is_active=True).order_by(FPACategoryRule.priority.asc()).all()
            
            # 按优先级依次匹配规则
            for rule in rules:
                matched = False
                
                if rule.rule_type == 'endswith' and item_text.endswith(rule.keyword):
                    matched = True
                elif rule.rule_type == 'contains' and rule.keyword in item_text:
                    matched = True
                elif rule.rule_type == 'startswith' and item_text.startswith(rule.keyword):
                    matched = True
                elif rule.rule_type == 'special':
                    # 特殊规则，可以根据需要扩展
                    matched = rule.keyword in item_text
                
                if matched:
                    return rule.category, rule.ufp_value
            
            # 如果没有匹配到任何规则，返回默认值
            # 根据功能点名称特征判断
            if item_text.endswith('表') or any(kw in item_text for kw in ['数据表', '配置表', '结果表', '详单表']):
                return 'ILF', 7
            elif any(keyword in item_text for keyword in [
                '录入', '修改', '删除', '增', '删', '改', '同步', '导入', '添加', '设置', '保存', '提交', '移交', '回单', '赋值'
            ]):
                return 'EI', 4
            elif any(kw in item_text for kw in [
                '判定', '分析', '计算', '处理', '识别', '匹配', '切换', '导出', '上报', '调度', '推送',
                '验证', '检测', '剔除', '运算', '渲染', '生成', '跳转', '控制', '监听', '播报', '触发',
                '过滤', '建议输出', '排查', '关联', '复盘', '审核', '流转', '总结', '报告',
                '标签输出', '执行情况', '存在问题', '简要说明', '照片上传', '自动流转',
                '消息通知', '确认', '驳回', '归档', '选择', '执行', '映射', '采集',
                '自动派发', '人工派发', '配置化', '下钻'
            ]):
                return 'EO', 5
            elif any(kw in item_text for kw in ['列表', '快速查询', '查询', '搜索', '查看', '浏览', '筛选', '详情', '展示', '显示', '获取', '读取']):
                return 'EQ', 4
            elif '呈现' in item_text:
                if any(kw in item_text for kw in ['关联', '隐患', '规则', '列表']):
                    return 'EO', 5
                else:
                    return 'EQ', 4
            else:
                return 'EO', 5
                
        except Exception as e:
            # 如果数据库不可用，使用硬编码规则
            if current_app:
                current_app.logger.error(f"应用类别规则失败：{e}，使用硬编码规则")
            
            # 硬编码规则（降级方案）
            if item_text.endswith('表') or any(kw in item_text for kw in ['数据表', '配置表', '结果表', '详单表']):
                return 'ILF', 7
            elif any(keyword in item_text for keyword in [
                '录入', '修改', '删除', '增', '删', '改', '同步', '导入', '添加', '设置', '保存', '提交', '移交', '回单', '赋值'
            ]):
                return 'EI', 4
            elif any(kw in item_text for kw in [
                '判定', '分析', '计算', '处理', '识别', '匹配', '切换', '导出', '上报', '调度', '推送',
                '验证', '检测', '剔除', '运算', '渲染', '生成', '跳转', '控制', '监听', '播报', '触发',
                '过滤', '建议输出', '排查', '关联', '复盘', '审核', '流转', '总结', '报告',
                '标签输出', '执行情况', '存在问题', '简要说明', '照片上传', '自动流转',
                '消息通知', '确认', '驳回', '归档', '选择', '执行', '映射', '采集',
                '自动派发', '人工派发', '配置化', '下钻'
            ]):
                return 'EO', 5
            elif any(kw in item_text for kw in ['列表', '快速查询', '查询', '搜索', '查看', '浏览', '筛选', '详情', '展示', '显示', '获取', '读取']):
                return 'EQ', 4
            elif '呈现' in item_text:
                if any(kw in item_text for kw in ['关联', '隐患', '规则', '列表']):
                    return 'EO', 5
                else:
                    return 'EQ', 4
            else:
                return 'EO', 5
