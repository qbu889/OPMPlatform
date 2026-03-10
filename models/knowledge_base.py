# models/knowledge_base.py
"""知识库数据模型 - MySQL 版本"""

import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import os
import pymysql


class KnowledgeBaseManager:
    """知识库管理器（MySQL）"""
    
    def __init__(self):
        # 使用 MySQL
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', '123456'),
            'database': os.getenv('KNOWLEDGE_BASE_DB', 'knowledge_base'),
            'charset': os.getenv('MYSQL_CHARSET', 'utf8mb4')
        }
        
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 文档表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                original_filename VARCHAR(255),
                file_type VARCHAR(50),
                file_size INT,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                content_hash VARCHAR(255),
                status VARCHAR(20) DEFAULT 'active',
                metadata TEXT,
                created_by INT,
                FOREIGN KEY (created_by) REFERENCES users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 专业领域表（新增）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                color VARCHAR(20) DEFAULT '#1890ff',
                is_active TINYINT DEFAULT 1,
                sort_order INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # FAQ 表增加 domain_id 字段
        try:
            cursor.execute('''
                ALTER TABLE faqs ADD COLUMN domain_id INT AFTER category
            ''')
        except Exception as e:
            # 字段可能已存在
            if 'Duplicate column name' not in str(e):
                raise
        
        # FAQ 表（知识库核心）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faqs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                document_id INT,
                category VARCHAR(100),
                tags TEXT,
                similarity_score FLOAT DEFAULT 0.0,
                view_count INT DEFAULT 0,
                is_verified TINYINT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 对话历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                user_id INT,
                message_role VARCHAR(20) NOT NULL,
                message_content TEXT NOT NULL,
                related_faq_ids TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建索引
        try:
            cursor.execute('CREATE INDEX idx_faqs_question ON faqs(question)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_faqs_category ON faqs(category)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_faqs_domain ON faqs(domain_id)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_faqs_tags ON faqs(tags(255))')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_conversation_session ON conversation_history(session_id)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_conversation_user ON conversation_history(user_id)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_categories_name ON categories(name)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        try:
            cursor.execute('CREATE INDEX idx_categories_active ON categories(is_active)')
        except Exception as e:
            if 'Duplicate key name' not in str(e):
                raise
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """获取数据库连接"""
        return pymysql.connect(**self.mysql_config)
    
    # ========== 文档管理方法 ==========
    
    def add_document(self, filename: str, original_filename: str, file_type: str, 
                     file_size: int = None, content_hash: str = None, 
                     metadata: Dict = None, created_by: int = None) -> int:
        """添加文档记录"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO documents (filename, original_filename, file_type, file_size, 
                                      content_hash, metadata, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (filename, original_filename, file_type, file_size, 
                  content_hash, json.dumps(metadata) if metadata else None, created_by))
            
            conn.commit()
            doc_id = cursor.lastrowid
            conn.close()
            
            return doc_id
        except Exception as e:
            print(f"添加文档失败：{e}")
            return -1
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """获取文档信息"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM documents WHERE id = %s', (doc_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'filename': row[1],
                    'original_filename': row[2],
                    'file_type': row[3],
                    'file_size': row[4],
                    'upload_time': row[5],
                    'content_hash': row[6],
                    'status': row[7],
                    'metadata': json.loads(row[8]) if row[8] else None,
                    'created_by': row[9]
                }
            return None
        except Exception as e:
            print(f"获取文档失败：{e}")
            return None
    
    def list_documents(self, status: str = 'active') -> List[Dict]:
        """获取文档列表"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM documents WHERE status = %s ORDER BY upload_time DESC', (status,))
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'filename': row[1],
                'original_filename': row[2],
                'file_type': row[3],
                'file_size': row[4],
                'upload_time': row[5],
                'status': row[7]
            } for row in rows]
        except Exception as e:
            print(f"获取文档列表失败：{e}")
            return []
    
    def delete_document(self, doc_id: int) -> bool:
        """删除文档（软删除）"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE documents SET status = %s WHERE id = %s', ('deleted', doc_id))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"删除文档失败：{e}")
            return False
    
    # ========== FAQ 管理方法 ==========
    
    def add_faq(self, question: str, answer: str, document_id: int = None,
                category: str = None, tags: List[str] = None) -> int:
        """添加 FAQ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO faqs (question, answer, document_id, category, tags)
                VALUES (%s, %s, %s, %s, %s)
            ''', (question, answer, document_id, category, 
                  ','.join(tags) if tags else None))
            
            faq_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return faq_id
        except Exception as e:
            print(f"添加 FAQ 失败：{e}")
            return -1
    
    def batch_add_faqs(self, faqs: List[Dict]) -> int:
        """批量添加 FAQ"""
        count = 0
        for faq in faqs:
            faq_id = self.add_faq(
                question=faq.get('question'),
                answer=faq.get('answer'),
                document_id=faq.get('document_id'),
                category=faq.get('category'),
                tags=faq.get('tags')
            )
            if faq_id > 0:
                count += 1
        return count
    
    def search_faqs(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索 FAQ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 使用全文搜索（简单 LIKE 匹配，可升级为 FTS5）
            cursor.execute('''
                SELECT id, question, answer, category, tags, similarity_score, view_count
                FROM faqs
                WHERE question LIKE %s OR answer LIKE %s OR tags LIKE %s
                ORDER BY view_count DESC, created_at DESC
                LIMIT %s
            ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'question': row[1],
                'answer': row[2],
                'category': row[3],
                'tags': row[4].split(',') if row[4] else [],
                'similarity_score': row[5],
                'view_count': row[6]
            } for row in rows]
        except Exception as e:
            print(f"搜索 FAQ 失败：{e}")
            return []
    
    def get_faq(self, faq_id: int) -> Optional[Dict]:
        """获取 FAQ 详情"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM faqs WHERE id = %s', (faq_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'question': row[1],
                    'answer': row[2],
                    'document_id': row[3],
                    'category': row[4],
                    'tags': row[5].split(',') if row[5] else [],
                    'view_count': row[7],
                    'is_verified': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                }
            return None
        except Exception as e:
            print(f"获取 FAQ 失败：{e}")
            return None
    
    def increment_faq_view(self, faq_id: int) -> bool:
        """增加 FAQ 浏览次数"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('UPDATE faqs SET view_count = view_count + 1 WHERE id = %s', (faq_id,))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"更新浏览次数失败：{e}")
            return False
    
    def list_all_faqs(self) -> List[Dict]:
        """获取所有 FAQ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM faqs ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'question': row[1],
                'answer': row[2],
                'category': row[4],
                'tags': row[5].split(',') if row[5] else [],
                'view_count': row[7],
                'is_verified': row[8]
            } for row in rows]
        except Exception as e:
            print(f"获取 FAQ 列表失败：{e}")
            return []
    
    # ========== 对话历史方法 ==========
    
    def add_conversation_message(self, session_id: str, message_role: str, 
                                  message_content: str, user_id: int = None,
                                  related_faq_ids: List[int] = None) -> int:
        """添加对话消息"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversation_history (session_id, user_id, message_role, 
                                                  message_content, related_faq_ids)
                VALUES (%s, %s, %s, %s, %s)
            ''', (session_id, user_id, message_role, message_content,
                  json.dumps(related_faq_ids) if related_faq_ids else None))
            
            msg_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return msg_id
        except Exception as e:
            print(f"添加对话消息失败：{e}")
            return -1
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取对话历史"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, message_role, message_content, related_faq_ids, created_at
                FROM conversation_history
                WHERE session_id = %s
                ORDER BY created_at ASC
                LIMIT %s
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'related_faq_ids': json.loads(row[3]) if row[3] else [],
                'created_at': row[4]
            } for row in rows]
        except Exception as e:
            print(f"获取对话历史失败：{e}")
            return []
    
    def clear_conversation_history(self, session_id: str) -> bool:
        """清空对话历史"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM conversation_history WHERE session_id = %s', (session_id,))
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"清空对话历史失败：{e}")
            return False
    
    # ========== 专业领域管理方法（新增） ==========
    
    def add_category(self, name: str, description: str = None, color: str = '#1890ff') -> int:
        """添加专业领域"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO categories (name, description, color)
                VALUES (%s, %s, %s)
            ''', (name, description, color))
            
            category_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return category_id
        except Exception as e:
            print(f"添加专业领域失败：{e}")
            return -1
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """获取专业领域详情"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM categories WHERE id = %s', (category_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'color': row[3],
                    'is_active': row[4],
                    'sort_order': row[5]
                }
            return None
        except Exception as e:
            print(f"获取专业领域失败：{e}")
            return None
    
    def list_categories(self, active_only: bool = True) -> List[Dict]:
        """获取专业领域列表"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if active_only:
                cursor.execute('SELECT * FROM categories WHERE is_active = 1 ORDER BY sort_order, name')
            else:
                cursor.execute('SELECT * FROM categories ORDER BY sort_order, name')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'color': row[3],
                'is_active': row[4],
                'sort_order': row[5]
            } for row in rows]
        except Exception as e:
            print(f"获取专业领域列表失败：{e}")
            return []
    
    def update_category(self, category_id: int, name: str = None, 
                       description: str = None, color: str = None,
                       is_active: bool = None) -> bool:
        """更新专业领域"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name:
                updates.append('name = %s')
                params.append(name)
            if description is not None:
                updates.append('description = %s')
                params.append(description)
            if color:
                updates.append('color = %s')
                params.append(color)
            if is_active is not None:
                updates.append('is_active = %s')
                params.append(is_active)
            
            if updates:
                params.append(category_id)
                sql = f"UPDATE categories SET {','.join(updates)} WHERE id = %s"
                cursor.execute(sql, params)
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"更新专业领域失败：{e}")
            return False
    
    def delete_category(self, category_id: int) -> bool:
        """删除专业领域（软删除）"""
        return self.update_category(category_id, is_active=0)
    
    def search_faqs_by_domain(self, keyword: str, domain_id: int = None, limit: int = 10) -> List[Dict]:
        """按专业领域搜索 FAQ"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if domain_id:
                cursor.execute('''
                    SELECT id, question, answer, category, tags, similarity_score, view_count, domain_id
                    FROM faqs
                    WHERE domain_id = %s AND (question LIKE %s OR answer LIKE %s OR tags LIKE %s)
                    ORDER BY view_count DESC, created_at DESC
                    LIMIT %s
                ''', (domain_id, f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            else:
                cursor.execute('''
                    SELECT id, question, answer, category, tags, similarity_score, view_count, domain_id
                    FROM faqs
                    WHERE question LIKE %s OR answer LIKE %s OR tags LIKE %s
                    ORDER BY view_count DESC, created_at DESC
                    LIMIT %s
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'id': row[0],
                'question': row[1],
                'answer': row[2],
                'category': row[3],
                'tags': row[4].split(',') if row[4] else [],
                'similarity_score': row[5],
                'view_count': row[6],
                'domain_id': row[7]
            } for row in rows]
        except Exception as e:
            print(f"按领域搜索 FAQ 失败：{e}")
            return []


# 全局知识库管理器实例
knowledge_base_manager = KnowledgeBaseManager()
