"""
SQL 智能生成器路由
功能：根据表结构和自然语言描述，自动生成 SQL 语句
支持：复杂查询、多表关联、聚合、子查询等
"""
from flask import Blueprint, request, jsonify, render_template
import logging
import json

sql_generator_bp = Blueprint('sql_generator', __name__)
logger = logging.getLogger(__name__)

@sql_generator_bp.route('/sql-generator')
def sql_generator_page():
    """SQL 智能生成器页面 - 已由 Vue 前端处理"""
    # Vue 前端会通过 Vite 代理访问此路由
    # 这里只需要返回成功,实际页面由 Vue 渲染
    from flask import jsonify
    return jsonify({'success': True, 'message': 'SQL Generator - Vue Frontend'})

@sql_generator_bp.route('/api/generate-sql', methods=['POST'])
def generate_sql():
    """
    根据表结构和需求生成 SQL
    
    请求参数：
    {
        "table_structure": "表结构信息（JSON 或文本）",
        "requirement": "需求描述（自然语言）",
        "database_type": "数据库类型（mysql/postgresql/oracle）",
        "sql_type": "SQL类型（select/insert/update/delete）",
        "optimization": "是否优化SQL（boolean）"
    }
    """
    try:
        data = request.json
        
        # 支持驼峰和下划线两种命名
        table_structure = data.get('table_structure') or data.get('tableStructure', '')
        requirement = data.get('requirement', '')
        database_type = data.get('database_type') or data.get('databaseType', 'mysql')
        sql_type = data.get('sql_type') or data.get('sqlType', 'select')
        optimization = data.get('optimization', True)
        
        if not table_structure or not requirement:
            return jsonify({
                'success': False,
                'message': '请提供表结构和需求描述'
            }), 400
        
        logger.info(f"收到 SQL 生成请求 - 数据库: {database_type}, 类型: {sql_type}")
        
        # 构建 AI 提示词
        prompt = build_sql_generation_prompt(
            table_structure, 
            requirement, 
            database_type, 
            sql_type,
            optimization
        )
        
        # 调用 AI 生成 SQL
        from utils.ollama_client import get_ollama_client
        client = get_ollama_client()
        
        response = client.chat(
            messages=[
                {
                    "role": "system",
                    "content": """你是一个专业的 SQL 生成助手，精通各种数据库的 SQL 语法。
你的任务是根据用户提供的表结构和需求，生成高质量、高效的 SQL 语句。

支持的数据库类型：
- MySQL: 标准 MySQL 语法
- PostgreSQL: PostgreSQL 语法，支持窗口函数、CTE
- Oracle: Oracle 语法，支持 ROWNUM、CONNECT BY
- SQL Server: T-SQL 语法，支持 TOP、CTE
- SQLite: SQLite 轻量级语法
- 达梦数据库(DM): 兼容 Oracle 语法，支持：
  * 使用 SYS_GUID() 生成唯一 ID
  * 使用 SYSDATE 获取当前时间
  * 支持 Oracle 风格的 ROWID、ROWNUM
  * 支持 CONNECT BY 递归查询
  * 数据类型：VARCHAR2, NUMBER, DATE, CLOB, BLOB
  * 分页：ROWNUM 或 OFFSET/FETCH

要求：
1. 生成的 SQL 必须符合指定的数据库语法
2. 如果需求涉及复杂查询，使用合适的 JOIN、子查询、窗口函数等
3. 添加必要的注释说明 SQL 的逻辑
4. 如果可能，提供 SQL 优化建议
5. 只返回 SQL 语句和相关说明，不要其他内容

输出格式：
```sql
-- SQL 语句
SELECT ...
```

说明：
- 简要说明 SQL 的逻辑
- 如果有优化建议，在这里说明
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # chat() 直接返回字符串内容
        generated_sql = response if isinstance(response, str) else response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 提取 SQL 语句和说明
        sql_result = extract_sql_and_explanation(generated_sql)
        
        logger.info(f"SQL 生成成功，长度: {len(generated_sql)} 字符")
        
        return jsonify({
            'success': True,
            'data': {
                'sql': sql_result['sql'],
                'explanation': sql_result['explanation'],
                'database_type': database_type,
                'sql_type': sql_type
            }
        })
        
    except Exception as e:
        logger.error(f"SQL 生成失败: {e}")
        return jsonify({
            'success': False,
            'message': f'SQL 生成失败: {str(e)}'
        }), 500

@sql_generator_bp.route('/api/optimize-sql', methods=['POST'])
def optimize_sql():
    """
    优化现有 SQL 语句
    
    请求参数：
    {
        "sql": "原始 SQL 语句",
        "table_structure": "表结构信息",
        "database_type": "数据库类型"
    }
    """
    try:
        data = request.json
        sql = data.get('sql', '')
        table_structure = data.get('table_structure', '')
        database_type = data.get('database_type', 'mysql')
        
        if not sql:
            return jsonify({
                'success': False,
                'message': '请提供 SQL 语句'
            }), 400
        
        logger.info(f"收到 SQL 优化请求 - 数据库: {database_type}")
        
        prompt = f"""请优化以下 {database_type.upper()} SQL 语句：

表结构信息：
{table_structure}

原始 SQL：
{sql}

请提供：
1. 优化后的 SQL
2. 优化说明（为什么这样优化）
3. 性能提升建议
"""
        
        from utils.ollama_client import get_ollama_client
        client = get_ollama_client()
        
        response = client.chat(
            messages=[
                {
                    "role": "system",
                    "content": """你是一个 SQL 优化专家。请分析用户提供的 SQL 语句，并提供优化版本。

优化原则：
1. 使用合适的索引
2. 避免 SELECT *
3. 优化 JOIN 顺序
4. 使用 EXISTS 替代 IN（适当场景）
5. 避免在 WHERE 子句中使用函数
6. 合理使用子查询和 CTE
7. 添加必要的注释
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # chat() 直接返回字符串
        optimized_result = response if isinstance(response, str) else response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return jsonify({
            'success': True,
            'data': {
                'optimized_sql': optimized_result,
                'database_type': database_type
            }
        })
        
    except Exception as e:
        logger.error(f"SQL 优化失败: {e}")
        return jsonify({
            'success': False,
            'message': f'SQL 优化失败: {str(e)}'
        }), 500

@sql_generator_bp.route('/api/explain-sql', methods=['POST'])
def explain_sql():
    """
    解释 SQL 语句的含义
    
    请求参数：
    {
        "sql": "需要解释的 SQL 语句",
        "table_structure": "表结构信息（可选）"
    }
    """
    try:
        data = request.json
        sql = data.get('sql', '')
        table_structure = data.get('table_structure', '')
        
        if not sql:
            return jsonify({
                'success': False,
                'message': '请提供 SQL 语句'
            }), 400
        
        logger.info(f"收到 SQL 解释请求")
        
        prompt = f"""请详细解释以下 SQL 语句的作用和执行逻辑：

表结构（如果有）：
{table_structure}

SQL 语句：
{sql}

请解释：
1. 这个 SQL 的功能是什么
2. 执行逻辑和步骤
3. 涉及哪些表和字段
4. 可能的性能问题
"""
        
        from utils.ollama_client import get_ollama_client
        client = get_ollama_client()
        
        response = client.chat(
            messages=[
                {
                    "role": "system",
                    "content": "你是一个 SQL 教学助手。请用通俗易懂的语言解释 SQL 语句的功能和执行逻辑。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # chat() 直接返回字符串
        explanation = response if isinstance(response, str) else response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return jsonify({
            'success': True,
            'data': {
                'explanation': explanation,
                'sql': sql
            }
        })
        
    except Exception as e:
        logger.error(f"SQL 解释失败: {e}")
        return jsonify({
            'success': False,
            'message': f'SQL 解释失败: {str(e)}'
        }), 500


def build_sql_generation_prompt(table_structure, requirement, database_type, sql_type, optimization):
    """构建 SQL 生成的提示词"""
    
    # 达梦数据库特殊处理
    dm_note = ""
    if database_type.lower() == 'dameng':
        dm_note = """

达梦数据库(DM)语法提示：
- 兼容 Oracle 语法
- 使用 SYS_GUID() 生成唯一 ID（代替 UUID）
- 使用 SYSDATE 获取当前时间
- 支持 ROWNUM 分页：SELECT * FROM table WHERE ROWNUM <= 10
- 支持 Oracle 风格的递归查询：CONNECT BY PRIOR
- 数据类型：VARCHAR2, NUMBER, DATE, CLOB, BLOB
- 字符串拼接使用 || 运算符
- 分页也可使用：OFFSET x ROWS FETCH NEXT y ROWS ONLY
"""
    
    prompt = f"""请根据以下信息生成 {database_type.upper()} {sql_type.upper()} 语句：

数据库类型：{database_type}
SQL 类型：{sql_type}

表结构信息：
{table_structure}

需求描述：
{requirement}
{dm_note}
要求：
1. 生成的 SQL 必须符合 {database_type.upper()} 语法
2. 如果需求不明确，请做出合理假设并在说明中注明
3. 添加必要的注释
4. 如果开启了优化，请提供优化建议
5. 只返回 SQL 和说明，不要其他内容

{"""6. 需要对 SQL 进行优化" """ if optimization else ""}
"""
    
    return prompt


def extract_sql_and_explanation(text):
    """从 AI 响应中提取 SQL 语句和说明"""
    
    import re
    
    # 提取 SQL 代码块
    sql_match = re.search(r'```(?:sql)?\s*(.*?)\s*```', text, re.DOTALL)
    
    if sql_match:
        sql = sql_match.group(1).strip()
        # 移除说明部分
        explanation = text[:sql_match.start()].strip()
        explanation_after = text[sql_match.end():].strip()
        explanation = (explanation + '\n\n' + explanation_after).strip()
    else:
        # 如果没有代码块，尝试提取 SQL 语句
        lines = text.split('\n')
        sql_lines = []
        explanation_lines = []
        
        in_sql = False
        for line in lines:
            if line.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE', 'ALTER')):
                in_sql = True
                sql_lines.append(line)
            elif in_sql and (line.strip() == '' or line.strip().startswith('--')):
                sql_lines.append(line)
            elif not in_sql:
                explanation_lines.append(line)
            else:
                explanation_lines.append(line)
        
        sql = '\n'.join(sql_lines).strip()
        explanation = '\n'.join(explanation_lines).strip()
    
    return {
        'sql': sql,
        'explanation': explanation
    }
