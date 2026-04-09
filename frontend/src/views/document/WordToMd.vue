<template>
  <div class="convert-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Document /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">Word 转 Markdown</span>
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
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">点击或拖拽文件到这里上传</div>
          <div class="upload-tip">支持 .docx 文件</div>
        </el-upload>
      </div>

      <div v-if="loading" class="loading-tip">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在转换...</span>
      </div>

      <div v-if="markdown" class="result-area">
        <el-divider>转换结果</el-divider>
        <el-input
          v-model="markdown"
          type="textarea"
          :rows="15"
          placeholder="转换结果..."
          resize="vertical"
        />
        <div class="action-buttons">
          <el-button type="primary" @click="copyMarkdown">
            <el-icon><DocumentCopy /></el-icon>
            复制结果
          </el-button>
          <el-button type="success" @click="downloadMarkdown">
            <el-icon><Download /></el-icon>
            下载文件
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, UploadFilled, Loading, DocumentCopy, Download } from '@element-plus/icons-vue'

const loading = ref(false)
const markdown = ref('')
const selectedFile = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file
  loading.value = true
  markdown.value = ''

  const formData = new FormData()
  formData.append('file', file.raw)

  fetch('/word-to-md/convert', {
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

const handleRemove = () => {
  selectedFile.value = null
  markdown.value = ''
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
.convert-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.upload-area {
  margin: 30px 0;
}

.upload-icon {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 15px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

.upload-tip {
  font-size: 14px;
  color: #909399;
}

.loading-tip {
  text-align: center;
  padding: 30px;
  color: #409eff;
  font-size: 16px;
}

.loading-tip .is-loading {
  margin-right: 10px;
  font-size: 20px;
}

.result-area {
  margin-top: 20px;
}

.action-buttons {
  margin-top: 15px;
  display: flex;
  gap: 15px;
}
</style>
