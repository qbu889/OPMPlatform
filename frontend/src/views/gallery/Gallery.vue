<template>
  <div class="gallery-container">
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
      <!-- 页面标题 -->
      <div class="page-header">
        <h1 class="page-title">🎨 艺术与诗集鉴赏</h1>
        <p class="page-subtitle">探索经典画作与传世诗文的永恒魅力</p>
      </div>

      <!-- 统计概览 -->
      <el-row :gutter="20" class="stats-bar">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <span class="stat-number">{{ stats.paintings_total || 0 }}</span>
              <span class="stat-label">画作</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <span class="stat-number">{{ stats.poetry_total || 0 }}</span>
              <span class="stat-label">诗歌</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <span class="stat-number">{{ paintingCategories.length }}</span>
              <span class="stat-label">画作分类</span>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-item">
              <span class="stat-number">{{ poetryCategories.length }}</span>
              <span class="stat-label">诗歌分类</span>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 标签切换：画作 / 诗集 -->
      <div class="tab-switch">
        <el-tabs v-model="activeTab" @tab-change="switchTab">
          <el-tab-pane label="🖼️ 画作鉴赏" name="paintings"></el-tab-pane>
          <el-tab-pane label="📜 诗集鉴赏" name="poetry"></el-tab-pane>
        </el-tabs>
      </div>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索标题、作者、描述或标签..."
          clearable
          @input="handleSearch"
          style="width: 300px; margin-right: 16px;"
          prefix-icon="Search"
        />
        <el-select
          v-model="selectedCategory"
          placeholder="选择分类"
          clearable
          @change="handleFilter"
          style="width: 160px; margin-right: 16px;"
        >
          <el-option
            v-for="cat in currentCategories"
            :key="cat"
            :label="cat"
            :value="cat"
          />
        </el-select>
        <el-button @click="resetFilters">重置筛选</el-button>
      </div>

      <!-- 画作展示区（瀑布流网格） -->
      <div v-if="activeTab === 'paintings'" class="gallery-grid">
        <el-row :gutter="20" v-loading="isLoading">
          <el-col
            v-for="item in filteredPaintings"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
          >
            <el-card
              class="painting-card"
              shadow="hover"
              @click="openPaintingDetail(item)"
            >
              <div class="painting-image-wrapper">
                <!-- 使用占位图，实际使用时替换为真实图片 -->
                <div class="painting-placeholder" :style="{ backgroundColor: getPaintingColor(item.category) }">
                  <span class="placeholder-icon">{{ getCategoryIcon(item.category) }}</span>
                </div>
                <div class="painting-overlay">
                  <el-button type="primary" size="small" circle>
                    <el-icon><ZoomIn /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="painting-info">
                <h3 class="painting-title">{{ item.title }}</h3>
                <p class="painting-artist">
                  {{ item.artist }} · {{ item.year }}年
                </p>
                <div class="painting-tags">
                  <el-tag v-for="tag in item.tags" :key="tag" size="small" effect="plain">
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredPaintings.length === 0 && !isLoading" description="暂无匹配的画作" />
      </div>

      <!-- 诗集展示区 -->
      <div v-if="activeTab === 'poetry'" class="poetry-list" v-loading="isLoading">
        <el-row :gutter="20">
          <el-col
            v-for="item in filteredPoetry"
            :key="item.id"
            :xs="24"
            :sm="12"
            :lg="8"
          >
            <el-card class="poetry-card" shadow="hover" @click="openPoetryDetail(item)">
              <div class="poetry-header">
                <span class="poetry-dynasty">{{ item.dynasty }}</span>
                <h3 class="poetry-title">{{ item.title }}</h3>
              </div>
              <p class="poetry-author">—— {{ item.author }}</p>

              <!-- 诗歌正文（折叠显示） -->
              <div class="poetry-content">
                {{ item.content }}
              </div>

              <el-divider />

              <p class="poetry-description">{{ item.description }}</p>
              <div class="poetry-tags">
                <el-tag v-for="tag in item.tags" :key="tag" size="small" effect="plain">
                  {{ tag }}
                </el-tag>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="filteredPoetry.length === 0 && !isLoading" description="暂无匹配的诗歌" />
      </div>

      <!-- 画作详情弹窗 -->
      <el-dialog
        v-model="paintingDialogVisible"
        :title="currentPainting?.title"
        width="700px"
        class="painting-dialog"
      >
        <div v-if="currentPainting" class="detail-content">
          <div class="detail-image">
            <div class="painting-placeholder large" :style="{ backgroundColor: getPaintingColor(currentPainting.category) }">
              <span class="placeholder-icon large">{{ getCategoryIcon(currentPainting.category) }}</span>
            </div>
          </div>
          <div class="detail-info">
            <h2>{{ currentPainting.title }}</h2>
            <p class="detail-artist">{{ currentPainting.artist }} · {{ currentPainting.year }}年</p>
            <el-tag>{{ currentPainting.category }}</el-tag>
            <div class="detail-tags">
              <el-tag v-for="tag in currentPainting.tags" :key="tag" size="small" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
            <p class="detail-description">{{ currentPainting.description }}</p>
          </div>
        </div>
      </el-dialog>

      <!-- 诗歌详情弹窗 -->
      <el-dialog
        v-model="poetryDialogVisible"
        :title="currentPoetry?.title"
        width="650px"
        class="poetry-dialog"
      >
        <div v-if="currentPoetry" class="detail-content poetry-detail">
          <div class="poetry-full-header">
            <span class="detail-dynasty">{{ currentPoetry.dynasty }}</span>
            <h2>{{ currentPoetry.title }}</h2>
            <p class="detail-author">—— {{ currentPoetry.author }}</p>
          </div>

          <el-divider class="poetry-divider" />

          <!-- 诗歌正文（大字展示） -->
          <div class="poetry-full-content">
            {{ currentPoetry.content }}
          </div>

          <el-divider />

          <h4>📖 赏析</h4>
          <p class="detail-description">{{ currentPoetry.description }}</p>

          <div class="poetry-full-tags">
            <el-tag v-for="tag in currentPoetry.tags" :key="tag" size="small" effect="plain">
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const API_BASE = '/api/gallery'

