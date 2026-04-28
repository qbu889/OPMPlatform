<template>
  <div class="field-meta-manager">
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
            <span>Kafka 字段映射管理</span>
          </div>
          <el-button type="primary" @click="showAddDialog">新增映射</el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" class="search-form">
        <el-form-item label="搜索">
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索 Kafka 字段、ES 字段、中文说明"
            clearable
            @clear="loadData"
            @keyup.enter="handleSearch"
            style="width: 300px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="kafka_field" label="Kafka 字段" width="200" />
        <el-table-column prop="es_field" label="ES 字段" width="200" />
        <el-table-column prop="label_cn" label="字段中文解释" width="150" />
        <el-table-column prop="db_cn" label="数据库中文" width="150" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="is_enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_enabled === 1 ? 'success' : 'info'">
              {{ row.is_enabled === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
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
            placeholder="例如：STANDARD_ALARM_ID"
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="ES 字段" prop="es_field">
          <el-input 
            v-model="form.es_field" 
            placeholder="例如：ALARM_STANDARD_ID"
          />
          <div class="form-tip">输入 ES 中的原始字段名，留空则使用默认映射</div>
        </el-form-item>
        <el-form-item label="字段中文解释" prop="label_cn">
          <el-input v-model="form.label_cn" placeholder="例如：网管告警ID" />
        </el-form-item>
        <el-form-item label="数据库中文" prop="db_cn">
          <el-input v-model="form.db_cn" placeholder="例如：告警标准化ID" />
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
const tableData = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const searchKeyword = ref('')

const dialogVisible = ref(false)
const dialogTitle = ref('新增映射')
const isEdit = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  kafka_field: '',
  es_field: '',
  db_cn: '',
  label_cn: '',
  remark: '',
  is_enabled: 1
})

const rules = {
  kafka_field: [
    { required: true, message: '请输入 Kafka 字段', trigger: 'blur' }
  ]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    if (searchKeyword.value) {
      params.keyword = searchKeyword.value
    }

    const res = await axios.get('/kafka-generator/field-meta/list', { params })
    if (res.data.success) {
      tableData.value = res.data.data.list
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

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

// 重置搜索
const resetSearch = () => {
  searchKeyword.value = ''
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
  dialogTitle.value = '新增映射'
  dialogVisible.value = true
}

// 显示编辑对话框
const showEditDialog = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑映射'
  Object.assign(form, {
    id: row.id,
    kafka_field: row.kafka_field,
    es_field: row.es_field,
    db_cn: row.db_cn,
    label_cn: row.label_cn,
    remark: row.remark,
    is_enabled: row.is_enabled
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEdit.value) {
        // 更新
        const res = await axios.put(`/kafka-generator/field-meta/${form.id}`, {
          es_field: form.es_field,
          db_cn: form.db_cn,
          label_cn: form.label_cn,
          remark: form.remark,
          is_enabled: form.is_enabled
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
        const res = await axios.post('/kafka-generator/field-meta', {
          kafka_field: form.kafka_field,
          es_field: form.es_field,
          db_cn: form.db_cn,
          label_cn: form.label_cn,
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
    `确定要删除字段映射 "${row.kafka_field}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const res = await axios.delete(`/kafka-generator/field-meta/${row.id}`)
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

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  Object.assign(form, {
    id: null,
    kafka_field: '',
    es_field: '',
    db_cn: '',
    label_cn: '',
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
  loadData()
})
</script>

<style scoped>
.field-meta-manager {
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

.search-form {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
