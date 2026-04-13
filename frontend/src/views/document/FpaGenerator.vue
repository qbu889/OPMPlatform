<template>
  <div class="fpa-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><el-icon :size="28" color="#67c23a"><DataAnalysis /></el-icon> FPA 预估表生成器</h2>
      <p class="subtitle">从需求文档自动生成 FPA 功能点估算表</p>
    </div>

    <!-- 功能说明 -->
    <el-card class="info-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><InfoFilled /></el-icon>
          <span>功能说明</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <h4><el-icon color="#67c23a"><CircleCheck /></el-icon> 支持的功能</h4>
          <ul class="feature-list">
            <li>自动识别需求文档的层级结构</li>
            <li>提取功能描述、输入、输出等关键信息</li>
            <li>统计内部/外部逻辑文件数量</li>
            <li>生成标准化的 FPA 预估 Excel 表格</li>
            <li>支持拖拽上传和批量处理</li>
          </ul>
        </el-col>
        <el-col :span="12">
          <h4><el-icon color="#409eff"><Document /></el-icon> 支持的文档格式</h4>
          <ul class="feature-list">
            <li>Markdown (.md) 格式需求文档</li>
            <li>Word (.docx) 格式需求文档</li>
            <li>符合 FPA 规范的功能需求章节</li>
            <li>包含完整的功能点描述信息</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>

    <!-- 上传区域 -->
    <el-card class="upload-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#67c23a"><UploadFilled /></el-icon>
          <span>上传需求文档</span>
        </div>
      </template>

      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        :on-remove="handleRemove"
        :limit="1"
        accept=".md,.docx"
        v-if="!taskId"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">点击选择文件或拖拽到此处</div>
        <div class="upload-tip">支持 Markdown (.md) 和 Word (.docx) 格式的需求规格说明书</div>
      </el-upload>

      <el-alert
        v-if="selectedFile && !taskId"
        :title="`已选择文件: ${selectedFile.name}`"
        type="success"
        show-icon
        :closable="false"
        class="mt-3"
      />

      <!-- 注意事项 -->
      <el-alert
        title="注意事项"
        type="warning"
        :closable="false"
        class="mt-3"
      >
        <template #default>
          <ul style="margin: 5px 0; padding-left: 20px;">
            <li>请确保文档包含完整的功能点描述 (功能描述、输入、输出、处理过程等)</li>
            <li>文档应符合 FPA 规范的层级结构 (一级分类、二级分类、三级分类...)</li>
            <li>生成的 Excel 文件将自动保存到服务器，请及时下载</li>
            <li><strong>生成过程较慢，系统会在后台处理，您可以实时查看进度和日志</strong></li>
          </ul>
        </template>
      </el-alert>

      <!-- 操作按钮 -->
      <div class="action-buttons mt-3" v-if="selectedFile && !taskId">
        <el-button type="primary" size="large" :loading="loading" @click="handleGenerate">
          <el-icon><Cpu /></el-icon>
          开始生成 FPA 预估表
        </el-button>
        <el-button type="info" size="large" @click="openRulesManagement">
          <el-icon><Tools /></el-icon>
          类别生成规则配置
        </el-button>
      </div>
    </el-card>

    <!-- 异步任务进度查询 -->
    <el-card v-if="taskId" class="task-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#409eff"><Tickets /></el-icon>
          <span>任务进度查询</span>
        </div>
      </template>

      <el-form label-width="100px">
        <el-form-item label="任务 ID">
          <el-input v-model="taskId" readonly />
        </el-form-item>
      </el-form>

      <div class="button-group">
        <el-button type="primary" @click="queryTaskProgress">
          <el-icon><Search /></el-icon>
          查询进度
        </el-button>
        <el-button 
          v-if="taskStatus === 'running' || taskStatus === 'pending'"
          type="danger" 
          @click="stopCurrentTask"
        >
          <el-icon><VideoPause /></el-icon>
          停止任务
        </el-button>
      </div>

      <!-- 进度显示 -->
      <div v-if="progressDisplay.visible" class="progress-section mt-3">
        <el-progress 
          :percentage="progressDisplay.percentage" 
          :status="progressDisplay.status"
          :stroke-width="30"
        >
          <template #default="{ percentage }">
            <span class="percentage-value">{{ percentage }}%</span>
          </template>
        </el-progress>
        <p class="progress-message">{{ progressDisplay.message }}</p>

        <!-- 日志显示 -->
        <div class="log-section mt-3">
          <h4>详细日志：</h4>
          <div class="log-container">
            <div v-for="(log, index) in taskLogs" :key="index" class="log-item">
              {{ log }}
            </div>
          </div>
        </div>

        <!-- 下载按钮 -->
        <div v-if="downloadUrl" class="download-section mt-3 text-center">
          <el-button type="success" size="large" @click="downloadFile">
            <el-icon><Download /></el-icon>
            下载生成的 FPA 文件
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 调整因子列表 -->
    <el-card class="factor-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><List /></el-icon>
          <span>调整因子列表</span>
        </div>
      </template>

      <el-table :data="adjustmentFactors" border stripe>
        <el-table-column prop="type" label="因子类型" width="200" />
        <el-table-column label="因子名称" min-width="400">
          <template #default="{ row }">
            <el-select 
              v-if="row.options" 
              v-model="row.selectedValue" 
              @change="updateFactorValue(row)"
              style="width: 100%"
            >
              <el-option
                v-for="opt in row.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
            <span v-else>{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="因子计算结果" width="150">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.value" 
              :precision="2" 
              :step="0.01" 
              disabled 
              style="width: 100%"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 评估结果表 -->
    <el-card class="result-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon><Grid /></el-icon>
          <span>评估结果表</span>
        </div>
      </template>

      <el-table :data="evaluationResults" border stripe>
        <el-table-column prop="category" label="类别" width="300" />
        <el-table-column label="数值" width="200">
          <template #default="{ row }">
            <el-input-number 
              v-if="row.editable"
              v-model="row.value" 
              :precision="2" 
              :step="0.01"
              @change="recalculateEvaluation"
              style="width: 100%"
            />
            <el-input-number 
              v-else
              v-model="row.value" 
              :precision="2" 
              :step="0.01"
              disabled
              style="width: 100%"
            />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" />
      </el-table>

      <div class="button-group mt-3">
        <el-button type="primary" @click="saveEvaluationResult">
          <el-icon><Save /></el-icon>
          保存评估结果
        </el-button>
        <span class="save-status">{{ saveStatus }}</span>
      </div>
    </el-card>

    <!-- 导出历史记录 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header-title justify-between">
          <div>
            <el-icon><Clock /></el-icon>
            <span>导出历史记录</span>
          </div>
          <el-button size="small" @click="loadExportHistory(1)">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="exportHistory" border stripe v-loading="historyLoading">
        <el-table-column prop="task_id" label="任务 ID" width="150" />
        <el-table-column prop="original_filename" label="原文件名" min-width="150" />
        <el-table-column prop="generated_filename" label="生成文件名" min-width="150" />
        <el-table-column prop="function_points" label="功能点数" width="100" />
        <el-table-column prop="file_size" label="文件大小" width="120" />
        <el-table-column prop="progress" label="进度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :status="getProgressStatus(row.status)" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="completed_at" label="完成时间" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'completed'" 
              size="small" 
              type="success"
              @click="downloadHistoryFile(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button 
              v-if="row.status === 'running' || row.status === 'pending'"
              size="small" 
              type="danger"
              @click="cancelHistoryTask(row.task_id)"
            >
              <el-icon><Close /></el-icon>
              停止
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-section mt-3">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalRecords"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  DataAnalysis,
  InfoFilled,
  CircleCheck,
  Document,
  UploadFilled,
  Cpu,
  Tools,
  Tickets,
  Search,
  VideoPause,
  List,
  Grid,
  Save,
  Clock,
  Refresh,
  Download,
  Close,
} from '@element-plus/icons-vue'

