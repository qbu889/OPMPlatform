<template>
  <div class="excel-to-cosmic">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Document /></el-icon> Excel 转 COSMIC</span>
        </div>
      </template>

      <!-- 文件上传 -->
      <el-upload
        class="upload-demo"
        drag
        :auto-upload="false"
        :on-change="handleFileSelect"
        :on-remove="handleRemove"
        :file-list="fileList"
        accept=".xlsx,.xls"
        :limit="1"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 xlsx/xls 文件
          </div>
        </template>
      </el-upload>

      <!-- 上传按钮 -->
      <div class="action-buttons" v-if="selectedFile && !uploadedFilename">
        <el-button type="primary" @click="uploadFile" :loading="uploading">
          <el-icon><UploadFilled /></el-icon> 上传文件
        </el-button>
      </div>

      <!-- 转换按钮 -->
      <div class="action-buttons" v-if="uploadedFilename">
        <el-button type="primary" @click="convertToWord" :loading="converting">
          <el-icon><VideoPlay /></el-icon> 开始转换
        </el-button>
        <el-button @click="getStats">
          <el-icon><DataAnalysis /></el-icon> 查看统计
        </el-button>
      </div>

      <!-- 进度条 -->
      <div class="progress-section" v-if="showProgress">
        <el-progress :percentage="progressPercent" :status="progressStatus" />
        <p class="progress-text">{{ progressText }}</p>
      </div>

      <!-- 下载链接 -->
      <div class="download-section" v-if="downloadUrl">
        <el-alert
          title="转换成功！"
          type="success"
          :closable="false"
          show-icon
        >
          <template #default>
            <el-button type="success" @click="downloadFile">
              <el-icon><Download /></el-icon> 下载 Word 文档
            </el-button>
          </template>
        </el-alert>
      </div>

      <!-- 统计信息 -->
      <el-dialog
        v-model="statsVisible"
        title="模块统计信息"
        width="800px"
      >
        <el-table :data="statsData" stripe style="width: 100%">
          <el-table-column prop="module_name" label="模块名称" min-width="200" />
          <el-table-column prop="l3_count" label="三级功能点数量" width="150" />
          <el-table-column prop="total_cfp" label="总CFP" width="120" />
        </el-table>
        <template #footer>
          <el-button @click="statsVisible = false">关闭</el-button>
          <el-button type="primary" @click="exportStats">
            <el-icon><Download /></el-icon> 导出统计
          </el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, VideoPlay, DataAnalysis, Download, Document } from '@element-plus/icons-vue'

const fileList = ref([])
const selectedFile = ref(null)
const uploadedFilename = ref('')
const originalFilename = ref('')
const uploading = ref(false)
const converting = ref(false)
const downloadUrl = ref('')
const showProgress = ref(false)
const progressPercent = ref(0)
const progressStatus = ref('')
const progressText = ref('')
const statsVisible = ref(false)
const statsData = ref([])

// 处理文件选择
const handleFileSelect = (file) => {
  selectedFile.value = file
  fileList.value = [file]
}

// 处理文件移除
const handleRemove = () => {
  selectedFile.value = null
  uploadedFilename.value = ''
  downloadUrl.value = ''
  fileList.value = []
}

// 上传文件
const uploadFile = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  uploading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value.raw)

  try {
    showProgress.value = true
    progressPercent.value = 50
    progressText.value = '正在上传文件...'

    const response = await fetch('/api/cosmic/upload', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (result.success) {
      uploadedFilename.value = result.filename
      originalFilename.value = result.original_name
      progressPercent.value = 100
      progressStatus.value = 'success'
      progressText.value = '文件上传成功'
      ElMessage.success('文件上传成功')

      setTimeout(() => {
        showProgress.value = false
      }, 1000)
    } else {
      ElMessage.error(result.message || '上传失败')
      showProgress.value = false
      selectedFile.value = null
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('网络错误，请稍后重试')
    showProgress.value = false
    selectedFile.value = null
  } finally {
    uploading.value = false
  }
}

// 转换为 Word
const convertToWord = async () => {
  if (!uploadedFilename.value) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  converting.value = true
  showProgress.value = true
  progressPercent.value = 50
  progressText.value = '正在转换...'
  
  try {
    const response = await fetch('/api/cosmic/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: uploadedFilename.value,
        original_name: originalFilename.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      downloadUrl.value = `/api/cosmic/download/${result.output_filename}`
      progressPercent.value = 100
      progressStatus.value = 'success'
      progressText.value = '转换成功'
      ElMessage.success('转换成功')
    } else {
      ElMessage.error(result.message || '转换失败')
      showProgress.value = false
    }
  } catch (error) {
    console.error('转换失败:', error)
    ElMessage.error('网络错误，请稍后重试')
    showProgress.value = false
  } finally {
    converting.value = false
  }
}

// 获取统计信息
const getStats = async () => {
  if (!uploadedFilename.value) {
    ElMessage.warning('请先上传文件')
    return
  }
  
  try {
    const response = await fetch('/api/cosmic/stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: uploadedFilename.value
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      const modules = result.data?.modules || result.modules || {}
      statsData.value = Object.entries(modules).map(([name, count]) => ({
        module_name: name || '未分类',
        l3_count: count,
        total_cfp: count
      }))
      statsVisible.value = true
    } else {
      ElMessage.error(result.message || '获取统计失败')
    }
  } catch (error) {
    console.error('获取统计失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 导出统计
const exportStats = async () => {
  try {
    const response = await fetch('/api/cosmic/export-stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: uploadedFilename.value
      })
    })
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `模块统计_${new Date().getTime()}.xlsx`
      a.click()
      window.URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } else {
      ElMessage.error('导出失败')
    }
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 下载文件
const downloadFile = () => {
  if (downloadUrl.value) {
    window.open(downloadUrl.value, '_blank')
  }
}
</script>

<style scoped>
.excel-to-cosmic {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.card-header .el-icon {
  margin-right: 8px;
}

.upload-demo {
  margin-bottom: 20px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.progress-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.progress-text {
  text-align: center;
  margin-top: 10px;
  color: #606266;
}

.download-section {
  margin-top: 20px;
}
</style>
