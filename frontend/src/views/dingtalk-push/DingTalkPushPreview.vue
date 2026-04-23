<!-- frontend/src/views/dingtalk-push/DingTalkPushPreview.vue -->
<template>
  <div class="dingtalk-push-preview">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>消息预览</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：配置面板 -->
        <el-col :span="10">
          <el-card shadow="never">
            <template #header>模拟数据配置</template>
            
            <el-form label-width="100px">
              <el-form-item label="消息类型">
                <el-radio-group v-model="previewConfig.message_type">
                  <el-radio label="markdown">Markdown</el-radio>
                  <el-radio label="actionCard">ActionCard</el-radio>
                  <el-radio label="text">Text</el-radio>
                </el-radio-group>
              </el-form-item>
              
              <el-form-item label="模板内容">
                <el-input
                  v-model="previewConfig.template_content"
                  type="textarea"
                  :rows="8"
                  placeholder="输入 Jinja2 模板"
                />
              </el-form-item>
              
              <el-form-item label="模拟数据">
                <el-input
                  v-model="sampleDataJson"
                  type="textarea"
                  :rows="10"
                  placeholder="JSON 格式的模拟数据"
                />
                <div style="margin-top: 5px">
                  <el-button size="small" @click="loadSampleData">加载示例</el-button>
                  <el-button size="small" @click="formatJson">格式化</el-button>
                </div>
              </el-form-item>
              
              <el-form-item label="@人员">
                <el-tag
                  v-for="(mobile, index) in previewConfig.at_mobiles"
                  :key="index"
                  closable
                  @close="removeMobile(index)"
                  style="margin-right: 5px"
                >
                  {{ mobile }}
                </el-tag>
                <el-input
                  v-model="newMobile"
                  placeholder="手机号"
                  size="small"
                  style="width: 150px; margin-left: 5px"
                  @keyup.enter="addMobile"
                />
              </el-form-item>
              
              <el-form-item label="@所有人">
                <el-switch v-model="previewConfig.at_all" />
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="updatePreview">刷新预览</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 右侧：预览效果 -->
        <el-col :span="14">
          <el-card shadow="never">
            <template #header>
              <span>预览效果</span>
              <el-button size="small" @click="showJsonDialog">查看 JSON</el-button>
            </template>
            
            <div v-if="previewResult" class="preview-content">
              <!-- Markdown 预览 -->
              <div v-if="previewConfig.message_type === 'markdown'" class="markdown-preview">
                <div v-html="renderedMarkdown"></div>
              </div>
              
              <!-- Text 预览 -->
              <div v-else-if="previewConfig.message_type === 'text'" class="text-preview">
                <pre>{{ previewResult.rendered_content }}</pre>
              </div>
              
              <!-- ActionCard 预览 -->
              <div v-else-if="previewConfig.message_type === 'actionCard'" class="actioncard-preview">
                <el-card>
                  <h3>{{ previewResult.message_json.actionCard?.title || '标题' }}</h3>
                  <div v-html="renderedMarkdown"></div>
                </el-card>
              </div>
              
              <el-divider />
              
              <div class="preview-info">
                <el-tag size="small">使用的变量: {{ previewResult.variables_used.join(', ') || '无' }}</el-tag>
                <el-tag v-if="previewResult.warnings.length" type="warning" size="small">
                  警告: {{ previewResult.warnings.join(', ') }}
                </el-tag>
              </div>
            </div>
            
            <el-empty v-else description="点击“刷新预览”查看效果" />
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- JSON 对话框 -->
    <el-dialog v-model="jsonDialogVisible" title="最终 JSON 结构" width="600px">
      <pre class="json-code">{{ formatJsonDisplay() }}</pre>
      <template #footer>
        <el-button @click="copyJson">复制 JSON</el-button>
        <el-button type="primary" @click="jsonDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

const previewConfig = ref({
  message_type: 'markdown',
  template_content: '',
  at_mobiles: [],
  at_all: false
})

