#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端 preprocessData 函数的修复逻辑
模拟 JavaScript 的 fixFieldInvalidEscapes 函数行为
"""

import re
import json

def fix_field_invalid_escapes(json_string, field_name):
    """
    修复指定 JSON 字段值中的非法转义字符
    Python 版本实现，模拟 JavaScript 的逻辑
    """
    print(f"  - 检查字段：{field_name}")
    
    # 匹配字段值的正则表达式："FIELD_NAME" : "VALUE" 或 "FIELD_NAME": "VALUE"
    field_pattern = rf'("{field_name}"\s*:\s*")(.+?)("\s*[,,}}])'
    
    match = re.search(field_pattern, json_string, re.DOTALL)
    if not match:
        print(f"    ✓ 字段 {field_name} 未找到或格式异常，跳过")
        return json_string
    
    field_value = match.group(2)
    print(f"    发现字段 {field_name}，值长度：{len(field_value)}")
    
    # 修复字段值中的非法转义
    fixed_value = field_value
    
    # 合法转义序列列表（JSON 标准允许的）
    valid_escapes = ['\\\\', '\\"', '\\/', '\\b', '\\f', '\\n', '\\r', '\\t']
    
    # 第一步：临时保护合法的转义序列
    placeholders = {}
    for index, escape in enumerate(valid_escapes):
        placeholder = f'__VALID_ESCAPE_{index}__'
        placeholders[placeholder] = escape
        fixed_value = fixed_value.replace(escape, placeholder)
    
    # 第二步：处理 \uXXXX 格式
    def protect_unicode(m):
        placeholder = f'__UNICODE_{m.group(0)[1:]}__'
        placeholders[placeholder] = m.group(0)
        return placeholder
    
    fixed_value = re.sub(r'\\u[0-9a-fA-F]{4}', protect_unicode, fixed_value)
    
    # 第三步：现在剩下的 \ 后跟其他字符都是非法的，双写反斜杠
    # 例如：\中 -> \\中，\( -> \\(
    fixed_value = re.sub(r'\\([^\\])', r'\\\\\1', fixed_value)
    
    # 第四步：恢复合法的转义序列
    for placeholder, escape in placeholders.items():
        fixed_value = fixed_value.replace(placeholder, escape)
    
    print(f"    ✓ 字段 {field_name} 修复完成")
    
    # 替换原 JSON 中的字段值
    before_fix = match.group(0)
    after_fix = match.group(1) + fixed_value + match.group(3)
    
    return json_string.replace(before_fix, after_fix)


def preprocess_es_data(raw_data):
    """模拟前端的 preprocessEsData 函数"""
    processed = raw_data
    
    # 1. 处理三重引号
    processed = processed.replace('"""', '"')
    
    # 2. 处理 HTML 实体
    html_entities = {
        '&lt;': '<',
        '&gt;': '>',
        '&amp;': '&',
        '&quot;': '"',
        '&#39;': "'",
        '&nbsp;': ' '
    }
    
    for entity, replacement in html_entities.items():
        processed = processed.replace(entity, replacement)
    
    # 3. 处理尾随逗号
    processed = re.sub(r',\s*([\}\]])', r'\1', processed)
    
    # 4. 移除控制字符
    processed = re.sub(r'[\x00-\x1F\x7F]', '', processed)
    
    # 5. 处理特殊 Unicode
    processed = processed.replace('\u003c', '<').replace('\u003e', '>')
    
    # 6. 标准化换行符
    processed = processed.replace('\r\n', '\n').replace('\r', '\n')
    
    # 7. 修复特定字段的非法转义
    print("\n开始修复特定字段的非法转义字符...")
    processed = fix_field_invalid_escapes(processed, 'EVENT_REASON')
    processed = fix_field_invalid_escapes(processed, 'SRC_ORG_ALARM_TEXT')
    processed = fix_field_invalid_escapes(processed, 'EVENT_EFFECT')
    
    return processed


