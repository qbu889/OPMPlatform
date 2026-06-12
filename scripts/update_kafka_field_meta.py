#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 Kafka 字段元数据脚本
根据表格_20260514.csv更新kafka_field_meta表
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mysql_helper import get_mysql_conn_dict_cursor

def backup_field_meta():
    """备份现有的字段元数据"""
    print("开始备份现有字段元数据...")
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        print("❌ 无法连接数据库")
        return False
    
    try:
        with conn.cursor() as cur:
            # 查询所有数据
            cur.execute("""
                SELECT id, kafka_field, es_field, db_cn, label_cn, remark, is_enabled, created_at, updated_at
                FROM kafka_field_meta
                ORDER BY kafka_field
            """)
            rows = cur.fetchall()
            
            # 创建备份文件
            backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'kafka_field_meta_backup_{timestamp}.sql')
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(f"-- Kafka 字段元数据备份\n")
                f.write(f"-- 备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"-- 记录数: {len(rows)}\n\n")
                
                # 生成 DROP 和 CREATE 语句
                f.write("DROP TABLE IF EXISTS kafka_field_meta_backup;\n\n")
                f.write("""CREATE TABLE kafka_field_meta_backup (
    id INT,
    kafka_field VARCHAR(100),
    es_field VARCHAR(100),
    db_cn VARCHAR(200),
    label_cn VARCHAR(200),
    remark TEXT,
    is_enabled TINYINT(1),
    created_at DATETIME,
    updated_at DATETIME
);\n\n""")
                
                # 生成 INSERT 语句
                for row in rows:
                    values = []
                    for col in ['id', 'kafka_field', 'es_field', 'db_cn', 'label_cn', 'remark', 'is_enabled', 'created_at', 'updated_at']:
                        val = row.get(col)
                        if val is None:
                            values.append('NULL')
                        elif isinstance(val, str):
                            values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")
                        elif isinstance(val, datetime):
                            values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'")
                        else:
                            values.append(str(val))
                    
                    f.write(f"INSERT INTO kafka_field_meta_backup VALUES ({','.join(values)});\n")
            
            print(f"✅ 备份完成，共 {len(rows)} 条记录")
            print(f"📁 备份文件: {backup_file}")
            return True
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


def update_field_meta():
    """根据表格更新字段元数据"""
    print("\n开始更新字段元数据...")
    
    # 根据表格数据构建更新映射
    # 格式: kafka_field -> {es_field, db_cn, label_cn}
    updates = {
        "NETWORK_TYPE_TOP": {
            "es_field": "NETWORK_TYPE_ID",
            "db_cn": "一级专业分类",
            "label_cn": "一级专业分类"
        },
        "REGION_NAME": {
            "es_field": "CITY_NAME",
            "db_cn": "地市",
            "label_cn": "地区"
        },
        "ACTIVE_STATUS": {
            "es_field": "CANCEL_STATUS",
            "db_cn": "清除状态",
            "label_cn": "告警清除状态"
        },
        "CITY_NAME": {
            "es_field": "COUNTY_NAME",
            "db_cn": "区县",
            "label_cn": "县市"
        },
        "EQP_LABEL": {
            "es_field": "EQUIPMENT_NAME",
            "db_cn": "网元名称",
            "label_cn": "网元名称"
        },
        "EQP_OBJECT_CLASS": {
            "es_field": "EQP_OBJECT_ID",
            "db_cn": "设备类型 ID",
            "label_cn": "设备类型"
        },
        "VENDOR_NAME": {
            "es_field": "VENDOR_NAME",
            "db_cn": "设备厂家",
            "label_cn": "设备厂家名称"
        },
        "VENDOR_ID": {
            "es_field": "VENDOR_NAME",
            "db_cn": "设备厂家",
            "label_cn": "设备厂家ID"
        },
        "ALARM_RESOURCE_STATUS": {
            "es_field": "ALARM_RESOURCE_STATUS",
            "db_cn": "告警工程状态",
            "label_cn": "告警工程状态"
        },
        "NE_LABEL": {
            "es_field": "NE_LABEL",
            "db_cn": "告警对象网元名称",
            "label_cn": "告警对象网元名称"
        },
        "OBJECT_LEVEL": {
            "es_field": "OBJECT_LEVEL",
            "db_cn": "告警对象重要级别",
            "label_cn": "告警对象重要级别"
        },
        "PROFESSIONAL_TYPE": {
            "es_field": "PROFESSIONAL_TYPE",
            "db_cn": "专业（旧概念）",
            "label_cn": "专业（旧概念）"
        },
        "NETWORK_TYPE": {
            "es_field": "NETWORK_SUB_TYPE_ID",
            "db_cn": "二级专业 ID",
            "label_cn": "二级专业分类"
        },
        "ORG_TYPE": {
            "es_field": "ORG_TYPE",
            "db_cn": "告警类别",
            "label_cn": "告警类别"
        },
        "VENDOR_TYPE": {
            "es_field": "VENDOR_TYPE",
            "db_cn": "厂家原始告警类别",
            "label_cn": "厂家原始告警类别"
        },
        "SEND_JT_FLAG": {
            "es_field": "SEND_JT_FLAG",
            "db_cn": "是否需要上报集团",
            "label_cn": "是否需要上报集团"
        },
        "VENDOR_SEVERITY": {
            "es_field": "VENDOR_SEVERITY",
            "db_cn": "厂家原始告警级别",
            "label_cn": "厂家原始告警级别"
        },
        "PROBABLE_CAUSE": {
            "es_field": "PROBABLE_CAUSE",
            "db_cn": "厂家告警号",
            "label_cn": "厂家告警号"
        },
        "NMS_ALARM_ID": {
            "es_field": "NMS_ALARM_ID",
            "db_cn": "告警流水号",
            "label_cn": "告警流水号"
        },
        "PREPROCESS_MANNER": {
            "es_field": "PREPROCESS_MANNER",
            "db_cn": "预处理方式",
            "label_cn": "预处理方式"
        },
        "EVENT_TIME": {
            "es_field": "EVENT_TIME",
            "db_cn": "事件发生时间",
            "label_cn": "告警发生时间"
        },
        "CANCEL_TIME": {
            "es_field": "CANCEL_TIME",
            "db_cn": "事件清除时间",
            "label_cn": "告警清除时间"
        },
        "INT_ID": {
            "es_field": "INT_ID",
            "db_cn": "告警对象 ID",
            "label_cn": "告警对象ID"
        },
        "TYPE_KEYCODE": {
            "es_field": "TYPE_KEYCODE",
            "db_cn": "类别关键字",
            "label_cn": "类别关键字"
        },
        "NE_LOCATION": {
            "es_field": "NE_LOCATION",
            "db_cn": "网元定位信息",
            "label_cn": "网元定位信息"
        },
        "MAINTAIN_GROUP": {
            "es_field": "MAINTAIN_TEAM",
            "db_cn": "主派维护组",
            "label_cn": "主派维护组"
        },
        "SUB_ALARM_TYPE": {
            "es_field": "SUB_ALARM_TYPE",
            "db_cn": "告警子类型",
            "label_cn": "告警子类型"
        },
        "EVENT_CAT": {
            "es_field": "EVENT_CAT",
            "db_cn": "事件描述",
            "label_cn": "事件描述"
        },
        "NMS_NAME": {
            "es_field": "NMS_NAME",
            "db_cn": "专业网管名称",
            "label_cn": "专业网管名称"
        },
        "CITY_ID": {
            "es_field": "COUNTY_ID",
            "db_cn": "区县 ID",
            "label_cn": "区县ID"
        },
        "REMOTE_EQP_LABEL": {
            "es_field": "REMOTE_EQUIPMENT_NAME",
            "db_cn": "对端设备名称",
            "label_cn": "对端设备名称"
        },
        "REMOTE_RESOURCE_STATUS": {
            "es_field": "REMOTE_RESOURCE_STATUS",
            "db_cn": "对端设备工程状态",
            "label_cn": "对端设备工程状态"
        },
        "REMOTE_PROJ_SUB_STATUS": {
            "es_field": "REMOTE_PROJ_SUB_STATUS",
            "db_cn": "对端设备工程细分状态",
            "label_cn": "对端设备工程细分状态"
        },
        "REMOTE_INT_ID": {
            "es_field": "REMOTE_INT_ID",
            "db_cn": "对端设备网元 ID",
            "label_cn": "对端设备网元ID"
        },
        "PROJ_NAME": {
            "es_field": "PROJ_NAME",
            "db_cn": "工程名",
            "label_cn": "工程名"
        },
        "PROJ_OA_FILE_CONTENT": {
            "es_field": "PROJ_OA_FILE_CONTENT",
            "db_cn": "网元工程公文正文",
            "label_cn": "网元工程公文正文"
        },
        "BUSINESS_REGION_IDS": {
            "es_field": "BUSINESS_REGION_IDS",
            "db_cn": "业务覆盖区域",
            "label_cn": "业务覆盖区域"
        },
        "BUSINESS_REGIONS": {
            "es_field": "BUSINESS_REGIONS",
            "db_cn": "业务覆盖区域名",
            "label_cn": "业务覆盖区域名"
        },
        "REMOTE_OBJECT_CLASS": {
            "es_field": "REMOTE_OBJECT_CLASS",
            "db_cn": "对端设备类型",
            "label_cn": "对端设备类型"
        },
        "TIME_STAMP_C": {
            "es_field": "CANCEL_COLLECT_TIME",
            "db_cn": "清除发现时间",
            "label_cn": "清除发现时间"
        },
        "ALARM_REASON": {
            "es_field": "ALARM_REASON",
            "db_cn": "断站告警原因",
            "label_cn": "断站告警原因"
        },
        "BUSINESS_SYSTEM": {
            "es_field": "BUSINESS_SYSTEM",
            "db_cn": "业务系统",
            "label_cn": "业务系统"
        },
        "NE_IP": {
            "es_field": "EQUIPMENT_IP",
            "db_cn": "网元 IP",
            "label_cn": "网元IP"
        },
        "LAYER_RATE": {
            "es_field": "LAYER_RATE",
            "db_cn": "标准化层速率",
            "label_cn": "标准化层速率"
        },
        "CIRCUIT_ID": {
            "es_field": "CIRCUIT_ID",
            "db_cn": "电路 ID",
            "label_cn": "电路ID"
        },
        "ALARM_ABNORMAL_TYPE": {
            "es_field": "ALARM_ABNORMAL_TYPE",
            "db_cn": "异常告警类型",
            "label_cn": "异常告警类型"
        },
        "PROJ_OA_FILE_ID": {
            "es_field": "PROJ_OA_FILE_ID",
            "db_cn": "网元工程公文号",
            "label_cn": "网元工程公文号"
        },
        "GCSS_CLIENT_GRADE": {
            "es_field": "GCSS_CLIENT_GRADE",
            "db_cn": "集客客户属性",
            "label_cn": "集客客户属性"
        },
        "EFFECT_CIRCUIT_NUM": {
            "es_field": "EFFECT_CIRCUIT_NUM",
            "db_cn": "影响电路数",
            "label_cn": "影响电路数"
        },
        "PREHANDLE": {
            "es_field": "PREHANDLE",
            "db_cn": "预处理",
            "label_cn": "预处理"
        },
        "OBJECT_CLASS_TEXT": {
            "es_field": "OBJECT_CLASS_TEXT",
            "db_cn": "网元类型 (text)",
            "label_cn": "网元类型(text)"
        },
        "BOARD_TYPE": {
            "es_field": "BOARD_TYPE",
            "db_cn": "设备单板",
            "label_cn": "设备单板"
        },
        "PROJ_START_TIME": {
            "es_field": "PROJ_START_TIME",
            "db_cn": "工程开始时间",
            "label_cn": "工程开始时间"
        },
        "PROJ_END_TIME": {
            "es_field": "PROJ_END_TIME",
            "db_cn": "工程结束时间",
            "label_cn": "工程结束时间"
        },
        "OBJECT_CLASS": {
            "es_field": "OBJECT_CLASS",
            "db_cn": "告警对象设备类型",
            "label_cn": "告警对象设备类型"
        },
        "LOGIC_ALARM_TYPE": {
            "es_field": "LOGIC_ALARM_TYPE",
            "db_cn": "告警逻辑分类",
            "label_cn": "告警逻辑分类"
        },
        "LOGIC_SUB_ALARM_TYPE": {
            "es_field": "LOGIC_SUB_ALARM_TYPE",
            "db_cn": "告警逻辑子类",
            "label_cn": "告警逻辑子类"
        },
        "EFFECT_NE": {
            "es_field": "EFFECT_NE",
            "db_cn": "该事件对设备的影响",
            "label_cn": "对设备的影响"
        },
        "EFFECT_SERVICE": {
            "es_field": "EFFECT_SERVICE",
            "db_cn": "该事件对业务的影响",
            "label_cn": "对业务的影响"
        },
        "SPECIAL_FIELD14": {
            "es_field": "NE_TAG.ROOM_ID",
            "db_cn": "机房 CUID",
            "label_cn": "机房CUID"
        },
        "SPECIAL_FIELD7": {
            "es_field": "NE_TAG.NE_ID",
            "db_cn": "网元 UUID",
            "label_cn": "网元UUID"
        },
        "SPECIAL_FIELD21": {
            "es_field": "NE_TAG.PORT_ID",
            "db_cn": "端口 UUID",
            "label_cn": "端口UUID"
        },
        "ALARM_SOURCE": {
            "es_field": "ALARM_SOURCE",
            "db_cn": "告警来源",
            "label_cn": "告警来源"
        },
        "BUSINESS_LAYER": {
            "es_field": "BUSINESS_LAYER",
            "db_cn": "业务层级",
            "label_cn": "业务层级"
        },
        "ALARM_INTEND_SEND_TIME": {
            "es_field": "ALARM_INTEND_SEND_TIME",
            "db_cn": "预处理时间",
            "label_cn": "预处理时间"
        },
        "ALARM_TEXT": {
            "es_field": "SRC_ORG_ALARM_TEXT",
            "db_cn": "原始告警报文",
            "label_cn": "原始告警报文"
        },
        "ROOT_EQP_LABEL": {
            "es_field": "ROOT_EQP_LABEL",
            "db_cn": "根因网元",
            "label_cn": "根因网元"
        },
        "EVENT_RECORD_ID": {
            "es_field": "EVENT_RECORD_ID",
            "db_cn": "事件流水号",
            "label_cn": "事件流水号"
        },
        "CIRCUIT_NO": {
            "es_field": "CIRCUIT_NO",
            "db_cn": "电路代号",
            "label_cn": "电路代号"
        },
        "PRODUCT_TYPE": {
            "es_field": "PRODUCT_TYPE",
            "db_cn": "产品类型",
            "label_cn": "产品类型"
        },
        "CIRCUIT_LEVEL": {
            "es_field": "CIRCUIT_LEVEL",
            "db_cn": "电路级别",
            "label_cn": "电路级别"
        },
        "BUSINESS_TYPE": {
            "es_field": "BUSINESS_TYPE",
            "db_cn": "业务类型",
            "label_cn": "业务类型"
        },
        "IRMS_GRID_NAME": {
            "es_field": "IRMS_GRID_NAME",
            "db_cn": "所属网格名称",
            "label_cn": "所属网格名称"
        },
        "ADMIN_GRID_ID": {
            "es_field": "ADMIN_GRID_ID",
            "db_cn": "所属网格编码",
            "label_cn": "所属网格编码"
        },
        "HOME_CLIENT_NUM": {
            "es_field": "HOME_CLIENT_NUM",
            "db_cn": "影响用户数",
            "label_cn": "影响用户数"
        },
        "ROOT_NETWORK_TYPE_TOP": {
            "es_field": "ROOT_NETWORK_TYPE_TOP",
            "db_cn": "根因专业",
            "label_cn": "根因专业"
        },
        "EVENT_SUMMARY": {
            "es_field": "EVENT_SUMMARY",
            "db_cn": "预处理步骤及结果",
            "label_cn": "预处理步骤及结果"
        },
        "EVENT_ROOT_CATEGORY": {
            "es_field": "EVENT_ROOT_CATEGORY",
            "db_cn": "故障根因分类",
            "label_cn": "故障根因分类"
        },
        "SPECIAL_FIELD17": {
            "es_field": "FAULT_DIAGNOSIS",
            "db_cn": "故障初判",
            "label_cn": "故障初判"
        },
        "CI": {
            "es_field": "CI",
            "db_cn": "CI",
            "label_cn": "CI"
        },
        "EXTRA_ID2": {
            "es_field": "",  # 表格中标注为"未找到"
            "db_cn": "",
            "label_cn": "额外ID2"
        },
        "EXTRA_STRING1": {
            "es_field": "",  # 表格中标注为"未找到"
            "db_cn": "",
            "label_cn": "额外字符串1"
        },
        "PORT_NUM": {
            "es_field": "PORT_NUM",
            "db_cn": "采集端口号",
            "label_cn": "采集端口号"
        },
        "NE_ADMIN_STATUS": {
            "es_field": "NE_ADMIN_STATUS",
            "db_cn": "告警对象管理状态",
            "label_cn": "告警对象管理状态"
        },
        "RELATED_MAINTAIN_GROUP": {
            "es_field": "RELATED_MAINTAIN_GROUP",
            "db_cn": "抄送维护组",
            "label_cn": "抄送维护组"
        },
    }
    
    conn = get_mysql_conn_dict_cursor()
    if not conn:
        print("❌ 无法连接数据库")
        return False
    
    try:
        updated_count = 0
        inserted_count = 0
        
        with conn.cursor() as cur:
            for kafka_field, values in updates.items():
                # 检查是否已存在
                cur.execute("SELECT id FROM kafka_field_meta WHERE kafka_field = %s", (kafka_field,))
                existing = cur.fetchone()
                
                if existing:
                    # 更新现有记录
                    cur.execute("""
                        UPDATE kafka_field_meta 
                        SET es_field = %s, db_cn = %s, label_cn = %s
                        WHERE kafka_field = %s
                    """, (values['es_field'], values['db_cn'], values['label_cn'], kafka_field))
                    updated_count += 1
                    print(f"✅ 更新: {kafka_field} -> {values['es_field']} ({values['db_cn']})")
                else:
                    # 插入新记录
                    cur.execute("""
                        INSERT INTO kafka_field_meta (kafka_field, es_field, db_cn, label_cn, is_enabled)
                        VALUES (%s, %s, %s, %s, 1)
                    """, (kafka_field, values['es_field'], values['db_cn'], values['label_cn']))
                    inserted_count += 1
                    print(f" 新增: {kafka_field} -> {values['es_field']} ({values['db_cn']})")
            
            conn.commit()
        
        print(f"\n✅ 更新完成！")
        print(f"   更新记录数: {updated_count}")
        print(f"   新增记录数: {inserted_count}")
        return True
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Kafka 字段元数据更新脚本")
    print("=" * 60)
    
    # 步骤1: 备份现有数据
    if not backup_field_meta():
        print("\n❌ 备份失败，终止更新")
        sys.exit(1)
    
    # 步骤2: 更新数据
    print("\n" + "=" * 60)
    if update_field_meta():
        print("\n✅ 全部完成！")
    else:
        print("\n 更新失败！")
        sys.exit(1)
