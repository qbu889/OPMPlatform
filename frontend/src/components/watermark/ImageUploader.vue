<template>
  <div class="image-uploader">
    <el-upload
      class="upload-area"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      accept=".jpg,.jpeg,.png,.bmp"
      :limit="1"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽图片到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 JPG、PNG、BMP 格式，文件大小不超过 10MB
        </div>
      </template>
    </el-upload>

    <!-- 预览区域 -->
    <div v-if="previewUrl" class="preview-section">
      <h3>图片预览</h3>
      <div class="preview-container">
        <img :src="previewUrl" alt="预览图" />
      </div>
      <div class="file-info">
        <p><strong>文件名：</strong>{{ fileInfo.name }}</p>
        <p><strong>大小：</strong>{{ formatFileSize(fileInfo.size) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { uploadImage } from '../../api/watermark'

const emit = defineEmits(['upload-success', 'upload-error'])

const previewUrl = ref('')
const fileInfo = ref({ name: '', size: 0 })

/**
 * 文件选择处理
 */
const handleFileChange = async (file) => {
  const rawFile = file.raw
  
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/bmp']
  if (!allowedTypes.includes(rawFile.type)) {
    ElMessage.error('仅支持 JPG、PNG、BMP 格式的图片')
    return false
  }
  
  // 验证文件大小（10MB）
  const maxSize = 10 * 1024 * 1024
  if (rawFile.size > maxSize) {
    ElMessage.error('文件大小不能超过 10MB')
    return false
  }
  
  // 显示预览
  fileInfo.value = {
    name: rawFile.name,
    size: rawFile.size
  }
  previewUrl.value = URL.createObjectURL(rawFile)
  
  // 上传文件
  try {
    const response = await uploadImage(rawFile)
    if (response.data.success) {
      emit('upload-success', response.data)
    } else {
      throw new Error(response.data.error || '上传失败')
    }
  } catch (error) {
    console.error('上传错误:', error)
    emit('upload-error', error.message || '上传失败')
  }
}

/**
 * 上传前验证
 */
const beforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
  }
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!')
  }
  
  return isImage && isLt10M
}

/**
 * 格式化文件大小
 */
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.image-uploader {
  width: 100%;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin-bottom: 16px;
}

.el-upload__text {
  color: #606266;
  font-size: 14px;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
}

.preview-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.preview-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
  max-height: 400px;
  overflow: hidden;
}

.preview-container img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.file-info {
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
}

.file-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #606266;
}
</style>
