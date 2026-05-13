"""
JSON对比工具核心算法
支持递归对比、忽略顺序、差异统计等功能
"""

def compare_json_data(left, right, options=None):
    """
    递归对比JSON数据
    
    Args:
        left: 左侧JSON数据
        right: 右侧JSON数据
        options: 对比选项 {strict_mode, ignore_case, ignore_whitespace}
    
    Returns:
        dict: {
            'left_tree': 左侧对比树,
            'right_tree': 右侧对比树,
            'stats': 统计信息
        }
    """
    if options is None:
        options = {}
    
    left_tree = build_diff_tree(left, right, 'left', options, path='')
    right_tree = build_diff_tree(left, right, 'right', options, path='')
    stats = calculate_stats(left_tree)
    
    return {
        'left_tree': left_tree,
        'right_tree': right_tree,
        'stats': stats
    }


def build_diff_tree(left, right, side, options, path=''):
    """
    构建对比树结构
    
    Args:
        left: 左侧数据
        right: 右侧数据
        side: 'left' 或 'right'
        options: 对比选项
        path: 当前JSON路径
    
    Returns:
        dict: 树节点字典
    """
    # 如果两侧都是对象（字典）
    if isinstance(left, dict) and isinstance(right, dict):
        return build_object_diff(left, right, side, options, path)
    # 如果两侧都是数组
    elif isinstance(left, list) and isinstance(right, list):
        return build_array_diff(left, right, side, options, path)
    # 其他类型（直接对比值）
    else:
        return build_value_diff(left, right, side, options, path)


def build_object_diff(left_obj, right_obj, side, options, path):
    """构建对象类型的对比树"""
    # 获取所有键（去重并排序）
    all_keys = sorted(set(list(left_obj.keys()) + list(right_obj.keys())))
    
    tree = {}
    for key in all_keys:
        current_path = f"{path}.{key}" if path else key
        
        if key not in left_obj:
            # 仅存在于右侧（新增）
            tree[key] = {
                'status': 'added' if side == 'right' else 'removed',
                'value': right_obj[key] if side == 'right' else None,
                'path': current_path,
                'type': get_type_name(right_obj[key])
            }
        elif key not in right_obj:
            # 仅存在于左侧（删除）
            tree[key] = {
                'status': 'removed' if side == 'left' else 'added',
                'value': left_obj[key] if side == 'left' else None,
                'path': current_path,
                'type': get_type_name(left_obj[key])
            }
        else:
            # 两侧都存在，递归对比
            left_val = left_obj[key]
            right_val = right_obj[key]
            
            if is_values_equal(left_val, right_val, options):
                # 值相同
                tree[key] = {
                    'status': 'same',
                    'value': left_val if side == 'left' else right_val,
                    'path': current_path,
                    'type': get_type_name(left_val)
                }
            else:
                # 值不同，判断是否为对象或数组
                if isinstance(left_val, dict) and isinstance(right_val, dict):
                    tree[key] = {
                        'status': 'different',
                        'children': build_diff_tree(left_val, right_val, side, options, current_path),
                        'path': current_path,
                        'type': 'object'
                    }
                elif isinstance(left_val, list) and isinstance(right_val, list):
                    tree[key] = {
                        'status': 'different',
                        'children': build_diff_tree(left_val, right_val, side, options, current_path),
                        'path': current_path,
                        'type': 'array'
                    }
                else:
                    # 基本类型不同
                    tree[key] = {
                        'status': 'different',
                        'left': left_val,
                        'right': right_val,
                        'path': current_path,
                        'type': get_type_name(left_val)
                    }
    
    return tree


