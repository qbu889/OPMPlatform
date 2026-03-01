import json

def load_json_file(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_field_order(data):
    """提取字段顺序"""
    if isinstance(data, dict):
        # 如果是字典，直接返回键的顺序
        return list(data.keys())
    elif isinstance(data, list) and len(data) > 0:
        # 如果是列表且有元素，取第一个元素
        return list(data[0].keys()) if isinstance(data[0], dict) else []
    return []

def compare_field_orders(expected_file, actual_file):
    """比较两个JSON文件的字段顺序"""
    # 加载预期顺序文件
    expected_data = load_json_file(expected_file)
    expected_fields = extract_field_order(expected_data)
    
    # 加载实际返回文件
    actual_data = load_json_file(actual_file)
    # 获取实际数据中的data字段
    if 'data' in actual_data:
        actual_fields = list(actual_data['data'].keys())
    else:
        actual_fields = extract_field_order(actual_data)
    
    print("=== 字段顺序对比分析 ===\n")
    
    print(f"预期字段数量: {len(expected_fields)}")
    print(f"实际字段数量: {len(actual_fields)}")
    print(f"共同字段数量: {len(set(expected_fields) & set(actual_fields))}\n")
    
    print("=== 详细对比 ===\n")
    
    # 找出只在预期中存在的字段
    expected_only = set(expected_fields) - set(actual_fields)
    if expected_only:
        print("只在预期顺序中存在的字段:")
        for field in sorted(expected_only):
            print(f"  - {field}")
        print()
    
    # 找出只在实际返回中存在的字段
    actual_only = set(actual_fields) - set(expected_fields)
    if actual_only:
        print("只在实际返回中存在的字段:")
        for field in sorted(actual_only):
            print(f"  - {field}")
        print()
    
    # 比较顺序差异
    print("=== 顺序差异分析 ===\n")
    
    # 创建位置映射
    expected_positions = {field: i for i, field in enumerate(expected_fields)}
    actual_positions = {field: i for i, field in enumerate(actual_fields)}
    
    # 分析相同字段的位置变化
    common_fields = set(expected_fields) & set(actual_fields)
    position_changes = []
    
    for field in common_fields:
        expected_pos = expected_positions[field]
        actual_pos = actual_positions[field]
        if expected_pos != actual_pos:
            position_changes.append((field, expected_pos, actual_pos))
    
    if position_changes:
        print("字段位置发生变化的字段:")
        for field, expected_pos, actual_pos in sorted(position_changes, key=lambda x: x[1]):
            print(f"  {field}: 预期位置 {expected_pos} -> 实际位置 {actual_pos}")
        print()
    
    # 显示前20个字段的对比
    print("=== 前20个字段顺序对比 ===\n")
    max_show = min(20, max(len(expected_fields), len(actual_fields)))
    
    print(f"{'位置':<4} {'预期字段':<30} {'实际字段':<30}")
    print("-" * 70)
    
    for i in range(max_show):
        exp_field = expected_fields[i] if i < len(expected_fields) else "-"
        act_field = actual_fields[i] if i < len(actual_fields) else "-"
        status = "✓" if exp_field == act_field else "✗"
        print(f"{i:<4} {exp_field:<30} {act_field:<30} {status}")

def main():
    expected_file = "/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/预计返回顺序.json"
    actual_file = "/Users/linziwang/PycharmProjects/wordToWord/routes/esToKafka/接口返回.json"
    
    compare_field_orders(expected_file, actual_file)

if __name__ == "__main__":
    main()