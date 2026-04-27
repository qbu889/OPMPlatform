<template>
  <div class="sql-generator">
    <div class="page-header">
      <h1> SQL 智能生成器</h1>
      <p class="subtitle">基于 AI 的智能 SQL 生成工具,支持复杂查询、多表关联、性能优化</p>
    </div>

    <!-- 统计面板 -->
    <div class="stats-panel">
      <div class="stat-card">
        <div class="stat-number">{{ stats.totalGenerated }}</div>
        <div class="stat-label">已生成 SQL</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.successRate }}%</div>
        <div class="stat-label">成功率</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.avgTime || '-' }}</div>
        <div class="stat-label">平均耗时</div>
      </div>
    </div>

    <div class="content-wrapper">
      <!-- 输入区域 -->
      <div class="input-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header-content">
              <el-icon><Document /></el-icon>
              <span>📋 输入信息</span>
            </div>
          </template>
          
          <el-form label-position="top">
            <el-form-item label="🗄️ 数据库类型">
              <el-select v-model="formData.databaseType" style="width: 100%">
                <el-option label="MySQL" value="mysql" />
                <el-option label="PostgreSQL" value="postgresql" />
                <el-option label="Oracle" value="oracle" />
                <el-option label="SQL Server" value="sqlserver" />
                <el-option label="SQLite" value="sqlite" />
                <el-option label="达梦数据库(DM)" value="dameng" />
              </el-select>
            </el-form-item>

            <el-form-item label="📝 SQL 类型">
              <el-select v-model="formData.sqlType" style="width: 100%">
                <el-option label="SELECT（查询）" value="select" />
                <el-option label="INSERT（插入）" value="insert" />
                <el-option label="UPDATE（更新）" value="update" />
                <el-option label="DELETE（删除）" value="delete" />
                <el-option label="CREATE（创建表）" value="create" />
              </el-select>
            </el-form-item>

            <el-form-item label="📊 表结构信息">
              <el-input
                v-model="formData.tableStructure"
                type="textarea"
                :rows="8"
                placeholder="请输入表结构信息,支持以下格式:

1. SQL CREATE 语句:
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

2. JSON 格式:
{
  &quot;table&quot;: &quot;users&quot;,
  &quot;columns&quot;: [
    {&quot;name&quot;: &quot;id&quot;, &quot;type&quot;: &quot;INT&quot;},
    {&quot;name&quot;: &quot;name&quot;, &quot;type&quot;: &quot;VARCHAR(50)&quot;}
  ]
}

3. 文本描述:
表名: users
字段:
- id (INT, 主键)
- name (VARCHAR(50))
- age (INT)"
              />
            </el-form-item>

            <el-form-item label="💡 需求描述">
              <el-input
                v-model="formData.requirement"
                type="textarea"
                :rows="4"
                placeholder="请描述您需要的 SQL 功能,例如:
