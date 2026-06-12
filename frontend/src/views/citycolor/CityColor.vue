<template>
  <div class="city-color-container">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <img src="/nokia-06.png" alt="NOKIA" class="logo-icon" />
          <span class="logo-text">OPM 系统</span>
        </div>
        <el-button size="small" @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </el-button>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <div class="main-content">
      <h1 class="page-title">CityColor 颜色提取器</h1>
      <p class="page-subtitle">输入内容，智能提取专属配色方案</p>

      <div class="content-wrapper" v-loading="isLoading">
        <!-- 左侧：输入与色板 -->
        <div class="left-panel">
          <!-- 输入区域 -->
          <el-card class="input-section" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><EditPen /></el-icon>
                <span>内容输入</span>
              </div>
            </template>

            <!-- 模式选择 -->
            <el-form :model="inputForm" label-position="top">
              <el-form-item label="提取模式">
                <el-radio-group v-model="inputForm.mode">
                  <el-radio-button value="auto">智能识别</el-radio-button>
                  <el-radio-button value="city">城市色彩</el-radio-button>
                  <el-radio-button value="brand">品牌色系</el-radio-button>
                  <el-radio-button value="random">随机配色</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="输入内容">
                <el-input
                  v-model="inputForm.content"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入城市名称、品牌描述或关键词..."
                />
                <div class="input-hint">
                  提示：支持输入城市名（如"巴黎""东京"）、品牌关键词、自然元素等
                </div>
              </el-form-item>

              <el-form-item label="颜色数量">
                <div class="count-slider">
                  <el-slider v-model="inputForm.count" :min="3" :max="12" :step="1" />
                  <span class="count-display">{{ inputForm.count }} 色</span>
                </div>
              </el-form-item>

              <el-button
                type="primary"
                @click="extractColors"
                :loading="isExtracting"
                class="extract-btn"
              >
                <el-icon><Search /></el-icon>
                提取颜色
              </el-button>
            </el-form>
          </el-card>

          <!-- 色板展示区 -->
          <el-card class="palette-section" shadow="hover" v-if="resultColors.length > 0">
            <template #header>
              <div class="card-header">
                <span>提取结果</span>
                <el-tag :type="getPaletteTypeTag(resultPaletteType)">
                  {{ getPaletteTypeName(resultPaletteType) }}
                </el-tag>
              </div>
            </template>

            <!-- 渐变预览 -->
            <div class="gradient-preview" :style="{ background: resultGradient }">
              <span class="gradient-label">渐变预览</span>
            </div>

            <!-- 色板 -->
            <div class="color-swatches">
              <div
                v-for="(color, index) in resultColors"
                :key="index"
                class="swatch-item"
                @click="selectResultColor(index)"
                :class="{ selected: selectedResultIndex === index }"
              >
                <div class="swatch-color" :style="{ backgroundColor: color.hex }"></div>
                <div class="swatch-info">
                  <div class="swatch-name">{{ color.name }}</div>
                  <div class="swatch-hex">{{ color.hex }}</div>
                  <div class="swatch-rgb">RGB({{ color.rgb?.r || 0 }}, {{ color.rgb?.g || 0 }}, {{ color.rgb?.b || 0 }})</div>
                  <div class="swatch-ratio" v-if="color.ratio">占比: {{ (color.ratio * 100).toFixed(0) }}%</div>
                </div>
                <el-button
                  size="small"
                  circle
                  @click.stop="copyColor(color.hex)"
                  title="复制色值"
                >
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button type="success" @click="saveScheme">
                <el-icon><Check /></el-icon> 保存方案
              </el-button>
              <el-button type="warning" @click="exportPNG">
                <el-icon><Download /></el-icon> 导出PNG
              </el-button>
              <el-button @click="resetInput">
                <el-icon><RefreshLeft /></el-icon> 重新提取
              </el-button>
            </div>
          </el-card>

          <!-- 空状态 -->
          <el-empty
            v-else
            description="输入内容后点击'提取颜色'"
            :image-size="150"
          >
            <el-button type="primary" @click="focusInput">开始提取</el-button>
          </el-empty>
        </div>

        <!-- 右侧：已保存方案列表 -->
        <div class="right-panel">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Collection /></el-icon>
                <span>已保存方案</span>
                <el-badge :value="totalSchemes" />
              </div>
            </template>

            <el-empty v-if="schemes.length === 0" description="暂无保存的方案">
              <el-button type="primary" size="small" @click="loadSchemes">刷新</el-button>
            </el-empty>

            <div v-else class="scheme-list">
              <div
                v-for="scheme in schemes"
                :key="scheme.id"
                class="scheme-item"
                @click="loadScheme(scheme.id)"
              >
                <!-- 迷你色板 -->
                <div class="mini-palette">
                  <div
                    v-for="(hex, idx) in getSchemeHexes(scheme)"
                    :key="idx"
                    class="mini-swatch"
                    :style="{ backgroundColor: hex }"
                  ></div>
                </div>
                <div class="scheme-info">
                  <div class="scheme-title">{{ scheme.title }}</div>
                  <div class="scheme-meta">
                    <el-tag size="small" type="info">{{ scheme.palette_type || 'custom' }}</el-tag>
                    <span class="scheme-date">{{ formatDate(scheme.created_at) }}</span>
                  </div>
                </div>
                <el-button
                  size="small"
                  type="danger"
                  circle
                  @click.stop="deleteScheme(scheme.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>

              <!-- 分页 -->
              <el-pagination
                v-if="totalSchemes > pageSize"
                background
                layout="prev, pager, next"
                :total="totalSchemes"
                :page-size="pageSize"
                v-model:current-page="currentPage"
                @current-change="loadSchemes"
              />
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 颜色详情弹窗 -->
    <el-dialog v-model="detailVisible" title="颜色详情" width="400px">
      <div v-if="selectedResultColor" class="color-detail">
        <div class="detail-swatch" :style="{ backgroundColor: selectedResultColor.hex }"></div>
        <div class="detail-info">
          <h3>{{ selectedResultColor.name }}</h3>
          <p>HEX: {{ selectedResultColor.hex }}</p>
          <p v-if="selectedResultColor.rgb">
            RGB: {{ selectedResultColor.rgb.r }}, {{ selectedResultColor.rgb.g }}, {{ selectedResultColor.rgb.b }}
          </p>
          <el-button type="primary" @click="copyColor(selectedResultColor.hex)">
            复制 HEX 值
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 保存方案弹窗 -->
    <el-dialog v-model="saveVisible" title="保存颜色方案" width="400px">
      <el-form :model="saveForm" label-width="80px">
        <el-form-item label="方案名称">
          <el-input v-model="saveForm.title" placeholder="输入方案名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSaveScheme">确认保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  EditPen, Search, CopyDocument, Check,
  Download, RefreshLeft, Collection, Delete, ArrowLeft
} from '@element-plus/icons-vue'

