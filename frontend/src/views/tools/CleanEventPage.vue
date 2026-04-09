<template>
  <div class="clean-event-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Edit /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">事件数据清洗</span>
        </div>
      </template>

      <div class="content-area">
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="input-section">
              <h4>原始数据</h4>
              <el-input
                v-model="rawData"
                type="textarea"
                :rows="15"
                placeholder="请粘贴需要清洗的事件数据..."
              />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="output-section">
              <h4>清洗结果</h4>
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

        <div class="action-area">
          <el-button type="primary" :loading="loading" @click="handleClean">
            <el-icon><Edit /></el-icon>
            开始清洗
          </el-button>
          <el-button type="success" @click="handleCopy">
            <el-icon><DocumentCopy /></el-icon>
            复制结果
          </el-button>
          <el-button type="info" @click="handleDownload">
            <el-icon><Download /></el-icon>
            下载 JSON
          </el-button>
          <el-button type="warning" @click="handleClear">
            <el-icon><Delete /></el-icon>
            清空
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Edit, DocumentCopy, Download, Delete } from '@element-plus/icons-vue'

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
