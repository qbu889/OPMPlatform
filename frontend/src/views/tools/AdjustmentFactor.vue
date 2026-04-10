<template>
  <div class="adjustment-factor">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Tools /></el-icon> 调整因子管理</span>
          <div>
            <el-upload
              action="/adjustment/api/import-excel"
              :on-success="handleImportSuccess"
              :on-error="handleImportError"
              accept=".xlsx,.xls"
              :show-file-list="false"
            >
              <el-button type="success">
                <el-icon><Upload /></el-icon> 导入 Excel
              </el-button>
            </el-upload>
            <el-button type="primary" @click="showAddDialog" style="margin-left: 10px;">
              <el-icon><Plus /></el-icon> 添加因子
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="因子类别">
          <el-select v-model="filters.factor_category" placeholder="全部" clearable @change="loadFactors">
            <el-option label="全部" value="" />
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="因子名称">
          <el-input v-model="filters.factor_name" placeholder="搜索因子名称" clearable @keyup.enter="loadFactors" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadFactors">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 因子列表 -->
      <el-table :data="factors" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="factor_category" label="因子类别" width="120" />
        <el-table-column prop="factor_name" label="因子名称" min-width="150" />
        <el-table-column prop="option_name" label="选项名称" min-width="150" />
        <el-table-column prop="score_value" label="分值" width="100" />
        <el-table-column prop="formula" label="公式" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <code>{{ row.formula || '-' }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editFactor(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="deleteFactor(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadFactors"
        @current-change="loadFactors"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="因子类别" prop="factor_category">
          <el-input v-model="form.factor_category" placeholder="请输入因子类别" />
        </el-form-item>
        <el-form-item label="因子名称" prop="factor_name">
          <el-input v-model="form.factor_name" placeholder="请输入因子名称" />
        </el-form-item>
        <el-form-item label="选项名称" prop="option_name">
          <el-input v-model="form.option_name" placeholder="请输入选项名称" />
        </el-form-item>
        <el-form-item label="分值" prop="score_value">
          <el-input-number v-model="form.score_value" :precision="2" :step="0.01" :min="0" :max="10" />
        </el-form-item>
        <el-form-item label="公式" prop="formula">
          <el-input v-model="form.formula" type="textarea" :rows="3" placeholder="请输入计算公式" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Upload, Tools } from '@element-plus/icons-vue'

const factors = ref([])
const categories = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加因子')
const submitting = ref(false)
const formRef = ref(null)

const filters = reactive({
  factor_category: '',
  factor_name: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const form = reactive({
  id: null,
  factor_category: '',
  factor_name: '',
  option_name: '',
  score_value: 0,
  formula: '',
  description: ''
})

const rules = {
  factor_name: [{ required: true, message: '请输入因子名称', trigger: 'blur' }]
}

// 加载因子列表
const loadFactors = async () => {
  try {
    const params = new URLSearchParams({
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters
    })
    
    const response = await fetch(`/adjustment/api/factors?${params}`)
    const result = await response.json()
    
    if (result.success) {
      factors.value = result.factors || []
      pagination.total = result.total || 0
      
      // 提取所有唯一的因子类别
      const cats = new Set(factors.value.map(f => f.factor_category).filter(Boolean))
      categories.value = Array.from(cats)
    } else {
      ElMessage.error(result.message || '加载失败')
    }
  } catch (error) {
    console.error('加载因子列表失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 重置筛选
const resetFilters = () => {
  Object.assign(filters, {
    factor_category: '',
    factor_name: ''
  })
  pagination.page = 1
  loadFactors()
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加因子'
  Object.assign(form, {
    id: null,
    factor_category: '',
    factor_name: '',
    option_name: '',
    score_value: 0,
    formula: '',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑因子
const editFactor = (row) => {
  dialogTitle.value = '编辑因子'
  Object.assign(form, {
    id: row.id,
    factor_category: row.factor_category || '',
    factor_name: row.factor_name,
    option_name: row.option_name || '',
    score_value: row.score_value || 0,
    formula: row.formula || '',
    description: row.description || ''
  })
  dialogVisible.value = true
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const url = form.id ? `/adjustment/api/factor/${form.id}` : '/adjustment/api/factor'
      const method = form.id ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      
      const result = await response.json()
      
      if (result.success) {
        ElMessage.success(form.id ? '更新成功' : '添加成功')
        dialogVisible.value = false
        await loadFactors()
      } else {
        ElMessage.error(result.message || '操作失败')
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error('网络错误，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

// 删除因子
const deleteFactor = (row) => {
  ElMessageBox.confirm(
    `确定要删除因子 "${row.factor_name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await fetch(`/adjustment/api/factor/${row.id}`, {
        method: 'DELETE'
      })
      
      const result = await response.json()
      
      if (result.success) {
        ElMessage.success('删除成功')
        await loadFactors()
      } else {
        ElMessage.error(result.message || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  }).catch(() => {
    // 用户取消
  })
}

// 导入成功
const handleImportSuccess = (response) => {
  if (response.success) {
    ElMessage.success(response.message || '导入成功')
    loadFactors()
  } else {
    ElMessage.error(response.message || '导入失败')
  }
}

// 导入失败
const handleImportError = () => {
  ElMessage.error('文件上传失败，请检查文件格式')
}

onMounted(() => {
  loadFactors()
})
</script>

<style scoped>
.adjustment-factor {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.card-header .el-icon {
  margin-right: 8px;
}

.filter-form {
  margin-bottom: 20px;
}
</style>
