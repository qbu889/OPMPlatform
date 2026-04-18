<template>
  <div class="watermark-remover">
    <el-card class="main-card">
      <template #header>
        <div class="card-header">
          <h2>图片水印清除工具</h2>
          <p class="subtitle">支持手动框选和自动识别两种模式去除图片水印</p>
        </div>
      </template>

      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" finish-status="success" class="steps">
        <el-step title="上传图片" />
        <el-step title="选择水印区域" />
        <el-step title="处理结果" />
      </el-steps>

      <!-- 步骤1: 上传图片 -->
      <div v-show="currentStep === 0" class="step-content">
        <ImageUploader 
          @upload-success="handleUploadSuccess"
          @upload-error="handleUploadError"
        />
      </div>

      <!-- 步骤2: 选择水印区域 -->
      <div v-show="currentStep === 1" class="step-content">
        <WatermarkSelector
          :image-url="uploadedImageUrl"
          :filename="uploadedFilename"
          @confirm-selection="handleSelectionConfirm"
          @cancel="handleCancel"
        />
      </div>

      <!-- 步骤3: 处理结果 -->
      <div v-show="currentStep === 2" class="step-content">
        <ResultViewer
          :original-image="uploadedImageUrl"
          :result-image="resultImageData"
          :processing-time="processingTime"
          @download="handleDownload"
          @retry="handleRetry"
        />
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button 
          v-if="currentStep === 0 && uploadedFilename" 
          type="primary" 
          @click="nextStep"
        >
          下一步
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import ImageUploader from '../../components/watermark/ImageUploader.vue'
import WatermarkSelector from '../../components/watermark/WatermarkSelector.vue'
import ResultViewer from '../../components/watermark/ResultViewer.vue'

// 状态管理
const currentStep = ref(0)
const uploadedFilename = ref('')
const uploadedImageUrl = ref('')
const resultImageData = ref('')
const processingTime = ref(0)

/**
 * 处理上传成功
 */
const handleUploadSuccess = (data) => {
  uploadedFilename.value = data.filename
  uploadedImageUrl.value = `/api/watermark/preview/${data.filename}`
  ElMessage.success('图片上传成功')
}

/**
 * 处理上传失败
 */
const handleUploadError = (error) => {
  ElMessage.error(error || '图片上传失败')
}

/**
 * 处理选择确认
 */
const handleSelectionConfirm = (result) => {
  resultImageData.value = result.image_data
  processingTime.value = result.processing_time
  currentStep.value = 2
  ElMessage.success('水印清除完成')
}

/**
 * 处理取消
 */
const handleCancel = () => {
  currentStep.value = 0
}

/**
 * 处理下载
 */
const handleDownload = (filename) => {
  const link = document.createElement('a')
  link.href = `/api/watermark/download/${filename}`
  link.download = filename
  link.click()
  ElMessage.success('开始下载')
}

/**
 * 处理重试
 */
const handleRetry = () => {
  currentStep.value = 1
  resultImageData.value = ''
  processingTime.value = 0
}

/**
 * 上一步
 */
const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

/**
 * 下一步
 */
const nextStep = () => {
  if (currentStep.value < 2) {
    currentStep.value++
  }
}
</script>

<style scoped>
.watermark-remover {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.main-card {
  min-height: 600px;
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.steps {
  margin-bottom: 40px;
}

.step-content {
  min-height: 400px;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
}
</style>
