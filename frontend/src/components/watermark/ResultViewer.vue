<template>
  <div class="result-viewer">
    <div class="viewer-header">
      <h3>处理结果</h3>
      <div v-if="processingTime" class="processing-info">
        <el-tag type="success" size="small">
          处理耗时: {{ processingTime }}秒
        </el-tag>
      </div>
    </div>

    <!-- 对比视图 -->
    <div class="comparison-container">
      <div class="image-panel">
        <h4>原图</h4>
        <div class="image-wrapper">
          <img :src="originalImage" alt="原图" />
        </div>
      </div>
      
      <div class="arrow">
        <el-icon :size="40" color="#409EFF"><Right /></el-icon>
      </div>
      
      <div class="image-panel">
        <h4>处理后</h4>
        <div class="image-wrapper">
          <img :src="resultImage" alt="处理后" />
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="handleRetry">重新处理</el-button>
      <el-button type="primary" @click="handleDownload">
        <el-icon><Download /></el-icon>
        下载图片
      </el-button>
    </div>

    <!-- 提示信息 -->
    <el-alert
      title="提示"
      type="info"
      :closable="false"
      show-icon
      class="tip-alert"
    >
      <template #default>
        <p>• 如果对结果不满意，可以点击"重新处理"调整参数后再次处理</p>
        <p>• 点击下载按钮保存处理后的图片到本地</p>
        <p>• 临时文件将在24小时后自动清理</p>
      </template>
    </el-alert>
  </div>
</template>

<script setup>
import { Right, Download } from '@element-plus/icons-vue'

const props = defineProps({
  originalImage: {
    type: String,
    required: true
  },
  resultImage: {
    type: String,
    required: true
  },
  processingTime: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['download', 'retry'])

/**
 * 处理下载
 */
const handleDownload = () => {
  // 从base64中提取文件名或使用默认名
  const timestamp = new Date().getTime()
  const filename = `watermark_removed_${timestamp}.jpg`
  emit('download', filename)
}

/**
 * 处理重试
 */
const handleRetry = () => {
  emit('retry')
}
</script>

<style scoped>
.result-viewer {
  width: 100%;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.viewer-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.processing-info {
  display: flex;
  gap: 10px;
}

.comparison-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 30px;
}

.image-panel {
  flex: 1;
  text-align: center;
}

.image-panel h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #606266;
}

.image-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background-color: #f5f7fa;
  padding: 10px;
}

.image-wrapper img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.arrow {
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.tip-alert {
  margin-top: 20px;
}

.tip-alert p {
  margin: 5px 0;
  font-size: 13px;
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .comparison-container {
    flex-direction: column;
  }
  
  .arrow {
    transform: rotate(90deg);
  }
}
</style>