- 查询所有年龄大于 18 岁的用户
- 统计每个部门的员工数量
- 关联订单表和用户表,查询用户的订单信息"
              />
            </el-form-item>

            <el-form-item>
              <el-checkbox v-model="formData.optimization">启用 SQL 优化建议</el-checkbox>
            </el-form-item>

            <div class="example-buttons">
              <el-button size="small" @click="loadExample(1)">示例 1: 基础查询</el-button>
              <el-button size="small" @click="loadExample(2)">示例 2: 多表关联</el-button>
              <el-button size="small" @click="loadExample(3)">示例 3: 聚合统计</el-button>
              <el-button size="small" @click="loadExample(4)">示例 4: 复杂查询</el-button>
            </div>

            <el-form-item style="margin-top: 20px">
              <el-button
                type="primary"
                size="large"
                @click="generateSQL"
                :loading="generating"
                style="width: 100%; height: 48px; font-size: 16px"
              >
                <el-icon v-if="!generating"><MagicStick /></el-icon>
                {{ generating ? '生成中...' : '生成 SQL' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 结果区域 -->
      <div class="result-section">
        <el-card class="section-card">
          <template #header>
            <div class="card-header-content">
              <el-icon><Check /></el-icon>
              <span>✅ 生成结果</span>
              <div class="header-actions" v-if="result.sql">
                <el-button size="small" @click="copySQL">
                  <el-icon><CopyDocument /></el-icon>
                  复制 SQL
                </el-button>
                <el-button size="small" @click="optimizeSQL">
                  <el-icon><Tools /></el-icon>
                  优化 SQL
                </el-button>
                <el-button size="small" @click="explainSQL">
                  <el-icon><QuestionFilled /></el-icon>
                  解释 SQL
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="!result.sql && !generating" class="empty-result">
            <el-empty description="输入表结构和需求,点击生成 SQL" />
          </div>

          <div v-else class="result-content">
            <div class="sql-output">
              <div class="sql-code">{{ result.sql }}</div>
            </div>

            <div v-if="result.explanation" class="explanation">
              <div class="explanation-title">📖 SQL 说明</div>
              <div class="explanation-content">{{ result.explanation }}</div>
            </div>
          </div>
        </el-card>

        <!-- 历史记录 -->
        <el-card class="section-card history-card" v-if="history.length > 0">
          <template #header>
            <div class="card-header-content">
              <el-icon><Clock /></el-icon>
              <span>📜 历史记录</span>
              <el-button size="small" type="danger" @click="clearHistory">清空</el-button>
            </div>
          </template>

          <div class="history-list">
            <div
              v-for="(item, index) in history"
              :key="index"
              class="history-item"
              @click="loadHistory(item)"
            >
              <div class="history-time">{{ item.time }}</div>
              <div class="history-sql">{{ item.sql.substring(0, 50) }}...</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  MagicStick,
  CopyDocument,
  Tools,
  QuestionFilled,
  Check,
  Clock
} from '@element-plus/icons-vue'

const formData = reactive({
  databaseType: 'mysql',
  sqlType: 'select',
  tableStructure: '',
  requirement: '',
  optimization: true
})

const result = reactive({
  sql: '',
  explanation: ''
})

const generating = ref(false)
const history = ref([])
const stats = reactive({
  totalGenerated: 0,
  successRate: 100,
  avgTime: 0,
  totalRequests: 0,
  failedRequests: 0,
  totalTime: 0
})

// 加载历史记录
onMounted(() => {
  const saved = localStorage.getItem('sqlGeneratorHistory')
  if (saved) {
    history.value = JSON.parse(saved)
  }
  const savedStats = localStorage.getItem('sqlGeneratorStats')
  if (savedStats) {
    Object.assign(stats, JSON.parse(savedStats))
  }
})

// 保存历史记录
const saveHistory = () => {
  localStorage.setItem('sqlGeneratorHistory', JSON.stringify(history.value))
  localStorage.setItem('sqlGeneratorStats', JSON.stringify(stats))
}

// 生成 SQL
const generateSQL = async () => {
  if (!formData.tableStructure || !formData.requirement) {
    ElMessage.warning('请填写表结构和需求描述')
    return
  }

  generating.value = true
  const startTime = Date.now()

  try {
    const response = await fetch('/api/generate-sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData)
    })

    const data = await response.json()

    if (data.success) {
      result.sql = data.data.sql
      result.explanation = data.data.explanation

      // 更新统计
      stats.totalGenerated++
      stats.totalRequests++
      const duration = ((Date.now() - startTime) / 1000).toFixed(2)
      stats.totalTime += parseFloat(duration)
      stats.avgTime = (stats.totalTime / stats.totalRequests).toFixed(2)
      stats.successRate = ((stats.totalRequests - stats.failedRequests) / stats.totalRequests * 100).toFixed(1)

      // 添加历史记录
      history.value.unshift({
        time: new Date().toLocaleString(),
        sql: data.data.sql,
        explanation: data.data.explanation,
        duration: duration
      })
      if (history.value.length > 20) history.value.pop()

      saveHistory()
      ElMessage.success('SQL 生成成功')
    } else {
      stats.failedRequests++
      stats.totalRequests++
      stats.successRate = ((stats.totalRequests - stats.failedRequests) / stats.totalRequests * 100).toFixed(1)
      saveHistory()
      ElMessage.error(data.message || '生成失败')
    }
  } catch (error) {
    stats.failedRequests++
    stats.totalRequests++
    stats.successRate = ((stats.totalRequests - stats.failedRequests) / stats.totalRequests * 100).toFixed(1)
    saveHistory()
    ElMessage.error('网络错误: ' + error.message)
  } finally {
    generating.value = false
  }
}

