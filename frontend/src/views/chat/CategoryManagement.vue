<template>
  <div class="category-management">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Collection /></el-icon> 专业领域管理</span>
          <el-button type="primary" @click="showAddDialog">
            <el-icon><Plus /></el-icon> 添加领域
          </el-button>
        </div>
      </template>

      <!-- 领域列表 -->
      <el-table :data="categories" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="领域名称" min-width="150">
          <template #default="{ row }">
            <el-tag :color="row.color" effect="dark">{{ row.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="启用状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.is_active" @change="toggleActive(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editCategory(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button size="small" type="danger" @click="deleteCategory(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="领域名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入领域名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="颜色标识" prop="color">
          <el-color-picker v-model="form.color" />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Collection } from '@element-plus/icons-vue'

const categories = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('添加领域')
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  description: '',
  color: '#1890ff',
  is_active: true,
  sort_order: 0
})

const rules = {
  name: [{ required: true, message: '请输入领域名称', trigger: 'blur' }]
}

// 加载领域列表
const loadCategories = async () => {
  try {
    const response = await fetch('/api/category/list?active_only=false')
    const result = await response.json()
    
    if (result.success) {
      categories.value = result.categories || []
    } else {
      ElMessage.error(result.error || '加载失败')
    }
  } catch (error) {
    console.error('加载领域列表失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 显示添加对话框
const showAddDialog = () => {
  dialogTitle.value = '添加领域'
  Object.assign(form, {
    id: null,
    name: '',
    description: '',
    color: '#1890ff',
    is_active: true,
    sort_order: 0
  })
  dialogVisible.value = true
}

// 编辑领域
const editCategory = (row) => {
  dialogTitle.value = '编辑领域'
  Object.assign(form, {
    id: row.id,
    name: row.name,
    description: row.description || '',
    color: row.color || '#1890ff',
    is_active: row.is_active,
    sort_order: row.sort_order || 0
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
      const url = form.id ? '/api/category/update' : '/api/category/add'
      const method = 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form)
      })
      
      const result = await response.json()
      
      if (result.success) {
        ElMessage.success(form.id ? '更新成功' : '添加成功')
        dialogVisible.value = false
        await loadCategories()
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
    const response = await fetch('/api/category/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: row.id,
        is_active: row.is_active
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
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

// 删除领域
const deleteCategory = (row) => {
  ElMessageBox.confirm(
    `确定要删除领域 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await fetch('/api/category/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: row.id })
      })
      
      const result = await response.json()
      
      if (result.success) {
        ElMessage.success('删除成功')
        await loadCategories()
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
  loadCategories()
})
</script>

<style scoped>
.category-management {
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
</style>
