<template>
  <div class="convert-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><DataBoard /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">Word 转 Excel</span>
        </div>
      </template>

      <el-form label-width="120px">
        <el-form-item label="上传 Word 文件">
          <el-upload
            drag
            action="/word-to-excel/upload"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleRemove"
            :limit="1"
          >
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">点击或拖拽文件到这里上传</div>
            <div class="upload-tip">支持 .docx 文件，解析技术规范书生成软件资产清单</div>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="loading" label="转换状态">
          <el-progress :percentage="50" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { DataBoard, UploadFilled } from '@element-plus/icons-vue'

const loading = ref(false)
const selectedFile = ref(null)

const handleFileChange = (file) => {
  selectedFile.value = file
  loading.value = true

  const formData = new FormData()
  formData.append('file', file.raw)

  fetch('/word-to-excel/convert', {
    method: 'POST',
    body: formData,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        ElMessage.success('转换成功！正在下载 Excel 文件')
        if (data.download_url) {
          window.open(data.download_url, '_blank')
        }
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
