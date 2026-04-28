<template>
  <div class="kafka-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div>
          <h2><el-icon :size="28" color="#667eea"><Operation /></el-icon> Kafka 消息生成器</h2>
          <p class="subtitle">根据 ES 数据生成 Kafka 消息</p>
        </div>
        <el-button type="primary" @click="goToFieldMetaManager">
          <el-icon><Setting /></el-icon>
          字段映射管理
        </el-button>
      </div>
    </div>

    <!-- ES 源数据输入 -->
    <el-card class="input-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#409eff"><Document /></el-icon>
          <span>ES 源数据</span>
        </div>
      </template>

      <div class="es-input-wrapper">
        <el-input
          v-model="esSourceData"
          type="textarea"
          :rows="10"
          placeholder="请输入 ES 查询结果的 JSON 数据"
        />
        <div class="es-input-buttons">
          <el-button 
            type="primary" 
            @click="showEsSourceHistory()"
            class="es-history-btn"
            title="查看历史数据"
          >
            <el-icon><Clock /></el-icon>
            历史数据
          </el-button>
          <el-button 
            type="warning" 
            @click="forceFormatJson()"
            class="format-btn"
            title="将 Python 三引号字符串转换为标准 JSON 格式"
          >
            <el-icon><MagicStick /></el-icon>
            强制格式化
          </el-button>
        </div>
      </div>

      <div class="button-group mt-3">
        <el-button type="primary" @click="generateMessage">
          <el-icon><Cpu /></el-icon>
          生成 Kafka 消息
        </el-button>
        <el-button type="info" @click="loadSampleData">
          <el-icon><Upload /></el-icon>
          加载示例数据
        </el-button>
        <el-button type="danger" @click="clearAllFields">
          <el-icon><Delete /></el-icon>
          清除所有字段
        </el-button>
        <!-- 【测试】前缀开关（与下方结果区域同步） -->
        <el-switch
          v-model="addTestPrefix"
          active-text="【测试】前缀"
          inline-prompt
          style="margin-left: 12px;"
          @change="handleTestPrefixChange"
        />
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
            <el-button size="small" @click="toggleAllFields">
              <el-icon><View /></el-icon>
              {{ showAllFields ? '隐藏所有字段' : '显示所有字段' }}
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
            <label>{{ field.name }}（{{ field.label }}）:</label>
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
                v-if="DICT_FIELDS.has(field.name)"
                size="small" 
                type="danger"
                @click="openFieldDict(field.name)"
                title="查看字段字典"
              >
                <el-icon><Notebook /></el-icon>
              </el-button>
              <el-button 
                size="small" 
                type="primary"
                @click="openHistoryModal(field.name)"
                title="查看历史记录"
              >
                <el-icon><Clock /></el-icon>
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
            <!-- 【测试】前缀开关 -->
            <el-switch
              v-model="addTestPrefix"
              active-text="【测试】前缀"
              inline-prompt
              @change="handleTestPrefixChange"
            />
            
            <!-- 延迟时间设置 -->
            <span class="delay-label">延迟时间</span>
            <el-input-number
              v-model="delayTime"
              :min="0"
              :max="1440"
              size="small"
              style="width: 120px; margin-left: 8px"
            >
              <template #append>分钟</template>
            </el-input-number>
          </div>
        </div>
      </template>

      <el-input
        v-model="resultJson"
        type="textarea"
        :rows="15"
        readonly
        class="result-textarea"
        :class="{ 'time-adjusted': timeFieldsAdjusted }"
      />

      <div class="button-group mt-3">
        <div class="left-buttons">
          <el-button type="success" @click="copyResult">
            <el-icon><CopyDocument /></el-icon>
            复制结果
          </el-button>
          <el-button type="primary" @click="copyFPValue">
            <el-icon><CopyDocument /></el-icon>
            复制 FP 值
          </el-button>
          <el-button type="warning" @click="generatePushMessage">
            <el-icon><ChatDotRound /></el-icon>
            生成推送消息
          </el-button>
          <el-button type="primary" @click="openRemarkDialog">
            <el-icon><Edit /></el-icon>
            添加备注
          </el-button>
        </div>
        <el-button type="danger" @click="regenerateMessage">
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

    <!-- 备注编辑弹窗 -->
    <el-dialog
      v-model="remarkDialogVisible"
      title="添加备注"
      width="50%"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item label="备注内容">
          <el-input
            v-model="remarkContent"
            type="textarea"
            :rows="4"
            placeholder="请输入备注信息..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="remarkDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRemarkFromResult" :loading="savingRemark">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 推送消息弹窗 -->
    <el-dialog
      v-model="pushMessageDialogVisible"
      title="推送消息"
      width="60%"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item label="FP值">
          <el-input v-model="pushMessageFp" />
        </el-form-item>
        
        <el-form-item label="事件时间">
          <el-input v-model="pushMessageEventTime" placeholder="请输入事件时间 (YYYY-MM-DD HH:mm:ss)">
            <template #append>
              <el-button @click="subtractPushMessageEventTime(15)">-15分钟</el-button>
              <el-button @click="subtractPushMessageEventYear(1)" type="warning">-1年</el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="激活状态">
          <el-input v-model="pushMessageActiveStatus" />
        </el-form-item>
        
        <el-divider>推送消息 JSON</el-divider>
        
        <el-input
          v-model="pushMessageJson"
          type="textarea"
          :rows="8"
          readonly
          class="result-textarea"
        />
      </el-form>

      <template #footer>
        <el-button type="primary" @click="updatePushMessageJson">
          <el-icon><Refresh /></el-icon>
          生成
        </el-button>
        <el-button type="success" @click="copyPushMessage">
          <el-icon><CopyDocument /></el-icon>
          复制推送消息
        </el-button>
        <el-button @click="pushMessageDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- ES 源数据历史记录弹窗 -->
    <el-dialog
      v-model="esSourceHistoryDialogVisible"
      :title="esHistoryDialogTitle"
      width="95%"
      :close-on-click-modal="false"
    >
      <div class="mb-3">
        <el-input
          v-model="esSourceHistoryKeyword"
          placeholder="搜索 FP 值、备注、生成时间..."
          clearable
          @keyup.enter="searchEsSourceHistory"
          @blur="esSourceHistoryKeyword = esSourceHistoryKeyword?.trim()"
          style="width: 400px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="searchEsSourceHistory">搜索</el-button>
          </template>
        </el-input>
      </div>

      <el-alert
        :title="`共 ${esSourceHistoryTotal} 条记录`"
        type="info"
        :closable="false"
        class="mb-3"
      />

      <el-table
        :data="esSourceHistoryData"
        border
        stripe
        max-height="500"
      >
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="useEsSourceHistory(row)"
              title="使用此记录"
            >
              <el-icon><Check /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="180" />
        <el-table-column prop="fp_value" label="FP 值" width="250" show-overflow-tooltip />
        <el-table-column label="备注" min-width="200">
          <template #default="{ row }">
            <div class="remark-cell">
              <div v-if="editingRemarkId === row.id" class="remark-edit-mode">
                <el-input
                  v-model="editingRemarkValue"
                  size="small"
                  placeholder="输入备注..."
                  clearable
                  @keyup.enter="saveRemark(row.id)"
                  @keyup.esc="cancelEditRemark()"
                />
                <div class="remark-actions">
                  <el-button size="small" type="primary" @click="saveRemark(row.id)">
                    <el-icon><Check /></el-icon>
                    确认
                  </el-button>
                  <el-button size="small" @click="cancelEditRemark()">
                    <el-icon><Close /></el-icon>
                    取消
                  </el-button>
                </div>
              </div>
              <div v-else class="remark-view-mode">
                <span class="remark-text" :title="row.remark || '点击编辑备注'">
                  {{ row.remark || '点击添加备注' }}
                </span>
                <el-button
                  v-if="row.remark"
                  size="small"
                  type="primary"
                  link
                  @click="showContentDialog('备注', row.remark)"
                  class="view-btn"
                  title="查看完整备注"
                >
                  <el-icon><View /></el-icon>
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  link
                  @click="startEditRemark(row)"
                  class="edit-btn"
                  title="修改备注"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 如果筛选了特定字段，显示该字段的值 -->
        <el-table-column 
          v-if="esHistoryFilterField" 
          :label="`${esHistoryFilterField} 字段值`" 
          min-width="150"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <!-- 先从 kafka_message 中查找，再从 custom_fields 中查找 -->
            <template v-if="row.kafka_message">
              {{ getFieldValueFromJson(row.kafka_message, esHistoryFilterField) || '-' }}
            </template>
            <template v-else-if="row.custom_fields">
              {{ getFieldValueFromJson(row.custom_fields, esHistoryFilterField) || '-' }}
            </template>
            <span v-else>-</span>
          </template>
        </el-table-column>
        
        <!-- 如果没有筛选字段，显示原来的列 -->
        <template v-else>
          <el-table-column label="ES 源数据" min-width="150" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                @click="showContentDialog('ES 源数据', formatJsonString(row.es_source_raw))"
              >
                <el-icon><View /></el-icon>
                查看内容
              </el-button>
            </template>
          </el-table-column>
          <el-table-column label="Kafka 消息" min-width="150" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                @click="showContentDialog('Kafka 消息', formatJsonString(row.kafka_message))"
              >
                <el-icon><View /></el-icon>
                查看内容
              </el-button>
            </template>
          </el-table-column>
        </template>
      </el-table>

      <div v-if="!esSourceHistoryData.length && esSourceHistoryTotal === 0" class="text-center py-5 text-muted">
        <el-empty description="暂无历史记录" />
      </div>

      <template #footer>
        <el-pagination
          v-if="esSourceHistoryTotal > 0"
          v-model:current-page="esSourceHistoryPage"
          :page-size="esSourceHistoryPageSize"
          :total="esSourceHistoryTotal"
          layout="prev, pager, next"
          @current-change="changeEsSourceHistoryPage"
        />
        <el-button @click="esSourceHistoryDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 历史记录弹窗 -->
    <el-dialog
      v-model="historyDialogVisible"
      :title="historyDialogTitle"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="mb-3">
        <el-input
          v-model="historyKeyword"
          placeholder="搜索 FP 值、生成时间..."
          clearable
          @keyup.enter="searchHistory"
          style="width: 400px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="searchHistory">搜索</el-button>
          </template>
        </el-input>
      </div>

      <el-alert
        :title="`共 ${historyTotal} 条记录`"
        type="info"
        :closable="false"
        class="mb-3"
      />

      <el-table
        :data="historyData"
        border
        stripe
        max-height="500"
        v-loading="!historyData.length && historyTotal === 0"
      >
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button
              size="small"
              type="primary"
              @click="useHistoryRecord(row)"
              title="使用此记录"
            >
              <el-icon><Check /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="生成时间" width="180" />
        <el-table-column prop="fp_value" label="FP 值" width="250" show-overflow-tooltip />
        <el-table-column 
          :label="`${currentHistoryField || '字段'} 值`" 
          min-width="200" 
          show-overflow-tooltip
        >
          <template #default="{ row }">
            {{ getFieldValueFromJson(row.kafka_message, currentHistoryField) || '-' }}
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!historyData.length && historyTotal === 0" class="text-center py-5 text-muted">
        <el-empty description="暂无历史记录" />
      </div>

      <template #footer>
        <el-pagination
          v-if="historyTotal > 0"
          v-model:current-page="historyCurrentPage"
          :page-size="historyPageSize"
          :total="historyTotal"
          layout="prev, pager, next"
          @current-change="changeHistoryPage"
        />
        <el-button @click="historyDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 内容查看弹窗 -->
    <el-dialog
      v-model="contentDialogVisible"
      :title="contentDialogTitle"
      width="70%"
      :close-on-click-modal="false"
    >
      <div class="content-viewer">
        <div class="content-header">
          <el-button
            type="primary"
            size="small"
            @click="copyText(contentData, contentDialogTitle)"
          >
            <el-icon><CopyDocument /></el-icon>
            复制内容
          </el-button>
        </div>
        <el-input
          v-model="contentData"
          type="textarea"
          :rows="20"
          readonly
          class="content-textarea"
        />
      </div>
      <template #footer>
        <el-button @click="contentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
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
  ChatDotRound,
  Clock,
  Search,
  Check,
  Upload,
  MagicStick,
  Edit,
  Setting,
} from '@element-plus/icons-vue'