// ==================== 状态 ====================
const isLoading = ref(false)
const isExtracting = ref(false)

const inputForm = reactive({
  content: '',
  mode: 'auto',
  count: 5
})

const resultColors = ref([])
const resultGradient = ref('')
const resultPaletteType = ref('')
const selectedResultIndex = ref(null)

const schemes = ref([])
const totalSchemes = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const detailVisible = ref(false)
const saveVisible = ref(false)
const saveForm = reactive({ title: '' })

// ==================== 核心功能 ====================

/** 提取颜色 */
async function extractColors() {
  if (!inputForm.content.trim()) {
    ElMessage.warning('请输入内容')
    return
  }

  isExtracting.value = true
  try {
    const res = await fetch('/api/city-color/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: inputForm.content,
        mode: inputForm.mode,
        count: inputForm.count
      })
    })

    const data = await res.json()
    if (data.success) {
      resultColors.value = data.data.colors
      resultGradient.value = data.data.gradient || ''
      resultPaletteType.value = data.data.palette_type || 'custom'
      selectedResultIndex.value = null
      ElMessage.success('颜色提取成功')
    } else {
      ElMessage.error(data.msg || '提取失败')
    }
  } catch (e) {
    ElMessage.error('网络错误: ' + e.message)
  } finally {
    isExtracting.value = false
  }
}

/** 保存方案 */
async function saveScheme() {
  if (resultColors.value.length === 0) {
    ElMessage.warning('请先提取颜色')
    return
  }

  saveForm.title = `${inputForm.mode}_${new Date().toLocaleDateString('zh-CN')}`
  saveVisible.value = true
}

async function confirmSaveScheme() {
  try {
    const res = await fetch('/api/city-color/schemes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: saveForm.title,
        colors: resultColors.value,
        gradient: resultGradient.value,
        palette_type: resultPaletteType.value,
        source_text: inputForm.content,
        extract_mode: inputForm.mode
      })
    })

    const data = await res.json()
    if (data.success) {
      ElMessage.success('方案保存成功')
      saveVisible.value = false
      loadSchemes() // 刷新列表
    } else {
      ElMessage.error(data.msg || '保存失败')
    }
  } catch (e) {
    ElMessage.error('网络错误: ' + e.message)
  }
}

/** 加载已保存方案 */
async function loadSchemes() {
  isLoading.value = true
  try {
    const res = await fetch(
      `/api/city-color/schemes?page=${currentPage}&page_size=${pageSize}`
    )
    const data = await res.json()
    if (data.success) {
      schemes.value = data.data.schemes
      totalSchemes.value = data.data.total
    }
  } catch (e) {
    ElMessage.error('加载失败')
  } finally {
    isLoading.value = false
  }
}

/** 加载单个方案 */
async function loadScheme(schemeId) {
  try {
    const res = await fetch(`/api/city-color/schemes/${schemeId}`)
    const data = await res.json()
    if (data.success) {
      resultColors.value = data.data.colors || []
      resultGradient.value = data.data.gradient || ''
      resultPaletteType.value = data.data.palette_type || 'custom'
      inputForm.content = data.data.source_text || ''
      inputForm.mode = data.data.extract_mode || 'auto'
      ElMessage.success('方案加载成功')
    } else if (data.msg && data.msg !== '方案不存在') {
      ElMessage.error(data.msg || '加载失败')
    }
  } catch (e) {
    ElMessage.error('加载失败')
  }
}

