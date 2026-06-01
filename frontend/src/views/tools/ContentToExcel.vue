<template>
  <div class="content-to-excel-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28"><Document /></el-icon> 内容转 Excel 工具</h2>
      <p class="subtitle">上传升级申请文档，自动生成标准化 Excel 装载记录表</p>
    </div>

    <!-- 主功能区域 -->
    <el-card class="main-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#667eea"><Upload /></el-icon>
          <span>文件上传与生成</span>
        </div>
      </template>

      <!-- 文件上传区域 -->
      <el-upload
        class="upload-area"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :file-list="fileList"
        accept=".md,.txt"
        multiple
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击选择</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .md / .txt 格式，单个文件不超过 5MB
          </div>
        </template>
      </el-upload>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button
          type="primary"
          :loading="previewLoading"
          :disabled="!selectedFile"
          @click="handlePreview"
        >
          <el-icon><View /></el-icon> 预览解析结果
        </el-button>
        <el-button
          type="success"
          :loading="generateLoading"
          :disabled="!selectedFile"
          @click="handleGenerate"
        >
          <el-icon><Download /></el-icon> 生成并下载 Excel
        </el-button>
        <el-button @click="handleReset">
          <el-icon><RefreshLeft /></el-icon> 重置
        </el-button>
      </div>

      <!-- 解析结果预览 -->
      <div v-if="previewRecords.length > 0" class="preview-section">
        <el-divider content-position="left">
          <el-icon><List /></el-icon>
          解析结果预览（共 {{ previewRecords.length }} 条升级记录）
        </el-divider>

        <el-table :data="previewRecords" border stripe max-height="400">
          <el-table-column prop="title" label="升级标题" min-width="280" show-overflow-tooltip />
          <el-table-column prop="date_str" label="日期" width="120" />
          <el-table-column prop="type_desc" label="类型" width="100" />
          <el-table-column label="匹配软件" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="sw in (row.matched_softwares || [])" :key="sw" size="small" style="margin-right: 4px;">
                {{ sw }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 生成结果 -->
      <div v-if="generateResult" class="result-section">
        <el-alert
          :title="generateResult.message"
          type="success"
          :closable="false"
          show-icon
        >
          <template #default>
            <div class="result-details">
              <p>✅ 包含 <strong>{{ generateResult.records_count }}</strong> 条升级记录，涉及 <strong>{{ generateResult.software_count }}</strong> 个软件</p>
              <el-button type="primary" size="small" @click="handleDownload">
                <el-icon><Download /></el-icon> 下载 Excel 文件
              </el-button>
            </div>
          </template>
        </el-alert>
      </div>

      <!-- 使用说明 -->
      <el-divider content-position="left">
        <el-icon><InfoFilled /></el-icon> 使用说明
      </el-divider>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="输入格式">
          升级申请文档（.md / .txt），每条记录以"监控综合应用平台YYYY年M月D日功能升级申请"开头
        </el-descriptions-item>
        <el-descriptions-item label="输出内容">
          包含 4 个 Sheet 的 .xlsx 文件：主表、版本号计算、初始版本号、软件名称和目标IP
        </el-descriptions-item>
        <el-descriptions-item label="软件匹配">
          3月升级仅匹配「智能调服务」，4月及之后匹配「省内工单服务」+「智能调服务」
        </el-descriptions-item>
        <el-descriptions-item label="日期修正">
          原始文档中"3月2日"自动修正为"3月11日"（历史约定）
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 关键字库管理 -->
    <el-card class="keyword-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#667eea"><Setting /></el-icon>
          <span>关键字库管理</span>
        </div>
      </template>

      <el-tabs v-model="keywordTab" type="border-card">
        <!-- 软件-IP映射管理 -->
        <el-tab-pane label="软件名称和目标IP" name="software-ip">
          <div class="keyword-actions">
            <el-button type="primary" size="small" @click="openSoftwareDialog()">
              <el-icon><Plus /></el-icon> 新增软件
            </el-button>
            <el-button size="small" @click="loadSoftwareList">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>

          <el-table :data="softwareList" border stripe max-height="400">
            <el-table-column prop="software_name" label="软件名称" width="160" />
            <el-table-column prop="target_ip" label="目标IP" min-width="250" show-overflow-tooltip />
            <el-table-column prop="operator" label="操作人员" width="100" />
            <el-table-column prop="verifier" label="验证人员" width="100" />
            <el-table-column prop="initial_version" label="初始版本" width="100" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="openSoftwareDialog(row)">编辑</el-button>
                <el-popconfirm
                  v-if="!isBuiltinSoftware(row.software_name)"
                  title="确认删除？"
                  @confirm="handleDeleteSoftware(row.software_name)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 初始版本号管理 -->
        <el-tab-pane label="初始版本号" name="initial-version">
          <div class="keyword-actions">
            <el-button type="primary" size="small" @click="openVersionDialog()">
              <el-icon><Plus /></el-icon> 新增版本
            </el-button>
            <el-button size="small" @click="loadVersionList">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>

          <el-table :data="versionList" border stripe max-height="400">
            <el-table-column prop="software_name" label="软件名称" width="160" />
            <el-table-column prop="initial_version" label="初始化基准版本" width="130" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="openVersionDialog(row)">编辑</el-button>
                <el-popconfirm
                  v-if="!isBuiltinVersion(row.software_name)"
                  title="确认删除？"
                  @confirm="handleDeleteVersion(row.software_name)"
                >
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 软件-IP编辑对话框 -->
    <el-dialog v-model="softwareDialogVisible" :title="isEditSoftware ? '编辑软件' : '新增软件'" width="600px">
      <el-form :model="softwareForm" label-width="100px">
        <el-form-item label="软件名称">
          <el-input v-model="softwareForm.software_name" :disabled="isEditSoftware && isBuiltinSoftware(softwareForm.software_name)" placeholder="如：省内工单服务" />
        </el-form-item>
        <el-form-item label="目标IP">
          <el-input v-model="softwareForm.target_ip" placeholder="如：10.44.225.197、10.43.118.48" />
        </el-form-item>
        <el-form-item label="操作人员">
          <el-input v-model="softwareForm.operator" placeholder="如：姚翔" />
        </el-form-item>
        <el-form-item label="验证人员">
          <el-input v-model="softwareForm.verifier" placeholder="如：林子旺" />
        </el-form-item>
        <el-form-item label="初始版本">
          <el-input v-model="softwareForm.initial_version" placeholder="如：1.5.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="softwareDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSoftware">保存</el-button>
      </template>
    </el-dialog>

    <!-- 初始版本编辑对话框 -->
    <el-dialog v-model="versionDialogVisible" :title="isEditVersion ? '编辑初始版本' : '新增初始版本'" width="500px">
      <el-form :model="versionForm" label-width="100px">
        <el-form-item label="软件名称">
          <el-select v-model="versionForm.software_name" placeholder="选择软件" filterable>
            <el-option
              v-for="sw in (softwareList.length > 0 ? softwareList : builtinSoftwareList)"
              :key="sw.software_name"
              :label="sw.software_name"
              :value="sw.software_name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="初始版本">
          <el-input v-model="versionForm.initial_version" placeholder="如：1.5.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveVersion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document, UploadFilled, View, Download, RefreshLeft, List, InfoFilled,
  Setting, Plus, Refresh
} from '@element-plus/icons-vue'