// ES 源数据
const esSourceData = ref('')

// 有字典的字段列表（与后端 FIELD_DICT_TABLES 保持一致）
const DICT_FIELDS = new Set([
  'ALARM_RESOURCE_STATUS',
  'BUSINESS_LAYER',
  'CIRCUIT_LEVEL',
  'EFFECT_NE',
  'EFFECT_SERVICE',
  'EQP_OBJECT_CLASS',
  'EXTRA_ID2',
  'LOGIC_ALARM_TYPE',
  'NE_ADMIN_STATUS',
  'NETWORK_TYPE',
  'NETWORK_TYPE_TOP',
  'ORG_SEVERITY',
  'ORG_TYPE',
  'PORT_NUM',
  'SUB_ALARM_TYPE',
])

// 字段配置（从后端动态加载）
const allFields = ref([])

// 从后端加载字段配置
const loadFieldMeta = async () => {
  try {
    // 获取字段元数据（label_cn, es_field, db_cn）
    const metaResponse = await fetch('/kafka-generator/field-meta')
    const metaResult = await metaResponse.json()
    const fieldMeta = metaResult.success ? metaResult.data : {}

    // 获取字段顺序
    const orderResponse = await fetch('/kafka-generator/field-order')
    const orderResult = await orderResponse.json()
    const fieldOrder = orderResult.success ? orderResult.data.fields : []

    // 构建完整的字段配置
    if (fieldOrder.length > 0) {
      allFields.value = fieldOrder.map(fieldName => {
        const meta = fieldMeta[fieldName] || {}
        return {
          name: fieldName,
          label: meta.db_cn || meta.label_cn || fieldName,
          esField: meta.es_field || '',
          placeholder: `请输入${meta.db_cn || meta.label_cn || fieldName}`,
        }
      })
    } else {
      // 回退到默认配置
      allFields.value = [
        { name: 'EQP_LABEL', label: '设备标签', esField: 'eqp_label', placeholder: '请输入设备标签' },
        { name: 'NE_LABEL', label: '网元标签', esField: 'ne_label', placeholder: '请输入网元标签' },
        { name: 'ALARM_TITLE', label: '告警标题', esField: 'alarm_title', placeholder: '请输入告警标题' },
        { name: 'SEVERITY', label: '严重程度', esField: 'severity', placeholder: '请输入严重程度' },
        { name: 'FP0_FP1_FP2_FP3', label: 'FP值', esField: 'fp', placeholder: '请输入FP值' },
        { name: 'CREATION_EVENT_TIME', label: '创建时间', esField: 'creation_time', placeholder: '请输入创建时间' },
        { name: 'EVENT_TYPE', label: '事件类型', esField: 'event_type', placeholder: '请输入事件类型' },
        { name: 'RESOURCE_TYPE', label: '资源类型', esField: 'resource_type', placeholder: '请输入资源类型' },
      ]
    }
  } catch (error) {
    console.error('加载字段配置失败:', error)
    // 回退到默认配置
    allFields.value = [
      { name: 'EQP_LABEL', label: '设备标签', esField: 'eqp_label', placeholder: '请输入设备标签' },
      { name: 'NE_LABEL', label: '网元标签', esField: 'ne_label', placeholder: '请输入网元标签' },
      { name: 'ALARM_TITLE', label: '告警标题', esField: 'alarm_title', placeholder: '请输入告警标题' },
      { name: 'SEVERITY', label: '严重程度', esField: 'severity', placeholder: '请输入严重程度' },
      { name: 'FP0_FP1_FP2_FP3', label: 'FP值', esField: 'fp', placeholder: '请输入FP值' },
      { name: 'CREATION_EVENT_TIME', label: '创建时间', esField: 'creation_time', placeholder: '请输入创建时间' },
      { name: 'EVENT_TYPE', label: '事件类型', esField: 'event_type', placeholder: '请输入事件类型' },
      { name: 'RESOURCE_TYPE', label: '资源类型', esField: 'resource_type', placeholder: '请输入资源类型' },
    ]
  }
}

