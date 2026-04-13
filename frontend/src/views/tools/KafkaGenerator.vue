<template>
  <div class="kafka-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#667eea"><Operation /></el-icon> Kafka 消息生成器</h2>
      <p class="subtitle">根据 ES 数据生成 Kafka 消息</p>
    </div>

    <!-- ES 源数据输入 -->
    <el-card class="input-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#409eff"><Document /></el-icon>
          <span>ES 源数据</span>
        </div>
      </template>

      <el-input
        v-model="esSourceData"
        type="textarea"
        :rows="10"
        placeholder="请输入 ES 查询结果的 JSON 数据"
      />

      <div class="button-group mt-3">
        <el-button type="primary" @click="generateMessage">
          <el-icon><Cpu /></el-icon>
          生成 Kafka 消息
        </el-button>
        <el-button type="info" @click="clearAllFields">
          <el-icon><Delete /></el-icon>
          清除所有字段
        </el-button>
      </div>
    </el-card>

    <!-- 自定义字段区域 -->
    <el-card class="fields-card" shadow="hover">
      <template #header>
        <div class="card-header-title justify-between">
          <div>
            <el-icon color="#67c23a"><Grid /></el-icon>
            <span>自定义字段</span>
          </div>
          <div>
            <el-button size="small" @click="showAllFields = !showAllFields">
              <el-icon><View /></el-icon>
              {{ showAllFields ? '隐藏空字段' : '显示所有字段' }}
            </el-button>
          </div>
        </div>
      </template>

      <div class="field-grid">
        <div 
          v-for="field in displayFields" 
          :key="field.name"
          class="field-item"
          :class="{ 'filled': fieldValues[field.name] }"
        >
          <div class="field-header">
            <label>{{ field.label }}</label>
            <div class="field-actions">
              <el-button 
                size="small" 
                :type="pinnedFields.has(field.name) ? 'warning' : 'info'"
                @click="toggleFieldPin(field.name)"
                title="置顶/取消置顶"
              >
                <el-icon><Top /></el-icon>
              </el-button>
              <el-button 
                size="small" 
                type="danger"
                @click="openFieldDict(field.name)"
                title="查看字段字典"
              >
                <el-icon><Notebook /></el-icon>
              </el-button>
            </div>
          </div>
          
          <el-input
            :id="`field_${field.name}`"
            v-model="fieldValues[field.name]"
            :placeholder="field.placeholder || '请输入'"
            size="small"
            @change="onFieldChange(field.name, fieldValues[field.name])"
          >
            <template #append>
              <el-select 
                v-if="historyValues[field.name] && historyValues[field.name].length > 0"
                v-model="fieldValues[field.name]"
                placeholder="历史值"
                size="small"
                style="width: 120px"
                @change="onFieldChange(field.name, fieldValues[field.name])"
              >
                <el-option
                  v-for="val in historyValues[field.name]"
                  :key="val"
                  :label="val"
                  :value="val"
                >
                  <span style="float: left">{{ val }}</span>
                  <el-button
                    size="small"
                    type="danger"
                    link
                    @click.stop="deleteHistoryValue(field.name, val)"
                    style="float: right; margin-right: 10px"
                  >
                    <el-icon><Close /></el-icon>
                  </el-button>
                </el-option>
              </el-select>
            </template>
          </el-input>
          
          <div v-if="field.esField" class="field-meta">
            ES字段: <span class="es-field" :title="field.esField">{{ field.esField }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 生成结果 -->
    <el-card v-if="resultData" class="result-card" shadow="hover">
      <template #header>
        <div class="card-header-title justify-between">
          <div>
            <el-icon color="#f56c6c"><CircleCheck /></el-icon>
            <span>生成结果</span>
          </div>
          <div class="result-actions">
            <!-- 事件时间设置 -->
            <div class="event-time-control">
              <el-input
                v-model="eventTime"
                placeholder="事件时间"
                size="small"
                style="width: 200px; margin-right: 10px"
              >
                <template #prepend>事件时间</template>
              </el-input>
              <el-button 
                size="small" 
                type="primary"
                @click="subtractEventTime(15)"
              >
                -15分钟
              </el-button>
            </div>
            
            <el-input-number
              v-model="delayTime"
              :min="0"
              :max="1440"
              size="small"
              style="width: 120px; margin-right: 10px"
            >
              <template #prepend>延迟(分钟)</template>
            </el-input-number>
            <el-checkbox v-model="addTestPrefix">添加【测试】前缀</el-checkbox>
          </div>
        </div>
      </template>

      <el-input
        v-model="resultJson"
        type="textarea"
        :rows="15"
        readonly
        class="result-textarea"
      />

      <div class="button-group mt-3">
        <el-button type="success" @click="copyResult">
          <el-icon><CopyDocument /></el-icon>
          复制结果
        </el-button>
        <el-button type="primary" @click="copyFPValue">
          <el-icon><CopyDocument /></el-icon>
          复制 FP 值
        </el-button>
        <el-button type="warning" @click="regenerateMessage">
          <el-icon><Refresh /></el-icon>
          重新生成
        </el-button>
      </div>

      <!-- ES 查询区域 -->
      <div v-if="esQuery" class="es-query-section mt-3">
        <el-divider>ES 查询语句</el-divider>
        <el-input
          v-model="esQuery"
          type="textarea"
          :rows="8"
          readonly
        />
        <el-button type="info" class="mt-2" @click="copyEsQuery">
          <el-icon><CopyDocument /></el-icon>
          复制 ES 查询
        </el-button>
      </div>
    </el-card>

    <!-- 字段字典弹窗 -->
    <el-dialog
      v-model="dictDialogVisible"
      title="字段字典"
      width="80%"
      :close-on-click-modal="false"
    >
      <el-table
        :data="dictData"
        border
        stripe
        max-height="500"
        @row-click="selectDictValue"
      >
        <el-table-column prop="field_name" label="字段名" width="150" />
        <el-table-column prop="field_value" label="字段值" min-width="200" />
        <el-table-column prop="description" label="说明" min-width="250" />
        <el-table-column prop="source" label="来源" width="120" />
      </el-table>

      <template #footer>
        <el-button @click="dictDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Operation,
  Document,
  Cpu,
  Delete,
  Grid,
  View,
  Top,
  Notebook,
  Close,
  CircleCheck,
  CopyDocument,
  Refresh,
} from '@element-plus/icons-vue'

