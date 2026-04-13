<template>
  <div class="es-to-excel-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Document /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">ES 查询结果转 Excel</span>
        </div>
      </template>

      <div class="content-area">
        <!-- 上传区域 -->
        <el-upload
          class="upload-area"
          drag
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="fileList"
          multiple
          accept=".txt"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处，或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .txt 格式（竖线分隔或 JSON 格式的 ES 查询结果），可上传多个文件
            </div>
          </template>
        </el-upload>

        <!-- 文件信息 -->
        <div v-if="uploadedFiles.length > 0" class="file-info">
          <el-alert
            :title="`已上传 ${uploadedFiles.length} 个文件`"
            type="success"
            :closable="false"
            show-icon
          >
            <template #default>
              <div style="margin-top: 10px;">
                <div v-for="(file, index) in uploadedFiles" :key="index" style="margin-bottom: 5px;">
                  <el-tag size="small">{{ file.original_name }}</el-tag>
                </div>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 上传按钮 -->
        <div v-if="pendingFiles.length > 0" class="upload-buttons">
          <el-button type="primary" :loading="uploading" @click="handleUploadAll">
            <el-icon><UploadFilled /></el-icon>
            上传全部文件 ({{ pendingFiles.length }} 个)
          </el-button>
        </div>

        <!-- 操作按钮 -->
        <div v-if="uploadedFiles.length > 0" class="action-buttons">
          <el-button type="primary" :loading="previewLoading" @click="handlePreview">
            <el-icon><View /></el-icon>
            预览数据
          </el-button>
          
          <!-- Excel 格式选择 -->
          <el-select v-model="excelFormat" placeholder="选择格式" style="width: 150px;">
            <el-option label="XLS (兼容旧版)" value="xls" />
            <el-option label="XLSX (推荐)" value="xlsx" />
          </el-select>
          
          <el-button type="success" :loading="convertLoading" @click="handleConvert">
            <el-icon><Download /></el-icon>
            转换为 Excel
          </el-button>
          <el-button type="info" @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重新上传
          </el-button>
        </div>

        <!-- 数据预览 -->
        <div v-if="previewData.length > 0" class="preview-section">
          <el-divider content-position="left">
            <el-icon><List /></el-icon>
            数据预览（共 {{ totalCount }} 条，显示前 {{ previewData.length }} 条）
          </el-divider>
          
          <el-table
            :data="previewData"
            border
            stripe
            max-height="500"
            style="width: 100%"
          >
            <el-table-column
              v-for="col in columns"
              :key="col"
              :prop="col"
              :label="col"
              min-width="150"
              show-overflow-tooltip
            />
          </el-table>
        </div>

        <!-- 转换结果 -->
        <div v-if="convertResult" class="result-section">
          <el-alert
            title="转换成功！"
            type="success"
            :closable="false"
            show-icon
          >
            <template #default>
              <div>
                <p>✅ 共处理 <strong>{{ convertResult.data_count }}</strong> 条数据，<strong>{{ convertResult.column_count }}</strong> 个字段</p>
                <el-button type="primary" size="small" @click="handleDownload">
                  <el-icon><Download /></el-icon>
                  下载 Excel 文件
                </el-button>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 使用说明 -->
        <el-divider content-position="left">
          <el-icon><InfoFilled /></el-icon>
          使用说明
        </el-divider>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="支持格式">
            <el-tag type="info">竖线分隔格式</el-tag>
            <el-tag type="info" style="margin-left: 5px">JSON 格式（ES SQL 查询结果）</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="自动检测">
            系统会自动识别文件格式并选择合适的解析方式
          </el-descriptions-item>
          <el-descriptions-item label="字段映射">
            自动将 ES 英文字段映射为中文标准字段
          </el-descriptions-item>
          <el-descriptions-item label="输出格式">
            <el-tag type="warning">XLS (兼容旧版 - 默认)</el-tag>
            <el-tag type="success" style="margin-left: 5px">XLSX (推荐)</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="时间格式">
            自动将 ISO 8601 格式转换为标准格式（去掉毫秒）：<br>
            <code>2026-04-09T03:47:03.000Z</code> → <code>2026-04-09 03:47:03</code>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, UploadFilled, View, Download, RefreshLeft, List, InfoFilled } from '@element-plus/icons-vue'

