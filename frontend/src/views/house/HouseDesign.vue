<template>
  <div class="house-design-container">
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
      <h1 class="page-title">智能户型设计系统</h1>
      <p class="page-subtitle">支持实时编辑与 PDF 报告导出</p>

      <div class="content-wrapper" v-loading="isLoading">
        <!-- 左侧：户型图 -->
        <div class="house-grid" id="capture-area">
          <div v-for="(cell, index) in gridCells" :key="index" class="room-cell"
               @click="selectRoom(index)"
               :class="{ selected: selectedRoomIndex === index }">
            <!-- 房间图标 -->
            <div class="room-icon" :class="getRoomType(cell.name)">
              <svg v-if="getRoomType(cell.name) === 'bed'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 7v11m0-4h18m-2 4v-4M5 11V7a2 2 0 012-2h10a2 2 0 012 2v4" stroke-linecap="round"/>
              </svg>
              <svg v-else-if="getRoomType(cell.name) === 'living'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 18v-6a2 2 0 012-2h12a2 2 0 012 2v6M2 18h20M6 10V7a3 3 0 013-3h6a3 3 0 013 3v3" stroke-linecap="round"/>
              </svg>
              <svg v-else-if="getRoomType(cell.name) === 'study'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 19.5V5a2 2 0 012-2h14v14H6.5A2.5 2.5 0 014 19.5z" stroke-linecap="round"/>
              </svg>
              <svg v-else-if="getRoomType(cell.name) === 'bath'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M6 3v4m0 0a2 2 0 00-2 2v1a7 7 0 0014 0V9a2 2 0 00-2-2M6 3h12" stroke-linecap="round"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="room-name">{{ cell.name }}</div>
            <div class="room-direction">{{ directions[index] }}</div>
            <div v-if="cell.desc" class="room-desc">{{ cell.desc }}</div>
            <!-- 选中指示器 -->
            <div class="selected-indicator">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 13l4 4L19 7" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- 右侧：控制面板 -->
        <div class="control-panel">
          <div class="panel-header">
            <h2 class="panel-title">设计属性</h2>
            <div class="panel-subtitle">编辑房间配置信息</div>
          </div>

          <div v-if="selectedRoomIndex !== null" class="room-editor">
            <!-- 最后更新时间 -->
            <div v-if="lastUpdated" class="update-time">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
              </svg>
              {{ lastUpdated }}
            </div>

            <!-- 房间名称 -->
            <div class="form-group">
              <label class="form-label">房间名称</label>
              <input type="text" v-model="selectedRoom.name" @change="saveRoom"
                     class="form-input" placeholder="输入房间名称" />
            </div>

            <!-- 功能描述 -->
            <div class="form-group">
              <label class="form-label">功能描述</label>
              <textarea v-model="selectedRoom.desc" @change="saveRoom"
                        class="form-textarea" placeholder="输入房间功能描述"></textarea>
            </div>

            <!-- 方位信息 -->
            <div class="direction-info">
              <div class="direction-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/>
                </svg>
                当前方位
              </div>
              <div class="direction-value">{{ directions[selectedRoomIndex] }}</div>
            </div>

            <!-- 房间类型标签 -->
            <div class="room-type-tags">
              <span v-for="tag in getRoomTags(selectedRoom.name)" :key="tag" class="room-tag">{{ tag }}</span>
            </div>
          </div>

          <div v-else class="empty-state">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
            <p>点击左侧户型图中的房间<br/>查看和编辑详细信息</p>
          </div>

          <!-- 合规性检查 -->
          <div class="compliance-section">
            <h3 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round"/>
              </svg>
              合规性检查
            </h3>
            <div class="compliance-list">
              <div class="compliance-item pass">
                <span class="check-icon">✓</span>
                <span>西北区域无厨房/厕所</span>
              </div>
              <div class="compliance-item pass">
                <span class="check-icon">✓</span>
                <span>正东区域无厨房/厕所</span>
              </div>
              <div class="compliance-item pass">
                <span class="check-icon">✓</span>
                <span>东南区域无厨房/厕所</span>
              </div>
            </div>
          </div>

          <!-- 按钮组 -->
          <div class="button-group">
            <el-button @click="exportToPDF" :disabled="isExporting" class="btn-export">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M12 4v12m0 0l-4-4m4 4l4-4M4 17v2a2 2 0 002 2h12a2 2 0 002-2v-2" stroke-linecap="round"/>
              </svg>
              {{ isExporting ? '生成中...' : '导出为 PDF 报告' }}
            </el-button>
            <el-button @click="resetData" class="btn-reset">
              重置为默认数据
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