// ES 源数据
const esSourceData = ref('')

// 字段配置
const allFields = ref([
  { name: 'EQP_LABEL', label: '设备标签', esField: 'eqp_label', placeholder: '请输入设备标签' },
  { name: 'NE_LABEL', label: '网元标签', esField: 'ne_label', placeholder: '请输入网元标签' },
  { name: 'ALARM_TITLE', label: '告警标题', esField: 'alarm_title', placeholder: '请输入告警标题' },
  { name: 'SEVERITY', label: '严重程度', esField: 'severity', placeholder: '请输入严重程度' },
  { name: 'FP0_FP1_FP2_FP3', label: 'FP值', esField: 'fp', placeholder: '请输入FP值' },
  { name: 'CREATION_EVENT_TIME', label: '创建时间', esField: 'creation_time', placeholder: '请输入创建时间' },
  { name: 'EVENT_TYPE', label: '事件类型', esField: 'event_type', placeholder: '请输入事件类型' },
  { name: 'RESOURCE_TYPE', label: '资源类型', esField: 'resource_type', placeholder: '请输入资源类型' },
])

// 字段值缓存
const fieldValues = reactive({})

// 置顶字段集合
const pinnedFields = ref(new Set())

// 历史值缓存
const historyValues = ref({})

// 显示所有字段
const showAllFields = ref(true)

// 显示字段(置顶的优先,且可选择是否显示空字段)
const displayFields = computed(() => {
  let fields = [...allFields.value]
  
  // 置顶字段排前面
  fields.sort((a, b) => {
    const aPinned = pinnedFields.value.has(a.name) ? 0 : 1
    const bPinned = pinnedFields.value.has(b.name) ? 0 : 1
    return aPinned - bPinned
  })
  
  // 如果不显示所有字段,过滤掉空值且未置顶的字段
  if (!showAllFields.value) {
    fields = fields.filter(f => {
      return pinnedFields.value.has(f.name) || fieldValues[f.name]
    })
  }
  
  return fields
})

// 生成结果
const resultData = ref(null)
const resultJson = ref('')
const eventTime = ref('')  // 事件时间
const delayTime = ref(15)
const addTestPrefix = ref(false)
const esQuery = ref('')

// 字典弹窗
const dictDialogVisible = ref(false)
const dictData = ref([])
const currentDictField = ref('')

// 字段值改变
const onFieldChange = async (field, value) => {
  if (value && value.trim()) {
    await saveHistoryToDB(field, value)
  }
}

