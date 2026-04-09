<template>
  <div class="convert-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Files /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">Markdown 转 Word</span>
        </div>
      </template>

      <el-form label-width="100px">
        <el-form-item label="Markdown 文件">
          <el-input
            v-model="markdownContent"
            type="textarea"
            :rows="10"
            placeholder="请在这里输入或粘贴 Markdown 内容..."
          />
        </el-form-item>
        <el-form-item label="或上传文件">
          <el-upload
            :auto-upload="true"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            action="/markdown-upload/upload"
          >
            <el-button type="primary">
              <el-icon><UploadFilled /></el-icon>
              选择文件
            </el-button>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="success" size="large" :loading="loading" @click="handleConvert">
            <el-icon><Finished /></el-icon>
            转换为 Word
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Files, UploadFilled, Finished } from '@element-plus/icons-vue'

const loading = ref(false)
const markdownContent = ref('')

const handleUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
}

const handleConvert = async () => {
  if (!markdownContent.value.trim()) {
    ElMessage.warning('请输入 Markdown 内容')
    return
  }

  loading.value = true
  try {
    const response = await fetch('/markdown-upload/convert', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: markdownContent.value }),
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('转换成功，正在下载 Word 文件')
      if (result.download_url) {
        window.open(result.download_url, '_blank')
      }
    } else {
      ElMessage.error(result.message || '转换失败')
    }
  } catch (error) {
    console.error('转换错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
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
</style>