// ==================== 状态 ====================
const activeTab = ref('paintings')
const isLoading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('')

// 画作数据
const paintings = ref([])
const paintingCategories = ref([])
const filteredPaintings = computed(() => filterList(paintings.value))

// 诗集数据
const poetry = ref([])
const poetryCategories = ref([])
const filteredPoetry = computed(() => filterList(poetry.value))

// 统计数据
const stats = ref({})

// 弹窗状态
const paintingDialogVisible = ref(false)
const poetryDialogVisible = ref(false)
const currentPainting = ref(null)
const currentPoetry = ref(null)

// ==================== 计算当前分类列表 ====================
const currentCategories = computed(() => {
  return activeTab.value === 'paintings' ? paintingCategories.value : poetryCategories.value
})

// ==================== 通用筛选逻辑 ====================
const filterList = (list) => {
  let result = [...list]

  // 按分类筛选
  if (selectedCategory.value) {
    const catKey = activeTab.value === 'paintings' ? 'category' : 'category'
    result = result.filter(item => item[catKey] === selectedCategory.value)
  }

  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const kw = searchKeyword.value.trim().toLowerCase()
    result = result.filter(item => (
      item.title?.toLowerCase().includes(kw) ||
      (item.artist || item.author)?.toLowerCase().includes(kw) ||
      item.description?.toLowerCase().includes(kw) ||
      item.content?.toLowerCase().includes(kw) ||
      item.tags?.some(tag => tag.toLowerCase().includes(kw))
    ))
  }

  return result
}

// ==================== API 调用 ====================
async function loadPaintings() {
  isLoading.value = true
  try {
    const params = {}
    if (selectedCategory.value) params.category = selectedCategory.value

    const res = await fetch(`${API_BASE}/paintings?${new URLSearchParams(params).toString()}`)
    const data = await res.json()

    if (data.code === 200) {
      paintings.value = data.data
      paintingCategories.value = data.categories || []
    }
  } catch (e) {
    console.error('加载画作失败:', e)
  } finally {
    isLoading.value = false
  }
}

async function loadPoetry() {
  isLoading.value = true
  try {
    const params = {}
    if (selectedCategory.value) params.category = selectedCategory.value

    const res = await fetch(`${API_BASE}/poetry?${new URLSearchParams(params).toString()}`)
    const data = await res.json()

    if (data.code === 200) {
      poetry.value = data.data
      poetryCategories.value = data.categories || []
    }
  } catch (e) {
    console.error('加载诗歌失败:', e)
  } finally {
    isLoading.value = false
  }
}

async function loadStats() {
  try {
    const res = await fetch(`${API_BASE}/stats`)
    const data = await res.json()

    if (data.code === 200) {
      stats.value = data.data
    }
  } catch (e) {
    console.error('加载统计失败:', e)
  }
}

// ==================== 交互方法 ====================
function switchTab(tab) {
  selectedCategory.value = ''
  searchKeyword.value = ''

  if (tab === 'paintings') {
    loadPaintings()
  } else {
    loadPoetry()
  }
}

function handleSearch() {
  // 搜索由 computed 自动处理
}

function handleFilter() {
  if (activeTab.value === 'paintings') {
    loadPaintings()
  } else {
    loadPoetry()
  }
}

function resetFilters() {
  selectedCategory.value = ''
  searchKeyword.value = ''
  if (activeTab.value === 'paintings') {
    loadPaintings()
  } else {
    loadPoetry()
  }
}

