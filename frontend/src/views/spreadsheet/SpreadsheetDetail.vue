<template>
  <div class="spreadsheet-detail-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
          <span class="title">{{ spreadsheet?.name }}</span>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      </div>

      <div v-else-if="spreadsheet" class="spreadsheet-content">
        <div class="toolbar">
          <el-button type="primary" @click="addRow">
            <el-icon><Plus /></el-icon>
            添加行
          </el-button>
          <el-button type="success" @click="saveData">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
        </div>

        <div class="table-container">
          <el-table :data="tableData" border style="width: 100%;">
            <el-table-column
              v-for="col in columns"
              :key="col.name"
              :prop="col.name"
              :label="col.name"
              :width="col.width"
              align="center"
            >
              <template #default="{ row }">
                <el-input
                  v-if="col.type === 'text'"
                  v-model="row[col.name]"
                  :placeholder="col.name"
                />
                <el-input-number
                  v-else-if="col.type === 'number'"
                  v-model="row[col.name]"
                  :placeholder="col.name"
                />
                <el-select
                  v-else-if="col.type === 'select'"
                  v-model="row[col.name]"
                  :placeholder="col.name"
                >
                  <el-option
                    v-for="opt in col.options"
                    :key="opt"
                    :label="opt"
                    :value="opt"
                  />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" width="80">
              <template #default="{ $index }">
                <el-button type="danger" text @click="deleteRow($index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Loading, Plus, Check } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const spreadsheet = ref(null)
const tableData = ref([])
const columns = ref([])

const loadSpreadsheet = async () => {
  loading.value = true
  try {
    const response = await fetch(`/spreadsheet/api/${route.params.id}`)
    const result = await response.json()
    if (result.success) {
      spreadsheet.value = result.data
      columns.value = result.data.columns || []
      tableData.value = result.data.rows || []
    } else {
      ElMessage.error(result.message || '加载失败')
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const addRow = () => {
  const newRow = {}
  columns.value.forEach((col) => {
    if (col.type === 'number') {
      newRow[col.name] = 0
    } else if (col.type === 'select' && col.options && col.options.length > 0) {
      newRow[col.name] = col.options[0]
    } else {
      newRow[col.name] = ''
    }
  })
  tableData.value.push(newRow)
}

const deleteRow = (index) => {
  tableData.value.splice(index, 1)
}

const saveData = async () => {
  try {
    const response = await fetch(`/spreadsheet/api/${route.params.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        rows: tableData.value,
      }),
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存错误:', error)
    ElMessage.error('保存失败')
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadSpreadsheet()
})
</script>

<style scoped>
.spreadsheet-detail-container {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: 600;
}

.loading-container {
  text-align: center;
  padding: 60px;
}

.toolbar {
  margin-bottom: 20px;
}

.table-container {
  overflow-x: auto;
}
</style>