// 文件上传相关
const selectedFile = ref(null)
const loading = ref(false)

// 任务相关
const taskId = ref('')
const taskStatus = ref('')
const progressDisplay = reactive({
  visible: false,
  percentage: 0,
  status: '',
  message: '',
})
const taskLogs = ref([])
const downloadUrl = ref('')

// 调整因子
const adjustmentFactors = ref([
  {
    type: '规模计数时机',
    name: 'cfTiming',
    selectedValue: '估算中期',
    value: 1.21,
    options: [
      { label: '估算早期（概算、预算阶段）', value: '估算早期', factor: 1.35 },
      { label: '估算中期（投标、项目计划阶段）', value: '估算中期', factor: 1.21 },
      { label: '估算晚期（需求分析阶段）', value: '估算晚期', factor: 1.08 },
      { label: '项目完成（项目交付后及运维阶段）', value: '项目完成', factor: 1.00 },
    ],
  },
  {
    type: '应用类型',
    name: 'applicationType',
    selectedValue: '业务处理',
    value: 1.00,
    options: [
      { label: '业务处理', value: '业务处理', factor: 1.00 },
      { label: '应用集成', value: '应用集成', factor: 1.10 },
      { label: '科技', value: '科技', factor: 1.20 },
      { label: '多媒体', value: '多媒体', factor: 1.15 },
      { label: '智能信息', value: '智能信息', factor: 1.25 },
      { label: '基础软件/支撑软件', value: '基础软件/支撑软件', factor: 1.30 },
      { label: '通信控制', value: '通信控制', factor: 1.20 },
      { label: '流程控制', value: '流程控制', factor: 1.25 },
    ],
  },
  {
    type: '质量特性 - 分布式处理',
    name: 'distributedProcessing',
    selectedValue: '没有明示对分布式处理的需求事项',
    value: -1.00,
    options: [
      { label: '没有明示 (-1)', value: '没有明示对分布式处理的需求事项', factor: -1.00 },
      { label: '客户端/服务器分布处理 (0)', value: '通过网络进行客户端/服务器及网络基础应用分布处理和传输', factor: 0.00 },
      { label: '多服务器并发处理 (1)', value: '在多个服务器及处理器上同时相互执行计算机系统中的处理功能', factor: 1.00 },
    ],
  },
  {
    type: '质量特性 - 性能',
    name: 'performance',
    selectedValue: '没有明示对性能的特别需求事项或活动，因此提供基本性能',
    value: -1.00,
    options: [
      { label: '没有明示性能需求 (-1)', value: '没有明示对性能的特别需求事项或活动，因此提供基本性能', factor: -1.00 },
      { label: '应答时间重要 (0)', value: '应答时间或处理率对高峰时间或所有业务时间来说都很重要，对连动系统结束处理时间的限制', factor: 0.00 },
      { label: '需要性能分析 (1)', value: '为满足性能需求事项，要求设计阶段开始进行性能分析，或在设计、开发阶段使用分析工具', factor: 1.00 },
    ],
  },
  {
    type: '质量特性 - 可靠性',
    name: 'reliability',
    selectedValue: '没有明示对可靠性的特别需求事项或活动，因此提供基本的可靠性',
    value: -1.00,
    options: [
      { label: '没有明示可靠性需求 (-1)', value: '没有明示对可靠性的特别需求事项或活动，因此提供基本的可靠性', factor: -1.00 },
      { label: '故障可轻易修复 (0)', value: '发生故障时可轻易修复，带来一定不便或经济损失', factor: 0.00 },
      { label: '故障难修复/重大损失 (1)', value: '发生故障时很难复，发生重大经济损失或有生命危害', factor: 1.00 },
    ],
  },
  {
    type: '质量特性 - 多重站点',
    name: 'multiSite',
    selectedValue: '在相同用途的硬件或软件环境下运行',
    value: -1.00,
    options: [
      { label: '相同环境 (-1)', value: '在相同用途的硬件或软件环境下运行', factor: -1.00 },
      { label: '类似环境 (0)', value: '在用途类似的硬件或软件环境下运行', factor: 0.00 },
      { label: '不同环境 (1)', value: '在不同用途的硬件或软件环境下运行', factor: 1.00 },
    ],
  },
  {
    type: '开发语言',
    name: 'language',
    selectedValue: 'JAVA、C++、C#及其他同级别语言/平台',
    value: 1.00,
    options: [
      { label: 'C 及同级别语言 (1.2)', value: 'C 及其他同级别语言/平台', factor: 1.20 },
      { label: 'JAVA、C++、C# (1.0)', value: 'JAVA、C++、C#及其他同级别语言/平台', factor: 1.00 },
      { label: 'PowerBuilder、ASP (0.8)', value: 'PowerBuilder、ASP 及其他同级别语言/平台', factor: 0.80 },
    ],
  },
  {
    type: '开发团队背景',
    name: 'teamBackground',
    selectedValue: '为本行业（政府）开发过类似的软件',
    value: 0.80,
    options: [
      { label: '本行业有类似经验 (0.8)', value: '为本行业（政府）开发过类似的软件', factor: 0.80 },
      { label: '其他行业有类似经验 (1.0)', value: '为其他行业开发过类似的软件，或为本行业（政府）开发过不同但相关的软件', factor: 1.00 },
      { label: '无类似经验 (1.2)', value: '未开发过类似软件', factor: 1.20 },
    ],
  },
])

