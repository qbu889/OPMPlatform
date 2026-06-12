
<template>
  <div class="wheel-lottery-container">
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
      <h1 class="page-title">🎰 彩色抽奖转盘</h1>
      <p class="page-subtitle">配置分区，点击抽奖，体验随机乐趣</p>

      <div class="content-wrapper" v-loading="isLoading">
        <!-- 左侧面板：配置表单 -->
        <div class="left-panel">
          <el-card class="config-section" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>分区配置</span>
                <el-button size="small" type="primary" @click="addItem">
                  <el-icon><Plus /></el-icon> 添加分区
                </el-button>
              </div>
            </template>

            <div class="items-list">
              <div v-for="(item, index) in wheelItems" :key="item.id" class="item-row">
                <el-input-number v-model="item.id" :min="1" :max="999" size="small" style="width: 70px" />
                <el-color-picker v-model="item.color" size="small" style="width: 50px; margin: 0 8px;" />
                <el-input v-model="item.name" placeholder="分区名称" size="small" style="flex: 1; margin-right: 8px;" />
                <el-input-number v-model="item.weight" :min="1" :max="100" size="small" style="width: 70px; margin-right: 8px;" />
                <el-button type="danger" size="small" circle @click="removeItem(index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>

            <div class="action-buttons">
              <el-button type="primary" @click="saveConfig" :disabled="wheelItems.length < 2">
                保存配置
              </el-button>
              <el-button @click="resetConfig">重置为默认</el-button>
            </div>
          </el-card>

          <!-- 抽奖按钮 -->
          <el-button
            type="primary"
            size="large"
            class="draw-button"
            :disabled="isDrawing || wheelItems.length < 2"
            @click="handleDraw"
          >
            {{ isDrawing ? '抽奖中...' : '🎲 开始抽奖' }}
          </el-button>

          <!-- 结果展示 -->
          <el-card v-if="lastResult" class="result-section" shadow="hover">
            <template #header>
              <span>🎉 抽奖结果</span>
            </template>
            <div class="result-display">
              <div class="result-color" :style="{ backgroundColor: lastResult.color }"></div>
              <div class="result-info">
                <h3>{{ lastResult.name }}</h3>
                <p>权重: {{ lastResult.weight }}</p>
              </div>
            </div>
          </el-card>

          <!-- 空状态 -->
          <el-empty v-if="wheelItems.length === 0" description="暂无分区，请添加后保存" />
        </div>

        <!-- 右侧面板：转盘 -->
        <div class="right-panel">
          <el-card shadow="hover" class="wheel-card">
            <div class="wheel-container" ref="wheelContainerRef">
              <!-- 转盘主体 -->
              <div class="wheel" ref="wheelRef" :style="wheelStyle">
                <!-- 扇形分区 -->
                <div v-for="(item, index) in wheelItems" :key="item.id" class="segment">
                  <div class="segment-label" :style="getSegmentLabelStyle(index)">
                    {{ item.name }}
                  </div>
                </div>
              </div>

              <!-- 中心指针 -->
              <div class="pointer">▼</div>

              <!-- 中心圆 -->
              <div class="center-circle"></div>
            </div>

            <!-- 分区统计 -->
            <div class="stats-bar" v-if="wheelItems.length > 0">
              <span>分区数: {{ wheelItems.length }}</span>
              <span>总权重: {{ totalWeight }}</span>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 结果弹窗 -->
    <el-dialog v-model="resultDialogVisible" title="抽奖结果" width="400px" center>
      <div class="dialog-result">
        <div class="result-icon" :style="{ backgroundColor: lastResult?.color }"></div>
        <h2>{{ lastResult?.name }}</h2>
      </div>
      <template #footer>
        <el-button type="primary" @click="resultDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Plus,
  Delete,
  Picture,
} from '@element-plus/icons-vue'
import { getWheelConfig, saveWheelConfig, drawWheel, resetWheel } from '@/api/wheel_lottery'

const router = useRouter()

// 状态变量
const wheelItems = ref([])
const isDrawing = ref(false)
const isLoading = ref(true)
const lastResult = ref(null)
const resultDialogVisible = ref(false)

// 转盘 DOM 引用
const wheelRef = ref(null)
const wheelContainerRef = ref(null)

// 转盘样式（CSS transform）
const wheelStyle = reactive({
  transition: 'none',
  transform: 'rotate(0deg)',
})

// 总权重（计算属性）
const totalWeight = computed(() => {
  return wheelItems.value.reduce((sum, item) => sum + (item.weight || 1), 0)
})

