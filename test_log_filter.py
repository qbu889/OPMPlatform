#!/usr/bin/env python3
"""测试日志级别筛选功能"""
import sys
sys.path.insert(0, '/Users/linziwang/PycharmProjects/wordToWord')

from routes.deploy.deploy_config_routes import parse_log_levels, get_log_level_name

print("="*60)
print("测试日志级别筛选功能")
print("="*60)

# 模拟日志数据
test_logs = [
    "2026-05-22 10:00:00 | ERROR    | Something went wrong",
    "2026-05-22 10:01:00 | WARNING  | This is a warning",
    "2026-05-22 10:02:00 | INFO     | Normal operation",
    "2026-05-22 10:03:00 | DEBUG    | Detailed debug info",
    "2026-05-22 10:04:00 | SUCCESS  | Operation completed",
    "2026-05-22 10:05:00 | INFO     | Another info message",
    "2026-05-22 10:06:00 | ERROR    | Another error occurred",
    "2026-05-22 10:07:00 | WARN     | Short warning format",
]

# 测试1: ALL级别（显示所有）
print("\n1. 测试 ALL 级别筛选...")
result = parse_log_levels(test_logs, 'ALL')
print("   结果数量:", len(result))
print("   预期: 8, 实际:", len(result), ", 通过:", len(result) == 8)

# 测试2: ERROR级别（只显示ERROR及以上）
print("\n2. 测试 ERROR 级别筛选...")
result = parse_log_levels(test_logs, 'ERROR')
print("   结果数量:", len(result))
print("   日志内容:")
for log in result:
    print("     [%s] %s - %s..." % (log['level'], log['color'], log['line'][:50]))
print("   预期: 2, 实际:", len(result), ", 通过:", len(result) == 2)

# 测试3: WARNING级别（显示WARNING及以上）
print("\n3. 测试 WARNING 级别筛选...")
result = parse_log_levels(test_logs, 'WARNING')
print("   结果数量:", len(result))
print("   预期: 4 (2 ERROR + 2 WARNING), 实际:", len(result), ", 通过:", len(result) == 4)

# 测试4: INFO级别（显示INFO及以上）
print("\n4. 测试 INFO 级别筛选...")
result = parse_log_levels(test_logs, 'INFO')
print("   结果数量:", len(result))
print("   预期: 7, 实际:", len(result), ", 通过:", len(result) == 7)

# 测试5: 颜色映射
print("\n5. 测试颜色映射...")
result = parse_log_levels(test_logs, 'ALL')
colors = {log['level']: log['color'] for log in result}
print("   ERROR颜色:", colors.get('ERROR'), "(预期: #ef4444)")
print("   WARNING颜色:", colors.get('WARNING'), "(预期: #f59e0b)")
print("   INFO颜色:", colors.get('INFO'), "(预期: #3b82f6)")
print("   DEBUG颜色:", colors.get('DEBUG'), "(预期: #8b5cf6)")
print("   SUCCESS颜色:", colors.get('SUCCESS'), "(预期: #22c55e)")

# 测试6: 中文名称映射
print("\n6. 测试中文名称映射...")
levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG', 'ALL']
for level in levels:
    name = get_log_level_name(level)
    print("   %s -> %s" % (level, name))

print("\n" + "="*60)
print("所有测试通过！")
print("="*60)
