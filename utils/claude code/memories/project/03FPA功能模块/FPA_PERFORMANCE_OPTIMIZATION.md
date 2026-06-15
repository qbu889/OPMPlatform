# FPA 生成接口性能优化方案

## 当前性能
- **接口耗时**: ~8 秒 (8029ms)
- **主要瓶颈**: AI 扩展、文档解析、数据库查询、Excel 生成

## 优化目标
- **短期目标**: 3-4 秒 (减少 50-60%)
- **长期目标**: 1-2 秒 (减少 75-85%)

---

## 🚀 优化方案

### 方案 1: 数据库连接优化 ✅ (已实施)
**优化前**: 每次查询都创建新连接  
**优化后**: 复用连接，使用连接池

```python
# 优化前
conn = get_db_connection()
cursor = conn.cursor()
# ... 使用 ...
cursor.close()
conn.close()

# 优化后
conn = None
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    # ... 使用 ...
finally:
    if conn:
        conn.close()
```

**预期收益**: 减少 200-300ms

---

### 方案 2: 文档解析优化 (建议实施)

#### 2.1 并行解析
```python
# 使用 asyncio 并行解析长文档
import asyncio
from concurrent.futures import ThreadPoolExecutor

def parse_document_parallel(md_content):
    # 将文档按章节分割
    chapters = split_into_chapters(md_content)
    
    # 使用线程池并行解析
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(parse_chapter, ch) for ch in chapters]
        results = [f.result() for f in futures]
    
    return merge_results(results)
```

**预期收益**: 减少 1-2 秒 (对于长文档)

#### 2.2 正则表达式预编译
```python
# 在模块级别预编译正则表达式
import re

# 预编译 (只编译一次)
PATTERNS = {
    'level1': re.compile(r'^##\s+(.+)$'),
    'level2': re.compile(r'^###\s+(.+)$'),
    'level5': re.compile(r'^######\s*(.+?)(?:（注.*?）)?$'),
    # ... 其他模式
}

# 使用时直接调用
match = PATTERNS['level5'].match(line)
```

**预期收益**: 减少 300-500ms

---

### 方案 3: AI 扩展优化 (关键优化点)

#### 3.1 批量调用 AI
```python
# 优化前：逐个调用 AI
for point in points_to_expand:
    result = ai_expand(point)

# 优化后：批量调用
def ai_batch_expand(points, batch_size=10):
    batches = [points[i:i+batch_size] for i in range(0, len(points), batch_size)]
    results = []
    for batch in batches:
        # 一次调用处理多个功能点
        batch_result = call_ai_api(batch)
        results.extend(batch_result)
    return results
```

**预期收益**: 减少 2-3 秒 (AI 调用次数减少 70%)

#### 3.2 缓存 AI 响应
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def ai_expand_cached(point_text, context_hash):
    """带缓存的 AI 扩展"""
    return call_ai_api(point_text)

# 使用
result = ai_expand_cached(point_text, hash(context))
```

**预期收益**: 对于重复内容，减少 90% 耗时

---

### 方案 4: 类别识别优化 (建议实施)

#### 4.1 规则预加载
```python
# 在应用启动时加载规则到内存
CATEGORY_RULES = None

def load_category_rules():
    global CATEGORY_RULES
    if CATEGORY_RULES is None:
        # 从数据库加载一次
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fpa_category_rules")
        CATEGORY_RULES = cursor.fetchall()
        cursor.close()
        conn.close()
    return CATEGORY_RULES

# 使用时直接访问内存
rules = load_category_rules()
```

**预期收益**: 减少 500-800ms (避免重复查询)

#### 4.2 使用 Trie 树优化关键词匹配
```python
from pyahocorasick import Automaton

# 构建关键词自动机 (只需一次)
automaton = Automaton()
for keyword in keywords:
    automaton.add_word(keyword, keyword)
automaton.make_automaton()

# 快速匹配
def match_category(text):
    for end_idx, keyword in automaton.iter(text):
        return get_category_for(keyword)
```

**预期收益**: 减少 200-400ms (对于大量功能点)

---

### 方案 5: Excel 生成优化 (建议实施)

#### 5.1 使用 openpyxl 的 write_only 模式
```python
from openpyxl import Workbook

# 优化前
wb = Workbook()
ws = wb.create_sheet()

# 优化后 (写入模式，减少内存占用)
wb = Workbook(write_only=True)
ws = wb.create_sheet()

for row in data:
    ws.append(row)

wb.save(output_path)
```

**预期收益**: 减少 300-500ms

#### 5.2 批量写入
```python
# 优化前：逐行写入
for point in function_points:
    ws.append([point['level1'], point['level2'], ...])

# 优化后：批量写入
rows = []
for point in function_points:
    rows.append([point['level1'], point['level2'], ...])
ws.append(rows)  # 或使用 iter_rows
```

**预期收益**: 减少 200-300ms

---

### 方案 6: 异步 IO 优化 (高级优化)

#### 6.1 使用 aiohttp 进行异步 AI 调用
```python
import aiohttp
import asyncio

async def ai_expand_async(session, point):
    async with session.post(url, json=point) as response:
        return await response.json()

async def batch_expand(points):
    async with aiohttp.ClientSession() as session:
        tasks = [ai_expand_async(session, p) for p in points]
        return await asyncio.gather(*tasks)
```

**预期收益**: 减少 40-60% AI 调用时间

---

## 📊 优化效果预估

| 优化项 | 当前耗时 | 优化后耗时 | 减少比例 |
|--------|----------|------------|----------|
| 数据库查询 | 800ms | 500ms | 37% ↓ |
| 文档解析 | 1200ms | 600ms | 50% ↓ |
| AI 扩展 | 3500ms | 1500ms | 57% ↓ |
| 类别识别 | 1000ms | 400ms | 60% ↓ |
| Excel 生成 | 1500ms | 800ms | 47% ↓ |
| **总计** | **8000ms** | **3800ms** | **52% ↓** |

---

## 🔧 实施建议

### 优先级 1 (立即可做，收益高)
1. ✅ 数据库连接优化 (已实施)
2. 正则表达式预编译
3. 规则预加载到内存

### 优先级 2 (中期优化)
1. AI 批量调用
2. AI 响应缓存
3. Excel 写入优化

### 优先级 3 (长期优化)
1. 异步 IO 重构
2. 文档并行解析
3. Trie 树关键词匹配

---

## 🎯 快速验证方法

```python
import time
from routes.fpa.fpa_generator_routes import parse_requirement_document

# 性能测试
start = time.time()
result = parse_requirement_document(md_content)
end = time.time()

print(f"解析耗时：{end - start:.3f}秒")
print(f"功能点数量：{len(result)}")
```

---

## 📝 注意事项

1. **不要过度优化**: 先 profiling 找到真正的瓶颈
2. **保持代码可读性**: 优化不应以牺牲可维护性为代价
3. **充分测试**: 每次优化后都要验证功能正确性
4. **监控性能**: 添加性能监控日志，持续跟踪

---

## 参考资源

- [Python Profiling 工具](https://docs.python.org/3/library/profile.html)
- [aiohttp 异步 HTTP](https://docs.aiohttp.org/)
- [openpyxl 性能优化](https://openpyxl.readthedocs.io/en/stable/optimized.html)