// 初始化加载配置
const loadConfig = async () => {
  isLoading.value = true
  try {
    const res = await getWheelConfig()
    if (res.code === 200 && res.data?.items) {
      wheelItems.value = [...res.data.items]
    } else {
      wheelItems.value = getDefaultItems()
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
    wheelItems.value = getDefaultItems()
  } finally {
    isLoading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  if (wheelItems.value.length < 2) {
    ElMessage.warning('至少需要 2 个分区')
    return
  }

  try {
    const res = await saveWheelConfig(wheelItems.value)
    if (res.code === 200) {
      ElMessage.success('配置保存成功')
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存配置失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 重置配置
const resetConfig = async () => {
  try {
    await ElMessageBox.confirm('确定要重置为默认配置吗？当前所有自定义分区将被清除。', '提示', {
      type: 'warning',
    })

    const res = await resetWheel()
    if (res.code === 200) {
      wheelItems.value = [...res.data.items]
      lastResult.value = null
      ElMessage.success('配置已重置')
    } else {
      ElMessage.error(res.msg || '重置失败')
    }
  } catch (error) {
    // 用户取消操作
  }
}

// 添加分区
const addItem = () => {
  const colors = ['#FF4444', '#44BB44', '#4488FF', '#FFAA00', '#CC44FF', '#44CCCC', '#FF8844', '#8844AA']
  const nextId = wheelItems.value.length > 0 ? Math.max(...wheelItems.value.map(i => i.id)) + 1 : 1
  wheelItems.value.push({
    id: nextId,
    name: `分区${nextId}`,
    color: colors[(wheelItems.value.length) % colors.length],
    weight: 1,
  })
}

// 删除分区
const removeItem = (index) => {
  wheelItems.value.splice(index, 1)
}

// 获取默认分区
const getDefaultItems = () => [
  { id: 1, name: '一等奖', color: '#FF4444', weight: 1 },
  { id: 2, name: '二等奖', color: '#44BB44', weight: 1 },
  { id: 3, name: '三等奖', color: '#4488FF', weight: 1 },
  { id: 4, name: '谢谢参与', color: '#AAAAAA', weight: 2 },
]

// 计算单个扇形角度
const getSegmentAngle = () => {
  const n = wheelItems.value.length
  return n > 0 ? 360 / n : 0
}

// 计算标签位置（每个扇形中心）
const getSegmentLabelStyle = (index) => {
  const n = wheelItems.value.length
  if (n === 0) return {}

  const segmentAngle = 360 / n
  // 标签角度：从顶部开始，每个扇形中心的角度
  const angle = (index * segmentAngle + segmentAngle / 2 - 90) * (Math.PI / 180)
  // 标签距离中心的半径（转盘半径的 65%）
  const radius = 35

  return {
    position: 'absolute',
    left: `calc(50% + ${Math.cos(angle) * radius}%)`,
    top: `calc(50% + ${Math.sin(angle) * radius}%)`,
    transform: 'translate(-50%, -50%)',
    color: '#fff',
    fontWeight: 'bold',
    fontSize: '13px',
    textShadow: '0 1px 2px rgba(0,0,0,0.5)',
    whiteSpace: 'nowrap',
    zIndex: 10,
    textAlign: 'center',
  }
}

// 执行抽奖
const handleDraw = async () => {
  if (isDrawing.value || wheelItems.value.length < 2) return

  isDrawing.value = true
  lastResult.value = null

  try {
    // 调用后端抽奖接口
    const res = await drawWheel()
    if (res.code !== 200) {
      ElMessage.error(res.msg || '抽奖失败')
      isDrawing.value = false
      return
    }

    const winner = res.data
    lastResult.value = winner

    // 执行转盘动画
    await nextTick()
    await animateWheel(winner)

    // 显示结果弹窗
    resultDialogVisible.value = true
  } catch (error) {
    console.error('抽奖失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    isDrawing.value = false
  }
}

// 当前累计旋转角度（保持连续，不重置）
let currentRotation = 0

// 转盘动画（从当前位置连续旋转）
const animateWheel = (winner) => {
  return new Promise((resolve) => {
    const n = wheelItems.value.length
    if (n === 0) return resolve()

    const segmentAngle = 360 / n
    // 找到中奖项的索引
    const winnerIndex = wheelItems.value.findIndex(i => i.id === winner.id)
    
    // 计算中奖分区中心应该对准顶部指针的角度
    const winnerCenterAngle = winnerIndex * segmentAngle + segmentAngle / 2
    // 目标角度：让中奖分区中心对准顶部（0度位置）
    const targetAngle = (360 - winnerCenterAngle) % 360
    
    // 计算从当前位置到目标位置需要旋转的角度（确保为正数）
    const currentAngle = currentRotation % 360
    let rotationDiff = (targetAngle - currentAngle + 360) % 360

    // 多圈旋转（8-12圈）+ 目标角度差
    const totalRotations = 360 * (8 + Math.floor(Math.random() * 4))
    const finalAngle = currentRotation + totalRotations + rotationDiff

    // 通过 Vue 响应式对象驱动动画（与 :style="wheelStyle" 绑定）
    const duration = 5000
    wheelStyle.transition = `transform ${duration}ms cubic-bezier(0.15, 0.85, 0.25, 1)`
    wheelStyle.transform = `rotate(${finalAngle}deg)`

    // 更新当前角度（保持连续）
    currentRotation = finalAngle

    setTimeout(() => {
      resolve()
    }, duration + 200)
  })
}

// 初始化转盘背景（conic-gradient）
const updateWheelBackground = () => {
  const items = wheelItems.value
  if (items.length === 0) return

  const segmentAngle = 360 / items.length
  const gradientParts = []

  let startAngle = 0
  for (const item of items) {
    const endAngle = startAngle + segmentAngle
    gradientParts.push(`${item.color} ${startAngle}deg ${endAngle}deg`)
    startAngle = endAngle
  }

  const wheelEl = wheelRef.value
  if (wheelEl) {
    wheelEl.style.background = `conic-gradient(${gradientParts.join(', ')})`
  }
}

// 监听 wheelItems 变化，更新转盘背景
import { watch, onBeforeUnmount } from 'vue'

const stopWatch = watch(
  wheelItems,
  () => {
    updateWheelBackground()
  },
  { deep: true }
)

onMounted(() => {
  loadConfig()
})

onBeforeUnmount(() => {
  stopWatch?.()
})
</script>

<style scoped>
.wheel-lottery-container {
  min-height: 100vh;
  background: var(--apple-bg, #f5f5f7);
}

/* 顶部导航栏 */
.header {
  background: #ffffff;
  border-bottom: 1px solid #e8e8e8;
  height: 56px;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo:hover { opacity: 0.8 }
.logo-icon { height: 24px; margin-right: 12px }
.logo-text { color: #1d1d1f; font-weight: 600; font-size: 15px; letter-spacing: 0.5px }

.header .el-button {
  color: #0071e3;
  font-size: 14px;
}

.header .el-button:hover {
  background: rgba(0, 113, 227, 0.1);
}

/* 主内容区 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 24px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #1d1d1f;
  text-align: center;
  margin: 0 0 8px;
}

.page-subtitle {
  font-size: 17px;
  color: #86868b;
  text-align: center;
  margin: 0 0 40px;
}

.content-wrapper {
  display: grid;
  grid-template-columns: 420px 1fr;
  gap: 32px;
  align-items: start;
}

/* 左侧面板 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 4px;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.draw-button {
  width: 100%;
  height: 56px;
  font-size: 20px;
  border-radius: 14px;
}

/* 结果展示 */
.result-section {
  border-radius: 14px;
}

.result-display {
  display: flex;
  align-items: center;
  gap: 16px;
}

.result-color {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  flex-shrink: 0;
}

.result-info h3 {
  margin: 0 0 4px;
  font-size: 18px;
  color: #1d1d1f;
}

.result-info p {
  margin: 0;
  font-size: 13px;
  color: #86868b;
}

/* 右侧面板：转盘 */
.right-panel {
  display: flex;
  justify-content: center;
}

.wheel-card {
  border-radius: 20px;
  padding: 32px;
}

.wheel-container {
  position: relative;
  width: 400px;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wheel {
  width: 380px;
  height: 380px;
  border-radius: 50%;
  position: relative;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15), inset 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 4px solid #fff;
}

.segment {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.segment-label {
  position: absolute;
  white-space: nowrap;
  pointer-events: none;
}

/* 中心指针 */
.pointer {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 32px;
  color: #ff3b30;
  z-index: 20;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

/* 中心圆 */
.center-circle {
  position: absolute;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 15;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  font-size: 13px;
  color: #86868b;
}

/* 结果弹窗 */
.dialog-result {
  text-align: center;
  padding: 20px 0;
}

.result-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 0 auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dialog-result h2 {
  margin: 16px 0 8px;
  font-size: 24px;
}

/* 响应式 */
@media (max-width: 900px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }

  .wheel-container {
    width: 320px;
    height: 320px;
  }

  .wheel {
    width: 300px;
    height: 300px;
  }
}

@media (max-width: 600px) {
  .wheel-container {
    width: 280px;
    height: 280px;
  }

  .wheel {
    width: 264px;
    height: 264px;
  }

  .page-title {
    font-size: 28px;
  }
}
</style>