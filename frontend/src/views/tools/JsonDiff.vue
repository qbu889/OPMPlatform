<template>
  <div class="json-diff-container">
    <!-- 标题栏 -->
    <div class="page-header">
      <h2>JSON 对比工具</h2>
      <p class="subtitle">智能对比两个 JSON 数据，忽略字段顺序差异</p>
    </div>

    <!-- 输入区域 -->
    <el-row :gutter="20" class="input-section">
      <!-- 左侧输入 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>左侧 JSON</span>
              <el-button size="small" @click="clearLeft">清空</el-button>
            </div>
          </template>
          <el-input
            v-model="leftJson"
            type="textarea"
            :rows="15"
            placeholder="请粘贴或输入左侧 JSON 数据..."
            @input="onLeftInput"
          />
          <div class="file-upload">
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="(file) => handleFileUpload(file, 'left')"
            >
              <el-button size="small" type="primary" plain>
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </el-upload>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧输入 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>右侧 JSON</span>
              <el-button size="small" @click="clearRight">清空</el-button>
            </div>
          </template>
          <el-input
            v-model="rightJson"
            type="textarea"
            :rows="15"
            placeholder="请粘贴或输入右侧 JSON 数据..."
            @input="onRightInput"
          />
          <div class="file-upload">
            <el-upload
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="(file) => handleFileUpload(file, 'right')"
            >
              <el-button size="small" type="primary" plain>
                <el-icon><Upload /></el-icon>
                上传文件
              </el-button>
            </el-upload>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" size="large" @click="compareJson" :loading="comparing">
        <el-icon><Search /></el-icon>
        开始对比
      </el-button>
      <el-button size="large" @click="loadExample">
        <el-icon><Document /></el-icon>
        加载示例
      </el-button>
      <el-switch
        v-model="autoCompare"
        active-text="实时对比"
        inactive-text="手动对比"
        style="margin-left: 20px"
      />
      <el-button 
        v-if="hasResult"
        size="large" 
        :type="compareMode === 'right' ? 'success' : 'default'"
        @click="toggleCompareMode"
        style="margin-left: 20px"
      >
        <el-icon><Switch /></el-icon>
        {{ compareMode === 'left' ? '以右侧字段为基准' : '以左侧字段为基准' }}
      </el-button>
    </div>

    <!-- 统计信息 -->
    <el-alert
      v-if="stats.total > 0"
      :title="`对比结果：共 ${stats.total} 个字段`"
      type="info"
      :closable="false"
      show-icon
      class="stats-alert"
    >
      <template #default>
        <el-tag type="success" style="margin-right: 10px">相同: {{ stats.same }}</el-tag>
        <el-tag type="danger" style="margin-right: 10px">不同: {{ stats.different }}</el-tag>
        <el-tag type="warning" style="margin-right: 10px">新增: {{ stats.added }}</el-tag>
        <el-tag type="info">删除: {{ stats.removed }}</el-tag>
      </template>
    </el-alert>

    <!-- 对比结果 -->
    <el-row v-if="hasResult" :gutter="20" class="result-section">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>左侧结果</span>
          </template>
          <div class="diff-viewer" ref="leftViewerRef" @scroll="handleLeftScroll">
            <pre v-html="renderDiffTree(diffResult.left_tree, 'left')"></pre>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>右侧结果</span>
          </template>
          <div class="diff-viewer" ref="rightViewerRef" @scroll="handleRightScroll">
            <pre v-html="renderDiffTree(diffResult.right_tree, 'right')"></pre>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Switch, Search, Document, Upload } from '@element-plus/icons-vue'
import axios from 'axios'

const leftJson = ref('')
const rightJson = ref('')
const comparing = ref(false)
const autoCompare = ref(false)
const diffResult = ref({})
const hasResult = ref(false)
const compareMode = ref('left') // 'left' 或 'right'
const leftViewerRef = ref(null)
const rightViewerRef = ref(null)
const isSyncingScroll = ref(false) // 防止循环触发

