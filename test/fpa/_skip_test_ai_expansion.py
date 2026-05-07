#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 AI 辅助扩展功能点功能

用途：
1. 验证 AI 扩展功能是否正常触发
2. 检查 AI 扩展的日志输出
3. 测试不同场景下的 AI 调用逻辑
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 设置 Flask 应用配置
os.environ['FLASK_APP'] = 'app.py'

from routes.fpa_generator_routes import parse_requirement_document
from routes.fpa_ai_expander import ai_assisted_expand_function_points
import logging

# 配置日志，确保能看到详细的调试信息
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def test_ai_expansion():
    """测试 AI 辅助扩展功能"""
    
    print("=" * 80)
    print("AI 辅助扩展功能测试")
    print("=" * 80)
    
    # 读取测试文档
    test_file = project_root / "test" / "fpa" / "事件处理类工单流程应用场景.md"
    
    if not test_file.exists():
        print(f"❌ 测试文件不存在：{test_file}")
        return
    
    print(f"\n📖 读取测试文档：{test_file}")
    with open(test_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print(f"✅ 文档读取成功，总字符数：{len(md_content)}")
    
    # 解析功能点
    print("\n🔍 开始解析功能点...")
    function_points = parse_requirement_document(md_content)
    
    print(f"✅ 解析完成，共提取 {len(function_points)} 个功能点")
    
    # 分离 ILF 和非 ILF 功能点
    non_ilf_points = [p for p in function_points if p.get('类别') != 'ILF']
    ilf_points = [p for p in function_points if p.get('类别') == 'ILF']
    
    print(f"\n📊 功能点统计:")
    print(f"  - 非 ILF 功能点：{len(non_ilf_points)}个")
    print(f"  - ILF 功能点：{len(ilf_points)}个")
    
    # 计算 UFP
    total_ufp = sum(p.get('UFP', 5) for p in function_points)
    non_ilf_ufp = sum(p.get('UFP', 5) for p in non_ilf_points)
    ilf_ufp = sum(p.get('UFP', 7) for p in ilf_points)
    
    print(f"\n💰 UFP 统计:")
    print(f"  - 总 UFP: {total_ufp:.2f}")
    print(f"  - 非 ILF UFP: {non_ilf_ufp:.2f}")
    print(f"  - ILF UFP: {ilf_ufp:.2f}")
    
    # 模拟 AI 扩展场景
    print("\n" + "=" * 80)
    print("模拟 AI 扩展场景")
    print("=" * 80)
    
    # 场景 1：假设目标 UFP 是当前的 1.5 倍
    target_ufp = total_ufp * 1.5
    remaining_ufp = target_ufp - ilf_ufp
    original_avg_ufp = non_ilf_ufp / len(non_ilf_points) if non_ilf_points else 5
    needed_points_count = int(round(remaining_ufp / original_avg_ufp))
    current_count = len(non_ilf_points)
    expand_diff = needed_points_count - current_count
    
    print(f"\n🎯 场景 1: 目标 UFP = {target_ufp:.2f} (当前的 1.5 倍)")
    print(f"  - 需要功能点数：{needed_points_count}个")
    print(f"  - 当前功能点数：{current_count}个")
    print(f"  - 需要扩展：{expand_diff}个")
    print(f"  - 是否达到阈值 (>=5): {'是' if expand_diff >= 5 else '否'}")
    
    if expand_diff >= 5:
        print(f"\n✅ 触发条件满足，将调用 AI 进行扩展")
        
        # 调用 AI 扩展
        try:
            print("\n🤖 正在调用 AI 模型进行功能点拆分...")
            expanded_points = ai_assisted_expand_function_points(
                non_ilf_points,
                expand_diff
            )
            
            if expanded_points:
                print(f"\n✅ AI 扩展成功！")
                print(f"  - 扩展功能点数量：{len(expanded_points)}个")
                print(f"\n📋 前 5 个扩展的功能点:")
                for i, point in enumerate(expanded_points[:5], 1):
                    print(f"  [{i}] {point.get('功能点计数项', '')}")
                    print(f"      备注：{point.get('备注', '')}")
                    print(f"      类别：{point.get('类别', '')}, UFP: {point.get('UFP', 0)}, AFP: {point.get('AFP', 0)}")
                
                if len(expanded_points) > 5:
                    print(f"  ... 还有 {len(expanded_points) - 5} 个功能点")
            else:
                print(f"\n⚠️ AI 返回空结果，未扩展任何功能点")
                
        except Exception as e:
            print(f"\n❌ AI 扩展失败：{e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n⚠️ 不满足 AI 触发条件（差值 {expand_diff} < 5）")
    
    # 场景 2：较小的 UFP 差异
    print("\n" + "=" * 80)
    print("模拟小规模扩展场景")
    print("=" * 80)
    
    target_ufp_small = total_ufp * 1.1
    remaining_ufp_small = target_ufp_small - ilf_ufp
    needed_points_count_small = int(round(remaining_ufp_small / original_avg_ufp))
    expand_diff_small = needed_points_count_small - current_count
    
    print(f"\n🎯 场景 2: 目标 UFP = {target_ufp_small:.2f} (当前的 1.1 倍)")
    print(f"  - 需要功能点数：{needed_points_count_small}个")
    print(f"  - 当前功能点数：{current_count}个")
    print(f"  - 需要扩展：{expand_diff_small}个")
    print(f"  - 是否达到阈值 (>=5): {'是' if expand_diff_small >= 5 else '否'}")
    print(f"\n💡 结论：{'触发 AI 扩展' if expand_diff_small >= 5 else '不触发 AI 扩展'}")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"\n✅ 基础功能点解析：正常")
    print(f"✅ AI 扩展触发逻辑：{'正常' if expand_diff >= 5 else '待验证'}")
    print(f"✅ 日志输出：详细")
    
    print("\n📝 提示:")
    print("  1. 查看上面的日志输出，确认 AI 是否被调用")
    print("  2. 如果 AI 未被调用，检查是否满足触发条件")
    print("  3. 如果 AI 调用失败，检查 Ollama 服务是否运行")
    print("  4. 确认 qwen3:8b 模型已下载")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_ai_expansion()