// 保存历史值到数据库
const saveHistoryToDB = async (field, value) => {
  try {
    const response = await fetch('/kafka-generator/field-history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_name: field,
        field_value: value,
      }),
    })
    const result = await response.json()
    
    if (result.success) {
      // 更新本地缓存
      if (!historyValues.value[field]) {
        historyValues.value[field] = []
      }
      // 去重并置顶
      historyValues.value[field] = historyValues.value[field].filter(v => v !== value)
      historyValues.value[field].unshift(value)
      // 限制数量
      historyValues.value[field] = historyValues.value[field].slice(0, 20)
    }
  } catch (error) {
    console.warn('保存历史值失败:', error)
  }
}

// 删除历史值
const deleteHistoryValue = async (field, value) => {
  try {
    await ElMessageBox.confirm(`确定要删除历史值 "${value}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch('/kafka-generator/field-history', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_name: field,
        value: value,
      }),
    })
    const result = await response.json()
    
    if (result.success) {
      // 更新本地缓存
      if (historyValues.value[field]) {
        historyValues.value[field] = historyValues.value[field].filter(v => v !== value)
      }
      ElMessage.success('已删除')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.warn('删除历史值失败:', error)
    }
  }
}

// 切换字段置顶
const toggleFieldPin = async (field) => {
  if (pinnedFields.value.has(field)) {
    pinnedFields.value.delete(field)
  } else {
    pinnedFields.value.add(field)
  }
  
  // 保存到数据库
  await saveFieldValue(field, fieldValues[field] || '')
}

// 保存字段值
const saveFieldValue = async (field, value) => {
  try {
    const isPinned = pinnedFields.value.has(field)
    const response = await fetch('/kafka-generator/field-cache', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_name: field,
        field_value: value,
        is_pinned: isPinned,
      }),
    })
    const result = await response.json()
    
    if (result.success) {
      console.log(`字段 ${field} 已保存`)
    }
  } catch (error) {
    console.warn('保存字段失败:', error)
  }
}

// 打开字段字典
const openFieldDict = async (field) => {
  currentDictField.value = field
  dictDialogVisible.value = true
  
  try {
    const response = await fetch(`/kafka-generator/field-dict?field=${field}`)
    const result = await response.json()
    
    if (result.success) {
      dictData.value = result.data || []
    } else {
      ElMessage.error(result.message || '加载字典失败')
    }
  } catch (error) {
    console.error('加载字典错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 选择字典值
const selectDictValue = (row) => {
  if (currentDictField.value) {
    fieldValues[currentDictField.value] = row.field_value
    onFieldChange(currentDictField.value, row.field_value)
    dictDialogVisible.value = false
    ElMessage.success('已填充字段值')
  }
}

// 生成消息
const generateMessage = async () => {
  if (!esSourceData.value.trim()) {
    ElMessage.warning('请输入 ES 源数据')
    return
  }

  try {
    // 收集自定义字段
    const customFields = {}
    allFields.value.forEach(field => {
      if (fieldValues[field.name]) {
        customFields[field.name] = fieldValues[field.name]
      }
    })

    const response = await fetch('/kafka-generator/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        es_source_raw: esSourceData.value,
        custom_fields: customFields,
        delay_time: delayTime.value,
        add_test_prefix: addTestPrefix.value,
      }),
    })
    
    const result = await response.json()

    if (result.success) {
      resultData.value = result.data
      
      // 处理测试前缀
      if (addTestPrefix.value) {
        if (resultData.value.EQP_LABEL) {
          resultData.value.EQP_LABEL = '【测试】' + resultData.value.EQP_LABEL
        }
        if (resultData.value.NE_LABEL) {
          resultData.value.NE_LABEL = '【测试】' + resultData.value.NE_LABEL
        }
      }
      
      resultJson.value = JSON.stringify(resultData.value, null, 2)
      delayTime.value = result.delay_time || 15
      esQuery.value = result.es_query || ''
      
      ElMessage.success('Kafka 消息生成成功')
    } else {
      ElMessage.error(result.message || '生成失败')
    }
  } catch (error) {
    console.error('生成错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 重新生成
const regenerateMessage = () => {
  generateMessage()
}

// 复制结果
const copyResult = async () => {
  if (!resultJson.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }

  try {
    await navigator.clipboard.writeText(resultJson.value)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 复制 FP 值
const copyFPValue = async () => {
  if (!resultData.value) {
    ElMessage.warning('请先生成 Kafka 消息')
    return
  }

  const fpValue = resultData.value.FP0_FP1_FP2_FP3
  if (!fpValue) {
    ElMessage.warning('结果中没有找到 FP 值')
    return
  }

  try {
    await navigator.clipboard.writeText(fpValue)
    ElMessage.success('FP 值已复制')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 复制 ES 查询
const copyEsQuery = async () => {
  if (!esQuery.value) {
    ElMessage.warning('没有 ES 查询语句')
    return
  }

  try {
    await navigator.clipboard.writeText(esQuery.value)
    ElMessage.success('ES 查询已复制')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 事件时间减指定分钟数
const subtractEventTime = (minutes) => {
  if (!eventTime.value) {
    ElMessage.warning('请先输入事件时间')
    return
  }

  try {
    // 解析时间字符串
    let date = new Date(eventTime.value)
    
    // 如果解析失败，尝试其他格式
    if (isNaN(date.getTime())) {
      // 尝试 YYYY-MM-DD HH:mm:ss 格式
      const parts = eventTime.value.split(/[- :]/)
      if (parts.length >= 6) {
        date = new Date(
          parseInt(parts[0]),
          parseInt(parts[1]) - 1,
          parseInt(parts[2]),
          parseInt(parts[3]),
          parseInt(parts[4]),
          parseInt(parts[5])
        )
      } else {
        ElMessage.error('时间格式不正确，请使用 YYYY-MM-DD HH:mm:ss 格式')
        return
      }
    }
    
    // 减去指定分钟数
    date.setMinutes(date.getMinutes() - minutes)
    
    // 格式化为 YYYY-MM-DD HH:mm:ss
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const mins = String(date.getMinutes()).padStart(2, '0')
    const secs = String(date.getSeconds()).padStart(2, '0')
    
    eventTime.value = `${year}-${month}-${day} ${hours}:${mins}:${secs}`
    
    ElMessage.success(`事件时间已减${minutes}分钟`)
  } catch (error) {
    console.error('时间计算错误:', error)
    ElMessage.error('时间格式错误，请检查输入')
  }
}

// 清除所有字段
const clearAllFields = async () => {
  try {
    await ElMessageBox.confirm('确定要清除所有已填写的字段值吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // 清空字段值
    Object.keys(fieldValues).forEach(key => {
      fieldValues[key] = ''
    })
    
    // 批量清除数据库记录
    const pinnedFieldsArray = Array.from(pinnedFields.value)
    await fetch('/kafka-generator/field-cache/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        field_cache: {},
        pinned_fields: pinnedFieldsArray,
      }),
    })
    
    ElMessage.success('已清除所有字段')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清除失败:', error)
    }
  }
}

// 从数据库加载缓存
const loadFieldCache = async () => {
  try {
    const response = await fetch('/kafka-generator/field-cache')
    const result = await response.json()
    
    if (result.success && result.data) {
      // 加载字段值
      Object.assign(fieldValues, result.data.field_cache || {})
      // 加载置顶字段
      pinnedFields.value = new Set(result.data.pinned_fields || [])
      // 加载历史值
      historyValues.value = result.data.history_values || {}
      
      console.log('已加载字段缓存')
    }
  } catch (error) {
    console.warn('加载缓存失败:', error)
  }
}

// 初始化
onMounted(() => {
  loadFieldCache()
})
</script>

<style scoped>
.kafka-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: #333;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.input-card,
.fields-card,
.result-card {
  margin-bottom: 25px;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.input-card:hover,
.fields-card:hover,
.result-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.card-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.justify-between {
  justify-content: space-between;
}

.button-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.mt-3 {
  margin-top: 15px;
}

.mt-2 {
  margin-top: 10px;
}

/* 字段网格 */
.field-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.field-item {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 15px;
  border-radius: 10px;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.field-item.filled {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border-color: #67c23a;
}

.field-item:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.field-header label {
  font-weight: 600;
  font-size: 14px;
  color: #495057;
}

.field-actions {
  display: flex;
  gap: 5px;
}

.field-meta {
  font-size: 12px;
  color: #6c757d;
  margin-top: 8px;
  font-style: italic;
}

.es-field {
  color: #667eea;
  cursor: help;
  text-decoration: underline dotted;
  font-weight: 500;
}

.result-textarea {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.event-time-control {
  display: flex;
  align-items: center;
}

.es-query-section {
  margin-top: 20px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
