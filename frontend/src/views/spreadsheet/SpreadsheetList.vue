<template>
  <div class="spreadsheet-list-container">
    <el-card class="header-card">
      <div class="header-content">
        <div>
          <h1>📊 在线表格</h1>
          <p>创建和管理您的电子表格</p>
        </div>
        <el-button type="primary" size="large" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          创建新表格
        </el-button>
      </div>
    </el-card>

    <div v-if="loading" class="loading-container">
      <el-icon class="is-loading" :size="40"><Loading /></el-icon>
      <p>加载中...</p>
    </div>

    <el-row :gutter="20" v-else-if="spreadsheets.length > 0">
      <el-col
        v-for="sheet in spreadsheets"
        :key="sheet.id"
        :xs="24"
        :sm="12"
        :lg="8"
      >
        <el-card class="spreadsheet-card" shadow="hover" @click="openSpreadsheet(sheet.id)">
          <div class="card-content">
            <div class="sheet-name">
              <el-icon><Grid /></el-icon>
              <span>{{ sheet.name }}</span>
            </div>
            <div class="sheet-desc">{{ sheet.description || '暂无描述' }}</div>
            <div class="sheet-meta">
              <span>{{ sheet.row_count }} 行 × {{ sheet.col_count }} 列</span>
              <el-button text type="danger" @click.stop="deleteSpreadsheet(sheet.id)">
                删除
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-else description="还没有创建任何表格">
      <el-button type="primary" @click="handleCreate">创建第一个表格</el-button>
    </el-empty>

    <!-- Create Dialog -->
    <el-dialog v-model="createDialogVisible" title="创建新表格" width="500px">
      <el-form :model="createForm" ref="createFormRef">
        <el-form-item label="表格名称" required>
          <el-input v-model="createForm.name" placeholder="请输入表格名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入表格描述（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="submitCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Loading, Grid } from '@element-plus/icons-vue'

const router = useRouter()
const loading = ref(false)
const spreadsheets = ref([])
const createDialogVisible = ref(false)
const creating = ref(false)

const createForm = ref({
  name: '',
  description: '',
})
const createFormRef = ref(null)

const loadSpreadsheets = async () => {
  loading.value = true
  try {
    const response = await fetch('/spreadsheet/api/list')
    const result = await response.json()
    if (result.success) {
      spreadsheets.value = result.data
    }
  } catch (error) {
    console.error('加载失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  createForm.value.name = ''
  createForm.value.description = ''
  createDialogVisible.value = true
}

const submitCreate = async () => {
  if (!createForm.value.name) {
    ElMessage.error('请输入表格名称')
    return
  }

  creating.value = true
  try {
    const response = await fetch('/spreadsheet/api/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: createForm.value.name,
        description: createForm.value.description,
        columns: [
          { name: '序号', type: 'number', width: 80 },
          { name: '项目名称', type: 'text', width: 200 },
          { name: '负责人', type: 'text', width: 120 },
          { name: '状态', type: 'select', width: 100, options: ['待处理', '进行中', '已完成'] },
          { name: '优先级', type: 'select', width: 100, options: ['高', '中', '低'] },
          { name: '备注', type: 'text', width: 300 },
        ],
      }),
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('表格创建成功')
      createDialogVisible.value = false
      loadSpreadsheets()
    } else {
      ElMessage.error(result.message || '创建失败')
    }
  } catch (error) {
    console.error('创建错误:', error)
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const openSpreadsheet = (id) => {
  router.push(`/spreadsheet/${id}`)
}

const deleteSpreadsheet = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个表格吗？此操作不可恢复。', '提示', {
      type: 'warning',
    })

    const response = await fetch(`/spreadsheet/api/${id}`, {
      method: 'DELETE',
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('删除成功')
      loadSpreadsheets()
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除错误:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadSpreadsheets()
})
</script>

<style scoped>
.spreadsheet-list-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  margin-bottom: 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.header-content h1 {
  margin: 0;
  font-size: 32px;
}

.header-content p {
  margin: 10px 0 0;
  font-size: 16px;
  opacity: 0.9;
}

.loading-container {
  text-align: center;
  padding: 60px;
}

.spreadsheet-card {
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.spreadsheet-card:hover {
  transform: translateY(-5px);
}

.card-content {
  padding: 10px 0;
}

.sheet-name {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.sheet-name .el-icon {
  margin-right: 8px;
  color: #409eff;
}

.sheet-desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.sheet-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.sheet-meta span {
  font-size: 13px;
  color: #999;
}
</style>