// 字段值缓存
const fieldValues = reactive({})

// 置顶字段集合
const pinnedFields = ref(new Set())

// 历史值缓存
const historyValues = ref({})

// 显示所有字段
const showAllFields = ref(false)  // 默认只显示常用字段

// 切换显示/隐藏所有字段
const toggleAllFields = () => {
  showAllFields.value = !showAllFields.value
}

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
const addTestPrefix = ref(true)
const esQuery = ref('')
const timeFieldsAdjusted = ref(false)  // 标记时间字段是否已调整

// 监听 NETWORK_TYPE_TOP 字段值变化
watch(
  () => fieldValues.NETWORK_TYPE_TOP,
  (newVal) => {
    console.log('NETWORK_TYPE_TOP 变化:', newVal, '类型:', typeof newVal)
    if (newVal === '20' || newVal === 20) {
      if (addTestPrefix.value) {
        ElMessage.warning({
          message: '提示：因为当前是虚拟化的一级专业 ID（NETWORK_TYPE_TOP=20），网元名称（EQP_LABEL）不能添加【测试】前缀。已自动关闭。',
          duration: 6000,
        })
        addTestPrefix.value = false
      }
    }
  }
)

// 处理【测试】前缀开关变化
const handleTestPrefixChange = (value) => {
  // 如果用户尝试打开开关
  if (value) {
    const networkTypeTop = fieldValues.NETWORK_TYPE_TOP
    console.log('handleTestPrefixChange - NETWORK_TYPE_TOP:', networkTypeTop)
    
    if (networkTypeTop === '20' || networkTypeTop === 20) {
      ElMessage.warning({
        message: '提示：因为当前是虚拟化的一级专业 ID（NETWORK_TYPE_TOP=20），网元名称（EQP_LABEL）不能添加【测试】前缀。',
        duration: 6000,
      })
      // 关闭开关
      addTestPrefix.value = false
    }
  }
}

// 字典弹窗
const dictDialogVisible = ref(false)
const dictData = ref([])
const currentDictField = ref('')

// 推送消息弹窗
const pushMessageDialogVisible = ref(false)
const pushMessageFp = ref('')
const pushMessageFpEditable = ref(false)
const pushMessageEventTime = ref('')
const pushMessageActiveStatus = ref('3')
const pushMessageActiveStatusEditable = ref(false)
const pushMessageJson = ref('')

// 历史记录弹窗
const historyDialogVisible = ref(false)
const historyData = ref([])
const historyTotal = ref(0)
const historyCurrentPage = ref(1)
const historyPageSize = 20
const historyKeyword = ref('')
const currentHistoryField = ref('')
const currentHistoryRequest = ref(0)  // 追踪当前最新的历史记录请求ID

// ES 源数据历史记录弹窗
const esSourceHistoryDialogVisible = ref(false)
const esSourceHistoryData = ref([])
const esSourceHistoryTotal = ref(0)
const esSourceHistoryPage = ref(1)
const esSourceHistoryPageSize = 10
const esSourceHistoryKeyword = ref('')
const currentEsHistoryRequest = ref(0)  // 追踪当前最新的 ES 历史记录请求ID

// 备注编辑相关
const editingRemarkId = ref(null)
const editingRemarkValue = ref('')

// 备注弹窗相关
const remarkDialogVisible = ref(false)
const remarkContent = ref('')
const savingRemark = ref(false)
const lastGeneratedHistoryId = ref(null)  // 保存最近一次生成的历史记录ID

// 内容查看弹窗相关
const contentDialogVisible = ref(false)
const contentDialogTitle = ref('')
const contentData = ref('')

// 显示内容弹窗
const showContentDialog = (title, data) => {
  contentDialogTitle.value = title
  contentData.value = data || ''
  contentDialogVisible.value = true
}

// 当前筛选的字段名（用于动态标题）
const esHistoryFilterField = ref('')

// 动态生成 ES 源数据历史记录弹窗标题
const esHistoryDialogTitle = computed(() => {
  if (esHistoryFilterField.value) {
    const field = allFields.value.find(f => f.name === esHistoryFilterField.value)
    if (field) {
      return `${esHistoryFilterField.value}（${field.label}）历史记录`
    }
  }
  return 'ES 源数据历史记录'
})