// 复制 SQL
const copySQL = () => {
  navigator.clipboard.writeText(result.sql)
  ElMessage.success('SQL 已复制到剪贴板')
}

// 优化 SQL
const optimizeSQL = async () => {
  if (!result.sql) return

  try {
    const response = await fetch('/api/optimize-sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sql: result.sql,
        table_structure: formData.tableStructure,
        database_type: formData.databaseType
      })
    })

    const data = await response.json()
    if (data.success) {
      result.sql = data.data.optimized_sql
      ElMessage.success('SQL 优化成功')
    }
  } catch (error) {
    ElMessage.error('优化失败: ' + error.message)
  }
}

// 解释 SQL
const explainSQL = async () => {
  if (!result.sql) return

  try {
    const response = await fetch('/api/explain-sql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sql: result.sql,
        database_type: formData.databaseType
      })
    })

    const data = await response.json()
    if (data.success) {
      result.explanation = data.data.explanation
      ElMessage.success('SQL 解释成功')
    }
  } catch (error) {
    ElMessage.error('解释失败: ' + error.message)
  }
}

// 加载示例
const loadExample = (type) => {
  const examples = {
    1: {
      tableStructure: `CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    age INT,
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);`,
      requirement: '查询所有年龄大于 18 岁的用户,按创建时间倒序排列'
    },
    2: {
      tableStructure: `CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10,2),
    status VARCHAR(20)
);

CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100)
);`,
      requirement: '关联订单表和用户表,查询每个用户的订单总金额,只显示有订单的用户'
    },
    3: {
      tableStructure: `CREATE TABLE sales (
    id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    amount DECIMAL(10,2),
    sale_date DATE
);`,
      requirement: '统计每个类别的销售总额和平均销售额,按销售总额降序排列'
    },
    4: {
      tableStructure: `CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    department_id INT,
    salary DECIMAL(10,2),
    hire_date DATE
);

CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    location VARCHAR(100)
);`,
      requirement: '查询每个部门薪资排名前 3 的员工,显示部门名称、员工姓名和薪资'
    }
  }

  const example = examples[type]
  if (example) {
    formData.tableStructure = example.tableStructure
    formData.requirement = example.requirement
    ElMessage.success('已加载示例')
  }
}

// 加载历史记录
const loadHistory = (item) => {
  result.sql = item.sql
  result.explanation = item.explanation
  ElMessage.success('已加载历史记录')
}

// 清空历史
const clearHistory = () => {
  history.value = []
  saveHistory()
  ElMessage.success('历史记录已清空')
}
</script>

<style scoped>
.sql-generator {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #666;
  font-size: 16px;
}

.stats-panel {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  flex: 1;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.section-card {
  margin-bottom: 20px;
}

.card-header-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.example-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.empty-result {
  padding: 60px 0;
}

.sql-output {
  position: relative;
  margin-bottom: 20px;
}

.sql-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 20px;
  border-radius: 8px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 400px;
  overflow-y: auto;
}

.explanation {
  background: #f8f9fa;
  border-left: 4px solid #667eea;
  padding: 15px;
  border-radius: 4px;
}

.explanation-title {
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.explanation-content {
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
}

.history-card {
  margin-top: 20px;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background 0.2s;
}

.history-item:hover {
  background: #f5f5f5;
}

.history-time {
  font-size: 12px;
  color: #999;
  margin-bottom: 5px;
}

.history-sql {
  font-family: 'Consolas', monospace;
  font-size: 13px;
  color: #333;
}

@media (max-width: 1200px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
}
</style>
