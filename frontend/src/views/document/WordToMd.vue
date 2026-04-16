<template>
  <div class="word-to-md-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#667eea"><Document /></el-icon> Word 转 Markdown</h2>
      <p class="subtitle">快速将 Word 文档转换为 Markdown 格式</p>
    </div>

    <!-- 文件上传卡片 -->
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#409eff"><UploadFilled /></el-icon>
          <span>上传 Word 文件</span>
        </div>
      </template>

      <div class="upload-area">
        <el-upload
          drag
          action="/word-to-md/upload"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleRemove"
          :limit="1"
          accept=".docx"
          :before-upload="beforeUpload"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 .docx 文件
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 上传并转换按钮 -->
      <div class="action-buttons" v-if="selectedFile">
        <el-button type="primary" @click="convertFile" :loading="loading" :disabled="!selectedFile">
          <el-icon><Upload /></el-icon> 上传并转换
        </el-button>
      </div>
    </el-card>

    <!-- 加载提示 -->
    <el-card v-if="loading" class="loading-card" shadow="hover">
      <div class="loading-content">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
        <p>正在转换中，请稍候...</p>
      </div>
    </el-card>

    <!-- 转换结果 -->
    <el-card v-if="markdown" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header-title justify-between">
          <div>
            <el-icon color="#67c23a"><CircleCheck /></el-icon>
            <span>转换结果</span>
          </div>
        </div>
      </template>

      <el-input
        v-model="markdown"
        type="textarea"
        :rows="20"
        placeholder="转换结果..."
        resize="vertical"
        readonly
      />

      <div class="action-buttons">
        <el-button type="primary" @click="copyMarkdown">
          <el-icon><DocumentCopy /></el-icon> 复制结果
        </el-button>
        <el-button type="success" @click="downloadMarkdown">
          <el-icon><Download /></el-icon> 下载 Markdown 文件
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, UploadFilled, Loading, DocumentCopy, Download, Upload, CircleCheck } from '@element-plus/icons-vue'

const loading = ref(false)
const markdown = ref('')
const selectedFile = ref(null)

// 上传前验证
const beforeUpload = (file) => {
  // 检查文件扩展名（不区分大小写）
  const fileName = file.name.toLowerCase()
  const isDocx = fileName.endsWith('.docx')
  
  // 检查 MIME 类型
  const isWordMime = file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  
  if (!isDocx || !isWordMime) {
    ElMessage.error('仅支持 .docx 格式的 Word 文件')
    return false
  }
  
  // 检查文件大小（最大 50MB）
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  
  return true
}

const handleFileChange = (file) => {
  selectedFile.value = file
  markdown.value = ''
}

const handleRemove = () => {
  selectedFile.value = null
  markdown.value = ''
}

const convertFile = () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  loading.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value.raw)

  fetch('/api/word-to-md/convert', {
    method: 'POST',
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        markdown.value = data.markdown || data.content
        ElMessage.success('转换成功')
      } else {
        ElMessage.error(data.message || '转换失败')
      }
    })
    .catch((err) => {
      console.error(err)
      ElMessage.error('转换失败')
    })
    .finally(() => {
      loading.value = false
    })
}

const copyMarkdown = () => {
  if (!markdown.value) return
  navigator.clipboard.writeText(markdown.value)
  ElMessage.success('已复制到剪贴板')
}

const downloadMarkdown = () => {
  if (!markdown.value) return
  const blob = new Blob([markdown.value], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'converted.md'
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}
</script>

<style scoped>
.word-to-md-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

/* 页面标题 */
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

/* 卡片通用样式 */
.upload-card,
.loading-card,
.result-card {
  margin-bottom: 25px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.upload-card:hover,
.loading-card:hover,
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

/* 上传区域 */
.upload-area {
  margin: 20px 0;
}

:deep(.el-upload-dragger) {
  padding: 40px;
  border-radius: 12px;
  border: 2px dashed #d9d9d9;
  transition: all 0.3s ease;
}

:deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f5f7fa;
}

:deep(.el-icon--upload) {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 15px;
}

:deep(.el-upload__text) {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-upload__text em) {
  color: #409eff;
  font-style: normal;
  font-weight: 500;
}

:deep(.el-upload__tip) {
  font-size: 14px;
  color: #909399;
}

/* 按钮组 */
.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

:deep(.el-button) {
  border-radius: 980px !important;
  padding: 0 24px !important;
  font-weight: 500 !important;
  height: 40px !important;
}

/* 加载卡片 */
.loading-content {
  text-align: center;
  padding: 40px 20px;
  color: #409eff;
}

.loading-content .is-loading {
  margin-bottom: 15px;
  color: #409eff;
}

.loading-content p {
  font-size: 16px;
  margin: 0;
  color: #606266;
}

/* 结果卡片 */
:deep(.result-card .el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  border-radius: 8px;
}
</style>
