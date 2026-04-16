<template>
  <div class="es-to-excel-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Document /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">ES 查询结果转 Excel</span>
          <el-button type="primary" size="small" @click="goToMappingConfig" style="margin-left: auto;">
            <el-icon><Setting /></el-icon>
            映射中文字段配置
          </el-button>
        </div>
      </template>

      <div class="content-area">
        <!-- 输入方式 Tab -->
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Tab 1: 文件上传 -->
          <el-tab-pane label="文件上传" name="upload">
            <el-upload
              class="upload-area"
              drag
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              multiple
              accept=".txt,.json"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处，或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 .txt（竖线分隔 / ES SQL 表格）和 .json（ES SQL 查询结果），可上传多个文件
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
          </el-tab-pane>

          <!-- Tab 2: 文本粘贴 -->
          <el-tab-pane label="文本粘贴" name="paste">
            <el-input
              v-model="pasteText"
              type="textarea"
              :rows="15"
              placeholder="请粘贴 ES SQL 查询结果（支持表格格式、JSON 格式、竖线分隔格式）&#10;例如：POST /_sql?format=txt 返回的结果"
              style="margin-bottom: 15px;"
            />
          </el-tab-pane>
        </el-tabs>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <!-- 文件模式按钮 -->
          <template v-if="activeTab === 'upload'">
            <el-button type="primary" :loading="previewLoading" :disabled="uploadedFiles.length === 0" @click="handlePreview">
              <el-icon><View /></el-icon>
              预览数据
            </el-button>
          </template>
          
          <!-- Excel 格式选择 -->
          <el-select v-model="excelFormat" placeholder="选择格式" style="width: 150px;">
            <el-option label="XLSX (推荐)" value="xlsx" />
            <el-option label="XLS (兼容旧版)" value="xls" />
          </el-select>
          
          <!-- 中文字段名开关 -->
          <el-checkbox v-model="useChineseNames" border>
            映射中文字段名
          </el-checkbox>
          
          <!-- 转换按钮（文件模式） -->
          <el-button v-if="activeTab === 'upload'" type="success" :loading="convertLoading" :disabled="uploadedFiles.length === 0" @click="handleConvert">
            <el-icon><Download /></el-icon>
            转换为 Excel
          </el-button>
          
          <!-- 处理按钮（粘贴模式） -->
          <el-button v-if="activeTab === 'paste'" type="success" :loading="pasteLoading" :disabled="!pasteText.trim()" @click="handlePaste">
            <el-icon><Download /></el-icon>
            处理并生成 Excel
          </el-button>
          
          <el-button type="info" @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
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
              v-for="col in displayColumns"
              :key="col.key"
              :prop="col.key"
              :label="col.label"
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
          <el-descriptions-item label="文件上传">
            支持 .txt（竖线分隔 / ES SQL 表格）和 .json（ES SQL 查询结果）
          </el-descriptions-item>
          <el-descriptions-item label="文本粘贴">
            直接粘贴 ES SQL 查询结果（POST /_sql?format=txt 返回的表格格式）
          </el-descriptions-item>
          <el-descriptions-item label="自动检测">
            系统会自动识别输入格式并选择合适的解析方式
          </el-descriptions-item>
          <el-descriptions-item label="字段映射">
            勾选「映射中文字段名」后，Excel 表头将显示中文名称（基于数据库配置）
          </el-descriptions-item>
          <el-descriptions-item label="时间格式">
            自动将 ISO 8601 格式转换为标准格式：<br>
            <code>2026-04-16T10:04:21.000Z</code> → <code>2026-04-16 10:04:21</code>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, UploadFilled, View, Download, RefreshLeft, List, InfoFilled, Setting } from '@element-plus/icons-vue'

const router = useRouter()

const activeTab = ref('upload')  // 当前激活的 Tab
const uploadedFiles = ref([])
const pendingFiles = ref([])
const fileList = ref([])
const pasteText = ref('')  // 粘贴的文本内容
const uploading = ref(false)
const previewLoading = ref(false)
const convertLoading = ref(false)
const pasteLoading = ref(false)  // 粘贴处理加载状态
const previewData = ref([])
const columns = ref([])
const totalCount = ref(0)
const convertResult = ref(null)
const excelFormat = ref('xlsx')  // 默认 xlsx 格式
const useChineseNames = ref(true)  // 是否使用中文字段名
const fieldMapping = ref({})  // 字段映射关系 {english: chinese}

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

// 加载字段映射关系
const loadFieldMapping = async () => {
  try {
    const response = await fetch('/api/es-field-mapping/all')
    const result = await response.json()
    if (result.success) {
      fieldMapping.value = result.data
    }
  } catch (error) {
    console.error('加载字段映射失败:', error)
  }
}