/** 删除方案 */
async function deleteScheme(schemeId) {
  try {
    const res = await fetch(`/api/city-color/schemes/${schemeId}`, { method: 'DELETE' })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('删除成功')
      loadSchemes()
    } else {
      ElMessage.error(data.msg || '删除失败')
    }
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

/** 复制颜色 */
function copyColor(hex) {
  navigator.clipboard.writeText(hex).then(() => {
    ElMessage.success(`已复制 ${hex}`)
  }).catch(() => {
    // fallback: 使用传统方式复制
    const textarea = document.createElement('textarea')
    textarea.value = hex
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    ElMessage.success(`已复制 ${hex}`)
  })
}

/** 导出PNG */
async function exportPNG() {
  if (resultColors.value.length === 0) return

  try {
    const res = await fetch('/api/city-color/export/png', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        colors: resultColors.value,
        title: saveForm.title || 'CityColor Palette'
      })
    })

    if (!res.ok) {
      const errData = await res.json()
      ElMessage.error(errData.msg || '导出失败')
      return
    }

    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${saveForm.title || 'palette'}.png`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败: ' + e.message)
  }
}

// ==================== 工具函数 ====================
function selectResultColor(index) {
  selectedResultIndex.value = index
  detailVisible.value = true
}

function getSchemeHexes(scheme) {
  if (!scheme.colors) return []
  // colors 可能是 JSON 字符串或数组
  const colors = typeof scheme.colors === 'string' ? JSON.parse(scheme.colors) : scheme.colors
  return colors.map(c => typeof c === 'string' ? c : (c.hex || '#000000'))
}

function getPaletteTypeTag(type) {
  const map = {
    'auto': '', 'city': 'success', 'brand': 'warning',
    'random': 'info', 'complementary': '', 'analogous': ''
  }
  return map[type] || ''
}

function getPaletteTypeName(type) {
  const map = {
    'auto': '智能识别', 'city': '城市色彩', 'brand': '品牌色系',
    'random': '随机配色', 'complementary': '互补色', 'analogous': '类似色'
  }
  return map[type] || type
}

function formatDate(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleDateString('zh-CN')
}

function focusInput() {
  // 聚焦到输入框（可通过 ref 实现）
}

function resetInput() {
  inputForm.content = ''
  resultColors.value = []
  resultGradient.value = ''
  resultPaletteType.value = ''
  selectedResultIndex.value = null
}

// 计算属性：选中的颜色详情
const selectedResultColor = computed(() => resultColors.value[selectedResultIndex.value] || null)

// ==================== 生命周期 ====================
onMounted(() => {
  loadSchemes()
})
</script>

<style scoped>
.city-color-container {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-icon {
  height: 36px;
  margin-right: 12px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 28px;
  color: #303133;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #909399;
  margin-bottom: 24px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
}

/* 左侧面板 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
}

.input-hint {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
}

.count-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.count-display {
  color: #409EFF;
  font-weight: bold;
  white-space: nowrap;
}

.extract-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
}

/* 色板区域 */
.gradient-preview {
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  color: #fff;
  font-weight: bold;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.color-swatches {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.swatch-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.swatch-item:hover {
  border-color: #409EFF;
  background: #f5f7fa;
}

.swatch-item.selected {
  border-color: #409EFF;
  background: #ecf5ff;
}

.swatch-color {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.swatch-info {
  flex: 1;
}

.swatch-name {
  font-weight: bold;
  color: #303133;
}

.swatch-hex {
  font-family: monospace;
  color: #409EFF;
  font-size: 13px;
}

.swatch-rgb {
  color: #909399;
  font-size: 12px;
}

.swatch-ratio {
  color: #67C23A;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

/* 右侧面板 */
.right-panel {
  display: flex;
  flex-direction: column;
}

.scheme-list {
  max-height: calc(100vh - 320px);
  overflow-y: auto;
}

.scheme-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.scheme-item:hover {
  background: #f5f7fa;
}

.mini-palette {
  display: flex;
  border-radius: 4px;
  overflow: hidden;
  height: 32px;
}

.mini-swatch {
  flex: 1;
}

.scheme-info {
  flex: 1;
}

.scheme-title {
  font-weight: bold;
  color: #303133;
  font-size: 14px;
}

.scheme-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.scheme-date {
  color: #909399;
  font-size: 12px;
}

/* 颜色详情 */
.color-detail {
  display: flex;
  gap: 20px;
}

.detail-swatch {
  width: 120px;
  height: 120px;
  border-radius: 8px;
  flex-shrink: 0;
}

.detail-info h3 {
  margin: 0 0 12px;
}

.detail-info p {
  margin: 6px 0;
  color: #606266;
}

/* 响应式 */
@media (max-width: 900px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .right-panel {
    max-height: 400px;
  }
}
</style>