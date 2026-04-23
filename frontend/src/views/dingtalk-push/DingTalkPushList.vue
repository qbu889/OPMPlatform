<!-- frontend/src/views/dingtalk-push/DingTalkPushList.vue -->
<template>
  <div class="dingtalk-push-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>钉钉推送管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="搜索">
          <el-input v-model="searchKeyword" placeholder="任务名称" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="filterCategory" placeholder="全部分类" clearable>
            <el-option label="排班" value="roster" />
            <el-option label="告警" value="alert" />
            <el-option label="日报" value="report" />
            <el-option label="其他" value="general" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterEnabled" placeholder="全部状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadConfigs">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 配置列表 -->
      <el-table :data="configList" v-loading="loading" stripe>
        <el-table-column prop="name" label="任务名称" min-width="200" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">
              {{ getCategoryName(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              v-model="row.enabled"
              @change="handleToggle(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="调度" min-width="180">
          <template #default="{ row }">
            {{ formatSchedule(row.schedule_config) }}
          </template>
        </el-table-column>
        <el-table-column label="上次执行" width="180">
          <template #default="{ row }">
            <span v-if="row.last_run">
              {{ row.last_run.time }}
              <el-icon :color="row.last_run.status === 'success' ? '#67c23a' : '#f56c6c'">
                <component :is="row.last_run.status === 'success' ? 'CircleCheck' : 'CircleClose'" />
              </el-icon>
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="380" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" @click="handlePreview(row)">预览</el-button>
            <el-button size="small" type="success" @click="handleExecute(row)">立即执行</el-button>
            <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
              <el-button size="small">
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="history">查看历史</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadConfigs"
        @current-change="loadConfigs"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, ArrowDown, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

// 数据
const loading = ref(false)
const configList = ref([])
const searchKeyword = ref('')
const filterCategory = ref('')
const filterEnabled = ref('')
const isUpdating = ref(false) // 标记是否正在更新数据，避免误触发 toggle
const pagination = ref({
  page: 1,
  size: 10,
  total: 0
})

// 加载配置列表
const loadConfigs = async () => {
  loading.value = true
  isUpdating.value = true // 标记开始更新
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size
    }
    
    if (filterCategory.value) params.category = filterCategory.value
    if (filterEnabled.value !== '') params.enabled = filterEnabled.value
    
    const res = await axios.get('/dingtalk-push/configs', { params })
    
    if (res.data.success) {
      // 转换 enabled 字段为布尔值，确保 el-switch 正确显示
      configList.value = res.data.data.list.map(config => ({
        ...config,
        enabled: Boolean(config.enabled)
      }))
      pagination.value.total = res.data.data.total
    } else {
      ElMessage.error(res.data.msg || '加载失败')
    }
  } catch (error) {
    ElMessage.error('加载配置列表失败')
    console.error(error)
  } finally {
    loading.value = false
    // 延迟解除标记，确保 DOM 更新完成
    setTimeout(() => {
      isUpdating.value = false
    }, 100)
  }
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  filterCategory.value = ''
  filterEnabled.value = ''
  pagination.value.page = 1
  loadConfigs()
}

// 新建任务
const handleCreate = () => {
  router.push('/dingtalk-push/config/new')
}

// 编辑任务
const handleEdit = (row) => {
  router.push(`/dingtalk-push/config/${row.id}`)
}

// 预览消息
const handlePreview = (row) => {
  router.push(`/dingtalk-push/preview/${row.id}`)
}

// 立即执行
const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm('确定要立即执行此推送任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await axios.post(`/dingtalk-push/configs/${row.id}/execute`)
    
    if (res.data.success) {
      ElMessage.success('推送任务已提交')
    } else {
      ElMessage.error(res.data.msg || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败')
      console.error(error)
    }
  }
}

// 切换启用状态
const handleToggle = async (row) => {
  // 如果正在更新数据，忽略此次触发
  if (isUpdating.value) return
  
  try {
    const res = await axios.patch(`/dingtalk-push/configs/${row.id}/toggle`, {
      enabled: row.enabled
    })
    
    if (res.data.success) {
      ElMessage.success(res.data.msg)
    } else {
      // 恢复原状态
      row.enabled = !row.enabled
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    // 恢复原状态
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
    console.error(error)
  }
}

// 下拉菜单命令
const handleCommand = (command, row) => {
  if (command === 'history') {
    router.push(`/dingtalk-push/history?config_id=${row.id}`)
  } else if (command === 'delete') {
    handleDelete(row)
  }
}

// 删除任务
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除任务"${row.name}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const res = await axios.delete(`/dingtalk-push/configs/${row.id}`)
    
    if (res.data.success) {
      ElMessage.success('删除成功')
      loadConfigs()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 获取分类类型
const getCategoryType = (category) => {
  const types = {
    roster: '',
    alert: 'danger',
    report: 'success',
    general: 'info'
  }
  return types[category] || 'info'
}

// 获取分类名称
const getCategoryName = (category) => {
  const names = {
    roster: '排班',
    alert: '告警',
    report: '日报',
    general: '其他'
  }
  return names[category] || category
}

// 格式化调度配置
const formatSchedule = (scheduleConfig) => {
  if (!scheduleConfig) return '-'
  
  try {
    const config = typeof scheduleConfig === 'string' 
      ? JSON.parse(scheduleConfig) 
      : scheduleConfig
    
    if (config.type === 'daily') {
      const times = config.config.times?.join(', ') || ''
      const weekdays = config.config.weekdays ? '(工作日)' : ''
      return `每天 ${times} ${weekdays}`
    } else if (config.type === 'weekly') {
      return `每周${config.config.day_of_week} ${config.config.time}`
    } else if (config.type === 'cron') {
      return `Cron: ${config.config.expression}`
    } else if (config.type === 'once') {
      return `单次: ${config.config.execute_at}`
    }
    
    return config.type
  } catch {
    return '-'
  }
}

onMounted(() => {
  loadConfigs()
})

// 监听路由变化，确保从编辑页返回时重新加载数据
watch(() => route.path, () => {
  if (route.path === '/dingtalk-push') {
    loadConfigs()
  }
})
</script>

<style scoped>
.dingtalk-push-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
