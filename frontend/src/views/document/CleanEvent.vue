<template>
  <div class="clean-event-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#667eea"><Filter /></el-icon> 事件数据清洗</h2>
      <p class="subtitle">处理 ES 查询结果，提取 EVENT_FP 并生成推送消息</p>
    </div>

    <!-- Tab 切换 -->
    <el-card class="tab-card" shadow="hover">
      <el-tabs v-model="activeTab" type="border-card" @tab-change="handleTabChange">
        <!-- 旧功能 Tab -->
        <el-tab-pane label="数据格式化（单条）" name="legacy-format">
          <div class="tab-content">
            <CleanEventPage />
          </div>
        </el-tab-pane>

        <!-- 新功能 Tab -->
        <el-tab-pane label="批量生成" name="es-processing">
          <div class="tab-content">
            <!-- 输入方式选择 -->
            <el-card class="input-card" shadow="never">
              <template #header>
                <div class="card-header-title">
                  <el-icon color="#409eff"><Setting /></el-icon>
                  <span>选择输入方式</span>
                </div>
              </template>

              <el-radio-group v-model="inputMode" size="large">
                <el-radio-button value="json">JSON 文件上传</el-radio-button>
                <el-radio-button value="textarea">粘贴 JSON 内容</el-radio-button>
              </el-radio-group>
            </el-card>

            <!-- 事件时间设置 -->
            <el-card class="event-time-card" shadow="never">
              <template #header>
                <div class="card-header-title">
                  <el-icon color="#e6a23c"><Clock /></el-icon>
                  <span>事件时间设置</span>
                </div>
              </template>

              <el-form label-width="120px">
                <el-form-item label="自定义事件时间">
                  <el-input
                    v-model="customEventTime"
                    placeholder="格式：YYYY-MM-DD HH:mm:ss 或留空使用数据中的时间"
                    clearable
                    style="width: 300px"
                  >
                    <template #prepend>
                      <el-icon><Clock /></el-icon>
                    </template>
                    <template #append>
                      <el-button @click="insertCurrentTime" title="插入当前时间">
                        <el-icon><Clock /></el-icon>
                      </el-button>
                    </template>
                  </el-input>
                  <div class="form-hint">例如：2026-04-13 14:30:00，留空则使用 ES 数据中的 EVENT_TIME</div>
                </el-form-item>
              </el-form>
            </el-card>

            <!-- JSON 文件上传 -->
            <el-card v-if="inputMode === 'json'" class="upload-card" shadow="never">
              <template #header>
                <div class="card-header-title">
                  <el-icon color="#67c23a"><UploadFilled /></el-icon>
                  <span>上传 JSON 文件</span>
                </div>
              </template>

              <el-upload
                drag
                action="/api/clean-event/upload"
                :auto-upload="false"
                :on-change="handleFileChange"
                :on-remove="handleRemove"
                :limit="1"
                accept=".json"
                :before-upload="beforeUpload"
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将 JSON 文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    只能上传 .json 文件
                  </div>
                </template>
              </el-upload>

              <!-- 上传并处理按钮 -->
              <div class="action-buttons" v-if="selectedFile">
                <el-button type="primary" @click="uploadAndProcess" :loading="loading">
                  <el-icon><Upload /></el-icon> 上传并处理
                </el-button>
              </div>
            </el-card>

            <!-- JSON 文本输入 -->
            <el-card v-if="inputMode === 'textarea'" class="textarea-card" shadow="never">
              <template #header>
                <div class="card-header-title">
                  <el-icon color="#67c23a"><EditPen /></el-icon>
                  <span>粘贴 JSON 内容</span>
                </div>
              </template>

              <el-input
                v-model="jsonText"
                type="textarea"
                :rows="15"
                placeholder="请粘贴 ES 查询结果的 JSON 内容..."
                resize="vertical"
              />

              <div class="action-buttons">
                <el-button type="primary" @click="processJsonText" :loading="loading">
                  <el-icon><VideoPlay /></el-icon> 开始处理
                </el-button>
                <el-button @click="clearText">
                  <el-icon><Delete /></el-icon> 清空
                </el-button>
              </div>
            </el-card>

            <!-- 加载提示 -->
            <el-card v-if="loading" class="loading-card" shadow="never">
              <template #header>
                <div class="card-header-title">
                  <el-icon color="#e6a23c" class="is-loading"><Loading /></el-icon>
                  <span>处理中...</span>
                </div>
              </template>
              <el-progress :percentage="80" status="warning" />
              <p class="loading-text">正在处理数据，请稍候...</p>
            </el-card>

            <!-- 处理结果 -->
            <el-card v-if="pushMessages.length > 0" class="result-card" shadow="never">
              <template #header>
                <div class="card-header-title">
                  <el-icon color="#67c23a"><SuccessFilled /></el-icon>
                  <span>处理结果</span>
                  <el-tag type="success" size="large">{{ pushMessages.length }} 条消息</el-tag>
                </div>
              </template>

              <!-- 统计信息 -->
              <div class="stats-info">
                <el-alert
                  title="处理成功"
                  :description="`共提取 ${pushMessages.length} 个唯一的 EVENT_FP，已生成 ${pushMessages.length} 条推送消息（${mainCount} 主单，${subCount} 子单）`"
                  type="success"
                  :closable="false"
                  show-icon
                />
              </div>

              <!-- 推送消息列表 -->
              <div class="messages-container">
                <div v-for="(msg, index) in pushMessages" :key="index" class="message-item">
                  <div class="message-header">
                    <div style="display: flex; align-items: center; gap: 10px;">
                      <el-tag type="primary">消息 {{ index + 1 }}</el-tag>
                      <el-tag :type="msg.IS_MAIN_ORDER ? 'success' : 'warning'" size="large">
                        {{ msg.ORDER_TYPE }}
                      </el-tag>
                      <el-tag v-if="msg.DISPATCH_REASON" type="info" size="small">
                        {{ msg.DISPATCH_REASON }}
                      </el-tag>
                    </div>
                    <el-button 
                      type="primary" 
                      size="small" 
                      @click="copyMessage(msg)"
                      :icon="CopyDocument"
                    >
                      复制
                    </el-button>
                  </div>
                  <div class="message-content">
                    <pre>{{ JSON.stringify(msg, null, 2) }}</pre>
                  </div>
                </div>
              </div>

              <!-- 批量操作 -->
              <div class="batch-actions">
                <el-button type="success" @click="copyAllMessages" :icon="CopyDocument">
                  复制所有消息
                </el-button>
                <el-button 
                  v-if="mainCount > 0" 
                  type="primary" 
                  @click="copyMainOrders" 
                  :icon="CopyDocument"
                >
                  复制所有主单 ({{ mainCount }})
                </el-button>
                <el-button 
                  v-if="subCount > 0" 
                  type="warning" 
                  @click="copySubOrders" 
                  :icon="CopyDocument"
                >
                  复制所有子单 ({{ subCount }})
                </el-button>
                <el-button type="warning" @click="downloadAllMessages" :icon="Download">
                  下载为 JSON 文件
                </el-button>
                <el-button @click="clearResults" :icon="Delete">
                  清空结果
                </el-button>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Filter,
  Setting,
  UploadFilled,
  Upload,
  EditPen,
  Delete,
  VideoPlay,
  Loading,
  SuccessFilled,
  CopyDocument,
  Download,
  Clock
} from '@element-plus/icons-vue'
import CleanEventPage from '../tools/CleanEventPage.vue'

