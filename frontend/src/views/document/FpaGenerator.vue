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
              v-if="row.editable && !row.isEffortField"
              v-model="row.value" 
              :precision="2" 
              :step="0.01"
              @change="recalculateEvaluation"
              style="width: 100%"
            />
            <el-input-number 
              v-else-if="row.editable && row.isEffortField"
              v-model="row.value" 
              :precision="2" 
              :step="0.01"
              @change="handleEffortChange"
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
        :before-upload="beforeUpload"
        :on-change="handleFileChange"
        :on-remove="handleRemove"
        :limit="1"
        accept=".md,.docx"
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
      <div class="action-buttons mt-3">
        <el-button type="primary" size="large" :loading="loading" @click="handleGenerate" :disabled="!selectedFile || (taskStatus === 'RUNNING' || taskStatus === 'PENDING')">
          <el-icon><Cpu /></el-icon>
          开始生成 FPA 预估表
        </el-button>
        <el-button type="info" size="large" @click="openRulesManagement">
          <el-icon><Tools /></el-icon>
          类别生成规则配置
        </el-button>
      </div>
    </el-card>

    <!-- 任务进度查询模块 -->
    <el-card class="task-card" shadow="hover" v-if="taskId">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#409eff"><List /></el-icon>
          <span>任务进度查询</span>
        </div>
      </template>

      <!-- 任务 ID 显示 -->
      <el-form label-position="top">
        <el-form-item label="任务 ID：">
          <el-input v-model="taskId" readonly>
            <template #append>
              <el-button @click="copyTaskId" :icon="Document">复制</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>

      <!-- 查询进度按钮 -->
      <div class="mt-3">
        <el-button type="primary" @click="queryTaskProgress" :loading="queryLoading">
          <el-icon><Search /></el-icon>
          查询进度
        </el-button>
        <el-button type="danger" @click="cancelTask" v-if="taskStatus === 'RUNNING' || taskStatus === 'PENDING'">
          <el-icon><Close /></el-icon>
          停止任务
        </el-button>
      </div>

      <!-- 进度条 -->
      <div class="mt-4" v-if="progressDisplay.visible">
        <el-progress 
          :percentage="progressDisplay.percentage" 
          :status="progressDisplay.status"
          :stroke-width="20"
        />
        <div class="progress-status" :class="`status-${progressDisplay.status}`">
          [{{ taskStatus }}] {{ progressDisplay.message }}
        </div>
      </div>

      <!-- 详细日志 -->
      <div class="mt-4" v-if="formattedLogs.length > 0">
        <h4 class="log-title">详细日志：</h4>
        <div class="log-container">
          <div 
            v-for="(log, index) in formattedLogs" 
            :key="index" 
            class="log-item"
            :class="{ 'log-success': log.type === 'success', 'log-error': log.type === 'error', 'log-warning': log.type === 'warning' }"
          >
            <span class="log-time">{{ log.time }}</span>
            <span class="log-message">{{ log.message }}</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 异步任务进度查询 -->
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

      <el-table :data="exportHistory" border stripe v-loading="historyLoading" max-height="400">
        <el-table-column prop="task_id" label="任务 ID" width="120" />
        <el-table-column prop="original_filename" label="原文件名" min-width="130" />
        <el-table-column label="生成文件名" min-width="130">
          <template #default="{ row }">
            {{ row.output_filename || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="功能点" width="70" align="center">
          <template #default="{ row }">
            {{ row.function_point_count || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="大小" width="70" align="center">
          <template #default="{ row }">
            {{ row.file_size ? (row.file_size / 1024).toFixed(0) + 'KB' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="70" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.progress || 0" :status="getProgressStatus(row.status)" :stroke-width="12" />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="完成时间" width="150">
          <template #default="{ row }">
            {{ row.completed_at ? formatDateTime(row.completed_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'COMPLETED'" 
              size="small" 
              type="success"
              @click="downloadHistoryFile(row)"
            >
              <el-icon><Download /></el-icon>
              下载
            </el-button>
            <el-button 
              v-if="row.status === 'RUNNING' || row.status === 'PENDING'"
              size="small" 
              type="danger"
              @click="cancelHistoryTask(row.task_id)"
            >
              <el-icon><Close /></el-icon>
              停止
            </el-button>
            <el-button 
              size="small" 
              type="info"
              @click="deleteHistory(row.task_id)"
            >
              <el-icon><Delete /></el-icon>
              删除
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

    <!-- 使用指南 -->
    <el-card class="guide-card" shadow="hover">
      <template #header>
        <div class="card-header-title">
          <el-icon color="#409eff"><Reading /></el-icon>
          <span>使用指南</span>
        </div>
      </template>

      <div class="guide-content">
        <h4>操作步骤：</h4>
        <ol class="guide-steps">
          <li>
            <strong>准备需求文档：</strong>
            <ul>
              <li>支持 Markdown (.md) 或 Word (.docx) 格式</li>
              <li>文档需包含完整的"功能需求"章节</li>
              <li>功能点描述需按照标准格式：## 一级分类 → ### 二级分类 → #### 三级分类 → ##### 功能点名称 → ###### 功能点计数项</li>
            </ul>
          </li>
          <li>
            <strong>上传文档：</strong>
            <ul>
              <li>点击上传区域或拖拽文件到上传框</li>
              <li>支持自动识别文档格式并解析</li>
            </ul>
          </li>
          <li>
            <strong>AI 智能分析：</strong>
            <ul>
              <li>系统自动解析功能点并识别类别（ILF/EO/EI/EQ/EIF）</li>
              <li>自动提取 ILF 表并插入到对应功能点之后</li>
              <li>从数据库读取目标 AFP 值进行对比</li>
              <li>如当前 AFP 不足，AI 自动扩展功能点以满足目标</li>
              <li>实时显示处理进度：读取文档 → 解析功能点 → AFP 对比 → AI 扩展 → 生成 Excel</li>
            </ul>
          </li>
          <li>
            <strong>查看历史记录：</strong>
            <ul>
              <li>在"导出历史记录"表格中查看任务状态</li>
              <li>RUNNING 状态：可点击"停止"按钮终止任务</li>
              <li>PENDING/RUNNING 状态：可点击"停止"按钮</li>
              <li>COMPLETED 状态：可下载 Excel 文件</li>
              <li>FAILED 状态：可查看错误消息</li>
            </ul>
          </li>
          <li>
            <strong>下载结果：</strong>
            <ul>
              <li>任务完成后，点击"下载"按钮获取 Excel 文件</li>
              <li>Excel 包含 4 个工作表：填写说明、规模估算、调整因子、评估结果</li>
              <li>所有功能点按文档顺序排列，类别和 AFP 自动计算</li>
            </ul>
          </li>
        </ol>

        <h4 class="mt-4">文档格式要求：</h4>
        <pre class="format-example"><code>## 一级分类（如：监控管理应用）
### 二级分类（如：故障监控应用）
#### 三级分类（如：集团事件对接）
##### 功能点名称（如：网络事件业务影响）
###### 功能点计数项（如：家宽业务 OLT 脱管场景业务采集）

**功能描述：**进行家宽业务 OLT 脱管场景业务采集
**系统界面：**无
**输入：**系统自动实时触发
**输出：**查询出满足条件的事件数据
**处理过程：**系统自动实时触发，进行数据采集和处理

**本事务功能预计涉及到 1 个内部逻辑文件，0 个外部逻辑文件**

本期新增/变更的内部逻辑文件：家宽业务影响指标清单表
本期涉及原有但没修改的内部逻辑文件：网络事件表
本期新增/变更的外部逻辑文件：无
本期涉及原有但没修改的外部逻辑文件：无</code></pre>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
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
  Clock,
  Refresh,
  Download,
  Close,
  Reading,
  Delete,
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
  { category: '调整后工作量（单位：人天）', value: 138.05, description: 'AE,S*PDR/8h*A*B*C*D', editable: true, highlight: true, isEffortField: true },
  { category: '预计功能点数量', value: 75, description: '根据 AFP 值估算（平均每功能点 AFP ≈ 1.66）', editable: false, highlight: true },
])

const saveStatus = ref('')

// 导出历史
const exportHistory = ref([])
const historyLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 任务进度查询相关
const queryLoading = ref(false)
let pollingTimer = null

// 格式化日志显示
const formattedLogs = computed(() => {
  if (!taskLogs.value || taskLogs.value.length === 0) return []
  
  console.log('Raw logs from backend:', taskLogs.value)
  
  return taskLogs.value.map(log => {
    // 处理对象格式的日志（后端返回的 JSON 对象）
    if (typeof log === 'object' && log !== null) {
      return formatLogItem(log)
    }
    
    // 处理字符串格式的日志
    if (typeof log === 'string') {
      try {
        const parsed = JSON.parse(log)
        return formatLogItem(parsed)
      } catch {
        return { time: '', message: log, type: '' }
      }
    }
    
    return { time: '', message: String(log), type: '' }
  })
})

// 辅助函数：格式化单条日志
const formatLogItem = (item) => {
  const time = item.timestamp 
    ? new Date(item.timestamp).toLocaleTimeString('zh-CN', { hour12: false })
    : ''
  const message = item.message || ''
  
  let type = ''
  if (message.includes('成功') || message.includes('完成')) type = 'success'
  else if (message.includes('失败') || message.includes('错误')) type = 'error'
  else if (message.includes('警告')) type = 'warning'
  
  return { time, message, type }
}

// 复制任务 ID
const copyTaskId = async () => {
  try {
    await navigator.clipboard.writeText(taskId.value)
    ElMessage.success('任务 ID 已复制')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

// 查询任务进度
const queryTaskProgress = async () => {
  if (!taskId.value) {
    ElMessage.warning('请输入任务 ID')
    return
  }

  queryLoading.value = true
  try {
    const response = await fetch(`/fpa-generator/api/task-status/${taskId.value}`)
    const result = await response.json()

    if (result.success) {
      const data = result.data
      taskStatus.value = data.status || ''
      progressDisplay.visible = true
      progressDisplay.percentage = data.progress || 0
      progressDisplay.message = data.message || ''
      
      // 设置进度条状态
      if (data.status === 'COMPLETED') {
        progressDisplay.status = 'success'
        downloadUrl.value = data.download_url || ''
        // 停止轮询
        if (pollingTimer) {
          clearInterval(pollingTimer)
          pollingTimer = null
        }
        
        // 刷新历史记录
        loadExportHistory(1)
        
        // 保留任务 ID 和进度显示，方便用户查看和下载
        ElMessage.success('任务完成！请在历史记录中下载文件')
        
      } else if (data.status === 'FAILED') {
        progressDisplay.status = 'exception'
        // 停止轮询
        if (pollingTimer) {
          clearInterval(pollingTimer)
          pollingTimer = null
        }
        
        // 保留任务 ID 和进度显示，方便用户查看错误日志
        ElMessage.error('任务失败，请检查日志或重试')
        
      } else if (data.status === 'CANCELLED') {
        progressDisplay.status = 'warning'
        // 停止轮询
        if (pollingTimer) {
          clearInterval(pollingTimer)
          pollingTimer = null
        }
      } else {
        progressDisplay.status = ''
        // 继续轮询
        if (!pollingTimer) {
          pollingTimer = setInterval(() => {
            queryTaskProgress()
          }, 3000)
        }
      }

      // 更新日志
      if (data.logs && data.logs.length > 0) {
        taskLogs.value = data.logs
      }
    } else {
      ElMessage.error(result.message || '查询失败')
    }
  } catch (error) {
    console.error('查询错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    queryLoading.value = false
  }
}

// 取消任务
const cancelTask = async () => {
  try {
    await ElMessageBox.confirm('确定要停止该任务吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`/fpa-generator/api/task-cancel/${taskId.value}`, {
      method: 'POST',
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('任务已停止')
      // 停止轮询
      if (pollingTimer) {
        clearInterval(pollingTimer)
        pollingTimer = null
      }
      // 查询最新状态
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

// 文件变化处理（可靠地跟踪文件状态）
const handleFileChange = (file, fileList) => {
  if (fileList.length > 0) {
    selectedFile.value = fileList[fileList.length - 1].raw
    ElMessage.success(`已选择文件: ${file.name}`)
  } else {
    selectedFile.value = null
  }
}

// 上传前确认（用于文件替换逻辑）
const beforeUpload = (file) => {
  if (selectedFile.value) {
    // 已有文件，弹窗确认是否替换，并对比文件名
    return new Promise((resolve, reject) => {
      ElMessageBox.confirm(
        `当前已选择文件：${selectedFile.value.name}\n\n是否替换为新文件：${file.name}？`,
        '文件替换确认',
        {
          confirmButtonText: '确认替换',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(() => {
          // file 是 Element Plus 的 File 包装对象，需要取 .raw
          selectedFile.value = file.raw || file
          ElMessage.success(`已替换为：${file.name}`)
          resolve(true) // 允许文件加入上传列表
        })
        .catch(() => {
          ElMessage.info('已取消替换')
          reject(false) // 阻止文件加入上传列表
        })
    })
  } else {
    // 首次上传，直接保存
    selectedFile.value = file.raw || file
    return true
  }
}

// 移除文件
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
  // selectedFile.value 已经是原生 File 对象，直接使用
  formData.append('requirement_file', selectedFile.value)

  try {
    const response = await fetch('/fpa-generator/api/generate-async', {
      method: 'POST',
      body: formData,
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('任务已提交，正在后台处理')
      taskId.value = result.task_id
      startPolling(taskId.value)
      // 立即刷新历史记录
      loadExportHistory(1)
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

// 开始轮询进度
const startPolling = (id) => {
  if (pollingTimer) clearInterval(pollingTimer)
  progressDisplay.visible = true
  
  // 立即查询一次
  queryTaskProgress()
  
  // 每 3 秒轮询一次
  pollingTimer = setInterval(() => {
    queryTaskProgress()
  }, 3000)
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
  // 如果用户正在编辑调整后工作量，跳过正向计算
  if (effortInputChanged.value) {
    return
  }
  
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
  
  // 预计功能点数量（使用 1.66 作为平均每功能点 AFP）
  const expectedPoints = Math.max(1, Math.round(afp / 1.66))
  evaluationResults.value[10].value = expectedPoints
}

// 从调整后工作量反向计算 AFP
const calculateFromEffort = (adjustedEffort) => {
  const cf = adjustmentFactors.value[0].value
  const pdr = evaluationResults.value[3].value
  const appType = adjustmentFactors.value[1].value
  const qualityFactors = adjustmentFactors.value.slice(2, 6)
  const qualitySum = qualityFactors.reduce((sum, f) => sum + f.value, 0)
  const qualityFactor = 1 + (qualitySum * 0.01)
  const language = adjustmentFactors.value[6].value
  const team = adjustmentFactors.value[7].value
  
  const totalFactor = appType * qualityFactor * language * team
  
  // 反向计算
  const unadjustedEffort = adjustedEffort / totalFactor
  const adjustedScale = (unadjustedEffort * 8) / pdr
  const afp = adjustedScale / cf
  
  return {
    afp: afp,
    adjusted_scale: adjustedScale,
    unadjusted_effort: unadjustedEffort
  }
}

// 监听调整后工作量的变化
const effortInputChanged = ref(false)

// 处理调整后工作量的变化（反向计算）
const handleEffortChange = () => {
  const adjustedEffort = evaluationResults.value[9].value
  
  if (adjustedEffort > 0) {
    effortInputChanged.value = true
    
    const result = calculateFromEffort(adjustedEffort)
    
    // 更新其他字段
    evaluationResults.value[0].value = parseFloat(result.afp.toFixed(2))
    evaluationResults.value[2].value = parseFloat(result.adjusted_scale.toFixed(2))
    evaluationResults.value[4].value = parseFloat(result.unadjusted_effort.toFixed(2))
    
    // 重新计算预计功能点数量
    const expectedPoints = Math.max(1, Math.round(result.afp / 1.66))
    evaluationResults.value[10].value = expectedPoints
    
    console.log(`反向计算：调整后工作量=${adjustedEffort}, 目标 AFP=${result.afp.toFixed(2)}`)
  }
}

// 监听评估结果变化，自动保存
let autoSaveTimer = null
const autoSaveEvaluationResult = () => {
  if (autoSaveTimer) {
    clearTimeout(autoSaveTimer)
  }
  
  autoSaveTimer = setTimeout(() => {
    recalculateEvaluation()
    saveEvaluationResult()
    saveStatus.value = '✓ 已自动保存'
    setTimeout(() => {
      saveStatus.value = ''
    }, 2000)
  }, 500)
}

// 加载评估结果
const loadEvaluationResult = async () => {
  try {
    const response = await fetch('/fpa-generator/api/evaluation-result')
    const result = await response.json()
    
    if (result.success && result.data) {
      const data = result.data
      // 映射数据库字段到 Vue 组件状态
      evaluationResults.value[0].value = data.afp || 125.27
      adjustmentFactors.value[0].value = data.cf || 1.21
      evaluationResults.value[2].value = data.adjusted_scale || 151.57
      evaluationResults.value[3].value = data.base_productivity || 10.12
      evaluationResults.value[4].value = data.unadjusted_effort || 191.74
      evaluationResults.value[5].value = data.factor_application_type || 1.00
      evaluationResults.value[6].value = data.factor_quality || 0.90
      evaluationResults.value[7].value = data.factor_language || 1.00
      evaluationResults.value[8].value = data.factor_team || 0.80
      evaluationResults.value[9].value = data.adjusted_effort || 138.05
      
      // 同步更新下拉框的选中项（如果需要）
      // ...此处省略复杂的下拉框同步逻辑，先保证数值加载...
      
      recalculateEvaluation()
    }
  } catch (error) {
    console.error('加载评估结果失败:', error)
  }
}

// 保存评估结果
const saveEvaluationResult = async () => {
  saveStatus.value = '保存中...'
  
  try {
    // 从评估结果中提取数据
    const evaluationData = {
      requirement_code: 'default',
      requirement_name: '默认需求',
      afp: evaluationResults.value[0].value,
      cf: adjustmentFactors.value[0].value,
      adjusted_scale: evaluationResults.value[2].value,
      base_productivity: evaluationResults.value[3].value,
      unadjusted_effort: evaluationResults.value[4].value,
      factor_application_type: adjustmentFactors.value[1].value,
      factor_quality: evaluationResults.value[6].value,
      factor_language: adjustmentFactors.value[6].value,
      factor_team: adjustmentFactors.value[7].value,
      adjusted_effort: evaluationResults.value[9].value,
    }

    const response = await fetch('/fpa-generator/api/evaluation-result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(evaluationData),
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
    const response = await fetch(`/fpa-generator/api/export-history?page=${page}&per_page=${pageSize.value}`)
    const result = await response.json()

    if (result.success && result.data) {
      // 适配后端返回的数据结构: result.data.list
      exportHistory.value = result.data.list || []
      totalRecords.value = result.data.total || 0
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
  if (status === 'COMPLETED') return 'success'
  if (status === 'FAILED') return 'exception'
  if (status === 'CANCELLED') return 'warning'
  return ''
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    'PENDING': 'info',
    'RUNNING': 'warning',
    'COMPLETED': 'success',
    'FAILED': 'danger',
    'CANCELLED': 'info',
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const map = {
    'PENDING': '等待中',
    'RUNNING': '运行中',
    'COMPLETED': '已完成',
    'FAILED': '失败',
    'CANCELLED': '已取消',
  }
  return map[status] || status
}

// 下载历史文件
const downloadHistoryFile = (row) => {
  // 使用 output_filename 拼接下载链接
  if (row.output_filename) {
    window.open(`/fpa-generator/download/${row.output_filename}`, '_blank')
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

    const response = await fetch(`/fpa-generator/api/task-cancel/${taskId}`, {
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

// 删除历史记录
const deleteHistory = async (taskId) => {
  try {
    await ElMessageBox.confirm(`确定要删除这条历史记录吗？\n任务 ID：${taskId}\n此操作不可恢复！`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    const response = await fetch(`/fpa-generator/api/export-history/${taskId}`, {
      method: 'DELETE',
    })
    const result = await response.json()

    if (result.success) {
      ElMessage.success('删除成功')
      loadExportHistory(currentPage.value)
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除错误:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  }
}

// 格式化时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  // 将 MySQL DATETIME 格式 (2026-04-15 10:30:00) 转换为 ISO 8601 格式
  // 避免 JavaScript Date 解析兼容性问题
  const isoDateStr = String(dateStr).replace(' ', 'T')
  const date = new Date(isoDateStr)
  
  // 检查日期是否有效
  if (isNaN(date.getTime())) return '-'
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

// 打开规则管理
const router = useRouter()
const openRulesManagement = () => {
  router.push('/fpa-category-rules')
}

// 初始化
onMounted(() => {
  loadExportHistory(1)
  loadEvaluationResult() // 从数据库加载评估结果
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

/* 使用指南样式 */
.guide-card {
  margin-bottom: 25px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.guide-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
}

.guide-content h4 {
  font-size: 18px;
  color: #303133;
  margin: 20px 0 15px 0;
  font-weight: 600;
}

.guide-content h4:first-child {
  margin-top: 0;
}

.guide-steps {
  padding-left: 20px;
  line-height: 1.8;
}

.guide-steps li {
  margin-bottom: 15px;
  color: #606266;
}

.guide-steps li strong {
  color: #303133;
  font-size: 15px;
}

.guide-steps ul {
  margin-top: 8px;
  padding-left: 20px;
}

.guide-steps ul li {
  margin-bottom: 5px;
  font-size: 14px;
}

.format-example {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 20px;
  margin-top: 15px;
  overflow-x: auto;
}

.format-example code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
  white-space: pre-wrap;
}

.mt-4 {
  margin-top: 20px;
}

/* 任务进度查询样式 */
.progress-status {
  text-align: center;
  margin-top: 10px;
  font-size: 15px;
  font-weight: 600;
}

.progress-status.status-success {
  color: #67c23a;
}

.progress-status.status-exception {
  color: #f56c6c;
}

.progress-status.status-warning {
  color: #e6a23c;
}

.log-title {
  font-size: 16px;
  color: #303133;
  margin-bottom: 10px;
  font-weight: 600;
}

.log-container {
  max-height: 350px;
  overflow-y: auto;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.8;
}

.log-item {
  padding: 6px 10px;
  border-bottom: 1px dashed #e4e7ed;
  color: #606266;
  display: flex;
  align-items: baseline;
  gap: 12px;
  line-height: 1.6;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #909399;
  font-size: 12px;
  font-weight: 500;
  min-width: 75px;
  flex-shrink: 0;
}

.log-message {
  flex: 1;
  word-break: break-word;
}

.log-success .log-message {
  color: #67c23a;
}

.log-error .log-message {
  color: #f56c6c;
}

.log-warning .log-message {
  color: #e6a23c;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  padding: 10px 0;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background: #fafafa;
}

:deep(.el-table__empty-block) {
  min-height: 200px;
}
</style>