// 计算是否可以操作（有上传文件或粘贴文本）
const canOperate = computed(() => {
  return (activeTab.value === 'upload' && uploadedFiles.value.length > 0) ||
         (activeTab.value === 'paste' && pasteText.value.trim().length > 0)
})

// 显示列（根据是否映射中文进行转换）
const displayColumns = computed(() => {
  if (!useChineseNames.value || !columns.value.length) {
    return columns.value.map(col => ({ key: col, label: col }))
  }
  
  // 使用字段映射关系转换列名
  return columns.value.map(col => {
    // 先尝试直接匹配
    if (fieldMapping.value[col]) {
      return { key: col, label: fieldMapping.value[col] }
    }
    
    // 如果包含点号，尝试匹配点号后面的部分
    if (col.includes('.')) {
      const simpleName = col.split('.').pop()
      if (fieldMapping.value[simpleName]) {
        return { key: col, label: fieldMapping.value[simpleName] }
      }
    }
    
    // 保持原名
    return { key: col, label: col }
  })
})

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
  if (!canOperate.value) {
    ElMessage.warning('请先上传文件或粘贴文本')
    return
  }

  previewLoading.value = true
  try {
    let response, result
    
    if (activeTab.value === 'upload') {
      // 文件上传模式：预览第一个文件
      const firstFile = uploadedFiles.value[0]
      response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename: firstFile.filename,
          limit: 10
        })
      })
    } else {
      // 文本粘贴模式
      response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/paste`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: pasteText.value,
          format: excelFormat.value,
          preview_only: true  // 仅预览，不生成文件
        })
      })
    }
    
    result = await response.json()

    if (result.success) {
      previewData.value = result.data || []
      columns.value = result.columns || []
      totalCount.value = result.total_count || result.data_count || 0
      ElMessage.success(`预览成功，共 ${totalCount.value} 条数据`)
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
  if (!canOperate.value) {
    ElMessage.warning('请先上传文件或粘贴文本')
    return
  }

  convertLoading.value = true
  try {
    let response, result
    
    if (activeTab.value === 'upload') {
      // 文件上传模式
      const filenames = uploadedFiles.value.map(f => f.filename)
      response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filenames: filenames,
          format: excelFormat.value,
          use_chinese_names: useChineseNames.value  // 传递中文字段名开关
        })
      })
    } else {
      // 文本粘贴模式
      response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/paste`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: pasteText.value,
          format: excelFormat.value,
          use_chinese_names: useChineseNames.value  // 传递中文字段名开关
        })
      })
    }
    
    result = await response.json()

    if (result.success) {
      convertResult.value = result
      const msg = activeTab.value === 'upload' && uploadedFiles.value.length > 1
        ? `转换成功！合并了 ${result.file_count} 个文件，共 ${result.data_count} 条数据`
        : `转换成功！共处理 ${result.data_count} 条数据，${result.column_count} 个字段`
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

const handlePaste = async () => {
  if (!pasteText.value.trim()) {
    ElMessage.warning('请先粘贴文本内容')
    return
  }

  pasteLoading.value = true
  try {
    const response = await fetch(`${apiBaseUrl.value}/api/es-to-excel/paste`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: pasteText.value,
        format: excelFormat.value,
        use_chinese_names: useChineseNames.value
      })
    })
    const result = await response.json()

    if (result.success) {
      convertResult.value = result
      ElMessage.success(`处理成功！共 ${result.data_count} 条数据，${result.column_count} 个字段`)
    } else {
      ElMessage.error(result.message || '处理失败')
    }
  } catch (error) {
    console.error('处理错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    pasteLoading.value = false
  }
}

const handleReset = () => {
  activeTab.value = 'upload'
  uploadedFiles.value = []
  pendingFiles.value = []
  fileList.value = []
  pasteText.value = ''
  previewData.value = []
  columns.value = []
  totalCount.value = 0
  convertResult.value = null
}

// 跳转到字段映射配置页面
const goToMappingConfig = () => {
  router.push('/es-field-mapping')
}

// 组件挂载时加载字段映射
onMounted(() => {
  loadFieldMapping()
})
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
  align-items: center;
  flex-wrap: wrap;
}

.preview-section {
  margin-top: 30px;
}

.result-section {
  margin-top: 20px;
}

.paste-textarea {
  margin-bottom: 15px;
}

.paste-tips {
  margin-top: 10px;
}

.input-tabs {
  margin-bottom: 20px;
}

.el-upload__tip {
  color: #909399;
  font-size: 12px;
  margin-top: 10px;
}
</style>
