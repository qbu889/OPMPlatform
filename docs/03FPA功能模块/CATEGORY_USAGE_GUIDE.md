# 专业领域分类管理系统 - 使用指南

## 🎯 功能概述

本系统支持基于**专业领域**的 FAQ 分类管理，实现更精准的智能客服问答匹配。

### 核心特性
- ✅ 可配置多个专业领域（如传输网、核心网、无线网等）
- ✅ 上传文档时选择所属领域
- ✅ FAQ 自动打上领域标签
- ✅ 提问时按领域过滤匹配
- ✅ 提高答案准确性和相关性

---

## 📋 使用步骤

### 步骤 1️⃣：配置专业领域

1. **访问管理页面**
   ```
   http://localhost:5001/api/category/page
   ```

2. **添加专业领域**
   - 输入领域名称（必填）
   - 填写描述（可选）
   - 选择颜色标识（用于界面展示）
   - 点击"添加"按钮

3. **示例领域**
   ```
   - 传输网
   - 核心网
   - 无线网
   - 数据网
   - 互联网
   - 电源和配套设备
   ```

4. **管理领域**
   - 编辑：点击编辑图标修改名称、描述、颜色
   - 停用：取消勾选"启用状态"
   - 删除：点击删除图标（软删除）

---

### 步骤 2️⃣：上传文档并选择领域

#### 方式 A：通过前端表单上传

```html
<form action="/api/chatbot/upload_document" method="POST" enctype="multipart/form-data">
    <!-- 选择文件 -->
    <input type="file" name="file" required>
    
    <!-- 选择领域 -->
    <select name="domain_id" required>
        <option value="">-- 请选择专业领域 --</option>
        <!-- 动态加载领域列表 -->
    </select>
    
    <button type="submit">上传文档</button>
</form>
```

#### 方式 B：通过 API 调用

```bash
curl -X POST 'http://localhost:5001/api/chatbot/upload_document' \
  -F 'file=@事件工单运维手册.md' \
  -F 'domain_id=1'
```

**请求参数说明：**
- `file`: 上传的文档文件（必填）
- `domain_id`: 专业领域 ID（可选，建议填写）

**响应示例：**
```json
{
  "success": true,
  "document_id": 123,
  "filename": "事件工单运维手册.md",
  "message": "文档已上传，FAQ 正在后台提取中...",
  "domain_id": 1,
  "status": "processing"
}
```

---

### 步骤 3️⃣：提问时选择领域

#### API 调用示例

```bash
curl -X POST 'http://localhost:5001/api/chatbot/chat' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "如何排查事件工单漏清除？",
    "domain_id": 1
  }'
```

**请求参数：**
- `message`: 用户问题（必填）
- `domain_id`: 专业领域 ID（可选）
  - 如果提供：只在该领域内匹配 FAQ
  - 如果不提供：在所有领域内搜索

**响应示例：**
```json
{
  "success": true,
  "answer": "排查步骤如下：\n1. 根据用户反馈工单号查询...\n...",
  "source": "knowledge_base",
  "retrieved_faqs": [
    {
      "id": 456,
      "question": "如何排查事件工单是否漏清除？",
      "answer": "完整的排查步骤...",
      "domain_id": 1,
      "similarity_score": 0.95
    }
  ],
  "domain_id": 1
}
```

---

## 🔧 技术实现细节

### 数据库表结构

#### 1. categories 表（专业领域）
```sql
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,      -- 领域名称
    description TEXT,                        -- 描述
    color VARCHAR(20) DEFAULT '#1890ff',    -- 颜色标识
    is_active TINYINT DEFAULT 1,            -- 是否启用
    sort_order INT DEFAULT 0,               -- 排序顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. faqs 表（增加 domain_id 字段）
```sql
ALTER TABLE faqs ADD COLUMN domain_id INT AFTER category;
-- domain_id 关联 categories.id
```

### 核心 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/category/list` | GET | 获取领域列表 |
| `/api/category/add` | POST | 添加领域 |
| `/api/category/update` | POST | 更新领域 |
| `/api/category/delete` | POST | 删除领域 |
| `/api/chatbot/upload_document` | POST | 上传文档（支持 domain_id） |
| `/api/chatbot/chat` | POST | 智能问答（支持 domain_id） |

### FAQ 提取流程

```
用户上传文档 + 选择 domain_id
    ↓
保存文档记录（包含 domain_id）
    ↓
后台线程异步提取 FAQ
    ↓
每个 FAQ 自动添加 domain_id 标签
    ↓
批量存入 faqs 表
```

---

## 🎨 前端集成示例

### 动态加载领域列表

```javascript
// 加载领域列表到下拉框
function loadCategories() {
    fetch('/api/category/list')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('domainSelect');
            data.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
        });
}
```

### 带领域的提问

```javascript
function askQuestion() {
    const message = document.getElementById('userInput').value;
    const domainId = document.getElementById('domainSelect').value;
    
    fetch('/api/chatbot/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            message: message,
            domain_id: parseInt(domainId)
        })
    })
    .then(response => response.json())
    .then(data => {
        // 显示答案
        console.log(data.answer);
    });
}
```

---

## ✅ 测试验证

### 1. 测试领域管理
```bash
# 获取领域列表
curl http://localhost:5001/api/category/list

# 添加领域
curl -X POST http://localhost:5001/api/category/add \
  -H 'Content-Type: application/json' \
  -d '{"name":"传输网","description":"传输网络相关","color":"#1890ff"}'
```

### 2. 测试带领域的文档上传
```bash
curl -X POST http://localhost:5001/api/chatbot/upload_document \
  -F 'file=@test.md' \
  -F 'domain_id=1'
```

### 3. 测试按领域问答
```bash
curl -X POST http://localhost:5001/api/chatbot/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"排查步骤","domain_id":1}'
```

---

## 🚀 优势总结

1. **精准匹配**：按领域过滤，避免跨专业误匹配
2. **灵活配置**：管理员可随时添加/修改领域
3. **自动标注**：FAQ 提取时自动打标签
4. **向后兼容**：不传 domain_id 时全局搜索
5. **可视化管理**：美观的前端管理界面

---

## 📝 注意事项

1. **领域 ID 必须存在**：上传文档前需先创建对应领域
2. **领域名称唯一**：不允许重名领域
3. **软删除机制**：删除领域只是标记为 inactive，数据保留
4. **领域停用影响**：停用的领域不会出现在下拉列表中，但历史 FAQ 仍保留

---

## 🛠️ 下一步优化建议

- [ ] 在聊天界面添加领域选择器
- [ ] 支持多领域联合搜索
- [ ] 领域统计分析（FAQ 数量、热度等）
- [ ] 领域权限控制（不同用户组访问不同领域）
- [ ] 领域推荐（根据问题自动推荐领域）

---

**开发完成时间**: 2026-03-08  
**版本**: v1.0