const stats = computed(() => {
  return diffResult.value.stats || { same: 0, different: 0, added: 0, removed: 0, total: 0 }
})

let compareTimer = null

// 左侧输入处理
const onLeftInput = () => {
  if (autoCompare.value && leftJson.value && rightJson.value) {
    clearTimeout(compareTimer)
    compareTimer = setTimeout(() => {
      compareJson()
    }, 1000)
  }
}

// 右侧输入处理
const onRightInput = () => {
  if (autoCompare.value && leftJson.value && rightJson.value) {
    clearTimeout(compareTimer)
    compareTimer = setTimeout(() => {
      compareJson()
    }, 1000)
  }
}

// 清空左侧
const clearLeft = () => {
  leftJson.value = ''
  hasResult.value = false
}

// 清空右侧
const clearRight = () => {
  rightJson.value = ''
  hasResult.value = false
}

// 文件上传处理
const handleFileUpload = (file, side) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    if (side === 'left') {
      leftJson.value = content
    } else {
      rightJson.value = content
    }
    ElMessage.success(`已加载文件: ${file.name}`)
  }
  reader.readAsText(file.raw)
}

// 执行对比
const compareJson = async () => {
  if (!leftJson.value.trim() || !rightJson.value.trim()) {
    ElMessage.warning('请填写左右两侧的 JSON 数据')
    return
  }

  comparing.value = true
  
  try {
    const response = await axios.post('/api/diff/compare', {
      left: leftJson.value,
      right: rightJson.value,
      options: {
        strict_mode: false,
        ignore_case: false,
        ignore_whitespace: false
      }
    })

    if (response.data.success) {
      diffResult.value = response.data.data
      hasResult.value = true
      ElMessage.success('对比完成')
    } else {
      ElMessage.error(response.data.message || '对比失败')
    }
  } catch (error) {
    console.error('对比错误:', error)
    ElMessage.error(error.response?.data?.message || '网络请求失败')
  } finally {
    comparing.value = false
  }
}

// 渲染对比树
const renderDiffTree = (tree, side) => {
  if (!tree) return ''
  
  let html = ''
  
  if (Array.isArray(tree)) {
    // 数组类型
    html += '[\n'
    tree.forEach((item, index) => {
      html += renderNode(item, side, index)
    })
    html += ']'
  } else if (typeof tree === 'object') {
    // 对象类型
    html += '{\n'
    Object.keys(tree).forEach(key => {
      const node = tree[key]
      // 根据对比模式过滤字段
      if (shouldShowNode(node, side)) {
        html += renderNode(node, side, key)
      }
    })
    html += '}'
  }
  
  return html
}

// 判断是否应该显示该节点
const shouldShowNode = (node, side) => {
  if (!node) return false
  
  // 以右侧为基准时，左侧视图不显示仅在左侧存在的字段（added状态）
  if (compareMode.value === 'right' && side === 'left') {
    return node.status !== 'added'
  }
  
  // 以左侧为基准时，右侧视图不显示仅在右侧存在的字段（removed状态在右侧是added）
  if (compareMode.value === 'left' && side === 'right') {
    return node.status !== 'added'
  }
  
  return true
}