// ============================================================================
// 文件上传相关状态
// ============================================================================
const fileList = ref([])
const selectedFile = ref(null)
const previewLoading = ref(false)
const generateLoading = ref(false)
const previewRecords = ref([])
const generateResult = ref(null)

// ============================================================================
// 关键字库管理状态
// ============================================================================
const keywordTab = ref('software-ip')
const softwareList = ref([])
const versionList = ref([])
const builtinSoftwareList = ref([])

// 软件编辑对话框
const softwareDialogVisible = ref(false)
const isEditSoftware = ref(false)
const editingSoftwareName = ref('')
const softwareForm = reactive({
  software_name: '',
  target_ip: '',
  operator: '',
  verifier: '',
  initial_version: '',
})

// 版本编辑对话框
const versionDialogVisible = ref(false)
const isEditVersion = ref(false)
const editingVersionName = ref('')
const versionForm = reactive({
  software_name: '',
  initial_version: '',
})

// ============================================================================
// API 基础 URL（开发环境通过 Vite 代理）
// ============================================================================
const API_BASE = '/api/content-to-excel'

// ============================================================================
// 文件处理
// ============================================================================
function handleFileChange(file) {
  // 只保留最后一个文件（单文件模式）
  fileList.value = [file]
  selectedFile.value = file.raw
}

function handleFileRemove() {
  fileList.value = []
  selectedFile.value = null
  previewRecords.value = []
  generateResult.value = null
}

function handleReset() {
  fileList.value = []
  selectedFile.value = null
  previewRecords.value = []
  generateResult.value = null
}

// ============================================================================
// 预览解析结果
// ============================================================================
async function handlePreview() {
  if (!selectedFile.value) return

  previewLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch(`${API_BASE}/preview`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: formData,
    })

    const result = await response.json()

    if (result.success) {
      previewRecords.value = result.records
      ElMessage.success(`成功解析 ${result.records.length} 条升级记录`)
    } else {
      ElMessage.error(result.message || '解析失败')
    }
  } catch (error) {
    ElMessage.error('网络请求失败: ' + error.message)
  } finally {
    previewLoading.value = false
  }
}

// ============================================================================
// 生成并下载 Excel
// ============================================================================
async function handleGenerate() {
  if (!selectedFile.value) return

  generateLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: formData,
    })

    const result = await response.json()

    if (result.success) {
      generateResult.value = result
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message || '生成失败')
    }
  } catch (error) {
    ElMessage.error('网络请求失败: ' + error.message)
  } finally {
    generateLoading.value = false
  }
}