// 评估结果
const evaluationResults = ref([
  { category: '规模估算结果（单位：功能点）', value: 125.27, description: 'AFP', editable: true },
  { category: '规模变更调整因子', value: 1.21, description: 'CF、项目阶段', editable: false },
  { category: '调整后规模（单位：功能点）', value: 151.57, description: 'S，等于 AFP*CF', editable: false, highlight: true },
  { category: '基准生产率（单位：人时/功能点）', value: 10.12, description: 'PDR，来自《2024 年软件行业基准数据》', editable: true },
  { category: '未调整工作量（单位：人天）', value: 191.74, description: 'S*PDR/8h', editable: false, highlight: true },
  { category: '调整因子 - 应用类型', value: 1.00, description: 'A，应用类型调整因子', editable: false },
  { category: '调整因子 - 质量特性', value: 0.90, description: 'B，质量特性调整因子', editable: false },
  { category: '调整因子 - 开发语言', value: 1.00, description: 'C，开发语言调整因子', editable: false },
  { category: '调整因子 - 开发团队背景', value: 0.80, description: 'D，开发团队背景调整因子', editable: false },
  { category: '调整后工作量（单位：人天）', value: 138.05, description: 'AE,S*PDR/8h*A*B*C*D', editable: true, highlight: true },
  { category: '预计功能点数量', value: 52, description: '根据 AFP 值估算（平均每功能点 AFP ≈ 2.5）', editable: false, highlight: true },
])