def test_problematic_json():
    """测试有问题的 JSON 数据"""
    
    # 从 前端展示Kafka 消息.txt 中复制的实际问题数据
    test_json = '''{
  "EVENT_REASON": """
定界结果：初判为市电停电导致；
定位结论：基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房_中兴 DU68 开关电源。
是否配备油机：是
机房续航情况：组合式开关电源 2(TOSWITCH-33004),理论续航时长 5.74H,剩余续航时长 5.74H;组合式开关电源 1(TOSWITCH-93628),理论续航时长 8.0H,剩余续航时长 8.0H;
温度：11.6
电压电流情况：组合式开关电源 2-电压（52）电流（64.3）；组合式开关电源 1-电压（54）电流（94.3）；
""",
  "SRC_ORG_ALARM_TEXT": """
<ALARMSTART>
SystemName:高新兴动环系统
Vendor_Name:中兴 DU68 开关电源
Speciality:动环专业
AlarmID:268994297
IntID:c4ce8047-c267-44e5-9e3f-277b015e075c
AlarmEquipment:基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房_中兴 DU68 开关电源
EquipmentClass:
EventTime:2026-03-19 18:37:05
Vendor_Severity:二级告警
AlarmTitle:触发值：1，告警区间为：1
ActiveStatus:1
ProbableCause:
ProbableCauseTxt:福州连江坪垱后山山头移动自建房\中兴 DU68 开关电源\触发值：1，告警区间为：1
MaintainPropose:006007,003,1
LocateInfo:基站_福州市_汇聚机房_连江县_福州连江坪垱后山山头移动自建房二楼设备间机房_中兴 DU68 开关电源
ClearID:268994297
LocateName:基站>福州市>汇聚机房>连江县>福州连江坪垱后山山头移动自建房二楼设备间机房 1
Version:
AckUser:
AckTerminal:
DispatchFlag:0
standard_alarm_id:609-006-00-006095
IRMS_CUID:TOSWITCH-33004
<ALARMEND>
""",
  "EVENT_EFFECT": """
网络影响：福州连江丹阳对面原 48 号厂房西侧 20 米处自建房二楼设备间机房 - 开关电源 -2；
机房下挂业务设备：无线设备：福州连江 - 丹阳 WJ 后山 B-HRHH-BBU-1、CBN-福州连江 - 丹阳虎山 C-HRHH-BBU-1、福州连江 - 蓬沿朱公 B-HRHH-BBU-1...等，传输设备：14079-连江丹阳街道（重要）、9190-连江丹阳汇聚环三-HW-OTM、1422-福州连江丹阳坪垱顶-HW-SPN(汇聚)...等，家宽设备：FZLJ 丹阳 -OLT002-AN5516-01、FZLJ 丹阳 -OLT001-AN5516-01
社会影响：暂无投诉。
"""
}'''
    
    print("="*80)
    print("测试前端预处理功能")
    print("="*80)
    print("\n原始 JSON:")
    print(test_json[:500])
    print("...\n")
    
    # 尝试直接解析（应该失败）
    print("\n[测试 1] 尝试直接解析原始 JSON...")
    try:
        json.loads(test_json)
        print("✅ 意外成功！原始 JSON 可以直接解析")
    except json.JSONDecodeError as e:
        print(f"❌ 预期失败：{e}")
        
        # 显示错误位置
        error_pos = e.pos
        start = max(0, error_pos - 100)
        end = min(len(test_json), error_pos + 100)
        print(f"\n错误位置附近：\n...{repr(test_json[start:end])}...")
    
    # 使用我们的预处理函数
    print("\n[测试 2] 使用前端逻辑进行预处理...")
    try:
        fixed_json = preprocess_es_data(test_json)
        
        print("\n处理后的 JSON:")
        print(fixed_json[:500])
        print("...\n")
        
        # 尝试解析处理后的 JSON
        print("[测试 3] 尝试解析处理后的 JSON...")
        parsed = json.loads(fixed_json)
        print(f"✅ 成功！解析出 {len(parsed)} 个字段")
        
        # 验证关键字段
        print("\n[验证] 检查关键字段内容:")
        print(f"  - EVENT_REASON 长度：{len(parsed.get('EVENT_REASON', ''))}")
        print(f"  - SRC_ORG_ALARM_TEXT 长度：{len(parsed.get('SRC_ORG_ALARM_TEXT', ''))}")
        print(f"  - EVENT_EFFECT 长度：{len(parsed.get('EVENT_EFFECT', ''))}")
        
        # 特别检查 ProbableCauseTxt 字段中的转义
        src_text = parsed.get('SRC_ORG_ALARM_TEXT', '')
        if '\\\\' in src_text:
            print("\n✅ 发现并正确处理了反斜杠转义")
            # 查找包含反斜杠的行
            for line in src_text.split('\n'):
                if 'ProbableCauseTxt' in line:
                    print(f"  ProbableCauseTxt: {repr(line)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 预处理后仍然失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_problematic_json()
    
    if success:
        print("\n" + "="*80)
        print("✅ 测试通过！前端预处理逻辑可以修复非法 JSON 转义")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ 测试失败！需要进一步调试")
        print("="*80)