// 动态生成历史记录弹窗标题
const historyDialogTitle = computed(() => {
  if (currentHistoryField.value) {
    const field = allFields.value.find(f => f.name === currentHistoryField.value)
    if (field) {
      return `${currentHistoryField.value}（${field.label}）历史记录`
    }
  }
  return '历史生成记录'
})

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
    // 使用 /field-options API
    const response = await fetch(`/kafka-generator/field-options?kafka_field=${field}`)
    const result = await response.json()
    
    if (result.success) {
      // 转换数据格式为表格所需格式
      const rows = result.data.rows || []
      const columns = result.data.columns || []
      
      // 将行数据转换为对象数组，添加字段名和说明列
      dictData.value = rows.map(row => ({
        field_name: field,
        field_value: row[columns[0]] || '',
        description: row[columns[1]] || row['description'] || '',
        source: '维表',
        ...row,
      }))
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

    // 校验：如果 NETWORK_TYPE_TOP 为 20，禁止开启测试前缀
    const networkTypeTop = customFields.NETWORK_TYPE_TOP
    console.log('校验 NETWORK_TYPE_TOP:', networkTypeTop, '类型:', typeof networkTypeTop)
    
    if (networkTypeTop === '20' || networkTypeTop === 20) {
      if (addTestPrefix.value) {
        ElMessage.warning({
          message: '提示：因为当前是虚拟化的一级专业 ID（NETWORK_TYPE_TOP=20），网元名称（EQP_LABEL）不能添加【测试】前缀。已自动关闭。',
          duration: 6000,
        })
        addTestPrefix.value = false
      }
    }

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
      
      // 保存历史记录ID
      if (result.history_id) {
        lastGeneratedHistoryId.value = result.history_id
      }

      // 处理测试前缀
      if (addTestPrefix.value) {
        if (resultData.value.EQP_LABEL && !resultData.value.EQP_LABEL.includes('【测试】')) {
          resultData.value.EQP_LABEL = '【测试】' + resultData.value.EQP_LABEL
        }
        if (resultData.value.NE_LABEL && !resultData.value.NE_LABEL.includes('【测试】')) {
          resultData.value.NE_LABEL = '【测试】' + resultData.value.NE_LABEL
        }
      }
      
      resultJson.value = JSON.stringify(resultData.value, null, 2)
      delayTime.value = result.delay_time || 15
      esQuery.value = result.es_query || ''
      timeFieldsAdjusted.value = false  // 重置调整标记
      
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
    // 尝试使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(resultJson.value)
      ElMessage.success('已复制到剪贴板')
    } else {
      // 降级方案：使用 execCommand
      const textarea = document.createElement('textarea')
      textarea.value = resultJson.value
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      
      try {
        document.execCommand('copy')
        ElMessage.success('已复制到剪贴板')
      } catch (err) {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动选择文本复制')
      } finally {
        document.body.removeChild(textarea)
      }
    }
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
    // 尝试使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(fpValue)
      ElMessage.success('FP 值已复制')
    } else {
      // 降级方案
      const textarea = document.createElement('textarea')
      textarea.value = fpValue
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      
      try {
        document.execCommand('copy')
        ElMessage.success('FP 值已复制')
      } catch (err) {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动选择文本复制')
      } finally {
        document.body.removeChild(textarea)
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 生成推送消息
const generatePushMessage = () => {
  if (!resultData.value) {
    ElMessage.warning('请先生成 Kafka 消息')
    return
  }

  const fpValue = resultData.value.FP0_FP1_FP2_FP3
  if (!fpValue) {
    ElMessage.warning('结果中没有找到 FP0_FP1_FP2_FP3 字段')
    return
  }

  // 填充推送消息字段
  pushMessageFp.value = fpValue
  
  // 使用 EVENT_TIME 或当前时间
  pushMessageEventTime.value = resultData.value.EVENT_TIME || formatCurrentTime()
  pushMessageActiveStatus.value = '3'
  
  // 生成推送消息 JSON
  updatePushMessageJson()
  
  // 显示弹窗
  pushMessageDialogVisible.value = true
}

// 格式化当前时间
const formatCurrentTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const mins = String(now.getMinutes()).padStart(2, '0')
  const secs = String(now.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${mins}:${secs}`
}

// 更新推送消息 JSON
const updatePushMessageJson = () => {
  const pushMessage = {
    ACTIVE_STATUS: pushMessageActiveStatus.value,
    CFP0_CFP1_CFP2_CFP3: pushMessageFp.value,
    EVENT_TIME: pushMessageEventTime.value,
    FP0_FP1_FP2_FP3: pushMessageFp.value,
  }
  pushMessageJson.value = JSON.stringify(pushMessage, null, 2)
  ElMessage.success('推送消息已更新')
}

// 切换 FP 值编辑状态
const toggleFpEditable = () => {
  pushMessageFpEditable.value = !pushMessageFpEditable.value
}

// 切换激活状态编辑状态
const toggleActiveStatusEditable = () => {
  pushMessageActiveStatusEditable.value = !pushMessageActiveStatusEditable.value
}

// 推送消息事件时间减指定分钟数
const subtractPushMessageEventTime = (minutes) => {
  if (!pushMessageEventTime.value) {
    ElMessage.warning('请先输入事件时间')
    return
  }

  try {
    // 解析时间字符串
    let date = new Date(pushMessageEventTime.value)
    
    // 如果解析失败，尝试其他格式
    if (isNaN(date.getTime())) {
      // 尝试 YYYY-MM-DD HH:mm:ss 格式
      const parts = pushMessageEventTime.value.split(/[- :]/)
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
    
    pushMessageEventTime.value = `${year}-${month}-${day} ${hours}:${mins}:${secs}`
    
    // 同时更新推送消息 JSON
    updatePushMessageJson()
    
    ElMessage.success(`事件时间已减${minutes}分钟`)
  } catch (error) {
    console.error('时间计算错误:', error)
    ElMessage.error('时间格式错误，请检查输入')
  }
}

// 推送消息事件时间减一年
const subtractPushMessageEventYear = (years) => {
  if (!pushMessageEventTime.value) {
    ElMessage.warning('请先输入事件时间')
    return
  }

  try {
    // 解析时间字符串
    let date = new Date(pushMessageEventTime.value)

    // 如果解析失败，尝试其他格式
    if (isNaN(date.getTime())) {
      // 尝试 YYYY-MM-DD HH:mm:ss 格式
      const parts = pushMessageEventTime.value.split(/[- :]/)
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

    // 减去指定年份
    date.setFullYear(date.getFullYear() - years)

    // 格式化为 YYYY-MM-DD HH:mm:ss
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const mins = String(date.getMinutes()).padStart(2, '0')
    const secs = String(date.getSeconds()).padStart(2, '0')

    pushMessageEventTime.value = `${year}-${month}-${day} ${hours}:${mins}:${secs}`

    // 同时更新推送消息 JSON
    updatePushMessageJson()

    ElMessage.success(`事件时间已减${years}年`)
  } catch (error) {
    console.error('时间计算错误:', error)
    ElMessage.error('时间格式错误，请检查输入')
  }
}

// 复制推送消息
const copyPushMessage = async () => {
  if (!pushMessageJson.value) {
    ElMessage.warning('没有可复制的内容')
    return
  }

  try {
    // 尝试使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(pushMessageJson.value)
      ElMessage.success('推送消息已复制')
    } else {
      // 降级方案
      const textarea = document.createElement('textarea')
      textarea.value = pushMessageJson.value
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      
      try {
        document.execCommand('copy')
        ElMessage.success('推送消息已复制')
      } catch (err) {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动选择文本复制')
      } finally {
        document.body.removeChild(textarea)
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 打开历史记录弹窗
const openHistoryModal = (field) => {
  currentHistoryField.value = field
  historyCurrentPage.value = 1
  historyKeyword.value = ''
  historyDialogVisible.value = true
  loadHistoryData()
}

// 加载历史记录数据
const loadHistoryData = async () => {
  // 生成请求ID，用于防止旧请求覆盖新请求
  const requestId = Date.now()
  currentHistoryRequest.value = requestId
  
  try {
    const params = new URLSearchParams({
      page: historyCurrentPage.value,
      per_page: historyPageSize,
    })
    
    // 如果指定了字段名，只查询该字段的记录
    if (currentHistoryField.value) {
      params.append('field_name', currentHistoryField.value)
    }
    
    if (historyKeyword.value) {
      params.append('keyword', historyKeyword.value)
    }
    
    const response = await fetch(`/kafka-generator/history?${params.toString()}`)
    const result = await response.json()
    
    // 检查是否是最新的请求
    if (requestId !== currentHistoryRequest.value) {
      return // 旧请求，忽略结果
    }
    
    if (result.success) {
      historyData.value = result.data.list || []
      historyTotal.value = result.data.total || 0
    } else {
      ElMessage.error(result.message || '加载历史记录失败')
    }
  } catch (error) {
    // 检查是否是最新的请求
    if (requestId !== currentHistoryRequest.value) {
      return // 旧请求，忽略错误
    }
    console.error('加载历史记录错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 切换页码
const changeHistoryPage = (page) => {
  historyCurrentPage.value = page
  loadHistoryData()
}

// 搜索历史记录
const searchHistory = () => {
  historyCurrentPage.value = 1
  loadHistoryData()
}

// 使用历史记录
const useHistoryRecord = (record) => {
  if (!currentHistoryField.value) {
    ElMessage.warning('未指定字段')
    return
  }
  
  // 从 kafka_message 中提取字段值
  const fieldValue = getFieldValueFromJson(record.kafka_message, currentHistoryField.value)
  
  if (fieldValue) {
    fieldValues[currentHistoryField.value] = fieldValue
    onFieldChange(currentHistoryField.value, fieldValue)
    ElMessage.success(`已填充 ${currentHistoryField.value} 字段值`)
    historyDialogVisible.value = false
  } else {
    ElMessage.warning('该记录中没有此字段的值')
  }
}

// 显示 ES 源数据历史记录（支持按字段筛选）
const showEsSourceHistory = (fieldName = '') => {
  esSourceHistoryDialogVisible.value = true
  esSourceHistoryKeyword.value = ''
  esSourceHistoryPage.value = 1
  esHistoryFilterField.value = fieldName  // 保存筛选字段名
  loadEsSourceHistoryData()
}

// 加载 ES 源数据历史记录
const loadEsSourceHistoryData = async () => {
  // 生成请求ID，用于防止旧请求覆盖新请求
  const requestId = Date.now()
  currentEsHistoryRequest.value = requestId
  
  try {
    const params = new URLSearchParams({
      page: esSourceHistoryPage.value,
      per_page: esSourceHistoryPageSize,
    })
    
    // 传入 field_name 参数筛选特定字段
    if (esHistoryFilterField.value) {
      params.append('field_name', esHistoryFilterField.value)
    }
    
    if (esSourceHistoryKeyword.value) {
      params.append('keyword', esSourceHistoryKeyword.value)
    }
    
    const response = await fetch(`/kafka-generator/history?${params.toString()}`)
    const result = await response.json()
    
    // 检查是否是最新的请求
    if (requestId !== currentEsHistoryRequest.value) {
      return // 旧请求，忽略结果
    }
    
    if (result.success) {
      esSourceHistoryData.value = result.data.list || []
      esSourceHistoryTotal.value = result.data.total || 0
    } else {
      ElMessage.error(result.message || '加载历史记录失败')
    }
  } catch (error) {
    // 检查是否是最新的请求
    if (requestId !== currentEsHistoryRequest.value) {
      return // 旧请求，忽略错误
    }
    console.error('加载 ES 源数据历史记录错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 搜索 ES 源数据历史
const searchEsSourceHistory = () => {
  esSourceHistoryKeyword.value = esSourceHistoryKeyword.value?.trim()
  esSourceHistoryPage.value = 1
  loadEsSourceHistoryData()
}

// 切换 ES 源数据历史页码
const changeEsSourceHistoryPage = (page) => {
  esSourceHistoryPage.value = page
  loadEsSourceHistoryData()
}

// 使用 ES 源数据历史记录
const useEsSourceHistory = (record) => {
  if (!record.es_source_raw) {
    ElMessage.warning('该记录没有 ES 源数据')
    return
  }
  
  // 询问是否同步自定义字段
  ElMessageBox.confirm(
    '是否要同步自定义字段数据？选择"否"则自定义字段将全部清空。',
    '同步确认',
    {
      confirmButtonText: '是，同步',
      cancelButtonText: '否，清空',
      type: 'warning',
      // 禁用点击遮罩层关闭，强制用户点击按钮
      closeOnClickModal: false,
      closeOnPressEscape: false,
      // 添加自定义类名以便区分
      customClass: 'sync-confirm-dialog'
    }
  ).then(() => {
    // 用户选择"是" - 同步自定义字段
    if (record.custom_fields) {
      try {
        const customFields = typeof record.custom_fields === 'string' 
          ? JSON.parse(record.custom_fields) 
          : record.custom_fields
        Object.assign(fieldValues, customFields)
        ElMessage.success('已加载 ES 源数据并同步自定义字段')
      } catch (e) {
        console.error('同步自定义字段失败:', e)
        // 即使同步失败，也清空所有字段值
        Object.keys(fieldValues).forEach(key => {
          fieldValues[key] = ''
        })
        ElMessage.warning('加载 ES 源数据成功，但自定义字段同步失败，已清空字段值')
      }
    } else {
      // 清空所有自定义字段
      Object.keys(fieldValues).forEach(key => {
        fieldValues[key] = ''
      })
      ElMessage.success('已加载 ES 源数据，自定义字段已清空')
    }
    esSourceData.value = typeof record.es_source_raw === 'string' 
      ? record.es_source_raw 
      : JSON.stringify(record.es_source_raw, null, 2)
    esSourceHistoryDialogVisible.value = false
  }).catch((action) => {
    // 用户选择"否" - 清空自定义字段并加载数据
    console.log('用户选择"否"（action:', action, '），清空自定义字段并加载数据')
    Object.keys(fieldValues).forEach(key => {
      fieldValues[key] = ''
    })
    esSourceData.value = typeof record.es_source_raw === 'string' 
      ? record.es_source_raw 
      : JSON.stringify(record.es_source_raw, null, 2)
    ElMessage.success('已加载 ES 源数据，自定义字段已清空')
    esSourceHistoryDialogVisible.value = false
  })
}

// 开始编辑备注
const startEditRemark = (row) => {
  editingRemarkId.value = row.id
  editingRemarkValue.value = row.remark || ''
}

// 保存备注
const saveRemark = async (historyId) => {
  if (editingRemarkId.value !== historyId) return

  try {
    const response = await fetch(`/kafka-generator/history/${historyId}/remark`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ remark: editingRemarkValue.value })
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success('备注已保存')
      // 更新本地数据
      const record = esSourceHistoryData.value.find(r => r.id === historyId)
      if (record) {
        record.remark = editingRemarkValue.value
      }
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存备注失败:', error)
    ElMessage.error('保存失败')
  } finally {
    editingRemarkId.value = null
    editingRemarkValue.value = ''
  }
}

// 取消编辑备注
const cancelEditRemark = () => {
  editingRemarkId.value = null
  editingRemarkValue.value = ''
}

// 打开备注弹窗
const openRemarkDialog = () => {
  if (!lastGeneratedHistoryId.value) {
    ElMessage.warning('请先生成 Kafka 消息')
    return
  }
  remarkContent.value = ''
  remarkDialogVisible.value = true
}

// 从生成结果保存备注
const saveRemarkFromResult = async () => {
  if (!lastGeneratedHistoryId.value) {
    ElMessage.warning('未找到历史记录ID')
    return
  }

  if (!remarkContent.value.trim()) {
    ElMessage.warning('请输入备注内容')
    return
  }

  savingRemark.value = true
  try {
    const response = await fetch(`/kafka-generator/history/${lastGeneratedHistoryId.value}/remark`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ remark: remarkContent.value })
    })

    const result = await response.json()
    if (result.success) {
      ElMessage.success('备注已保存')
      remarkDialogVisible.value = false
      remarkContent.value = ''
    } else {
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存备注失败:', error)
    ElMessage.error('保存失败')
  } finally {
    savingRemark.value = false
  }
}

// 格式化 JSON 字符串
const formatJsonString = (data) => {
  if (!data) return '-'
  if (typeof data === 'string') {
    try {
      const parsed = JSON.parse(data)
      return JSON.stringify(parsed, null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

// 从 JSON 字符串中提取字段值
const getFieldValueFromJson = (jsonData, fieldName) => {
  if (!jsonData || !fieldName) return null
  try {
    // 如果是字符串，先解析
    const parsed = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData
    // 尝试从 kafka_message 中获取（如果是字符串，可能包含字段名和值）
    if (typeof parsed === 'string') {
      // 尝试解析字符串为 JSON
      const innerParsed = JSON.parse(parsed)
      return innerParsed[fieldName] || null
    }
    // 直接从对象中获取
    return parsed[fieldName] || null
  } catch {
    // 如果是字符串，尝试直接匹配
    if (typeof jsonData === 'string') {
      const regex = new RegExp(`"${fieldName}"\\s*:\\s*"([^"]+)"`)
      const match = jsonData.match(regex)
      return match ? match[1] : null
    }
    return null
  }
}