const sampleDataJson = ref('{}')
const newMobile = ref('')
const previewResult = ref(null)
const jsonDialogVisible = ref(false)

// 渲染 Markdown
const renderedMarkdown = computed(() => {
  if (!previewResult.value) return ''
  return marked(previewResult.value.rendered_content || '')
})

// 加载示例数据
const loadSampleData = () => {
  const sampleData = {
    today: '2026-04-21',
    weekday: '周二',
    tomorrow: '2026-04-22',
    tomorrow_weekday: '周三',
    schedule: [
      { time: '8:00-9:00', staff: '张三' },
      { time: '9:00-12:00', staff: '李四' },
      { time: '13:30-18:00', staff: '王五' }
    ]
  }
  
  sampleDataJson.value = JSON.stringify(sampleData, null, 2)
}

// 格式化 JSON
const formatJson = () => {
  try {
    const data = JSON.parse(sampleDataJson.value)
    sampleDataJson.value = JSON.stringify(data, null, 2)
  } catch (error) {
    ElMessage.error('JSON 格式错误')
  }
}

// 添加手机号
const addMobile = () => {
  if (newMobile.value && !previewConfig.value.at_mobiles.includes(newMobile.value)) {
    previewConfig.value.at_mobiles.push(newMobile.value)
    newMobile.value = ''
  }
}

// 删除手机号
const removeMobile = (index) => {
  previewConfig.value.at_mobiles.splice(index, 1)
}

// 更新预览
const updatePreview = async () => {
  try {
    let sampleData = {}
    try {
      sampleData = JSON.parse(sampleDataJson.value)
    } catch (error) {
      ElMessage.error('模拟数据 JSON 格式错误')
      return
    }
    
    const res = await axios.post('/dingtalk-push/preview', {
      message_type: previewConfig.value.message_type,
      template_content: previewConfig.value.template_content,
      sample_data: sampleData,
      at_mobiles: previewConfig.value.at_mobiles,
      at_all: previewConfig.value.at_all
    })
    
    if (res.data.success) {
      previewResult.value = res.data.data
      ElMessage.success('预览已更新')
    } else {
      ElMessage.error(res.data.msg || '预览失败')
    }
  } catch (error) {
    ElMessage.error('预览失败')
    console.error(error)
  }
}

// 显示 JSON 对话框
const showJsonDialog = () => {
  jsonDialogVisible.value = true
}

// 格式化 JSON 显示
const formatJsonDisplay = () => {
  if (!previewResult.value) return '{}'
  return JSON.stringify(previewResult.value.message_json, null, 2)
}

// 复制 JSON
const copyJson = () => {
  const jsonStr = formatJsonDisplay()
  navigator.clipboard.writeText(jsonStr).then(() => {
    ElMessage.success('已复制到剪贴板')
  })
}

// 加载配置（如果从列表页进入）
const loadConfig = async () => {
  const configId = route.params.id
  
  if (!configId) {
    // 默认加载示例
    loadSampleData()
    previewConfig.value.template_content = `# 📅 排班信息推送

### **今天** {{ today }} ({{ weekday }})
{% for slot in schedule %}
- **{{ slot.time }}**: {{ slot.staff }}
{% endfor %}`
    return
  }
  
  try {
    const res = await axios.get(`/dingtalk-push/configs/${configId}`)
    
    if (res.data.success) {
      const config = res.data.data
      
      previewConfig.value = {
        message_type: config.message_type,
        template_content: config.template_content,
        at_mobiles: JSON.parse(config.at_mobiles || '[]'),
        at_all: config.at_all
      }
      
      // 尝试获取示例数据
      loadSampleData()
    }
  } catch (error) {
    console.error(error)
  }
}

// 返回
const goBack = () => {
  router.push('/dingtalk-push')
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.dingtalk-push-preview {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-content {
  min-height: 300px;
}

.markdown-preview,
.text-preview,
.actioncard-preview {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.text-preview pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.preview-info {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.json-code {
  background: #282c34;
  color: #abb2bf;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 400px;
}
</style>
