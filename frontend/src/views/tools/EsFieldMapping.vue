<template>
  <div class="field-mapping-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Setting /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">ES 字段映射配置</span>
          <el-button type="primary" size="small" @click="goToEsToExcel" style="margin-left: auto;">
            <el-icon><Document /></el-icon>
            ES 查询结果转 Excel
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索英文或中文字段名"
          clearable
          style="width: 300px;"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 数据表格 -->
      <el-table
        :data="tableData"
        border
        stripe
        v-loading="loading"
        style="width: 100%; margin-top: 20px;"
      >
        <el-table-column prop="english_name" label="英文字段名" width="250" />
        <el-table-column prop="chinese_name" label="中文字段名" width="200" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />

      <!-- 新增按钮 -->
      <div style="margin-top: 15px; text-align: right;">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增映射
        </el-button>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="英文字段名" required>
          <el-input v-model="form.english_name" :disabled="isEdit" placeholder="例如：EVENT_NUMBER" />
        </el-form-item>
        <el-form-item label="中文字段名" required>
          <el-input v-model="form.chinese_name" placeholder="例如：事件ID" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="字段说明（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Setting, Plus, Search, Document } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('新增映射')
const isEdit = ref(false)
const form = ref({
  id: null,
  english_name: '',
  chinese_name: '',
  description: '',
  sort_order: 0,
  is_active: true
})

// 获取列表数据
const fetchList = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchKeyword.value
    })
    
    const response = await fetch(`/api/es-field-mapping/list?${params}`)
    const result = await response.json()
    
    if (result.success) {
      tableData.value = result.data
      total.value = result.total
    } else {
      ElMessage.error(result.message || '获取数据失败')
    }
  } catch (error) {
    console.error('获取数据错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  fetchList()
}

// 重置
const handleReset = () => {
  searchKeyword.value = ''
  currentPage.value = 1
  fetchList()
}

// 分页变化
const handlePageChange = (page) => {
  currentPage.value = page
  fetchList()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchList()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增映射'
  form.value = {
    id: null,
    english_name: '',
    chinese_name: '',
    description: '',
    sort_order: 0,
    is_active: true
  }
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑映射'
  form.value = { ...row }
  dialogVisible.value = true
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除映射 "${row.english_name} -> ${row.chinese_name}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await fetch(`/api/es-field-mapping/delete/${row.id}`, {
      method: 'DELETE'
    })
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success('删除成功')
      fetchList()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除错误:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  }
}

// 提交
const handleSubmit = async () => {
  if (!form.value.english_name || !form.value.chinese_name) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  submitting.value = true
  try {
    let url, method
    if (isEdit.value) {
      url = `/api/es-field-mapping/update/${form.value.id}`
      method = 'PUT'
    } else {
      url = '/api/es-field-mapping/add'
      method = 'POST'
    }
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })
    const result = await response.json()
    
    if (result.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
      dialogVisible.value = false
      fetchList()
    } else {
      ElMessage.error(result.message || '操作失败')
    }
  } catch (error) {
    console.error('提交错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchList()
})

// 跳转到 EsToExcel 页面
const goToEsToExcel = () => {
  router.push('/es-to-excel')
}
</script>

<style scoped>
.field-mapping-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.search-bar {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>
