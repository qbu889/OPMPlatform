<!-- frontend/src/views/dingtalk-push/DingTalkPushHistory.vue -->
<template>
  <div class="dingtalk-push-history">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>推送历史</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部状态" clearable>
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHistory">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 历史列表 -->
      <el-table :data="historyList" v-loading="loading" stripe>
        <el-table-column prop="triggered_at" label="触发时间" width="180" />
        <el-table-column prop="config_name" label="配置名称" width="200" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_duration_ms" label="耗时(ms)" width="100" />
        <el-table-column prop="retry_count" label="重试次数" width="100" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看详情</el-button>
            <el-button 
              v-if="row.config_is_deleted === 1" 
              size="small" 
              type="warning"
              @click="restoreConfig(row.config_id, row.config_name)"
            >
              恢复配置
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadHistory"
        @current-change="loadHistory"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="推送详情" width="800px">
      <div v-if="currentDetail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="触发时间">
            {{ currentDetail.triggered_at }}
          </el-descriptions-item>
          <el-descriptions-item label="执行耗时">
            {{ currentDetail.execution_duration_ms }} ms
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentDetail.status === 'success' ? 'success' : 'danger'">
              {{ currentDetail.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="重试次数">
            {{ currentDetail.retry_count }}
          </el-descriptions-item>
          <el-descriptions-item label="触发类型">
            {{ currentDetail.trigger_type === 'manual' ? '手动' : '定时' }}
          </el-descriptions-item>
        </el-descriptions>

        <h4 style="margin-top: 20px">执行日志</h4>
        <el-timeline>
          <el-timeline-item
            v-for="log in currentDetail.logs"
            :key="log.id"
            :timestamp="log.created_at"
            :type="getLogType(log.step)"
          >
            {{ log.details }}
          </el-timeline-item>
        </el-timeline>

        <h4 style="margin-top: 20px">消息快照</h4>
        <pre style="background: #f5f7fa; padding: 10px; border-radius: 4px; overflow-x: auto">{{ 
          formatJson(currentDetail.message_content) 
        }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const historyList = ref([])
const filterStatus = ref('')
const pagination = ref({
  page: 1,
  size: 20,
  total: 0
})

const detailVisible = ref(false)
const currentDetail = ref(null)

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.size
    }
    
    if (route.query.config_id) {
      params.config_id = route.query.config_id
    }
    
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    
    const res = await axios.get('/dingtalk-push/history', { params })
    
    if (res.data.success) {
      historyList.value = res.data.data.list
      pagination.value.total = res.data.data.total
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = async (row) => {
  try {
    const res = await axios.get(`/dingtalk-push/history/${row.id}`)
    
    if (res.data.success) {
      currentDetail.value = res.data.data
      detailVisible.value = true
    }
  } catch (error) {
    console.error(error)
  }
}

// 获取日志类型
const getLogType = (level) => {
  const types = {
    INFO: '',
    WARNING: 'warning',
    ERROR: 'danger'
  }
  return types[level] || ''
}

// 格式化 JSON
const formatJson = (data) => {
  if (!data) return '{}'
  try {
    const obj = typeof data === 'string' ? JSON.parse(data) : data
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(data)
  }
}

// 返回
const goBack = () => {
  router.push('/dingtalk-push')
}

// 恢复配置
const restoreConfig = async (configId, configName) => {
  try {
    await ElMessageBox.confirm(
      `确定要恢复配置 "${configName}" 吗？`,
      '恢复配置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await axios.post(`/dingtalk-push/configs/${configId}/restore`)
    
    if (res.data.success) {
      ElMessage.success(res.data.msg || '配置已恢复')
      // 刷新历史列表
      loadHistory()
    } else {
      ElMessage.error(res.data.msg || '恢复失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error('恢复配置失败')
    }
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.dingtalk-push-history {
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

h4 {
  margin-bottom: 10px;
  color: #303133;
}
</style>