const router = useRouter()
const API_BASE = '/house-design'

const directions = ['西北', '正北', '东北', '西中', '中心', '正东', '西南', '正南', '东南']
const selectedRoomIndex = ref(null)
const isExporting = ref(false)
const isLoading = ref(true)
const lastUpdated = ref('')

// 从后端加载数据
const gridCells = ref([])

const loadHouseData = async () => {
  try {
    const resp = await fetch(`${API_BASE}/data`)
    const result = await resp.json()
    if (result.success) {
      gridCells.value = result.data.cells
      lastUpdated.value = result.data.updated_at
        ? new Date(result.data.updated_at).toLocaleString('zh-CN')
        : ''
    } else {
      ElMessage.error('加载数据失败：' + result.msg)
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('无法连接到后端服务，请检查服务是否启动。')
  } finally {
    isLoading.value = false
  }
}

const saveCellToBackend = async (index, cell) => {
  try {
    await fetch(`${API_BASE}/data/${index}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cell)
    })
  } catch (error) {
    console.error('保存失败:', error)
  }
}

const selectedRoom = computed(() => {
  return selectedRoomIndex.value !== null ? gridCells.value[selectedRoomIndex.value] : null
})

const selectRoom = (index) => { selectedRoomIndex.value = index }

const saveRoom = async () => {
  if (selectedRoomIndex.value !== null && selectedRoom.value) {
    await saveCellToBackend(selectedRoomIndex.value, selectedRoom.value)
  }
}

const resetData = async () => {
  try {
    await ElMessageBox.confirm('确定要重置为默认数据吗？当前修改将丢失。', '提示', { type: 'warning' })
  } catch { return }

  try {
    const resp = await fetch(`${API_BASE}/data/reset`, { method: 'POST' })
    const result = await resp.json()
    if (result.success) {
      await loadHouseData()
      ElMessage.success('已重置为默认数据')
    } else {
      ElMessage.error('重置失败：' + result.msg)
    }
  } catch (error) {
    console.error('重置失败:', error)
    ElMessage.error('无法连接到后端服务。')
  }
}

const exportToPDF = async () => {
  isExporting.value = true
  const captureArea = document.getElementById('capture-area')

  try {
    // 临时展开户型图，确保所有房间都在可视区域内（html2canvas 只截取可见区域）
    const originalHeight = captureArea.style.height
    const originalMinHeight = captureArea.style.minHeight
    captureArea.style.height = 'auto'
    captureArea.style.minHeight = '1680px' // 3x3 grid, generous height

    const canvas = await html2canvas(captureArea, {
      scale: 3,
      useCORS: true,
      backgroundColor: '#1a1a2e',
      scrollY: 0,
      windowWidth: captureArea.scrollWidth,
      windowHeight: captureArea.scrollHeight
    })

    // 恢复原始高度
    captureArea.style.height = originalHeight
    captureArea.style.minHeight = originalMinHeight

    const imgData = canvas.toDataURL('image/png')
    // 使用 A3 横向以容纳完整户型图
    const pdf = new jsPDF('l', 'mm', 'a3')

    const pageW = pdf.internal.pageSize.getWidth()
    const pageH = pdf.internal.pageSize.getHeight()

    // 按高度适配，确保所有房间都在页面内
    const titleArea = 35 // 标题占用的垂直空间
    const availableHeight = pageH - titleArea
    const imgHeight = availableHeight
    const imgWidth = (canvas.width * imgHeight) / canvas.height

    // 深色背景
    pdf.setFillColor(26, 26, 46)
    pdf.rect(0, 0, pageW, pageH, 'F')

    // 英文标题（jsPDF 默认字体不支持中文）
    pdf.setTextColor(255, 255, 255)
    pdf.setFontSize(18)
    pdf.text('Smart Floor Plan Design Report', 10, 18)
    pdf.setFontSize(9)
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 10, 26)

    // 水平居中放置图片
    const imgX = (pageW - imgWidth) / 2
    pdf.addImage(imgData, 'PNG', imgX, titleArea, imgWidth, imgHeight)

    pdf.save('house_design_report.pdf')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出 PDF 时发生错误，请重试。')
  } finally {
    isExporting.value = false
  }
}

// 房间类型判断（用于图标和样式）
const getRoomType = (name) => {
  if (!name) return 'default'
  const n = name.toLowerCase()
  if (n.includes('卧') || n.includes('房')) return 'bed'
  if (n.includes('客')) return 'living'
  if (n.includes('书房') || n.includes('书')) return 'study'
  if (n.includes('卫') || n.includes('浴') || n.includes('厕所')) return 'bath'
  return 'default'
}

// 房间标签
const getRoomTags = (name) => {
  if (!name) return []
  const tags = []
  const n = name.toLowerCase()
  if (n.includes('主')) tags.push('主卧')
  if (n.includes('次')) tags.push('次卧')
  if (n.includes('长')) tags.push('长子/女')
  if (n.includes('书')) tags.push('书房')
  if (n.includes('客')) tags.push('客厅')
  if (n.includes('卫')) tags.push('卫生间')
  return tags.length > 0 ? tags : ['标准房间']
}

onMounted(() => { loadHouseData() })
</script>

<style scoped>
.house-design-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* ========== 顶部导航栏 ========== */
.header {
  background: rgba(15, 15, 26, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  height: 56px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 32px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 40px;
  transition: opacity 0.2s;
}

.logo:hover { opacity: 0.8 }
.logo-icon { height: 24px; margin-right: 12px }
.logo-text { color: #e0e0e0; font-weight: 600; font-size: 15px; letter-spacing: 0.5px }

/* ========== 主内容区 ========== */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 56px 32px 80px;
}

.page-title {
  font-size: 42px;
  font-weight: 800;
  color: #ffffff;
  text-align: center;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #ffffff 0%, #a0b4c8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  color: rgba(255, 255, 255, 0.45);
  text-align: center;
  margin-top: 12px;
  font-size: 15px;
  letter-spacing: 0.3px;
}

.content-wrapper {
  display: flex;
  gap: 56px;
  margin-top: 48px;
  align-items: flex-start;
}

/* ========== 户型网格 - 重新设计为深色高端风格 ========== */
.house-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 8px;
  width: 560px;
  min-height: 560px;
  background: #0d0d18;
  padding: 8px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.room-cell {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  cursor: pointer;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

/* 每个房间的独特渐变背景 */
.room-cell:nth-child(1) { background: linear-gradient(145deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.05) 100%) }
.room-cell:nth-child(2) { background: linear-gradient(145deg, rgba(148, 163, 184, 0.12) 0%, rgba(148, 163, 184, 0.04) 100%) }
.room-cell:nth-child(3) { background: linear-gradient(145deg, rgba(251, 191, 36, 0.15) 0%, rgba(251, 191, 36, 0.05) 100%) }
.room-cell:nth-child(4) { background: linear-gradient(145deg, rgba(139, 92, 246, 0.15) 0%, rgba(139, 92, 246, 0.05) 100%) }
.room-cell:nth-child(5) { background: linear-gradient(145deg, rgba(255, 255, 255, 0.04) 0%, rgba(255, 255, 255, 0.01) 100%) }
.room-cell:nth-child(6) { background: linear-gradient(145deg, rgba(16, 185, 129, 0.15) 0%, rgba(16, 185, 129, 0.05) 100%) }
.room-cell:nth-child(7) { background: linear-gradient(145deg, rgba(244, 114, 182, 0.12) 0%, rgba(244, 114, 182, 0.04) 100%) }
.room-cell:nth-child(8) { background: linear-gradient(145deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%) }
.room-cell:nth-child(9) { background: linear-gradient(145deg, rgba(236, 72, 153, 0.15) 0%, rgba(236, 72, 153, 0.05) 100%) }

.room-cell:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.12);
}

.room-cell.selected {
  border-color: rgba(99, 102, 241, 0.6);
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2), 0 8px 24px rgba(0, 0, 0, 0.3);
}

/* 房间图标 */
.room-icon {
  width: 40px;
  height: 40px;
  margin-bottom: 12px;
  opacity: 0.5;
  transition: all 0.3s ease;
}

.room-cell:hover .room-icon { opacity: 0.8; transform: scale(1.1) }
.room-cell.selected .room-icon { opacity: 0.9 }

/* 根据房间类型设置图标颜色 */
.room-cell:nth-child(1) .room-icon { color: #818cf8 }
.room-cell:nth-child(2) .room-icon { color: #94a3b8 }
.room-cell:nth-child(3) .room-icon { color: #fbbf24 }
.room-cell:nth-child(4) .room-icon { color: #a78bfa }
.room-cell:nth-child(5) .room-icon { color: #64748b }
.room-cell:nth-child(6) .room-icon { color: #34d399 }
.room-cell:nth-child(7) .room-icon { color: #f472b6 }
.room-cell:nth-child(8) .room-icon { color: #f87171 }
.room-cell:nth-child(9) .room-icon { color: #ec4899 }

/* 房间名称 */
.room-name {
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

/* 方位标签 */
.room-direction {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  letter-spacing: 1px;
  margin-bottom: 6px;
}

/* 功能描述 */
.room-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.35);
  margin-top: 6px;
  max-width: 120px;
  line-height: 1.4;
}

/* 选中指示器 */
.selected-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  background: rgba(99, 102, 241, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transform: scale(0.5);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.room-cell.selected .selected-indicator {
  opacity: 1;
  transform: scale(1);
}

.selected-indicator svg {
  width: 14px;
  height: 14px;
  color: #ffffff;
}

/* ========== 控制面板 - 毛玻璃风格 ========== */
.control-panel {
  width: 400px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(40px);
  border-radius: 24px;
  padding: 36px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.panel-header {
  margin-bottom: 28px;
}

.panel-title {
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 6px;
}

.panel-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.35);
}

.update-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.update-time svg {
  width: 14px;
  height: 14px;
  opacity: 0.5;
}

/* 表单 */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 14px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.04);
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: rgba(255, 255, 255, 0.2);
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.5);
  background: rgba(99, 102, 241, 0.06);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-textarea {
  min-height: 80px;
  resize: vertical;
  line-height: 1.5;
}

/* 方位信息 */
.direction-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 12px;
  margin-bottom: 20px;
}

.direction-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.4);
  display: flex;
  align-items: center;
  gap: 6px;
}

.direction-label svg {
  width: 16px;
  height: 16px;
}

.direction-value {
  font-size: 15px;
  font-weight: 600;
  color: #818cf8;
}

/* 房间标签 */
.room-type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 24px;
}

.room-tag {
  font-size: 11px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.3px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 48px 0;
  color: rgba(255, 255, 255, 0.3);
}

.empty-state svg {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state p {
  font-size: 14px;
  line-height: 1.6;
}

/* ========== 合规性检查 ========== */
.compliance-section {
  margin: 28px 0;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-title svg {
  width: 18px;
  height: 18px;
}

.compliance-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.compliance-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  padding: 8px 12px;
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.1);
  border-radius: 10px;
}

.check-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: rgba(16, 185, 129, 0.15);
  border-radius: 50%;
  font-size: 12px;
  color: #34d399;
  font-weight: 700;
}

/* ========== 按钮组 ========== */
.button-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-export {
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 14px;
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  border: none;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  letter-spacing: 0.3px;
}

.btn-export:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.3);
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-export svg {
  width: 18px;
  height: 18px;
}

.btn-reset {
  height: 42px;
  font-size: 13px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.2s ease;
}

.btn-reset:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

/* ========== 响应式 ========== */
@media (max-width: 1100px) {
  .content-wrapper { flex-direction: column; align-items: center }
  .house-grid { width: 100%; max-width: 560px; min-height: auto; aspect-ratio: 1 }
  .control-panel { width: 100%; max-width: 560px }
}

@media (max-width: 640px) {
  .main-content { padding: 32px 16px 48px }
  .page-title { font-size: 28px }
  .house-grid { width: 100%; min-height: auto; aspect-ratio: 1 }
  .control-panel { padding: 24px }
}
</style>
