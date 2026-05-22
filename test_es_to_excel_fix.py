#!/usr/bin/env python3
"""测试 EsToExcel.py 修复"""
import sys
import pandas as pd

sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')

from utils.ES结果导Excel.EsToExcel import _format_time_columns

def test_format_time_columns_with_duplicate_columns():
    """测试有重复列名时的时间字段格式化"""
    print("="*60)
    print("测试 _format_time_columns 修复")
    print("="*60)
    
    # 创建一个有重复列名的 DataFrame
    data = {
        'name': ['test1', 'test2', 'test3'],
        'time': ['2024-01-01T12:00:00Z', '2024-01-02T13:00:00Z', '2024-01-03T14:00:00+08:00'],
        'time': ['2024-01-01T10:00:00Z', '2024-01-02T11:00:00Z', '2024-01-03T12:00:00+08:00']  # 重复列名
    }
    
    df = pd.DataFrame(data)
    print(f"DataFrame 列名: {list(df.columns)}")
    print(f"列名是否有重复: {len(df.columns) != len(set(df.columns))}")
    print(f"df['time'] 类型: {type(df['time'])}")
    
    try:
        _format_time_columns(df)
        print("\n✅ _format_time_columns 执行成功!")
        print(f"格式化后的时间列:\n{df['time']}")
        return True
    except AttributeError as e:
        print(f"\n❌ 修复失败: {e}")
        return False

def test_format_time_columns_normal():
    """测试正常情况（无重复列名）"""
    print("\n" + "="*60)
    print("测试正常情况（无重复列名）")
    print("="*60)
    
    data = {
        'name': ['test1', 'test2', 'test3'],
        'timestamp': ['2024-01-01T12:00:00Z', '2024-01-02T13:00:00Z', '2024-01-03T14:00:00+08:00']
    }
    
    df = pd.DataFrame(data)
    
    try:
        _format_time_columns(df)
        print("\n✅ 正常情况测试通过!")
        print(f"格式化后的时间列:\n{df['timestamp']}")
        return True
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success1 = test_format_time_columns_with_duplicate_columns()
    success2 = test_format_time_columns_normal()
    
    print("\n" + "="*60)
    if success1 and success2:
        print("✅ 所有测试通过！修复有效！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
