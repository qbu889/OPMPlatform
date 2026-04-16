<template>
  <div class="fpa-category-rules">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button type="text" @click="goBack" class="back-btn">
              <el-icon><ArrowLeft /></el-icon> 返回
            </el-button>
            <span class="title-text"><el-icon><Document /></el-icon> FPA 类别规则管理</span>
          </div>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon> 添加规则
          </el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="功能点类型">
          <el-select v-model="filters.category" placeholder="全部" clearable @change="loadRules" style="width: 150px;">
            <el-option label="全部" value="" />
            <el-option label="EI" value="EI" />
            <el-option label="EO" value="EO" />
            <el-option label="EQ" value="EQ" />
            <el-option label="ILF" value="ILF" />
            <el-option label="EIF" value="EIF" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索关键词" clearable @keyup.enter="loadRules" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable @change="loadRules" style="width: 120px;">
            <el-option label="全部" value="" />
            <el-option label="启用" value="true" />
            <el-option label="禁用" value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadRules">
            <el-icon><Search /></el-icon> 查询
          </el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 规则列表 -->
      <el-table :data="rules" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="category" label="功能点类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column prop="rule_type" label="规则类型" width="120" />
        <el-table-column prop="keyword" label="关键词" min-width="150" />
        <el-table-column prop="ufp_value" label="UFP值" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="启用状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editRule(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="deleteRule(row)">
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
        @size-change="loadRules"
        @current-change="loadRules"
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
        <el-form-item label="功能点类型" prop="category">
          <el-select v-model="form.category" placeholder="请选择功能点类型">
            <el-option label="EI (外部输入)" value="EI" />
            <el-option label="EO (外部输出)" value="EO" />
            <el-option label="EQ (外部查询)" value="EQ" />
            <el-option label="ILF (内部逻辑文件)" value="ILF" />
            <el-option label="EIF (外部接口文件)" value="EIF" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-input-number v-model="form.priority" :min="1" :max="100" />
          <div class="form-tip">数字越小优先级越高</div>
        </el-form-item>
        <el-form-item label="规则类型" prop="rule_type">
          <el-select v-model="form.rule_type" placeholder="请选择规则类型">
            <el-option label="结尾匹配 (endswith)" value="endswith" />
            <el-option label="包含匹配 (contains)" value="contains" />
            <el-option label="开头匹配 (startswith)" value="startswith" />
            <el-option label="特殊规则 (special)" value="special" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词" prop="keyword">
          <el-input v-model="form.keyword" placeholder="请输入匹配的关键词" />
        </el-form-item>
        <el-form-item label="UFP值" prop="ufp_value">
          <el-input-number v-model="form.ufp_value" :precision="2" :step="0.5" :min="0" :max="50" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入规则描述" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="form.is_active" />
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
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Document, ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

// 返回上一页
const goBack = () => {
  router.push('/fpa-generator')
}

const rules = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加规则')
const submitting = ref(false)
const formRef = ref(null)

const filters = reactive({
  category: '',
  keyword: '',
  is_active: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const form = reactive({
  id: null,
  category: '',
  priority: 1,
  rule_type: 'endswith',
  keyword: '',
  description: '',
  ufp_value: 3.0,
  is_active: true
})

const validateRules = {
  category: [{ required: true, message: '请选择功能点类型', trigger: 'change' }],
  priority: [{ required: true, message: '请输入优先级', trigger: 'blur' }],
  rule_type: [{ required: true, message: '请选择规则类型', trigger: 'change' }],
  keyword: [{ required: true, message: '请输入关键词', trigger: 'blur' }],
  ufp_value: [{ required: true, message: '请输入UFP值', trigger: 'blur' }]
}

// 加载规则列表
const loadRules = async () => {
  try {
    // 构建参数对象，只包含有值的筛选条件
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
    }
    
    // 只添加非空字符串的参数
    if (filters.category) params.category = filters.category
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.is_active !== '') params.is_active = filters.is_active === 'true' ? true : false
    
    const queryString = new URLSearchParams(params).toString()
    const response = await fetch(`/fpa-rules/api/rules?${queryString}`)
    const result = await response.json()
    
    if (result.rules) {
      rules.value = result.rules
      pagination.total = result.total || 0
    } else {
      ElMessage.error(result.error || '加载失败')
    }
  } catch (error) {
    console.error('加载规则列表失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 重置筛选
const resetFilters = () => {
  filters.category = ''
  filters.keyword = ''
  filters.is_active = ''
  pagination.page = 1
  loadRules()
}

// 获取类别标签类型
const getCategoryType = (category) => {
  const types = {
    'EI': 'primary',
    'EO': 'success',
    'EQ': 'warning',
    'ILF': 'danger',
    'EIF': 'info'
  }
  return types[category] || ''
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加规则'
  Object.assign(form, {
    id: null,
    category: '',
    priority: 1,
    rule_type: 'endswith',
    keyword: '',
    description: '',
    ufp_value: 3.0,
    is_active: true
  })
  dialogVisible.value = true
}

// 编辑规则
const editRule = (row) => {
  dialogTitle.value = '编辑规则'
  Object.assign(form, {
    id: row.id,
    category: row.category,
    priority: row.priority,
    rule_type: row.rule_type,
    keyword: row.keyword,
    description: row.description || '',
    ufp_value: row.ufp_value,
    is_active: row.is_active
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
      const url = form.id ? `/fpa-rules/api/rules/${form.id}` : '/fpa-rules/api/rules'
      const method = form.id ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      
      const result = await response.json()
      
      if (result.message) {
        ElMessage.success(form.id ? '更新成功' : '添加成功')
        dialogVisible.value = false
        await loadRules()
      } else {
        ElMessage.error(result.error || '操作失败')
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error('网络错误，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

// 切换启用状态
const toggleActive = async (row) => {
  try {
    const response = await fetch(`/fpa-rules/api/rules/${row.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        is_active: row.is_active
      })
    })
    
    const result = await response.json()
    
    if (result.message) {
      ElMessage.success('状态更新成功')
    } else {
      ElMessage.error(result.error || '更新失败')
      row.is_active = !row.is_active // 恢复原状态
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    ElMessage.error('网络错误，请稍后重试')
    row.is_active = !row.is_active // 恢复原状态
  }
}

// 删除规则
const deleteRule = (row) => {
  ElMessageBox.confirm(
    `确定要删除该规则吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await fetch(`/fpa-rules/api/rules/${row.id}`, {
        method: 'DELETE'
      })
      
      const result = await response.json()
      
      if (result.message) {
        ElMessage.success('删除成功')
        await loadRules()
      } else {
        ElMessage.error(result.error || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  }).catch(() => {
    // 用户取消
  })
}

onMounted(() => {
  loadRules()
})
</script>

<style scoped>
.fpa-category-rules {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  padding: 4px 8px;
  color: #606266;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.back-btn:hover {
  color: #409eff;
}

.title-text {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-header .el-icon {
  margin-right: 8px;
}

.filter-form {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
