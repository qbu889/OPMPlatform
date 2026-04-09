<template>
  <div class="faq-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><ChatLineSquare /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">FAQ 预览</span>
        </div>
      </template>

      <el-form :inline="true" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filter.category" placeholder="全部分类" clearable>
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="filter.keyword"
            placeholder="搜索问题..."
            clearable
            @change="loadFaqs"
          />
        </el-form-item>
      </el-form>

      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
      </div>

      <el-collapse v-else>
        <el-collapse-item
          v-for="faq in faqs"
          :key="faq.id"
          :title="faq.question"
        >
          <div class="faq-answer">{{ faq.answer }}</div>
        </el-collapse-item>
      </el-collapse>

      <el-empty v-if="!loading && faqs.length === 0" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ChatLineSquare, Loading } from '@element-plus/icons-vue'

const loading = ref(false)
const faqs = ref([])
const categories = ref([])
const filter = ref({
  category: null,
  keyword: '',
})

const loadFaqs = async () => {
  loading.value = true
  try {
    const response = await fetch('/chat/api/faq/list')
    const result = await response.json()
    if (result.success) {
      faqs.value = result.data
      categories.value = result.categories || []
    }
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadFaqs()
})
</script>

<style scoped>
.faq-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.filter-form {
  margin-bottom: 20px;
}

.loading-container {
  text-align: center;
  padding: 40px;
}

.faq-answer {
  padding: 15px;
  line-height: 1.8;
  color: #606266;
}
</style>
