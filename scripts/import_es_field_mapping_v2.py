"""
从 CSV 文件导入 ES 字段映射到 MySQL 数据库
字段ES.csv 格式：ID,FIELD_INFO_ID,PARENT_ID,FIELD_NAME_EN,FIELD_NAME_CN,TABLE_NAME,...
"""
import csv
import mysql.connector
import sys
from pathlib import Path

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '12345678',
    'database': 'knowledge_base',
    'charset': 'utf8mb4'
}

def import_field_mapping():
    """从 CSV 文件导入字段映射"""
    csv_path = Path(__file__).parent.parent / 'test' / 'esToExcel' / '字段ES.csv'
    
    if not csv_path.exists():
        print(f"❌ CSV 文件不存在: {csv_path}")
        return False
    
    print(f"📖 读取 CSV 文件: {csv_path}")
    
    try:
        # 连接数据库
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS es_field_mapping (
            id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
            english_name VARCHAR(200) NOT NULL UNIQUE COMMENT '英文字段名',
            chinese_name VARCHAR(200) NOT NULL COMMENT '中文字段名',
            description VARCHAR(500) COMMENT '字段描述',
            is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
            sort_order INT DEFAULT 0 COMMENT '排序顺序',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_english_name (english_name),
            INDEX idx_chinese_name (chinese_name),
            INDEX idx_is_active (is_active)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='ES字段中英文映射表';
        """
        cursor.execute(create_table_sql)
        print("✅ 数据表已就绪")
        
        # 读取 CSV 文件
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # 跳过表头
            
            print(f"📋 CSV 表头: {headers}")
            
            # 批量插入数据
            insert_sql = """
            INSERT INTO es_field_mapping (english_name, chinese_name, description, is_active, sort_order)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                chinese_name = VALUES(chinese_name),
                description = VALUES(description),
                updated_at = CURRENT_TIMESTAMP
            """
            
            data = []
            row_count = 0
            for row in reader:
                row_count += 1
                if len(row) < 5:
                    print(f"⚠️  跳过第 {row_count} 行：列数不足")
                    continue
                
                field_name_en = row[3].strip()  # FIELD_NAME_EN
                field_name_cn = row[4].strip()  # FIELD_NAME_CN
                remark = row[9].strip() if len(row) > 9 else ''  # REMARK
                
                if field_name_en and field_name_cn:
                    data.append((field_name_en, field_name_cn, remark, True, row_count))
            
            if data:
                cursor.executemany(insert_sql, data)
                conn.commit()
                print(f"✅ 成功导入 {len(data)} 条字段映射")
            else:
                print("⚠️  没有有效数据可导入")
        
        # 查询统计
        cursor.execute("SELECT COUNT(*) FROM es_field_mapping")
        count = cursor.fetchone()[0]
        print(f"📈 数据库中共有 {count} 条字段映射记录")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("ES 字段映射导入工具")
    print("=" * 60)
    
    success = import_field_mapping()
    
    if success:
        print("\n✅ 导入完成！")
        sys.exit(0)
    else:
        print("\n❌ 导入失败！")
        sys.exit(1)
