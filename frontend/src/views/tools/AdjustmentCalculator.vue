<template>
  <div class="adjustment-calculator">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span><el-icon><Calculator /></el-icon> 调整因子计算器</span>
          <el-button type="primary" @click="showConfigDialog">
            <el-icon><Setting /></el-icon> 规模计数时机配置
          </el-button>
        </div>
      </template>

      <!-- 计算器表单 -->
      <el-form :model="form" label-width="180px" class="calculator-form">
        <!-- 规模计数时机 -->
        <el-form-item label="规模计数时机">
          <el-select v-model="form.scale_timing" style="width: 100%">
            <el-option
              v-for="item in scaleTimingOptions"
              :key="item.option_name"
              :label="`${item.option_name} - ${item.score_value}`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <!-- 应用类型 -->
        <el-form-item label="应用类型">
          <el-select v-model="form.application_type" style="width: 100%">
            <el-option
              v-for="item in applicationTypeOptions"
              :key="item.option_name"
              :label="`${item.option_name} - ${item.score_value}`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <!-- 质量特性 -->
        <el-divider content-position="left">质量特性</el-divider>
        
        <el-form-item label="分布式处理">
          <el-select v-model="form.distributed_processing" style="width: 100%">
            <el-option
              v-for="item in distributedProcessingOptions"
              :key="item.option_name"
              :label="`${item.option_name} (${item.score_value})`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="性能">
          <el-select v-model="form.performance" style="width: 100%">
            <el-option
              v-for="item in performanceOptions"
              :key="item.option_name"
              :label="`${item.option_name} (${item.score_value})`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="可靠性">
          <el-select v-model="form.reliability" style="width: 100%">
            <el-option
              v-for="item in reliabilityOptions"
              :key="item.option_name"
              :label="`${item.option_name} (${item.score_value})`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="多重站点">
          <el-select v-model="form.multi_site" style="width: 100%">
            <el-option
              v-for="item in multiSiteOptions"
              :key="item.option_name"
              :label="`${item.option_name} (${item.score_value})`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <!-- 开发语言 -->
        <el-divider content-position="left">开发环境</el-divider>

        <el-form-item label="开发语言">
          <el-select v-model="form.language" style="width: 100%">
            <el-option
              v-for="item in languageOptions"
              :key="item.option_name"
              :label="`${item.option_name} - ${item.score_value}`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="开发团队背景">
          <el-select v-model="form.team_background" style="width: 100%">
            <el-option
              v-for="item in teamBackgroundOptions"
              :key="item.option_name"
              :label="`${item.option_name} - ${item.score_value}`"
              :value="item.option_name"
            />
          </el-select>
        </el-form-item>

        <!-- 修改类型和重用程度 -->
        <el-divider content-position="left">其他因素</el-divider>

        <el-form-item label="修改类型">
          <el-select v-model="form.change_type" style="width: 100%">
            <el-option label="新增 - 本期项目新增的功能模块" value="新增" />
            <el-option label="修改 - 修改往期项目的功能模块" value="修改" />
            <el-option label="删除 - 删除往期项目的功能模块" value="删除" />
          </el-select>
        </el-form-item>

        <el-form-item label="重用程度">
          <el-select v-model="form.reuse_level" style="width: 100%">
            <el-option label="低" value="低" />
            <el-option label="中" value="中" />
            <el-option label="高" value="高" />
          </el-select>
        </el-form-item>

        <!-- 计算按钮 -->
        <el-form-item>
          <el-button type="primary" size="large" @click="calculate" :loading="calculating" style="width: 100%;">
            <el-icon><VideoPlay /></el-icon> 计算总调整因子
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 计算结果 -->
      <el-card v-if="result" class="result-card" shadow="hover">
        <template #header>
          <div class="result-header">
            <span><el-icon><TrendCharts /></el-icon> 计算结果</span>
          </div>
        </template>

        <div class="result-content">
          <div class="result-item">
            <span class="result-label">规模变更调整因子 (CF):</span>
            <span class="result-value">{{ result.scale_factor }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">应用类型调整因子:</span>
            <span class="result-value">{{ result.application_factor }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">质量特性调整因子:</span>
            <span class="result-value">{{ result.quality_factor }}</span>
          </div>
          <div class="result-detail">
            <small>分布式处理: {{ result.quality_details?.distributed || 0 }}</small><br>
            <small>性能: {{ result.quality_details?.performance || 0 }}</small><br>
            <small>可靠性: {{ result.quality_details?.reliability || 0 }}</small><br>
            <small>多重站点: {{ result.quality_details?.multi_site || 0 }}</small>
          </div>
          <div class="result-item">
            <span class="result-label">开发语言调整因子:</span>
            <span class="result-value">{{ result.language_factor }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">开发团队背景调整因子:</span>
            <span class="result-value">{{ result.team_factor }}</span>
          </div>
          <el-divider />
          <div class="result-item total">
            <span class="result-label">总调整因子:</span>
            <span class="result-value highlight">{{ result.total_factor }}</span>
          </div>
        </div>
      </el-card>
    </el-card>

    <!-- 配置对话框 -->
    <el-dialog
      v-model="configDialogVisible"
      title="规模计数时机配置"
      width="700px"
    >
      <el-table :data="scaleTimingConfigs" stripe style="width: 100%">
        <el-table-column prop="option_name" label="选项名称" min-width="200" />
        <el-table-column prop="score_value" label="分值" width="100" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="editConfig(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-divider />
      
      <el-form :model="configForm" label-width="100px">
        <el-form-item label="选项名称">
          <el-input v-model="configForm.option_name" placeholder="请输入选项名称" />
        </el-form-item>
        <el-form-item label="分值">
          <el-input-number v-model="configForm.score_value" :precision="2" :step="0.01" :min="0" :max="10" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="savingConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calculator, Setting, VideoPlay, TrendCharts } from '@element-plus/icons-vue'

const form = reactive({
  scale_timing: '估算中期',
  application_type: '业务处理',
  distributed_processing: '',
  performance: '',
  reliability: '',
  multi_site: '',
  language: '',
  team_background: '',
  change_type: '新增',
  reuse_level: '低'
})

const result = ref(null)
const calculating = ref(false)
const configDialogVisible = ref(false)
const savingConfig = ref(false)

// 下拉选项数据
const scaleTimingOptions = ref([])
const applicationTypeOptions = ref([])
const distributedProcessingOptions = ref([])
const performanceOptions = ref([])
const reliabilityOptions = ref([])
const multiSiteOptions = ref([])
const languageOptions = ref([])
const teamBackgroundOptions = ref([])

// 配置相关
const scaleTimingConfigs = ref([])
const configForm = reactive({
  id: null,
  option_name: '',
  score_value: 0
})

// 加载计算器数据
const loadCalculatorData = async () => {
  try {
    const response = await fetch('/adjustment-calc/api/calculator-data')
    const data = await response.json()
    
    if (data.success) {
      // 分组存储选项
      data.data.forEach(item => {
        switch(item.factor_category) {
          case '规模计数时机':
            scaleTimingOptions.value.push(item)
            break
          case '应用类型':
            applicationTypeOptions.value.push(item)
            break
          case '分布式处理':
            distributedProcessingOptions.value.push(item)
            break
          case '性能':
            performanceOptions.value.push(item)
            break
          case '可靠性':
            reliabilityOptions.value.push(item)
            break
          case '多重站点':
            multiSiteOptions.value.push(item)
            break
          case '开发语言':
            languageOptions.value.push(item)
            break
          case '开发团队背景':
            teamBackgroundOptions.value.push(item)
            break
        }
      })
      
      // 设置默认值
      if (scaleTimingOptions.value.length > 0) {
        form.scale_timing = scaleTimingOptions.value.find(o => o.option_name === '估算中期')?.option_name || scaleTimingOptions.value[0].option_name
      }
      if (applicationTypeOptions.value.length > 0) {
        form.application_type = applicationTypeOptions.value.find(o => o.option_name === '业务处理')?.option_name || applicationTypeOptions.value[0].option_name
      }
    } else {
      ElMessage.error(data.message || '加载数据失败')
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  }
}

// 执行计算
const calculate = async () => {
  calculating.value = true
  
  try {
    const response = await fetch('/adjustment-calc/api/calculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form)
    })
    
    const data = await response.json()
    
    if (data.success) {
      result.value = data.result
      ElMessage.success('计算完成')
    } else {
      ElMessage.error(data.message || '计算失败')
    }
  } catch (error) {
    console.error('计算失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    calculating.value = false
  }
}

// 显示配置对话框
const showConfigDialog = async () => {
  configDialogVisible.value = true
  await loadScaleTimingConfigs()
}

// 加载规模计数时机配置
const loadScaleTimingConfigs = async () => {
  try {
    const response = await fetch('/adjustment-calc/api/scale-timing-config')
    const data = await response.json()
    
    if (data.success) {
      scaleTimingConfigs.value = data.configs || []
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

// 编辑配置
const editConfig = (row) => {
  Object.assign(configForm, {
    id: row.id,
    option_name: row.option_name,
    score_value: row.score_value
  })
}

// 保存配置
const saveConfig = async () => {
  if (!configForm.option_name) {
    ElMessage.warning('请输入选项名称')
    return
  }
  
  savingConfig.value = true
  
  try {
    const url = configForm.id ? `/adjustment-calc/api/scale-timing-config/${configForm.id}` : '/adjustment-calc/api/scale-timing-config'
    const method = configForm.id ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(configForm)
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success('保存成功')
      Object.assign(configForm, { id: null, option_name: '', score_value: 0 })
      await loadScaleTimingConfigs()
      await loadCalculatorData() // 重新加载计算器数据
    } else {
      ElMessage.error(data.message || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    savingConfig.value = false
  }
}

onMounted(() => {
  loadCalculatorData()
})
</script>

<style scoped>
.adjustment-calculator {
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

.calculator-form {
  max-width: 900px;
  margin: 0 auto;
}

.result-card {
  margin-top: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.result-header {
  font-size: 16px;
  font-weight: bold;
}

.result-content {
  padding: 10px 0;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.result-item:last-child {
  border-bottom: none;
}

.result-item.total {
  font-size: 18px;
  font-weight: bold;
  margin-top: 10px;
}

.result-label {
  font-weight: 500;
}

.result-value {
  font-weight: bold;
}

.result-value.highlight {
  font-size: 24px;
  color: #ffd700;
}

.result-detail {
  padding-left: 20px;
  margin-top: 10px;
  opacity: 0.9;
}

.result-detail small {
  display: block;
  margin: 5px 0;
}
</style>