// 渲染单个节点
const renderNode = (node, side, key) => {
  if (!node) return ''
  
  let html = ''
  const indent = '  '
  
  // 添加键名（如果不是数组元素）
  if (typeof key !== 'number') {
    html += `${indent}"${key}": `
  }
  
  // 根据状态设置样式
  const statusClass = getStatusClass(node.status)
  
  if (node.children) {
    // 有子节点（对象或数组）
    html += `<span class="${statusClass}">${node.type === 'object' ? '{' : '['}</span>\n`
    html += renderDiffTree(node.children, side)
    html += `\n${indent}<span class="${statusClass}">${node.type === 'object' ? '}' : ']'}</span>,\n`
  } else {
    // 叶子节点 - 特殊处理 null/undefined
    let value
    
    // same 状态的节点使用 value 字段
    if (node.status === 'same') {
      value = node.value
    } else {
      // different/added/removed 状态使用 left/right 字段
      if (compareMode.value === 'right') {
        // 以右侧为基准：优先显示右侧值
        value = node.right !== undefined && node.right !== null ? node.right : node.left
      } else {
        // 以左侧为基准：优先显示左侧值
        value = node.left !== undefined && node.left !== null ? node.left : node.right
      }
    }
    
    const formattedValue = formatValue(value)
    html += `<span class="${statusClass}">${formattedValue}</span>,\n`
  }
  
  return html
}

// 获取状态对应的CSS类
const getStatusClass = (status) => {
  switch (status) {
    case 'same':
      return 'diff-same'
    case 'different':
      return 'diff-different'
    case 'added':
      return 'diff-added'
    case 'removed':
      return 'diff-removed'
    default:
      return ''
  }
}

// 格式化值显示
const formatValue = (value) => {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return `"${value}"`
  if (typeof value === 'boolean') return value.toString()
  return String(value)
}

// 加载示例数据
const loadExample = () => {
  leftJson.value = JSON.stringify({
    name: "张三",
    age: 25,
    city: "北京",
    email: "zhangsan@example.com"
  }, null, 2)
  
  rightJson.value = JSON.stringify({
    city: "北京",
    name: "张三",
    age: 26,
    phone: "13800138000"
  }, null, 2)
  
  ElMessage.info('已加载示例数据，点击“开始对比”查看效果')
}

// 切换对比模式
const toggleCompareMode = async () => {
  compareMode.value = compareMode.value === 'left' ? 'right' : 'left'
  ElMessage.success(`已切换到以${compareMode.value === 'left' ? '左侧' : '右侧'}字段为基准`)
  
  // 重新渲染
  await nextTick()
}

// 同步滚动 - 左侧
const handleLeftScroll = (event) => {
  if (isSyncingScroll.value) return
  isSyncingScroll.value = true
  
  const scrollTop = event.target.scrollTop
  if (rightViewerRef.value) {
    rightViewerRef.value.scrollTop = scrollTop
  }
  
  setTimeout(() => {
    isSyncingScroll.value = false
  }, 10)
}

// 同步滚动 - 右侧
const handleRightScroll = (event) => {
  if (isSyncingScroll.value) return
  isSyncingScroll.value = true
  
  const scrollTop = event.target.scrollTop
  if (leftViewerRef.value) {
    leftViewerRef.value.scrollTop = scrollTop
  }
  
  setTimeout(() => {
    isSyncingScroll.value = false
  }, 10)
}
</script>

<style scoped>
.json-diff-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h2 {
  font-size: 28px;
  color: #303133;
  margin-bottom: 10px;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.input-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-upload {
  margin-top: 10px;
  text-align: right;
}

.action-bar {
  text-align: center;
  margin: 30px 0;
}

.stats-alert {
  margin-bottom: 20px;
}

.result-section {
  margin-top: 20px;
}

.diff-viewer {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  min-height: 400px;
  max-height: 600px;
  overflow: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.diff-viewer pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 差异高亮样式 */
:deep(.diff-same) {
  background-color: #e1f3d8;
  color: #67c23a;
  padding: 2px 4px;
  border-radius: 3px;
}

:deep(.diff-different) {
  background-color: #fde2e2;
  color: #f56c6c;
  padding: 2px 4px;
  border-radius: 3px;
}

:deep(.diff-added) {
  background-color: #e1f0ff;
  color: #409eff;
  padding: 2px 4px;
  border-radius: 3px;
}

:deep(.diff-removed) {
  background-color: #f4f4f5;
  color: #909399;
  padding: 2px 4px;
  border-radius: 3px;
  text-decoration: line-through;
}
</style>