const activeTab = ref('legacy-format')
const inputMode = ref('textarea')
const selectedFile = ref(null)
const jsonText = ref('')
const loading = ref(false)
const pushMessages = ref([])
const customEventTime = ref('')
const mainCount = ref(0)
const subCount = ref(0)

// Tab 切换处理
const handleTabChange = (tabName) => {
  console.log('切换到 Tab:', tabName)
}

// 插入当前时间
const insertCurrentTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  
  customEventTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 强制格式化 JSON（将 Python 三引号字符串转换为标准 JSON 格式）
const formatTripleQuotes = (text) => {
  // 匹配 Python 三引号字符串："""内容"""
  // 替换为转义后的 JSON 字符串："内容"
  const tripleQuoteRegex = /"""([\s\S]*?)"""/g
  
  return text.replace(tripleQuoteRegex, (match, content) => {
    // 转义内容中的双引号和反斜杠
    const escaped = content
      .replace(/\\/g, '\\\\')  // 先转义反斜杠
      .replace(/"/g, '\\"')     // 再转义双引号
      .replace(/\n/g, '\\n')    // 转义换行符
      .replace(/\r/g, '\\r')    // 转义回车符
      .replace(/\t/g, '\\t')    // 转义制表符
    return `"${escaped}"`
  })
}

// 文件上传前验证
const beforeUpload = (file) => {
  const isJson = file.name.endsWith('.json')
  if (!isJson) {
    ElMessage.error('只能上传 JSON 文件')
    return false
  }
  return true
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file
}

// 处理文件移除
const handleRemove = () => {
  selectedFile.value = null
}

// 上传并处理 JSON 文件
const uploadAndProcess = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  loading.value = true

  try {
    // 读取文件内容
    const fileContent = await selectedFile.value.raw.text()
    
    // 强制格式化：将三引号转换为标准 JSON 格式（处理 SRC_ORG_ALARM_TEXT、EVENT_EFFECT 等字段）
    const formattedContent = formatTripleQuotes(fileContent)
    
    // 解析 JSON
    let data
    try {
      const parsed = JSON.parse(formattedContent)
      
      // 如果是 ES 查询结果格式，提取 hits.hits 数组
      if (parsed.hits && parsed.hits.hits && Array.isArray(parsed.hits.hits)) {
        data = parsed.hits.hits.map(hit => hit._source).filter(source => source)
      } else if (Array.isArray(parsed)) {
        // 如果已经是数组，直接使用
        data = parsed
      } else {
        // 单个对象
        data = parsed
      }
    } catch (e) {
      ElMessage.error('JSON 格式错误：' + e.message)
      loading.value = false
      return
    }
    
    console.log('文件上传 - 发送的数据:', {
      data: data,
      custom_event_time: customEventTime.value || undefined
    })
    console.log('文件上传 - data 类型:', typeof data, Array.isArray(data) ? '数组' : '对象')
    if (Array.isArray(data)) {
      console.log('文件上传 - data 长度:', data.length)
      console.log('文件上传 - 第一个对象的 EVENT_FP:', data[0]?.EVENT_FP)
    }
    
    const response = await fetch('/api/clean-event/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: data,
        custom_event_time: customEventTime.value || undefined
      })
    })

    const result = await response.json()

    if (result.success) {
      pushMessages.value = result.data || []
      mainCount.value = result.main_count || 0
      subCount.value = result.sub_count || 0
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理粘贴的 JSON 文本
const processJsonText = async () => {
  if (!jsonText.value.trim()) {
    ElMessage.warning('请输入 JSON 内容')
    return
  }

  loading.value = true

  try {
    // 强制格式化：将三引号转换为标准 JSON 格式（处理 SRC_ORG_ALARM_TEXT、EVENT_EFFECT 等字段）
    const formattedText = formatTripleQuotes(jsonText.value)
    
    // 先验证 JSON 格式
    let data
    try {
      const parsed = JSON.parse(formattedText)
      
      // 如果是 ES 查询结果格式，提取 hits.hits 数组
      if (parsed.hits && parsed.hits.hits && Array.isArray(parsed.hits.hits)) {
        data = parsed.hits.hits.map(hit => hit._source).filter(source => source)
      } else if (Array.isArray(parsed)) {
        // 如果已经是数组，直接使用
        data = parsed
      } else {
        // 单个对象
        data = parsed
      }
    } catch (e) {
      ElMessage.error('JSON 格式错误：' + e.message)
      loading.value = false
      return
    }

    console.log('文本粘贴 - 发送的数据:', {
      data: data,
      custom_event_time: customEventTime.value || undefined
    })
    console.log('文本粘贴 - data 类型:', typeof data, Array.isArray(data) ? '数组' : '对象')
    if (Array.isArray(data)) {
      console.log('文本粘贴 - data 长度:', data.length)
      console.log('文本粘贴 - 第一个对象的 EVENT_FP:', data[0]?.EVENT_FP)
    }

    const response = await fetch('/api/clean-event/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        data: data,
        custom_event_time: customEventTime.value || undefined
      })
    })

    const result = await response.json()

    if (result.success) {
      pushMessages.value = result.data || []
      mainCount.value = result.main_count || 0
      subCount.value = result.sub_count || 0
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('处理失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 清空文本
const clearText = () => {
  jsonText.value = ''
}

// 复制到剪贴板的通用函数
const copyToClipboard = async (text, successMsg) => {
  try {
    // 方法1：使用现代 Clipboard API（仅在 HTTPS 或 localhost 下可用）
    if (typeof navigator !== 'undefined' && navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
      await navigator.clipboard.writeText(text)
      ElMessage.success(successMsg || '已复制到剪贴板')
      return
    }
    
    // 方法2：降级方案 - 使用传统的 execCommand（适用于 HTTP 环境）
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.left = '-999999px'
    textarea.style.top = '-999999px'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.focus()
    textarea.select()
    
    const successful = document.execCommand('copy')
    document.body.removeChild(textarea)
    
    if (successful) {
      ElMessage.success(successMsg || '已复制到剪贴板')
    } else {
      throw new Error('execCommand 复制失败')
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动选择文本复制（Ctrl+C）')
  }
}

// 复制单条消息
const copyMessage = (msg) => {
  const text = JSON.stringify(msg)
  copyToClipboard(text, '已复制到剪贴板')
}

// 复制所有消息
const copyAllMessages = () => {
  const text = pushMessages.value.map(msg => JSON.stringify(msg)).join('\n')
  copyToClipboard(text, '所有消息已复制到剪贴板')
}

// 复制所有主单
const copyMainOrders = () => {
  const mainOrders = pushMessages.value.filter(msg => msg.IS_MAIN_ORDER)
  
  if (mainOrders.length === 0) {
    ElMessage.warning('没有主单数据')
    return
  }
  
  const text = mainOrders.map(msg => JSON.stringify(msg)).join('\n')
  copyToClipboard(text, `已复制 ${mainOrders.length} 条主单`)
}

// 复制所有子单
const copySubOrders = () => {
  const subOrders = pushMessages.value.filter(msg => !msg.IS_MAIN_ORDER)
  
  if (subOrders.length === 0) {
    ElMessage.warning('没有子单数据')
    return
  }
  
  const text = subOrders.map(msg => JSON.stringify(msg)).join('\n')
  copyToClipboard(text, `已复制 ${subOrders.length} 条子单`)
}

// 下载所有消息为 JSON 文件
const downloadAllMessages = () => {
  const text = pushMessages.value.map(msg => JSON.stringify(msg)).join('\n')
  const blob = new Blob([text], { type: 'application/json' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `push_messages_${new Date().getTime()}.json`
  a.click()
  window.URL.revokeObjectURL(url)
  ElMessage.success('下载成功')
}

// 清空结果
const clearResults = () => {
  pushMessages.value = []
  mainCount.value = 0
  subCount.value = 0
}
</script>

<style scoped>
.clean-event-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.page-header h2 {
  margin: 0 0 10px 0;
  font-size: 32px;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-header .subtitle {
  margin: 0;
  font-size: 16px;
  color: #909399;
}

.tab-card {
  border-radius: 16px;
  transition: all 0.3s ease;
}

.tab-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.tab-content {
  min-height: 500px;
}

/* 覆盖 el-tabs 样式 */
:deep(.el-tabs--border-card) {
  border: none;
  box-shadow: none;
  background: transparent;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  padding: 0;
}

.input-card,
.upload-card,
.textarea-card,
.event-time-card,
.loading-card,
.result-card {
  margin-bottom: 20px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.form-hint {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
  padding-left: 5px;
  line-height: 1.5;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.loading-text {
  text-align: center;
  margin-top: 15px;
  color: #909399;
  font-size: 14px;
}

.stats-info {
  margin-bottom: 20px;
}

.messages-container {
  max-height: 600px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.message-item {
  margin-bottom: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  background: #f5f7fa;
  transition: all 0.3s ease;
}

.message-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.message-content {
  background: #fff;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.message-content pre {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.batch-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  padding-top: 20px;
  border-top: 2px solid #e4e7ed;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 2px solid #ebeef5;
}

:deep(.el-card__body) {
  padding: 20px;
}

:deep(.el-button) {
  border-radius: 980px !important;
  padding: 0 24px !important;
  font-weight: 500 !important;
  height: 40px !important;
}

:deep(.el-button--large) {
  height: 44px !important;
  padding: 0 28px !important;
  font-size: 15px !important;
}

:deep(.el-radio-button__inner) {
  border-radius: 980px !important;
}

:deep(.el-upload-dragger) {
  border-radius: 12px !important;
  padding: 40px 20px !important;
}
</style>