const uploadedFiles = ref([])
const pendingFiles = ref([])
const fileList = ref([])
const uploading = ref(false)
const previewLoading = ref(false)
const convertLoading = ref(false)
const previewData = ref([])
const columns = ref([])
const totalCount = ref(0)
const convertResult = ref(null)
const excelFormat = ref('xls')  // 默认 xls 格式（兼容达梦数据库）

// 计算后端 API 基础 URL
const apiBaseUrl = computed(() => {
  // 开发环境使用相对路径,通过 Vite 代理到后端
  return ''
})

// 计算上传 URL(开发环境代理到后端)
const uploadUrl = computed(() => {
  return '/api/es-to-excel/upload'
})

// 上传请求头
const uploadHeaders = computed(() => ({
  'Accept': 'application/json'
}))

const handleFileChange = (file, files) => {
  fileList.value = files
  pendingFiles.value = files.filter(f => f.status === 'ready')
}

const handleFileRemove = (file, files) => {
  fileList.value = files
  pendingFiles.value = files.filter(f => f.status === 'ready')
}

const handleUploadAll = async () => {
  if (pendingFiles.value.length === 0) {
    ElMessage.warning('没有待上传的文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    pendingFiles.value.forEach(file => {
      formData.append('files', file.raw)
    })

    const response = await fetch(uploadUrl.value, {
      method: 'POST',
      body: formData
    })
    const result = await response.json()

    if (result.success) {
      uploadedFiles.value = result.files
      pendingFiles.value = []
      ElMessage.success(result.message || '文件上传成功！')
      // 重置之前的预览和转换结果
      previewData.value = []
      convertResult.value = null
    } else {
      ElMessage.error(result.message || '上传失败')
    }
  } catch (error) {
    console.error('上传错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    uploading.value = false
  }
}

const handlePreview = async () => {
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  previewLoading.value = true
  try {
    // 只预览第一个文件
    const firstFile = uploadedFiles.value[0]
    const response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: firstFile.filename,
        limit: 10
      })
    })
    const result = await response.json()

    if (result.success) {
      previewData.value = result.data
      columns.value = result.columns
      totalCount.value = result.total_count
      ElMessage.success(`预览成功，共 ${result.total_count} 条数据（仅显示第一个文件）`)
    } else {
      ElMessage.error(result.message || '预览失败')
    }
  } catch (error) {
    console.error('预览错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    previewLoading.value = false
  }
}

const handleConvert = async () => {
  if (uploadedFiles.value.length === 0) {
    ElMessage.warning('请先上传文件')
    return
  }

  convertLoading.value = true
  try {
    const filenames = uploadedFiles.value.map(f => f.filename)
    const response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filenames: filenames,
        format: excelFormat.value  // 传递格式参数
      })
    })
    const result = await response.json()

    if (result.success) {
      convertResult.value = result
      const msg = uploadedFiles.value.length > 1 
        ? `转换成功！合并了 ${result.file_count} 个文件，共 ${result.data_count} 条数据`
        : `转换成功！共处理 ${result.data_count} 条数据`
      ElMessage.success(msg)
    } else {
      ElMessage.error(result.message || '转换失败')
    }
  } catch (error) {
    console.error('转换错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    convertLoading.value = false
  }
}

const handleDownload = () => {
  if (!convertResult.value) {
    ElMessage.warning('没有可下载的文件')
    return
  }

  const downloadUrl = `${apiBaseUrl.value}/api/es-to-excel/download/${convertResult.value.output_filename}`
  window.open(downloadUrl, '_blank')
}

const handleReset = () => {
  uploadedFiles.value = []
  previewData.value = []
  columns.value = []
  totalCount.value = 0
  convertResult.value = null
}
</script>

<style scoped>
.es-to-excel-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.content-area {
  margin-top: 20px;
}

.upload-area {
  margin-bottom: 20px;
}

.upload-buttons {
  margin: 15px 0;
  text-align: center;
}

.file-info {
  margin-bottom: 20px;
}

.action-buttons {
  margin: 20px 0;
  display: flex;
  gap: 15px;
}

.preview-section {
  margin-top: 30px;
}

.result-section {
  margin-top: 20px;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 10px;
}
</style>
