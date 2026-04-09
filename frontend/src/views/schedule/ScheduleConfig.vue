<template>
  <div class="schedule-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Calendar /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">排班配置管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="排班列表" name="list">
          <div class="toolbar">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增排班
            </el-button>
            <el-button @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </div>

          <el-table :data="schedules" border style="width: 100%;" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="排班名称" />
            <el-table-column prop="department" label="部门" />
            <el-table-column prop="startDate" label="开始日期" width="120" />
            <el-table-column prop="endDate" label="结束日期" width="120" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'">
                  {{ row.status === 'active' ? '进行中' : '已结束' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="200">
              <template #default="{ row }">
                <el-button type="primary" text @click="handleEdit(row)">
                  编辑
                </el-button>
                <el-button type="danger" text @click="handleDelete(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.size"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            @size-change="loadSchedules"
            @current-change="loadSchedules"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>

        <el-tab-pane label="配置规则" name="rules">
          <el-form label-width="120px">
            <el-form-item label="班次类型">
              <el-select v-model="config.shiftType" placeholder="请选择班次类型">
                <el-option label="早班" value="morning" />
                <el-option label="中班" value="afternoon" />
                <el-option label="晚班" value="night" />
                <el-option label="三班倒" value="three-shift" />
              </el-select>
            </el-form-item>
            <el-form-item label="每班人数">
              <el-input-number v-model="config.shiftSize" :min="1" :max="100" />
            </el-form-item>
            <el-form-item label="休息日">
              <el-checkbox-group v-model="config.restDays">
                <el-checkbox v-for="day in weekDays" :key="day.value" :label="day.value">
                  {{ day.label }}
                </el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Add/Edit Dialog -->
    <el-dialog :title="editForm.id ? '编辑排班' : '新增排班'" v-model="dialogVisible" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="排班名称" required>
          <el-input v-model="editForm.name" placeholder="请输入排班名称" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="editForm.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="editForm.startDate" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="editForm.endDate" type="date" placeholder="选择日期" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Calendar, Plus, Download } from '@element-plus/icons-vue'

const activeTab = ref('list')
const loading = ref(false)
const schedules = ref([])
const pagination = ref({
  page: 1,
  size: 10,
  total: 0,
})
const dialogVisible = ref(false)
const config = ref({
  shiftType: 'three-shift',
  shiftSize: 5,
  restDays: [],
})
const editForm = ref({
  id: null,
  name: '',
  department: '',
  startDate: null,
  endDate: null,
})

const weekDays = [
  { label: '周一', value: 0 },
  { label: '周二', value: 1 },
  { label: '周三', value: 2 },
  { label: '周四', value: 3 },
  { label: '周五', value: 4 },
  { label: '周六', value: 5 },
  { label: '周日', value: 6 },
]

const loadSchedules = async () => {
  loading.value = true
  try {
    const response = await fetch(`/schedule/api/list?page=${pagination.value.page}&size=${pagination.value.size}`)
    const result = await response.json()
    if (result.success) {
      schedules.value = result.data
      pagination.value.total = result.total
    }
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  editForm.value = {
    id: null,
    name: '',
    department: '',
    startDate: null,
    endDate: null,
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  editForm.value = { ...row }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    const method = editForm.value.id ? 'PUT' : 'POST'
    const url = editForm.value.id ? `/schedule/api/${editForm.value.id}` : '/schedule/api/create'

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm.value),
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success(editForm.value.id ? '编辑成功' : '新增成功')
      dialogVisible.value = false
      loadSchedules()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个排班吗？', '提示', { type: 'warning' })
    const response = await fetch(`/schedule/api/${row.id}`, { method: 'DELETE' })
    const result = await response.json()
    if (result.success) {
      ElMessage.success('删除成功')
      loadSchedules()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleExport = () => {
  window.location.href = '/schedule/api/export'
}

const saveConfig = () => {
  ElMessage.success('配置已保存')
}

onMounted(() => {
  loadSchedules()
})
</script>

<style scoped>
.schedule-container {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.toolbar {
  margin-bottom: 20px;
}
</style>