def build_array_diff(left_arr, right_arr, side, options, path):
    """构建数组类型的对比树"""
    # 简单实现：按索引对比
    max_len = max(len(left_arr), len(right_arr))
    tree = []
    
    for i in range(max_len):
        current_path = f"{path}[{i}]"
        
        if i >= len(left_arr):
            # 仅存在于右侧
            tree.append({
                'status': 'added' if side == 'right' else 'removed',
                'value': right_arr[i] if side == 'right' else None,
                'path': current_path,
                'type': get_type_name(right_arr[i]) if i < len(right_arr) else None
            })
        elif i >= len(right_arr):
            # 仅存在于左侧
            tree.append({
                'status': 'removed' if side == 'left' else 'added',
                'value': left_arr[i] if side == 'left' else None,
                'path': current_path,
                'type': get_type_name(left_arr[i])
            })
        else:
            # 两侧都有，递归对比
            left_val = left_arr[i]
            right_val = right_arr[i]
            
            if is_values_equal(left_val, right_val, options):
                tree.append({
                    'status': 'same',
                    'value': left_val if side == 'left' else right_val,
                    'path': current_path,
                    'type': get_type_name(left_val)
                })
            else:
                if isinstance(left_val, dict) and isinstance(right_val, dict):
                    tree.append({
                        'status': 'different',
                        'children': build_diff_tree(left_val, right_val, side, options, current_path),
                        'path': current_path,
                        'type': 'object'
                    })
                elif isinstance(left_val, list) and isinstance(right_val, list):
                    tree.append({
                        'status': 'different',
                        'children': build_diff_tree(left_val, right_val, side, options, current_path),
                        'path': current_path,
                        'type': 'array'
                    })
                else:
                    tree.append({
                        'status': 'different',
                        'left': left_val,
                        'right': right_val,
                        'path': current_path,
                        'type': get_type_name(left_val)
                    })
    
    return tree


def build_value_diff(left_val, right_val, side, options, path):
    """构建基本类型的对比树"""
    if is_values_equal(left_val, right_val, options):
        return {
            'status': 'same',
            'value': left_val if side == 'left' else right_val,
            'path': path,
            'type': get_type_name(left_val)
        }
    else:
        return {
            'status': 'different',
            'left': left_val,
            'right': right_val,
            'path': path,
            'type': get_type_name(left_val)
        }


def is_values_equal(left, right, options):
    """
    判断两个值是否相等
    
    Args:
        left: 左侧值
        right: 右侧值
        options: 对比选项
    
    Returns:
        bool: 是否相等
    """
    # 类型不同
    if type(left) != type(right):
        # 宽松模式：数字和字符串可以比较
        if not options.get('strict_mode', True):
            try:
                return str(left) == str(right)
            except:
                return False
        return False
    
    # 都是字符串
    if isinstance(left, str):
        if options.get('ignore_whitespace', False):
            left = left.strip()
            right = right.strip()
        if options.get('ignore_case', False):
            return left.lower() == right.lower()
        return left == right
    
    # 都是数字
    if isinstance(left, (int, float)):
        return left == right
    
    # 都是布尔值
    if isinstance(left, bool):
        return left == right
    
    # 都是None
    if left is None and right is None:
        return True
    
    # 默认不相等
    return False


def get_type_name(value):
    """获取值的类型名称"""
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return 'boolean'
    elif isinstance(value, int):
        return 'number'
    elif isinstance(value, float):
        return 'number'
    elif isinstance(value, str):
        return 'string'
    elif isinstance(value, dict):
        return 'object'
    elif isinstance(value, list):
        return 'array'
    else:
        return 'unknown'


def calculate_stats(tree):
    """
    计算对比统计信息
    
    Args:
        tree: 对比树
    
    Returns:
        dict: 统计信息
    """
    stats = {
        'same': 0,
        'different': 0,
        'added': 0,
        'removed': 0,
        'total': 0
    }
    
    _count_stats(tree, stats)
    
    stats['total'] = stats['same'] + stats['different'] + stats['added'] + stats['removed']
    
    return stats


def _count_stats(node, stats):
    """递归统计节点"""
    if isinstance(node, dict):
        # 检查是否是树节点（包含status）
        if 'status' in node:
            status = node['status']
            if status == 'same':
                stats['same'] += 1
            elif status == 'different':
                stats['different'] += 1
            elif status == 'added':
                stats['added'] += 1
            elif status == 'removed':
                stats['removed'] += 1
            
            # 递归子节点
            if 'children' in node:
                _count_stats(node['children'], stats)
        
        # 遍历字典的所有值
        else:
            for key, value in node.items():
                _count_stats(value, stats)
    
    elif isinstance(node, list):
        # 遍历数组的所有元素
        for item in node:
            _count_stats(item, stats)
