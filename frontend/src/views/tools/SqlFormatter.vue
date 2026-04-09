<template>
  <div class="sql-formatter-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><DataBoard /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">SQL ID 格式化</span>
        </div>
      </template>

      <el-descriptions title="使用说明" border size="small">
        <el-descriptions-item>
          在左侧输入 ID 列表（每行一个或用逗号分隔），点击"格式化"按钮生成 SQL IN 语句
        </el-descriptions-item>
      </el-descriptions>

      <div class="content-area">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="input-section">
              <h4>输入 ID 列表</h4>
              <el-input
                v-model="idList"
                type="textarea"
                :rows="12"
                placeholder="请输入 ID 列表，例如：&#10;123&#10;456&#10;789&#10;或用逗号分隔：123, 456, 789"
              />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="output-section">
              <h4>格式化结果</h4>
              <el-input
                v-model="sqlResult"
                type="textarea"
                :rows="12"
                placeholder="格式化后的 SQL IN 语句..."
                readonly
              />
            </div>
          </el-col>
        </el-row>

        <div class="action-area">
          <el-button type="primary" @click="handleFormat">
            <el-icon><Sort /></el-icon>
            格式化为 IN 语句
          </el-button>
          <el-button type="success" @click="handleCopy">
            <el-icon><DocumentCopy /></el-icon>
            复制结果
          </el-button>
          <el-button type="info" @click="handleClear">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DataBoard, Sort, DocumentCopy, Delete } from '@element-plus/icons-vue'

const idList = ref('')
const sqlResult = ref('')

const parseIds = () => {
  if (!idList.value.trim()) return []
  return idList.value
    .split(/[,,\n]/g)
    .map((id) => id.trim())
    .filter((id) => id)
}

const handleFormat = () => {
  const ids = parseIds()

  if (ids.length === 0) {
    ElMessage.warning('请输入 ID 列表')
    return
  }

  // 格式化 ID（数字加引号，字符串检查）
  const formattedIds = ids.map((id) => {
    if (!isNaN(id)) {
      return id // 数字 ID 不加引号
    } else {
      return `'${id.replace(/'/g, "''")}'` // 字符串加引号
    }
  })

  sqlResult.value = `WHERE id IN (${formattedIds.join(', ')} )`
  ElMessage.success(`已格式化 ${ids.length} 个 ID`)
}

const handleCopy = () => {
  if (!sqlResult.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  navigator.clipboard.writeText(sqlResult.value)
  ElMessage.success('已复制到剪贴板')
}

const handleClear = () => {
  idList.value = ''
  sqlResult.value = ''
}
</script>

<style scoped>
.sql-formatter-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.content-area {
  margin-top: 20px;
}

.input-section,
.output-section {
  margin-bottom: 20px;
}

.input-section h4,
.output-section h4 {
  margin-bottom: 10px;
  color: #606266;
}

.action-area {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}
</style>