// ============================================================================
// 下载 Excel 文件
// ============================================================================
function handleDownload() {
  if (!generateResult.value?.file_path) return

  // 从后端路径提取文件名，构建下载 URL
  const fileName = generateResult.value.file_path.split('/').pop()
  window.open(`/api/content-to-excel/download/${fileName}`, '_blank')
}

// ============================================================================
// 关键字库管理 - 软件-IP映射
// ============================================================================
async function loadSoftwareList() {
  try {
    const response = await fetch(`${API_BASE}/software-ip-list`)
    const result = await response.json()
    if (result.success) {
      softwareList.value = result.data
    }
  } catch (error) {
    console.error('加载软件列表失败:', error)
  }
}

async function loadBuiltinSoftwareList() {
  try {
    const response = await fetch(`${API_BASE}/builtin-software-list`)
    const result = await response.json()
    if (result.success) {
      builtinSoftwareList.value = result.data
    }
  } catch (error) {
    console.error('加载内置软件列表失败:', error)
  }
}

function openSoftwareDialog(row = null) {
  if (row) {
    isEditSoftware.value = true
    editingSoftwareName.value = row.software_name
    Object.assign(softwareForm, {
      software_name: row.software_name,
      target_ip: row.target_ip || '',
      operator: row.operator || '',
      verifier: row.verifier || '',
      initial_version: row.initial_version || '',
    })
  } else {
    isEditSoftware.value = false
    editingSoftwareName.value = ''
    Object.assign(softwareForm, {
      software_name: '',
      target_ip: '',
      operator: '',
      verifier: '',
      initial_version: '',
    })
  }
  softwareDialogVisible.value = true
}

async function handleSaveSoftware() {
  if (!softwareForm.software_name.trim()) {
    ElMessage.warning('软件名称不能为空')
    return
  }

  try {
    const url = isEditSoftware.value
      ? `${API_BASE}/software-ip/${encodeURIComponent(editingSoftwareName.value)}`
      : `${API_BASE}/software-ip`

    const method = isEditSoftware.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(softwareForm),
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success(result.message)
      softwareDialogVisible.value = false
      loadSoftwareList()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('请求失败: ' + error.message)
  }
}

async function handleDeleteSoftware(softwareName) {
  try {
    const response = await fetch(`${API_BASE}/software-ip/${encodeURIComponent(softwareName)}`, {
      method: 'DELETE',
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success(result.message)
      loadSoftwareList()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('请求失败: ' + error.message)
  }
}

// ============================================================================
// 关键字库管理 - 初始版本号
// ============================================================================
async function loadVersionList() {
  try {
    const response = await fetch(`${API_BASE}/initial-version-list`)
    const result = await response.json()
    if (result.success) {
      versionList.value = result.data
    }
  } catch (error) {
    console.error('加载版本列表失败:', error)
  }
}

function openVersionDialog(row = null) {
  if (row) {
    isEditVersion.value = true
    editingVersionName.value = row.software_name
    Object.assign(versionForm, {
      software_name: row.software_name,
      initial_version: row.initial_version || '',
    })
  } else {
    isEditVersion.value = false
    editingVersionName.value = ''
    Object.assign(versionForm, {
      software_name: '',
      initial_version: '',
    })
  }
  versionDialogVisible.value = true
}

async function handleSaveVersion() {
  if (!versionForm.software_name || !versionForm.initial_version.trim()) {
    ElMessage.warning('软件名称和版本号均不能为空')
    return
  }

  try {
    const url = isEditVersion.value
      ? `${API_BASE}/initial-version/${encodeURIComponent(editingVersionName.value)}`
      : `${API_BASE}/initial-version`

    const method = isEditVersion.value ? 'PUT' : 'POST'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(versionForm),
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success(result.message)
      versionDialogVisible.value = false
      loadVersionList()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('请求失败: ' + error.message)
  }
}

async function handleDeleteVersion(softwareName) {
  try {
    const response = await fetch(`${API_BASE}/initial-version/${encodeURIComponent(softwareName)}`, {
      method: 'DELETE',
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success(result.message)
      loadVersionList()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('请求失败: ' + error.message)
  }
}

// ============================================================================
// 工具函数
// ============================================================================
function isBuiltinSoftware(name) {
  return builtinSoftwareList.value.some(s => s.software_name === name)
}

function isBuiltinVersion(name) {
  return builtinSoftwareList.value.some(s => s.software_name === name)
}

// ============================================================================
// 初始化加载
// ============================================================================
onMounted(() => {
  loadSoftwareList()
  loadBuiltinSoftwareList()
})
</script>

<style scoped>
.content-to-excel-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-header h2 {
  color: #333;
  margin-bottom: 8px;
}

.page-header .subtitle {
  color: #666;
  font-size: 14px;
}

.main-card {
  margin-bottom: 20px;
}

.keyword-card {
  margin-bottom: 20px;
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.upload-area {
  margin-bottom: 16px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.preview-section {
  margin-bottom: 20px;
}

.result-section {
  margin-bottom: 20px;
}

.result-details {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.keyword-actions {
  margin-bottom: 16px;
}
</style>
