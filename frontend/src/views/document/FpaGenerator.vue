<template>
  <div class="fpa-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><DataAnalysis /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">FPA 预估表生成</span>
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="上传需求文档">
          <el-upload
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleRemove"
            :limit="1"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">点击或拖拽文件到这里上传</div>
            <div class="upload-tip">支持 .docx 文件，从需求文档自动生成 FPA 功能点估算表</div>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="loading" label="生成状态">
          <el-progress :percentage="50" />
        </el-form-item>

        <el-form-item>
          <el-button type="success" size="large" :loading="loading" @click="handleGenerate">
            <el-icon><Finished /></el-icon>
            生成 FPA 预估表
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, UploadFilled, Finished } from '@element-plus/icons-vue'

const loading = ref(false)
const selectedFile = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file
}

const handleRemove = () => {
  selectedFile.value = null
}

const handleGenerate = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先上传需求文档')
    return
  }

  loading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value.raw)

  try {
    const response = await fetch('/fpa-generator/generate', {
      method: 'POST',
      body: formData,
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('FPA 预估表生成成功！正在下载 Excel 文件')
      if (result.download_url) {
        window.open(result.download_url, '_blank')
      }
    } else {
      ElMessage.error(result.message || '生成失败')
    }
  } catch (error) {
    console.error('生成错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fpa-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.upload-icon {
  font-size: 64px;
  color: #67c23a;
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
</style>