// 复制文本
const copyText = async (text, label) => {
  if (!text) {
    ElMessage.warning('没有可复制的内容')
    return
  }
  
  try {
    const textToCopy = typeof text === 'string' ? text : JSON.stringify(text, null, 2)
    
    // 尝试使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(textToCopy)
      ElMessage.success(`${label}已复制`)
    } else {
      // 降级方案：使用 execCommand
      const textarea = document.createElement('textarea')
      textarea.value = textToCopy
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      
      try {
        document.execCommand('copy')
        ElMessage.success(`${label}已复制`)
      } catch (err) {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动选择文本复制')
      } finally {
        document.body.removeChild(textarea)
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 强制格式化 JSON（将 Python 三引号字符串转换为标准 JSON 格式）
const forceFormatJson = () => {
  if (!esSourceData.value.trim()) {
    ElMessage.warning('请先输入 ES 源数据')
    return
  }

  try {
    let text = esSourceData.value
    
    // 匹配 Python 三引号字符串："""内容"""
    // 替换为转义后的 JSON 字符串："内容"
    const tripleQuoteRegex = /"""([\s\S]*?)"""/g
    
    let hasChanges = false
    const formattedText = text.replace(tripleQuoteRegex, (match, content) => {
      hasChanges = true
      // 转义内容中的双引号和反斜杠
      const escaped = content
        .replace(/\\/g, '\\\\')  // 先转义反斜杠
        .replace(/"/g, '\\"')     // 再转义双引号
        .replace(/\n/g, '\\n')    // 转义换行符
        .replace(/\r/g, '\\r')    // 转义回车符
        .replace(/\t/g, '\\t')    // 转义制表符
      return `"${escaped}"`
    })
    
    if (hasChanges) {
      esSourceData.value = formattedText
      ElMessage.success('格式化成功！已将 Python 三引号字符串转换为标准 JSON 格式')
    } else {
      ElMessage.info('未检测到需要格式化的内容')
    }
  } catch (error) {
    console.error('格式化失败:', error)
    ElMessage.error('格式化失败：' + error.message)
  }
}

// 加载示例数据
const loadSampleData = () => {
  const sampleData = {
    "HOME_BROAD_BAND_LIST": [],
    "FULL_REGION_ID": "35000/350600/350623",
    "EVENT_LEVEL": 4,
    "ORG_TYPE": 14104,
    "EVENT_LOCATION": "MSP",
    "INDUSTRY_CUST_TYPE": "10",
    "TOPIC_PREFIX": "EVENT-GZ",
    "REMOTE_OBJECT_NAME": "SSAP",
    "EVENT_TIME": "2026-02-09 14:03:50",
    "IS_TEST": 0,
    "PORT_NUM_CN": "集客直真",
    "EVENT_REASON": "告警分析：设备脱网\n定位信息：MSP。",
    "VENDOR_ID": 323,
    "REMOTE_EQUIPMENT_NAME": "",
    "SRC_ORG_ALARM_TEXT": "【发生时间】2026-02-09 14:03:50;\n【告警对象】MSP;\n【告警内容】设备脱网(影响1条电路);\n【业务影响情况】1条业务;\n(1).数据专线(5901351420250509296606),漳州漳浦消防救援(古雷EE)宿舍楼-漳州漳浦消防救援(杜浔AG专职站)FE5980KA\n【归属客户】漳州市消防救援支队(5916596304)(金牌,非直服直管);\n【A端】福建省漳州漳浦县古雷镇古雷港经济开发区新港城裕民路801号;\n【业务信息】数据专线,本地专线,A;\n;【告警分析】设备脱网;\n【预定位信息】【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息\n\n【客户侧信息查询】1、客户侧网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1\n2、告警情况：客户侧无相关告警\n【对端故障信息查询】对端无故障\n【集客动环信息查询】1、故障网元：62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1\n2、查询资源：初步核实归属机房名称为漳州漳浦消防救援(杜浔AG专职站)一楼办公室机房，归属站点名称为3、查询告警：经核实查询最近6小时无相关停电故障，设备所在机房动环运行正常;",
    "ALARM_SOURCE": "直真专线监控系统",
    "CITY_NAME": "漳州市",
    "EQUIPMENT_NAME": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
    "NETWORK_SUB_TYPE_ID": "1100",
    "EVENT_ID": 311980616,
    "SITE_TYPE": "",
    "EVENT_NUM": 2,
    "DETAIL_STATUS": 2,
    "CANCEL_STATUS": 1,
    "PROJ_INTERFERENCE_FLAG": 0,
    "ROOT_NETWORK_TYPE_ID": "1",
    "NETWORK_SUB_TYPE_NAME": "集客",
    "ALARM_STANDARD_NAME": "设备脱网",
    "ALARM_STANDARD_FLAG": 2,
    "MAINTAIN_TEAM": "漳州漳浦集客铁通维护组",
    "EQP_OBJECT_ID": "87002",
    "EVENT_ROOT_CATEGORY": "客户侧故障",
    "EVENT_SOURCE": 2,
    "EVENT_STATUS": 0,
    "KEY_CELL": "0",
    "NE_LABEL": "[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
    "TYPE_KEYCODE": "预处理,",
    "EVENT_EXPLANATION": "",
    "ALARM_RESOURCE_STATUS": "1",
    "EFFECT_CLIENT_LEVEL": "1",
    "SERVICE_ASSURANCE_LEVEL": "2",
    "SUPPRESS_NIGHT": "0",
    "NMS_ALARM_ID": "2020740405373157376",
    "EXCEPTION_SUPPRESS_DISPATCH": 0,
    "EVENT_NAME": "单条集客A本地专线故障事件-设备脱网",
    "EQUIPMENT_IP": "5901351420250509296606",
    "FAULT_LOCATION": "【告警对象】MSP;<br>",
    "EVENT_COLLECTION_TIME": "2026-02-09 14:04:57",
    "TOPIC_PARTITION": 12,
    "SPECIFIC_PROBLEMS": "631ed71a84cadfbeb9d29c7659232abf",
    "FULL_REGION_NAME": "福建省/漳州市/漳浦县",
    "EXTRA_STRING1": "",
    "IS_EFFECT_BUSINESS": "是",
    "EVENT_CAT": "【工程信息查询】1、自身工程：初步核实故障网元62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1近24小时无工程割接信息",
    "ALARM_UNIQUE_ID": "2028480021",
    "ALARM_NAME": "设备脱网(影响1条电路)",
    "VENDOR_NAME": "瑞斯康达",
    "RECOGNITION_STANDARD_ID": "WLSJ-YW-B-03-80-0032",
    "5G_CUSTOMER_LIST": [],
    "EVENT_TYPE_ID": "业务类",
    "MAIN_NET_SORT_ONE": "集团专线",
    "EVENT_STANDARD_FLAG": 2,
    "VENDOR_EVENT_TYPE": "14202",
    "ALARM_REASON": "",
    "OBJECT_CLASS_ID": 87002,
    "PORT_NUM": "300205",
    "COUNTY_ID": "350623",
    "EVENT_LEVEL_NAME": "四级",
    "ALARM_LEVEL_NAME": "二级告警",
    "EVENT_EFFECT": "网络层面：[集客]62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1；\n业务层面：影响集客业务1条，涉及客户：漳州市消防救援支队(5916596304)；\n社会层面：无。\n",
    "EVENT_FP": "1713996274_3872318956_2520283298_4136070826_2",
    "SERVICE_EFFECT_STATUS": "有影响",
    "EVENT_ARRIVAL_TIME": "2026-02-09 14:04:59",
    "FAULT_DIAGNOSIS": "经核实无工程操作、无传输故障，无光功率异常，无动环停电，初步判断为对端故障导致，请进一步核实。",
    "EFFECT_SERVICE_LEVEL": "2",
    "PROJ_INTERFERENCE_TYPE": "【是否干扰告警】：否。",
    "TMSC_CAT": "",
    "FAULT_TYPE_ID": "设备",
    "GZ_EVENT_STATUS": 2,
    "EVENT_PROVINCE_LEVEL": "2",
    "NETWORK_TYPE_ID": "11",
    "NE_ADMIN_STATUS": "",
    "NMS_NAME": "集客网管",
    "NETWORK_TYPE_NAME": "集客",
    "FAULT_SUB_TYPE_ID": "产品故障类",
    "PROVINCE_NAME": "福建省",
    "EVENT_PROBABLE_CAUSE_TXT": "",
    "OBJECT_CLASS_TEXT": "SSAP",
    "ALARM_STANDARD_ID": "1100-064-371-10-860022",
    "EXTRA_ID2": "",
    "INTELLIGENT": 0,
    "MAIN_NET_SORT_TWO": "传输专线",
    "COUNTY_NAME": "漳浦县",
    "SATOTAL": 3,
    "EVENT_STANDARD_ID": "WLSJ-YW-B-03-80-0032",
    "EFFECT_NE_NUM": 1,
    "ROOT_NETWORK_TYPE_TOP": "集客",
    "LAST_EVENT_TIME": "2026-02-09 14:03:50",
    "EVENT_EXPLANATION_ADDITION": "",
    "VENDOR_SEVERITY": "1",
    "INTERFERENCE_FLAG": "0",
    "EQP_OBJECT_NAME": "SSAP",
    "OLD_EVENT_NAME": "单条集客A本地专线故障事件-设备脱网",
    "EVENT_SUMMARY": "预处理步骤： 1.核查是否工程操作导致；\n 2.核查是否动环停电故障导致；\n 3.核查是否传输光缆故障导致；\n 4.核查是否设备故障导致；\n 5.核查是否客户下电导致。\n",
    "PROVINCE_ID": "35000",
    "EVENT_CLEAR_FP": "1713996274_3872318956_2520283298_4136070826_2",
    "GROUP_CUSTOMER_LINE_LIST": "[]",
    "ALARM_LEVEL": 2,
    "EVENT_ROOT_CATEGORY_ID": "11002",
    "EVENT_STANDARD_NAME": "单条集客专线故障事件",
    "NE_LOCATION": "62-1147-漳州-漳浦-杜浔镇漳州消防救援(杜浔AG专职站)-RC-CPE1",
    "EFFECT_CIRCUIT_LEVEL": "1403",
    "MAINTAIN_TEAM_SOURCE": "1",
    "CITY_ID": "350600",
    "REMOTE_OBJECT_CLASS": "87002",
    "MAIN_NET_SORT_THREE": "SSAP",
    "CUSTOMER_SERVICE_LEVEL": "1",
    "CREATION_EVENT_TIME": "2026-02-09 14:04:59",
    "FIRST_EVENT_TIME": "2026-02-09 14:03:50",
    "SERV_EFFECT_TYPE": "政企业务-集团专线"
  }
  
  esSourceData.value = JSON.stringify(sampleData, null, 2)
  ElMessage.success('示例数据已加载')
}

// 跳转到字段映射管理页面
const goToFieldMetaManager = () => {
  window.location.href = '/kafka-field-meta'
}

// 复制 ES 查询
const copyEsQuery = async () => {
  if (!esQuery.value) {
    ElMessage.warning('没有 ES 查询语句')
    return
  }

  try {
    // 尝试使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(esQuery.value)
      ElMessage.success('ES 查询已复制')
    } else {
      // 降级方案
      const textarea = document.createElement('textarea')
      textarea.value = esQuery.value
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      
      try {
        document.execCommand('copy')
        ElMessage.success('ES 查询已复制')
      } catch (err) {
        console.error('复制失败:', err)
        ElMessage.error('复制失败，请手动选择文本复制')
      } finally {
        document.body.removeChild(textarea)
      }
    }
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 调整所有时间字段（eventTime、EVENT_ARRIVAL_TIME、CREATION_EVENT_TIME）
const adjustAllTimeFields = () => {
  const minutes = delayTime.value
  if (!minutes || minutes <= 0) {
    ElMessage.warning('请先设置延迟时间（分钟）')
    return
  }

  try {
    // 1. 调整 eventTime 输入框
    if (eventTime.value) {
      let date = new Date(eventTime.value)
      
      if (isNaN(date.getTime())) {
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
          ElMessage.error('事件时间格式不正确，请使用 YYYY-MM-DD HH:mm:ss 格式')
          return
        }
      }
      
      date.setMinutes(date.getMinutes() - minutes)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const mins = String(date.getMinutes()).padStart(2, '0')
      const secs = String(date.getSeconds()).padStart(2, '0')
      
      eventTime.value = `${year}-${month}-${day} ${hours}:${mins}:${secs}`
    }

    // 2. 调整 JSON 结果中的时间字段
    if (resultJson.value) {
      const jsonData = JSON.parse(resultJson.value)
      
      // 需要调整的时间字段
      const timeFields = ['EVENT_ARRIVAL_TIME', 'CREATION_EVENT_TIME']
      let adjustedCount = 0
      
      timeFields.forEach(fieldName => {
        if (jsonData[fieldName]) {
          let date = new Date(jsonData[fieldName])
          
          if (!isNaN(date.getTime())) {
            date.setMinutes(date.getMinutes() - minutes)
            const year = date.getFullYear()
            const month = String(date.getMonth() + 1).padStart(2, '0')
            const day = String(date.getDate()).padStart(2, '0')
            const hours = String(date.getHours()).padStart(2, '0')
            const mins = String(date.getMinutes()).padStart(2, '0')
            const secs = String(date.getSeconds()).padStart(2, '0')
            
            jsonData[fieldName] = `${year}-${month}-${day} ${hours}:${mins}:${secs}`
            adjustedCount++
          }
        }
      })
      
      // 更新 JSON 显示
      resultJson.value = JSON.stringify(jsonData, null, 2)
      
      // 标记已调整，触发高亮效果
      timeFieldsAdjusted.value = true
      
      // 3 秒后移除高亮
      setTimeout(() => {
        timeFieldsAdjusted.value = false
      }, 3000)
      
      ElMessage.success(`已调整 ${adjustedCount + (eventTime.value ? 1 : 0)} 个时间字段（-${minutes}分钟）`)
    } else {
      ElMessage.warning('请先生成结果')
    }
  } catch (error) {
    console.error('时间调整错误:', error)
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

// 从数据库加载缓存（自定义字段默认全部为空，不恢复缓存值）
const loadFieldCache = async () => {
  try {
    const response = await fetch('/kafka-generator/field-cache')
    const result = await response.json()
    
    if (result.success && result.data) {
      // 【需求3】自定义字段默认全部为空，不恢复缓存的字段值
      // 只加载置顶字段和历史值
      pinnedFields.value = new Set(result.data.pinned_fields || [])
      historyValues.value = result.data.history_values || {}
      
      console.log('已加载字段缓存（字段值已清空）')
    }
  } catch (error) {
    console.warn('加载缓存失败:', error)
  }
}

// 初始化
onMounted(() => {
  loadFieldMeta()
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
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
  transition: background-color 0.3s ease;
}

/* 时间调整高亮效果 */
.result-textarea.time-adjusted {
  background-color: #fff9e6 !important;
  animation: highlightFade 3s ease-in-out;
}

@keyframes highlightFade {
  0% {
    background-color: #fff9e6;
  }
  70% {
    background-color: #fff9e6;
  }
  100% {
    background-color: transparent;
  }
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.delay-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.delay-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.delay-label {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  white-space: nowrap;
}

.event-time-control {
  display: flex;
  align-items: center;
}

.es-query-section {
  margin-top: 20px;
}

.text-center {
  text-align: center;
}

.py-5 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}

.text-muted {
  color: #6c757d;
}

.mb-3 {
  margin-bottom: 1rem;
}

/* ES 输入框包装器 */
.es-input-wrapper {
  position: relative;
}

.es-input-buttons {
  position: absolute;
  right: 10px;
  bottom: 10px;
  z-index: 10;
  display: flex;
  gap: 8px;
}

.es-history-btn,
.format-btn {
  white-space: nowrap;
}

/* JSON 预览样式 */
.json-preview {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.json-textarea {
  font-family: 'Courier New', monospace;
  font-size: 11px;
}

.mt-2 {
  margin-top: 8px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

/* 隐藏同步确认弹窗的关闭按钮 */
:deep(.sync-confirm-dialog) {
  .el-message-box__headerbtn {
    display: none !important;
  }
}

/* 备注列样式 */
.remark-cell {
  display: flex;
  align-items: center;
  min-height: 32px;
}

.remark-edit-mode {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.remark-actions {
  display: flex;
  gap: 8px;
}

.remark-view-mode {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.remark-text {
  flex: 1;
  color: #606266;
  padding: 4px 8px;
  border-radius: 4px;
  transition: all 0.2s;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  
  &:hover {
    background-color: #f5f7fa;
    color: #409eff;
  }
  
  &:empty::before {
    content: '点击添加备注';
    color: #c0c4cc;
    font-style: italic;
  }
}

.edit-btn,
.view-btn {
  flex-shrink: 0;
  padding: 4px;
  min-width: auto;
}

/* 内容查看弹窗样式 */
.content-viewer {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content-header {
  display: flex;
  justify-content: flex-end;
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
}

.content-textarea {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

/* 按钮组左右分布 - 只作用于生成结果区域 */
.result-card .button-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .left-buttons {
    display: flex;
    gap: 10px;
  }
}
</style>
