<template>
  <div class="watermark-selector">
    <div class="selector-header">
      <h3>框选水印区域</h3>
      <div class="mode-switch">
        <el-radio-group v-model="mode" size="small">
          <el-radio-button label="basic">基础模式</el-radio-button>
          <el-radio-button label="ai">AI智能模式</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 基础模式 -->
    <div v-if="mode === 'basic'" class="canvas-container">
      <div class="canvas-wrapper" ref="canvasWrapper">
        <canvas
          ref="canvas"
          @mousedown="startDrawing"
          @mousemove="draw"
          @mouseup="stopDrawing"
          @mouseleave="stopDrawing"
        ></canvas>
      </div>
      
      <!-- 已选择的区域列表 -->
      <div v-if="bboxes.length > 0" class="bbox-list">
        <h4>已选择的水印区域 ({{ bboxes.length }})</h4>
        <div v-for="(bbox, index) in bboxes" :key="index" class="bbox-item">
          <span>区域 {{ index + 1 }}: [{{ bbox.x }}, {{ bbox.y }}, {{ bbox.w }}, {{ bbox.h }}]</span>
          <el-button 
            type="danger" 
            size="small" 
            text
            @click="removeBbox(index)"
          >
            删除
          </el-button>
        </div>
      </div>

      <!-- AI模式提示 -->
      <el-alert
        v-if="mode === 'ai'"
        title="AI智能模式说明"
        type="info"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #default>
          <p>• AI模式使用深度学习模型，能更好地处理复杂背景（如花纹边框）</p>
          <p>• 需要确保IOPaint服务正在运行 (http://localhost:8080)</p>
          <p>• 处理时间较长，请耐心等待</p>
        </template>
      </el-alert>

      <!-- 参数设置 -->
      <div class="settings">
        <h4>处理参数</h4>
        <el-form :inline="true" size="small">
          <el-form-item label="修复算法">
            <el-select v-model="algorithm" style="width: 150px" :disabled="mode === 'ai'">
              <el-option label="Telea (快速)" value="telea" />
              <el-option label="Navier-Stokes (精细)" value="ns" />
            </el-select>
          </el-form-item>
          <el-form-item label="修复半径">
            <el-input-number 
              v-model="radius" 
              :min="1" 
              :max="10" 
              style="width: 100px"
              :disabled="mode === 'ai'"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- AI模式 -->
    <div v-else-if="mode === 'ai'" class="ai-mode">
      <div class="preview-image">
        <img :src="imageUrl" alt="原图" />
      </div>
      
      <el-alert
        title="AI智能模式"
        type="success"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      >
        <template #default>
          <p>• 使用LaMa深度学习模型，智能重建纹理</p>
          <p>• 适合处理复杂背景（花纹、渐变等）</p>
          <p>• 确保IOPaint服务运行: <code>iopaint start --model=lama --device=cpu --port=8080</code></p>
        </template>
      </el-alert>
      
      <div class="settings">
        <h4>处理参数</h4>
        <el-form :inline="true" size="small">
          <el-form-item label="修复算法">
            <el-select v-model="algorithm" style="width: 120px">
              <el-option label="Telea" value="telea" />
              <el-option label="Navier-Stokes" value="ns" />
            </el-select>
          </el-form-item>
          <el-form-item label="修复半径">
            <el-input-number 
              v-model="radius" 
              :min="1" 
              :max="10" 
              style="width: 100px"
            />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button @click="handleCancel">取消</el-button>
      <el-button 
        v-if="mode === 'basic'" 
        type="warning" 
        @click="clearAll"
        :disabled="bboxes.length === 0"
      >
        清除所有选择
      </el-button>
      <el-button 
        type="primary" 
        @click="handleProcess"
        :loading="processing"
        :disabled="mode === 'basic' && bboxes.length === 0"
      >
        {{ processing ? '处理中...' : '开始处理' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { removeWatermark, autoRemoveWatermark } from '../../api/watermark'

const props = defineProps({
  imageUrl: {
    type: String,
    required: true
  },
  filename: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['confirm-selection', 'cancel'])

// 状态
const mode = ref('basic')
const algorithm = ref('telea')
const radius = ref(3)
const processing = ref(false)
const bboxes = ref([])
const scaleRatio = ref(1) // 缩放比例：原始尺寸 / Canvas尺寸

// Canvas相关
const canvas = ref(null)
const canvasWrapper = ref(null)
const isDrawing = ref(false)
const startX = ref(0)
const startY = ref(0)
let ctx = null
let image = null

/**
 * 初始化Canvas
 */
onMounted(() => {
  initCanvas()
})

/**
 * 监听图片URL变化，重新加载
 */
watch(() => props.imageUrl, (newUrl) => {
  if (newUrl) {
    initCanvas()
  }
}, { immediate: true })

/**
 * 初始化Canvas
 */
const initCanvas = async () => {
  if (!props.imageUrl) return
  
  // 等待canvas元素渲染完成
  await nextTick()
  
  if (!canvas.value) return
  
  const canvasEl = canvas.value
  ctx = canvasEl.getContext('2d')
  
  // 加载图片
  image = new Image()
  image.crossOrigin = 'anonymous'
  image.onload = () => {
    // 设置canvas尺寸为图片尺寸（最大800px宽度）
    const maxWidth = 800
    let width = image.width
    let height = image.height
    
    // 计算缩放比例
    if (width > maxWidth) {
      scaleRatio.value = image.width / maxWidth
      height = (height * maxWidth) / width
      width = maxWidth
    } else {
      scaleRatio.value = 1
    }
    
    canvasEl.width = width
    canvasEl.height = height
    
    // 绘制图片
    ctx.drawImage(image, 0, 0, width, height)
    
    console.log('图片尺寸:', { original: `${image.width}x${image.height}`, canvas: `${width}x${height}`, scaleRatio: scaleRatio.value })
  }
  image.src = props.imageUrl
}

/**
 * 获取Canvas坐标（考虑CSS缩放）
 */
const getCanvasCoordinates = (e) => {
  const rect = canvas.value.getBoundingClientRect()
  const displayRatioX = canvas.value.width / rect.width
  const displayRatioY = canvas.value.height / rect.height
  
  return {
    x: (e.clientX - rect.left) * displayRatioX,
    y: (e.clientY - rect.top) * displayRatioY
  }
}

/**
 * 开始绘制
 */
const startDrawing = (e) => {
  if (mode.value !== 'basic') return
  
  isDrawing.value = true
  const coords = getCanvasCoordinates(e)
  startX.value = coords.x
  startY.value = coords.y
}

/**
 * 绘制中
 */
const draw = (e) => {
  if (!isDrawing.value || mode.value !== 'basic') return
  
  const coords = getCanvasCoordinates(e)
  const currentX = coords.x
  const currentY = coords.y
  
  // 重绘图片和已有框
  redrawCanvas()
  
  // 绘制当前框
  ctx.strokeStyle = '#409EFF'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.strokeRect(
    startX.value,
    startY.value,
    currentX - startX.value,
    currentY - startY.value
  )
}

/**
 * 停止绘制
 */
const stopDrawing = (e) => {
  if (!isDrawing.value || mode.value !== 'basic') return
  
  isDrawing.value = false
  
  const coords = getCanvasCoordinates(e)
  const endX = coords.x
  const endY = coords.y
  
  // 计算边界框
  const x = Math.min(startX.value, endX)
  const y = Math.min(startY.value, endY)
  const w = Math.abs(endX - startX.value)
  const h = Math.abs(endY - startY.value)
  
  // 忽略太小的框
  if (w < 10 || h < 10) {
    redrawCanvas()
    return
  }
  
  // 添加到列表
  bboxes.value.push({ x, y, w, h })
  
  // 重绘
  redrawCanvas()
  
  ElMessage.success(`已添加区域 ${bboxes.value.length}`)
}

/**
 * 重绘Canvas
 */
const redrawCanvas = () => {
  if (!ctx || !image) return
  
  // 清空并重绘图片
  ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
  ctx.drawImage(image, 0, 0, canvas.value.width, canvas.value.height)
  
  // 绘制所有框
  ctx.strokeStyle = '#F56C6C'
  ctx.lineWidth = 2
  ctx.setLineDash([])
  
  bboxes.value.forEach((bbox) => {
    ctx.strokeRect(bbox.x, bbox.y, bbox.w, bbox.h)
    
    // 填充半透明红色
    ctx.fillStyle = 'rgba(245, 108, 108, 0.2)'
    ctx.fillRect(bbox.x, bbox.y, bbox.w, bbox.h)
  })
}

/**
 * 删除边界框
 */
const removeBbox = (index) => {
  bboxes.value.splice(index, 1)
  redrawCanvas()
  ElMessage.info('已删除该区域')
}

/**
 * 清除所有选择
 */
const clearAll = () => {
  bboxes.value = []
  redrawCanvas()
  ElMessage.info('已清除所有选择')
}

/**
 * 处理水印
 */
const handleProcess = async () => {
  if (mode.value === 'basic' && bboxes.value.length === 0) {
    ElMessage.warning('请至少选择一个水印区域')
    return
  }
  
  processing.value = true
  
  try {
    let response
    
    if (mode.value === 'basic') {
      // 手动模式 - 将Canvas坐标转换为原始图片坐标
      const bboxData = bboxes.value.map(b => [
        Math.round(b.x * scaleRatio.value),
        Math.round(b.y * scaleRatio.value),
        Math.round(b.w * scaleRatio.value),
        Math.round(b.h * scaleRatio.value)
      ])
      
      console.log('发送的bbox（已缩放）:', bboxData, '缩放比例:', scaleRatio.value)
      
      response = await removeWatermark({
        filename: props.filename,
        bboxes: bboxData,
        algorithm: algorithm.value,
        radius: radius.value
      })
    } else {
      // 自动模式
      response = await autoRemoveWatermark({
        filename: props.filename,
        algorithm: algorithm.value,
        radius: radius.value
      })
    }
    
    if (response.data.success) {
      emit('confirm-selection', response.data)
    } else {
      throw new Error(response.data.error || '处理失败')
    }
  } catch (error) {
    console.error('处理错误:', error)
    ElMessage.error(error.message || '处理失败')
  } finally {
    processing.value = false
  }
}

/**
 * 取消
 */
const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.watermark-selector {
  width: 100%;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.selector-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.canvas-container {
  margin-bottom: 20px;
}

.canvas-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background-color: #f5f7fa;
}

canvas {
  cursor: crosshair;
  display: block;
  max-width: 100%;
}

.bbox-list {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.bbox-list h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
}

.bbox-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  margin-bottom: 5px;
  background-color: #fff;
  border-radius: 4px;
  font-size: 13px;
}

.settings {
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.settings h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #606266;
}

.auto-mode {
  text-align: center;
}

.preview-image {
  margin-bottom: 20px;
}

.preview-image img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tip {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
}
</style>