const saveStatus = ref('')

// 导出历史
const exportHistory = ref([])
const historyLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 文件处理
const handleFileChange = (file) => {
  selectedFile.value = file
}

const handleRemove = () => {
  selectedFile.value = null
}

// 生成 FPA
const handleGenerate = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先上传需求文档')
    return
  }

  loading.value = true
  const formData = new FormData()
  formData.append('requirement_file', selectedFile.value.raw)

  try {
    const response = await fetch('/fpa-generator/upload', {
      method: 'POST',
      body: formData,
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('任务已提交，正在后台处理')
      taskId.value = result.task_id
      queryTaskProgress()
    } else {
      ElMessage.error(result.message || '生成失败')
    }
  } catch (error) {
    console.error('生成错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 查询任务进度
const queryTaskProgress = async () => {
  if (!taskId.value) {
    ElMessage.warning('请输入任务 ID')
    return
  }

  try {
    const response = await fetch(`/fpa-generator/task/${taskId.value}/progress`)
    const result = await response.json()

    if (result.success) {
      taskStatus.value = result.status
      progressDisplay.visible = true
      progressDisplay.percentage = result.progress || 0
      progressDisplay.message = result.message || ''
      
      if (result.status === 'completed') {
        progressDisplay.status = 'success'
        downloadUrl.value = result.download_url || ''
      } else if (result.status === 'failed') {
        progressDisplay.status = 'exception'
      } else if (result.status === 'cancelled') {
        progressDisplay.status = 'warning'
      } else {
        progressDisplay.status = ''
      }

      // 更新日志
      if (result.logs && result.logs.length > 0) {
        taskLogs.value = result.logs
      }
    } else {
      ElMessage.error(result.message || '查询失败')
    }
  } catch (error) {
    console.error('查询错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 停止任务
const stopCurrentTask = async () => {
  try {
    await ElMessageBox.confirm('确定要停止当前任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`/fpa-generator/task/${taskId.value}/cancel`, {
      method: 'POST',
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('任务已停止')
      queryTaskProgress()
    } else {
      ElMessage.error(result.message || '停止失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止错误:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  }
}

// 下载文件
const downloadFile = () => {
  if (downloadUrl.value) {
    window.open(downloadUrl.value, '_blank')
  }
}

// 更新因子值
const updateFactorValue = (row) => {
  const option = row.options.find(opt => opt.value === row.selectedValue)
  if (option) {
    row.value = option.factor
  }
  recalculateEvaluation()
}

// 重新计算评估结果
const recalculateEvaluation = () => {
  // 获取各个因子值
  const afp = evaluationResults.value[0].value
  const cf = adjustmentFactors.value[0].value
  
  // 计算调整后规模
  const adjustedScale = afp * cf
  evaluationResults.value[2].value = parseFloat(adjustedScale.toFixed(2))
  
  // 计算未调整工作量
  const pdr = evaluationResults.value[3].value
  const unadjustedEffort = (adjustedScale * pdr) / 8
  evaluationResults.value[4].value = parseFloat(unadjustedEffort.toFixed(2))
  
  // 获取质量特性因子
  const qualityFactors = adjustmentFactors.value.slice(2, 6)
  const qualitySum = qualityFactors.reduce((sum, f) => sum + f.value, 0)
  const qualityFactor = 1 + (qualitySum * 0.01)
  evaluationResults.value[6].value = parseFloat(qualityFactor.toFixed(2))
  
  // 计算调整后工作量
  const appType = adjustmentFactors.value[1].value
  const language = adjustmentFactors.value[6].value
  const team = adjustmentFactors.value[7].value
  const adjustedEffort = unadjustedEffort * appType * qualityFactor * language * team
  evaluationResults.value[9].value = parseFloat(adjustedEffort.toFixed(2))
  
  // 预计功能点数量
  const expectedPoints = Math.round(afp / 2.5)
  evaluationResults.value[10].value = expectedPoints
}

// 保存评估结果
const saveEvaluationResult = async () => {
  saveStatus.value = '保存中...'
  
  try {
    const response = await fetch('/fpa-generator/save-evaluation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        evaluation_results: evaluationResults.value,
        adjustment_factors: adjustmentFactors.value,
      }),
    })
    const result = await response.json()

    if (result.success) {
      saveStatus.value = '✓ 保存成功'
      ElMessage.success('评估结果已保存')
    } else {
      saveStatus.value = '✗ 保存失败'
      ElMessage.error(result.message || '保存失败')
    }
  } catch (error) {
    console.error('保存错误:', error)
    saveStatus.value = '✗ 网络错误'
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 加载导出历史
const loadExportHistory = async (page = 1) => {
  historyLoading.value = true
  try {
    const response = await fetch(`/fpa-generator/export-history?page=${page}&per_page=${pageSize.value}`)
    const result = await response.json()

    if (result.success) {
      exportHistory.value = result.history || []
      totalRecords.value = result.total || 0
      currentPage.value = page
    } else {
      ElMessage.error(result.message || '加载失败')
    }
  } catch (error) {
    console.error('加载错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    historyLoading.value = false
  }
}

// 分页变化
const handlePageChange = (page) => {
  loadExportHistory(page)
}

// 获取进度状态
const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  if (status === 'cancelled') return 'warning'
  return ''
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'info',
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    'pending': '等待中',
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败',
    'cancelled': '已取消',
  }
  return map[status] || status
}

// 下载历史文件
const downloadHistoryFile = (row) => {
  if (row.download_url) {
    window.open(row.download_url, '_blank')
  }
}

// 取消历史任务
const cancelHistoryTask = async (taskId) => {
  try {
    await ElMessageBox.confirm('确定要停止该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`/fpa-generator/task/${taskId}/cancel`, {
      method: 'POST',
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('任务已停止')
      loadExportHistory(currentPage.value)
    } else {
      ElMessage.error(result.message || '停止失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止错误:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  }
}

// 打开规则管理
const openRulesManagement = () => {
  window.open('/fpa/category-rules', '_blank')
}

// 初始化
onMounted(() => {
  loadExportHistory(1)
  recalculateEvaluation()
})
</script>

<style scoped>
.fpa-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  padding: 40px 20px;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.page-header h2 {
  font-size: 32px;
  margin: 0 0 10px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.subtitle {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.info-card,
.upload-card,
.task-card,
.factor-card,
.result-card,
.history-card {
  margin-bottom: 25px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.info-card:hover,
.upload-card:hover,
.task-card:hover,
.factor-card:hover,
.result-card:hover,
.history-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
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

.feature-list {
  list-style: none;
  padding: 0;
  margin: 10px 0;
}

.feature-list li {
  padding: 8px 0;
  padding-left: 25px;
  position: relative;
  color: #606266;
}

.feature-list li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
  font-weight: bold;
}

.upload-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 15px;
}

.upload-text {
  font-size: 18px;
  color: #303133;
  margin-bottom: 8px;
  font-weight: 500;
}

.upload-tip {
  font-size: 14px;
  color: #909399;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

.mt-3 {
  margin-top: 15px;
}

.text-center {
  text-align: center;
}

.percentage-value {
  font-size: 16px;
  font-weight: bold;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.progress-message {
  text-align: center;
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.log-section h4 {
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
}

.log-container {
  max-height: 300px;
  overflow-y: auto;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.log-item {
  padding: 5px 0;
  border-bottom: 1px solid #e4e7ed;
  color: #606266;
}

.log-item:last-child {
  border-bottom: none;
}

.save-status {
  margin-left: 15px;
  color: #67c23a;
  font-weight: 500;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #fafafa;
}
</style>