function openPaintingDetail(item) {
  currentPainting.value = item
  paintingDialogVisible.value = true
}

function openPoetryDetail(item) {
  currentPoetry.value = item
  poetryDialogVisible.value = true
}

// ==================== 视觉辅助 ====================
const categoryColors = {
  '后印象派': '#e74c3c',
  '印象派': '#2ecc71',
  '古代绘画': '#f39c12',
  '文艺复兴': '#9b59b6',
  '表现主义': '#3498db'
}

const categoryIcons = {
  '后印象派': '🌟',
  '印象派': '🌸',
  '古代绘画': '🏯',
  '文艺复兴': '🎭',
  '表现主义': '😱'
}

function getPaintingColor(category) {
  return categoryColors[category] || '#95a5a6'
}

function getCategoryIcon(category) {
  return categoryIcons[category] || '🎨'
}

// ==================== 生命周期 ====================
onMounted(() => {
  loadStats()
  loadPaintings()
})
</script>

<style scoped>
.gallery-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
}

/* ========== 顶部导航栏 ========== */
.header {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e8e8e8;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.logo-icon {
  height: 32px;
  margin-right: 10px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

/* ========== 主内容区 ========== */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 16px;
  color: #7f8c8d;
}

/* ========== 统计栏 ========== */
.stats-bar {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  cursor: default;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #3498db;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
}

/* ========== Tab 切换 ========== */
.tab-switch {
  margin-bottom: 20px;
}

/* ========== 筛选栏 ========== */
.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 10px;
}

/* ========== 画作网格 ========== */
.gallery-grid {
  margin-bottom: 40px;
}

.painting-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.painting-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.painting-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 75%; /* 4:3 比例 */
  overflow: hidden;
  border-radius: 8px 8px 0 0;
}

.painting-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 48px;
  opacity: 0.6;
}

.painting-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.painting-card:hover .painting-overlay {
  opacity: 1;
}

.painting-info {
  padding: 12px;
}

.painting-title {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.painting-artist {
  font-size: 13px;
  color: #95a5a6;
  margin-bottom: 8px;
}

.painting-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* ========== 诗集列表 ========== */
.poetry-list {
  margin-bottom: 40px;
}

.poetry-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.poetry-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.poetry-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.poetry-dynasty {
  font-size: 13px;
  color: #e67e22;
  background: #fef5e7;
  padding: 2px 8px;
  border-radius: 4px;
}

.poetry-title {
  font-size: 18px;
  color: #2c3e50;
  margin: 0;
}

.poetry-author {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 12px;
}

.poetry-content {
  font-size: 16px;
  line-height: 2;
  color: #34495e;
  text-align: center;
  white-space: pre-line;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.poetry-description {
  font-size: 13px;
  color: #7f8c8d;
  line-height: 1.6;
}

.poetry-tags {
  display: flex;
  gap: 4px;
  margin-top: 8px;
}

/* ========== 画作详情弹窗 ========== */
.painting-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.detail-content {
  display: flex;
  gap: 24px;
}

.detail-image {
  flex: 1;
  min-width: 280px;
}

.detail-image .painting-placeholder.large {
  width: 100%;
  padding-top: 75%;
}

.placeholder-icon.large {
  font-size: 72px;
}

.detail-info {
  flex: 1;
}

.detail-info h2 {
  font-size: 24px;
  color: #2c3e50;
  margin-bottom: 8px;
}

.detail-artist {
  font-size: 15px;
  color: #7f8c8d;
  margin-bottom: 12px;
}

.detail-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 16px;
}

.detail-description {
  font-size: 15px;
  line-height: 1.8;
  color: #34495e;
}

/* ========== 诗歌详情弹窗 ========== */
.poetry-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.poetry-detail .poetry-full-header {
  text-align: center;
  margin-bottom: 16px;
}

.detail-dynasty {
  font-size: 14px;
  color: #e67e22;
}

.poetry-detail h2 {
  font-size: 26px;
  color: #2c3e50;
  margin-bottom: 4px;
}

.detail-author {
  font-size: 15px;
  color: #7f8c8d;
}

.poetry-divider {
  margin: 16px 0;
}

.poetry-full-content {
  font-size: 20px;
  line-height: 2.2;
  color: #2c3e50;
  text-align: center;
  white-space: pre-line;
  padding: 24px;
  background: linear-gradient(to bottom, #fdfcfb, #f5e6d3);
  border-radius: 12px;
  font-family: "STKaiti", "KaiTi", "楷体", serif;
}

.poetry-full-tags {
  display: flex;
  gap: 6px;
  margin-top: 12px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .detail-content {
    flex-direction: column;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-bar > * {
    width: 100% !important;
    margin-right: 0 !important;
  }

  .stat-number {
    font-size: 22px;
  }
}
</style>
