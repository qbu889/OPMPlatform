<template>
  <div class="field-dict-manager">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button 
              type="info" 
              plain
              @click="goBack"
              style="margin-right: 15px"
            >
              <el-icon><ArrowLeft /></el-icon>
              返回
            </el-button>
            <span>Kafka 字段字典管理</span>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="showAddDialog">新增字典项</el-button>
            <el-button type="success" @click="showBatchImportDialog">批量导入</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="Kafka 字段">
          <el-select 
            v-model="filterField" 
            placeholder="选择字段" 
            clearable
            filterable
            @change="handleFilterChange"
            style="width: 250px"
          >
            <el-option
              v-for="field in fieldOptions"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="kafka_field" label="Kafka 字段" width="200" />
        <el-table-column prop="dict_key" label="字典键" width="150" />
        <el-table-column prop="dict_value" label="字典值" min-width="150" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="is_enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled === 1 ? 'success' : 'info'">
              {{ row.is_enabled === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="updated_at" label="更新时间" width="160" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="showEditDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="Kafka 字段" prop="kafka_field">
          <el-input 
            v-model="form.kafka_field" 
            placeholder="输入字段名称"
            :disabled="isEdit"
            style="width: 100%"
          />
          <div v-if="fieldOptions.length > 0" class="field-suggestions">
            <span class="suggestions-label">常用字段：</span>
            <el-tag 
              v-for="field in fieldOptions" 
              :key="field" 
              size="small"
              @click="form.kafka_field = field"
              class="suggestion-tag"
            >
              {{ field }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="字典键" prop="dict_key">
          <el-input 
            v-model="form.dict_key" 
            placeholder="例如：1、CORE、ENABLED"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="字典值" prop="dict_value">
          <el-input 
            v-model="form.dict_value" 
            placeholder="例如：核心层、已启用"
          />
        </el-form-item>
        <el-form-item label="排序" prop="sort_order">
          <el-input-number 
            v-model="form.sort_order" 
            :min="0" 
            :max="9999"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input 
            v-model="form.remark" 
            type="textarea" 
            :rows="3"
            placeholder="可选的备注信息"
          />
        </el-form-item>
        <el-form-item label="状态" v-if="isEdit">
          <el-radio-group v-model="form.is_enabled">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="batchImportVisible"
      title="批量导入字典项"
      width="700px"
    >
      <el-form :model="batchForm" label-width="120px">
        <el-form-item label="Kafka 字段">
          <el-select 
            v-model="batchForm.kafka_field" 
            placeholder="选择字段"
            filterable
            allow-create
            style="width: 100%"
          >
            <el-option
              v-for="field in fieldOptions"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="JSON 数据">
          <el-input 
            v-model="batchForm.jsonData" 
            type="textarea" 
            :rows="10"
            placeholder='格式示例：[{"dict_key": "1", "dict_value": "核心层", "sort_order": 0, "remark": "备注"}]'
          />
          <div class="form-tip">支持 JSON 数组格式，每个对象包含 dict_key、dict_value、sort_order（可选）、remark（可选）</div>
        </el-form-item>
        <el-form-item label="覆盖模式">
          <el-switch 
            v-model="batchForm.overwrite" 
            active-text="覆盖已存在"
            inactive-text="跳过已存在"
          />
          <div class="form-tip">开启后，如果 dict_key 已存在则更新；关闭则跳过</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchImportVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchImport" :loading="importing">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import axios from 'axios'

// 数据
const loading = ref(false)
const submitting = ref(false)
const importing = ref(false)
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const filterField = ref('')
const fieldOptions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新增字典项')
const isEdit = ref(false)
const formRef = ref(null)

const batchImportVisible = ref(false)
const batchForm = reactive({
  kafka_field: '',
  jsonData: '',
  overwrite: false
})

const form = reactive({
  id: null,
  kafka_field: '',
  dict_key: '',
  dict_value: '',
  sort_order: 0,
  remark: '',
  is_enabled: 1
})

const rules = {
  kafka_field: [
    { required: true, message: '请选择 Kafka 字段', trigger: 'change' }
  ],
  dict_key: [
    { required: true, message: '请输入字典键', trigger: 'blur' }
  ],
  dict_value: [
    { required: true, message: '请输入字典值', trigger: 'blur' }
  ]
}

// 加载字段选项
const loadFieldOptions = async () => {
  try {
    const res = await axios.get('/kafka-generator/field-order')
    if (res.data.success) {
      fieldOptions.value = res.data.data.fields || []
    }
  } catch (error) {
    console.error('加载字段选项失败:', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (filterField.value) {
      params.kafka_field = filterField.value
    }

    const res = await axios.get('/kafka-generator/field-dict', { params })
    if (res.data.success) {
      tableData.value = res.data.data.items
      total.value = res.data.data.total
    } else {
      ElMessage.error(res.data.message || '加载失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 筛选变化
const handleFilterChange = () => {
  currentPage.value = 1
  loadData()
}

// 重置筛选
const resetFilter = () => {
  filterField.value = ''
  currentPage.value = 1
  loadData()
}

// 分页
const handlePageChange = (page) => {
  currentPage.value = page
  loadData()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadData()
}

// 显示新增对话框
const showAddDialog = () => {
  isEdit.value = false
  dialogTitle.value = '新增字典项'
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑字典项'
  Object.assign(form, {
    id: row.id,
    kafka_field: row.kafka_field,
    dict_key: row.dict_key,
    dict_value: row.dict_value,
    sort_order: row.sort_order,
    remark: row.remark,
    is_enabled: row.is_enabled
  })
  dialogVisible.value = true
}

// 检查是否存在重复的字典项
const checkDuplicate = async () => {
  try {
    const res = await axios.get('/kafka-generator/field-dict', {
      params: {
        page: 1,
        page_size: 1,
        kafka_field: form.kafka_field,
        dict_key: form.dict_key
      }
    })
    if (res.data.success && res.data.data.total > 0) {
      return true
    }
  } catch (error) {
    console.error('检查重复失败:', error)
  }
  return false
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 新增时检查重复
    if (!isEdit.value) {
      submitting.value = true
      const isDuplicate = await checkDuplicate()
      submitting.value = false
      
      if (isDuplicate) {
        ElMessage.warning(`已存在相同的字典项: ${form.kafka_field}.${form.dict_key}`)
        return
      }
    }

    submitting.value = true
    try {
      if (isEdit.value) {
        // 更新
        const res = await axios.put(`/kafka-generator/field-dict/${form.id}`, {
          dict_value: form.dict_value,
          sort_order: form.sort_order,
          is_enabled: form.is_enabled,
          remark: form.remark
        })
        
        if (res.data.success) {
          ElMessage.success('更新成功')
          dialogVisible.value = false
          loadData()
        } else {
          ElMessage.error(res.data.message || '更新失败')
        }
      } else {
        // 新增
        const res = await axios.post('/kafka-generator/field-dict', {
          kafka_field: form.kafka_field,
          dict_key: form.dict_key,
          dict_value: form.dict_value,
          sort_order: form.sort_order,
          remark: form.remark
        })
        
        if (res.data.success) {
          ElMessage.success('新增成功')
          dialogVisible.value = false
          loadData()
        } else {
          ElMessage.error(res.data.message || '新增失败')
        }
      }
    } catch (error) {
      console.error('提交失败:', error)
      ElMessage.error(error.response?.data?.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除字典项 "${row.kafka_field}.${row.dict_key}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await axios.delete(`/kafka-generator/field-dict/${row.id}`)
      if (res.data.success) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error(error.response?.data?.message || '删除失败')
    }
  }).catch(() => {})
}

// 显示批量导入对话框
const showBatchImportDialog = () => {
  batchImportVisible.value = true
  batchForm.kafka_field = filterField.value || ''
  batchForm.jsonData = ''
  batchForm.overwrite = false
}

// 批量导入
const handleBatchImport = async () => {
  if (!batchForm.kafka_field) {
    ElMessage.warning('请选择 Kafka 字段')
    return
  }

  if (!batchForm.jsonData.trim()) {
    ElMessage.warning('请输入 JSON 数据')
    return
  }

  let items
  try {
    items = JSON.parse(batchForm.jsonData)
    if (!Array.isArray(items)) {
      ElMessage.error('JSON 数据必须是数组格式')
      return
    }
  } catch (e) {
    ElMessage.error('JSON 格式错误：' + e.message)
    return
  }

  importing.value = true
  try {
    const res = await axios.post('/kafka-generator/field-dict/batch-import', {
      kafka_field: batchForm.kafka_field,
      items: items,
      overwrite: batchForm.overwrite
    })
    
    if (res.data.success) {
      ElMessage.success(res.data.message)
      batchImportVisible.value = false
      loadData()
      
      // 显示详细结果
      if (res.data.data.error_count > 0) {
        console.warn('导入错误:', res.data.data.errors)
      }
    } else {
      ElMessage.error(res.data.message || '导入失败')
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error(error.response?.data?.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    id: null,
    kafka_field: '',
    dict_key: '',
    dict_value: '',
    sort_order: 0,
    remark: '',
    is_enabled: 1
  })
}

// 返回上一页
const goBack = () => {
  window.history.back()
}

// 初始化
onMounted(() => {
  loadFieldOptions()
  loadData()
})
</script>

<style scoped>
.field-dict-manager {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  gap: 10px;
}

.filter-form {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.field-suggestions {
  margin-top: 8px;
}

.suggestions-label {
  font-size: 12px;
  color: #909399;
  margin-right: 8px;
}

.suggestion-tag {
  cursor: pointer;
  margin-right: 6px;
  margin-bottom: 4px;
  transition: all 0.2s;
}

.suggestion-tag:hover {
  background-color: #1890ff;
  color: white;
}
</style>
