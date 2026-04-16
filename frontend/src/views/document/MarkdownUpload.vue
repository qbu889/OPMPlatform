<template>
  <div class="markdown-upload-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>
        <el-icon :size="36"><Files /></el-icon>
        Markdown 上传转换
      </h2>
      <p class="subtitle">将 Markdown 文件转换为 Word 文档</p>
    </div>

    <!-- 上传转换卡片 -->
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><UploadFilled /></el-icon>
          <span>文件上传</span>
        </div>
      </template>

      <div class="converter-body">
        <el-alert v-if="error" type="error" :closable="true" show-icon style="margin-bottom: 20px;">
          {{ error }}
        </el-alert>

        <el-form label-width="120px">
          <el-form-item label="选择文件">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".md"
              drag
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  仅支持 .md 格式文件
                </div>
              </template>
            </el-upload>
          </el-form-item>

          <el-form-item>
            <div class="action-area">
              <el-button 
                type="primary" 
                size="large" 
                :loading="uploading" 
                :disabled="!selectedFile"
                @click="handleUpload"
              >
                <el-icon><Upload /></el-icon>
                上传并转换
              </el-button>
              <el-button type="success" size="large" @click="openKeywordModal">
                <el-icon><Key /></el-icon>
                关键词管理
              </el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 关键词管理对话框 -->
    <el-dialog
      v-model="keywordModalVisible"
      title="关键词管理"
      width="90%"
      :close-on-click-modal="false"
    >
      <!-- 统计信息 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="12">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-content">
              <div>
                <div class="stats-label">人工操作关键词</div>
                <div class="stats-number">{{ personKeywords.length }}</div>
              </div>
              <el-icon :size="60" color="#667eea" style="opacity: 0.1;"><User /></el-icon>
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover" class="stats-card">
            <div class="stats-content">
              <div>
                <div class="stats-label">系统操作关键词</div>
                <div class="stats-number">{{ systemKeywords.length }}</div>
              </div>
              <el-icon :size="60" color="#f6ad55" style="opacity: 0.1;"><Monitor /></el-icon>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 操作按钮 -->
      <div style="margin-bottom: 16px;">
        <el-button type="primary" @click="openAddDialog('person')">
          <el-icon><Plus /></el-icon>
          添加人工关键词
        </el-button>
        <el-button type="warning" @click="openAddDialog('system')">
          <el-icon><Plus /></el-icon>
          添加系统关键词
        </el-button>
        <el-button @click="loadKeywords">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>

      <!-- 关键词表格 -->
      <el-table :data="allKeywords" border stripe max-height="400">
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === '人工' ? 'primary' : 'warning'">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="keyword" label="关键词" />
        <el-table-column label="操作" width="180" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="editKeyword(row.originalType, row.keyword)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="deleteKeyword(row.originalType, row.keyword)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="keywordModalVisible = false">关闭</el-button>
        <el-button type="info" @click="openHistoryModal">
          <el-icon><Clock /></el-icon>
          历史记录
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑关键词对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="isEdit ? '编辑关键词' : '添加关键词'"
      width="500px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="关键词">
          <el-input v-model="editForm.keyword" placeholder="请输入关键词" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="editForm.comment"
            type="textarea"
            :rows="3"
            placeholder="可选备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveKeyword">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 历史记录对话框 -->
    <el-dialog
      v-model="historyModalVisible"
      title="关键词修改历史"
      width="90%"
    >
      <div style="margin-bottom: 16px;">
        <el-button type="success" @click="createSnapshot('person')">
          <el-icon><Camera /></el-icon>
          创建人工版本快照
        </el-button>
        <el-button type="primary" @click="createSnapshot('system')">
          <el-icon><Camera /></el-icon>
          创建系统版本快照
        </el-button>
        <el-button @click="loadHistory">
          <el-icon><Refresh /></el-icon>
          刷新历史
        </el-button>
      </div>

      <el-table :data="historyList" border stripe max-height="500">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.keyword_type === 'person_keywords' ? 'primary' : 'warning'">
              {{ row.keyword_type === 'person_keywords' ? '人工' : '系统' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)">
              {{ getActionText(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="keyword" label="关键词" width="150" />
        <el-table-column prop="original_keyword" label="原关键词" width="150">
          <template #default="{ row }">
            {{ row.original_keyword || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="200" />
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="restoreHistory(row.id)">
              <el-icon><RefreshLeft /></el-icon>
              {{ row.is_snapshot ? '完整恢复' : '恢复' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button @click="historyModalVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Files,
  UploadFilled,
  Upload,
  Key,
  User,
  Monitor,
  Plus,
  Refresh,
  Edit,
  Delete,
  Check,
  Clock,
  Camera,
  RefreshLeft
} from '@element-plus/icons-vue'

// 状态变量
const uploading = ref(false)
const error = ref('')
const selectedFile = ref(null)
const uploadRef = ref(null)

// 关键词管理
const keywordModalVisible = ref(false)
const personKeywords = ref([])
const systemKeywords = ref([])

// 编辑对话框
const editDialogVisible = ref(false)
const isEdit = ref(false)
const editForm = ref({
  type: '',
  keyword: '',
  original: '',
  comment: ''
})

// 历史记录
const historyModalVisible = ref(false)
const historyList = ref([])

// 计算所有关键词
const allKeywords = computed(() => {
  const list = []
  personKeywords.value.forEach(kw => {
    list.push({ type: '人工', keyword: kw, originalType: 'person' })
  })
  systemKeywords.value.forEach(kw => {
    list.push({ type: '系统', keyword: kw, originalType: 'system' })
  })
  return list
})

// 文件选择处理
const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

// 上传文件
const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)

    const response = await fetch('/markdown-upload/upload', {
      method: 'POST',
      body: formData
    })

    const result = await response.json()

    if (result.success) {
      ElMessage.success('转换成功，正在下载 Word 文件')
      if (result.download_url) {
        window.open(result.download_url, '_blank')
      }
      // 清空选择
      selectedFile.value = null
      if (uploadRef.value) {
        uploadRef.value.clearFiles()
      }
    } else {
      ElMessage.error(result.message || '转换失败')
    }
  } catch (err) {
    console.error('上传错误:', err)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    uploading.value = false
  }
}

// 打开关键词管理对话框
const openKeywordModal = () => {
  loadKeywords()
  keywordModalVisible.value = true
}

// 加载关键词
const loadKeywords = async () => {
  try {
    const response = await fetch('/api/keywords')
    const data = await response.json()
    personKeywords.value = data.person_keywords || []
    systemKeywords.value = data.system_keywords || []
  } catch (err) {
    console.error('加载关键词失败:', err)
    ElMessage.error('加载关键词失败')
  }
}

// 打开添加对话框
const openAddDialog = (type) => {
  isEdit.value = false
  editForm.value = {
    type: type + '_keywords',
    keyword: '',
    original: '',
    comment: ''
  }
  editDialogVisible.value = true
}

// 编辑关键词
const editKeyword = (type, keyword) => {
  isEdit.value = true
  editForm.value = {
    type: type + '_keywords',
    keyword: keyword,
    original: keyword,
    comment: ''
  }
  editDialogVisible.value = true
}

// 保存关键词
const saveKeyword = async () => {
  if (!editForm.value.keyword.trim()) {
    ElMessage.warning('请输入关键词')
    return
  }

  try {
    const response = await fetch('/api/keywords', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editForm.value)
    })

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success(isEdit.value ? '编辑成功' : '添加成功')
      editDialogVisible.value = false
      await loadKeywords()
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (err) {
    console.error('保存关键词失败:', err)
    ElMessage.error('保存失败')
  }
}

// 删除关键词
const deleteKeyword = async (type, keyword) => {
  try {
    await ElMessageBox.confirm(`确定要删除关键词 "${keyword}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await fetch('/api/keywords', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ type: type + '_keywords', keyword })
    })

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('删除成功')
      await loadKeywords()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除关键词失败:', err)
      ElMessage.error('删除失败')
    }
  }
}

// 打开历史记录对话框
const openHistoryModal = () => {
  loadHistory()
  historyModalVisible.value = true
}

// 加载历史记录
const loadHistory = async () => {
  try {
    const response = await fetch('/api/keywords/history?page=1&per_page=50')
    const result = await response.json()

    if (result.status === 'success') {
      historyList.value = result.data || []
    } else {
      ElMessage.error('加载历史失败')
    }
  } catch (err) {
    console.error('加载历史失败:', err)
    ElMessage.error('加载历史失败')
  }
}

// 恢复历史记录
const restoreHistory = async (historyId) => {
  try {
    await ElMessageBox.confirm('确定要恢复到此历史版本吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await fetch(`/api/keywords/history/${historyId}/restore`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('恢复成功')
      await loadKeywords()
      await loadHistory()
    } else {
      ElMessage.error(result.message || '恢复失败')
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('恢复失败:', err)
      ElMessage.error('恢复失败')
    }
  }
}

// 创建版本快照
const createSnapshot = async (type) => {
  try {
    const remark = await ElMessageBox.prompt('请输入版本快照备注（可选）', '创建版本快照', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: '手动创建版本快照'
    })

    const response = await fetch('/api/keywords/snapshot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        type: type,
        remark: remark.value || '手动创建版本快照'
      })
    })

    const result = await response.json()

    if (result.status === 'success') {
      ElMessage.success('版本快照创建成功')
      await loadHistory()
    } else {
      ElMessage.error(result.message || '创建失败')
    }
  } catch (err) {
    if (err !== 'cancel') {
      console.error('创建快照失败:', err)
      ElMessage.error('创建失败')
    }
  }
}

// 获取操作标签类型
const getActionTagType = (action) => {
  const types = {
    add: 'success',
    edit: 'info',
    delete: 'danger',
    snapshot: 'primary',
    restore_add: 'warning',
    restore_edit: 'warning',
    restore_delete: 'warning',
    restore_snapshot: 'warning'
  }
  return types[action] || ''
}

// 获取操作文本
const getActionText = (action) => {
  const texts = {
    add: '添加',
    edit: '编辑',
    delete: '删除',
    snapshot: '版本快照',
    restore_add: '恢复添加',
    restore_edit: '恢复编辑',
    restore_delete: '恢复删除',
    restore_snapshot: '恢复快照'
  }
  return texts[action] || action
}

// 格式化时间
const formatDateTime = (datetimeStr) => {
  if (!datetimeStr) return '-'
  const date = new Date(datetimeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.markdown-upload-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: #333;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 卡片通用样式 */
.upload-card {
  margin-bottom: 25px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.upload-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.converter-body {
  padding: 20px 0;
}

/* 修复表单布局 */
:deep(.el-form-item__label) {
  font-weight: 500;
  white-space: nowrap;
}

/* 上传区域样式 */
:deep(.el-upload-dragger) {
  padding: 40px 20px;
  border-radius: 12px;
}

:deep(.el-icon--upload) {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 15px;
}

:deep(.el-upload__text) {
  font-size: 16px;
  color: #606266;
  margin-bottom: 8px;
}

:deep(.el-upload__text em) {
  color: #409eff;
  font-style: normal;
  font-weight: 500;
}

:deep(.el-card__header) {
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* 按钮区域优化 */
.action-area {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-top: 24px;
}

/* 统计卡片 */
.stats-card {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
  border-radius: 12px;
}

.stats-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-label {
  font-size: 0.875rem;
  color: #718096;
  margin-bottom: 8px;
}

.stats-number {
  font-size: 2rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>
