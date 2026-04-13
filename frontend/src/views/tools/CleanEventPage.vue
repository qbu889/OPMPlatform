<template>
  <div class="clean-event-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#409eff"><Edit /></el-icon> 事件数据清洗</h2>
      <p class="subtitle">清洗和格式化事件数据，生成标准 JSON 格式</p>
    </div>

    <el-card class="cleaner-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><Document /></el-icon>
          <span>数据输入与输出</span>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <div class="input-section">
            <h4><el-icon color="#409eff"><Document /></el-icon> 原始数据</h4>
            <el-input
              v-model="rawData"
              type="textarea"
              :rows="15"
              placeholder="请粘贴需要清洗的事件数据..."
            />
          </div>
        </el-col>
        <el-col :xs="24" :lg="12">
          <div class="output-section">
            <h4><el-icon color="#67c23a"><CircleCheck /></el-icon> 清洗结果</h4>
            <el-input
              v-model="cleanedData"
              type="textarea"
              :rows="15"
              placeholder="清洗后的数据..."
              readonly
            />
          </div>
        </el-col>
      </el-row>

      <div class="button-group mt-3">
        <el-button type="primary" size="large" :loading="loading" @click="handleClean">
          <el-icon><MagicStick /></el-icon>
          开始清洗
        </el-button>
        <el-button type="success" size="large" @click="handleCopy">
          <el-icon><DocumentCopy /></el-icon>
          复制结果
        </el-button>
        <el-button type="info" size="large" @click="handleDownload">
          <el-icon><Download /></el-icon>
          下载 JSON
        </el-button>
        <el-button type="warning" size="large" @click="handleClear">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Document,
  CircleCheck,
  MagicStick,
  DocumentCopy,
  Download,
  Delete,
} from '@element-plus/icons-vue'

const loading = ref(false)
const rawData = ref('')
const cleanedData = ref('')

const handleClean = async () => {
  if (!rawData.value.trim()) {
    ElMessage.warning('请输入原始数据')
    return
  }

  loading.value = true
  try {
    const response = await fetch('/clean-event-page/clean', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: rawData.value }),
    })
    const result = await response.json()

    if (result.success) {
      cleanedData.value = JSON.stringify(result.data, null, 2)
      ElMessage.success(`清洗完成，共处理 ${result.count || 0} 条数据`)
    } else {
      ElMessage.error(result.message || '清洗失败')
    }
  } catch (error) {
    console.error('清洗错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const handleCopy = () => {
  if (!cleanedData.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  navigator.clipboard.writeText(cleanedData.value)
  ElMessage.success('已复制到剪贴板')
}

const handleDownload = () => {
  if (!cleanedData.value) {
    ElMessage.warning('没有可下载的内容')
    return
  }
  const blob = new Blob([cleanedData.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'cleaned-data.json'
  a.click()
  URL.revokeObjectURL(url)
}

const handleClear = () => {
  rawData.value = ''
  cleanedData.value = ''
}
</script>

<style scoped>
.clean-event-container {
  padding: 20px;
  max-width: 1400px;
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

.cleaner-card {
  margin-bottom: 25px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.cleaner-card:hover {
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

.input-section,
.output-section {
  margin-bottom: 20px;
}

.input-section h4,
.output-section h4 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.button-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.mt-3 {
  margin-top: 15px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
