<template>
  <div class="sql-formatter-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#67c23a"><DataBoard /></el-icon> SQL ID 格式化工具</h2>
      <p class="subtitle">快速格式化 ID 列表，添加单引号并换行</p>
    </div>

    <el-card class="formatter-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><EditPen /></el-icon>
          <span>输入 ID 列表</span>
        </div>
      </template>

      <el-alert
        title="使用说明"
        type="info"
        :closable="false"
        show-icon
        class="mb-3"
      >
        <template #default>
          在下方输入 ID 列表（每行一个或用逗号分隔），点击“格式化”按钮生成带引号的 ID 列表
        </template>
      </el-alert>

      <el-input
        v-model="idList"
        type="textarea"
        :rows="12"
        placeholder="请输入 ID 列表，例如：&#10;123&#10;456&#10;789&#10;或用逗号分隔：123, 456, 789"
      />

      <div class="button-group mt-3">
        <el-button type="primary" size="large" @click="handleFormat">
          <el-icon><Sort /></el-icon>
          格式化
        </el-button>
        <el-button type="info" size="large" @click="handleClear">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </el-card>

    <!-- 格式化结果 -->
    <el-card v-if="sqlResult" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header-title justify-between">
          <div>
            <el-icon color="#67c23a"><CircleCheck /></el-icon>
            <span>格式化结果</span>
          </div>
          <el-button type="success" @click="handleCopy">
            <el-icon><DocumentCopy /></el-icon>
            复制结果
          </el-button>
        </div>
      </template>

      <div class="result-content">
        {{ sqlResult }}
      </div>

      <el-alert
        :title="`已格式化 ${idCount} 个 ID`"
        type="success"
        show-icon
        :closable="false"
        class="mt-3"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DataBoard,
  EditPen,
  Sort,
  DocumentCopy,
  Delete,
  CircleCheck,
} from '@element-plus/icons-vue'

const idList = ref('')
const sqlResult = ref('')

const idCount = computed(() => {
  if (!sqlResult.value) return 0
  // 计算换行分隔的 ID 数量
  return sqlResult.value.split(',\n').length
})

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

  // 格式化 ID（所有 ID 都加单引号）
  const formattedIds = ids.map((id) => {
    return `'${id.replace(/'/g, "''")}'` // 所有 ID 都加引号，并转义单引号
  })

  // 直接输出带引号的 ID 列表，每行一个
  sqlResult.value = formattedIds.join(',\n')
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
  max-width: 1000px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: #333;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.formatter-card,
.result-card {
  margin-bottom: 25px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.formatter-card:hover,
.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.justify-between {
  justify-content: space-between;
}

.button-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.mt-3 {
  margin-top: 15px;
}

.mb-3 {
  margin-bottom: 15px;
}

.result-content {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  color: #2d3748;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.6;
  max-height: 500px;
  overflow-y: auto;
}

:deep(.el-card__header) {
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
