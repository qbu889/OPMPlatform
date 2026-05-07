<template>
  <div class="clean-event-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#409eff"><Edit /></el-icon> 事件数据清洗工具</h2>
      <p class="subtitle">清洗和格式化事件数据，生成标准格式的JSON数据</p>
    </div>

    <el-card class="cleaner-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><Document /></el-icon>
          <span>数据输入</span>
        </div>
      </template>

      <el-form :model="formData" label-width="120px" class="clean-form">
        <el-form-item label="FP值" required>
          <el-input
            v-model="formData.fpValue"
            placeholder="格式: 数字_数字_数字_数字_数字"
            clearable
          >
            <template #prepend>
              <el-icon><Document /></el-icon>
            </template>
          </el-input>
          <div class="form-hint">例如: 1713996274_3872318956_2520283298_4136070826_2</div>
        </el-form-item>
        
        <el-form-item label="事件时间" required>
          <el-input
            v-model="formData.eventTime"
            placeholder="格式：YYYY/MM/DD HH:MM 或 YYYY-MM-DD HH:MM"
            clearable
          >
            <template #prepend>
              <el-icon><Clock /></el-icon>
            </template>
            <template #append>
              <el-button @click="insertCurrentTime" title="插入当前时间">
                <el-icon><Clock /></el-icon>
              </el-button>
            </template>
          </el-input>
          <div class="form-hint">例如：2026/01/12 16:00 或 2026/01/12 16:00:03</div>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            @click="handleClean"
            class="clean-button"
          >
            <el-icon><MagicStick /></el-icon>
            清洗数据
          </el-button>
        </el-form-item>
      </el-form>
      
      <!-- 错误提示 -->
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        :closable="false"
        show-icon
        class="error-alert"
      />
      
      <!-- 结果展示 -->
      <div v-if="cleanedData" class="result-section">
        <el-divider />
        <div class="result-header">
          <h4>
            <el-icon color="#10b981"><CircleCheck /></el-icon>
            清洗结果
            <el-tag type="success" size="small" class="ml-2">成功</el-tag>
          </h4>
          <el-button type="success" @click="handleCopy">
            <el-icon><DocumentCopy /></el-icon>
            复制结果
          </el-button>
        </div>
        <el-input
          v-model="cleanedData"
          type="textarea"
          :rows="15"
          readonly
          class="result-textarea"
        />
        <div v-if="copySuccess" class="copy-success">
          <el-icon color="#10b981"><Check /></el-icon>
          已复制到剪贴板
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Edit,
  Document,
  CircleCheck,
  MagicStick,
  DocumentCopy,
  Clock,
  Check,
} from '@element-plus/icons-vue'

const loading = ref(false)
const errorMessage = ref('')
const cleanedData = ref('')
const copySuccess = ref(false)

const formData = reactive({
  fpValue: '',
  eventTime: '',
})

// 验证时间格式
const validateDateTimeFormat = (dateTimeStr) => {
  // 支持 YYYY/MM/DD HH:MM, YYYY-MM-DD HH:MM, YYYY/MM/DD HH:MM:SS, YYYY-MM-DD HH:MM:SS
  const regex = /^(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})\s(\d{1,2}):(\d{2})(?::(\d{2}))?$/
  return regex.test(dateTimeStr)
}

// 插入当前时间
const insertCurrentTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  // 格式：YYYY/MM/DD HH:MM:SS
  formData.eventTime = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`
}

const handleClean = async () => {
  // 清空之前的错误和结果
  errorMessage.value = ''
  cleanedData.value = ''
  copySuccess.value = false
  
  // 基本验证
  if (!formData.fpValue || !formData.eventTime) {
    errorMessage.value = '请填写所有字段'
    return
  }
  
  // 时间格式验证
  if (!validateDateTimeFormat(formData.eventTime)) {
    errorMessage.value = '时间格式不正确，请使用格式: YYYY/MM/DD HH:MM 或 YYYY-MM-DD HH:MM (支持带秒格式: HH:MM:SS)'
    return
  }

  loading.value = true
  try {
    const response = await fetch('/api/clean-event', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fp_value: formData.fpValue,
        event_time: formData.eventTime,
      }),
    })
    const result = await response.json()

    if (result.error) {
      errorMessage.value = result.error
    } else {
      cleanedData.value = JSON.stringify(result.result, null, 2)
      ElMessage.success('清洗成功')
      
      // 滚动到结果区域
      setTimeout(() => {
        const resultSection = document.querySelector('.result-section')
        if (resultSection) {
          resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
        }
      }, 100)
    }
  } catch (error) {
    console.error('清洗错误:', error)
    errorMessage.value = '处理数据时发生错误: ' + error.message
  } finally {
    loading.value = false
  }
}

const handleCopy = async () => {
  if (!cleanedData.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  
  try {
    // 方法1：尝试使用现代 Clipboard API（仅在 HTTPS 或 localhost 下可用）
    if (typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      await navigator.clipboard.writeText(cleanedData.value)
    } else {
      // 方法2：降级方案 - 使用传统的 execCommand（适用于 HTTP 环境）
      const textarea = document.createElement('textarea')
      textarea.value = cleanedData.value
      textarea.style.position = 'fixed'
      textarea.style.left = '-999999px'
      textarea.style.top = '-999999px'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.focus()
      textarea.select()
      
      const successful = document.execCommand('copy')
      document.body.removeChild(textarea)
      
      if (!successful) {
        throw new Error('execCommand 复制失败')
      }
    }
    
    copySuccess.value = true
    ElMessage.success('已复制到剪贴板')
    setTimeout(() => {
      copySuccess.value = false
    }, 2000)
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择文本复制（Ctrl+C）')
  }
}
</script>

<style scoped>
.clean-event-container {
  padding: 0;
  max-width: 100%;
  margin: 0;
  min-height: auto;
}

.page-header {
  text-align: center;
  padding: 50px 30px;
  margin-bottom: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
  color: white;
}

.page-header h2 {
  font-size: 36px;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-weight: 600;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: 18px;
  opacity: 0.95;
  margin: 0;
  font-weight: 300;
}

.cleaner-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
}

.cleaner-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.clean-form {
  margin-top: 25px;
  padding: 0 10px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #555;
  font-size: 15px;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.form-hint {
  font-size: 13px;
  color: #999;
  margin-top: 8px;
  padding-left: 5px;
  line-height: 1.5;
}

.clean-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

:deep(.clean-button:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

:deep(.clean-button:active) {
  transform: translateY(0);
}

.error-alert {
  margin-top: 25px;
  border-radius: 10px;
  border: none;
}

.result-section {
  margin-top: 30px;
  animation: fadeInUp 0.5s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 5px;
}

.result-header h4 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 20px;
  color: #333;
  font-weight: 600;
}

.ml-2 {
  margin-left: 10px;
}

.result-textarea {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  border-radius: 10px;
}

:deep(.result-textarea .el-textarea__inner) {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  padding: 20px;
  color: #2d3748;
}

.copy-success {
  text-align: center;
  margin-top: 15px;
  color: #10b981;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

:deep(.el-card__header) {
  padding: 20px 25px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-bottom: 2px solid #f0f0f0;
}

:deep(.el-card__body) {
  padding: 30px 25px;
}

:deep(.el-divider) {
  margin: 30px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .clean-event-container {
    padding: 20px 15px;
  }
  
  .page-header {
    padding: 30px 20px;
  }
  
  .page-header h2 {
    font-size: 28px;
  }
  
  .subtitle {
    font-size: 15px;
  }
  
  :deep(.el-card__body) {
    padding: 20px 15px;
  }
}
</style>
