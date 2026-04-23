<!-- frontend/src/views/dingtalk-push/DingTalkPushConfig.vue -->
<template>
  <div class="dingtalk-push-config">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑推送任务' : '新建推送任务' }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <!-- 步骤1: 基础配置 -->
        <h3>步骤 1/4: 基础配置</h3>
        
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        
        <el-form-item label="任务描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入任务描述" />
        </el-form-item>
        
        <el-form-item label="任务分类">
          <el-select v-model="form.category">
            <el-option label="排班" value="roster" />
            <el-option label="告警" value="alert" />
            <el-option label="日报" value="report" />
            <el-option label="其他" value="general" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Webhook URL" prop="webhook_url">
          <el-input v-model="form.webhook_url" placeholder="https://oapi.dingtalk.com/robot/send?access_token=xxx" />
          <el-button size="small" @click="testWebhook" style="margin-left: 10px">测试连接</el-button>
        </el-form-item>
        
        <el-form-item label="加签密钥">
          <el-input v-model="form.secret_key" placeholder="可选" />
        </el-form-item>
        
        <el-form-item label="推送对象">
          <el-radio-group v-model="atType">
            <el-radio label="all">@所有人</el-radio>
            <el-radio label="specific">@指定人员</el-radio>
          </el-radio-group>
          
          <div v-if="atType === 'specific'" style="margin-top: 10px">
            <el-tag
              v-for="(mobile, index) in form.at_mobiles"
              :key="index"
              closable
              @close="removeMobile(index)"
              style="margin-right: 5px"
            >
              {{ mobile }}
            </el-tag>
            <el-input
              v-model="newMobile"
              placeholder="输入手机号后按回车"
              size="small"
              style="width: 200px"
              @keyup.enter="addMobile"
            />
          </div>
        </el-form-item>

        <!-- 步骤2: 消息配置 -->
        <h3 style="margin-top: 30px">步骤 2/4: 消息配置</h3>
        
        <el-form-item label="消息类型">
          <el-radio-group v-model="form.message_type">
            <el-radio label="markdown">Markdown</el-radio>
            <el-radio label="actionCard">ActionCard</el-radio>
            <el-radio label="text">Text</el-radio>
          </el-radio-group>
          <el-button size="small" type="primary" link @click="showDemo" style="margin-left: 10px">
            查看示例
          </el-button>
        </el-form-item>
        
        <el-form-item label="模板内容" prop="template_content">
          <el-input
            v-model="form.template_content"
            type="textarea"
            :rows="10"
            placeholder="支持 Jinja2 模板语法，例如：{{ now }}"
          />
          <div style="margin-top: 5px; color: #e6a23c; font-size: 12px">
            ⚠️ 重要：变量必须使用双大括号语法，如 <code>{{ now }}</code>、<code>{{ variable }}</code>，否则会被当作普通文本处理
          </div>
        </el-form-item>
        
        <el-form-item label="数据源类型">
          <el-select v-model="dataSourceType">
            <el-option label="静态数据" value="static" />
            <el-option label="API" value="api" />
            <el-option label="SQL查询" value="sql" />
          </el-select>
        </el-form-item>

        <!-- 步骤3: 调度配置 -->
        <h3 style="margin-top: 30px">步骤 3/4: 调度配置</h3>
        
        <el-form-item label="调度类型">
          <el-select v-model="scheduleType">
            <el-option label="单次推送" value="once" />
            <el-option label="每日推送" value="daily" />
            <el-option label="每周推送" value="weekly" />
            <el-option label="Cron表达式" value="cron" />
          </el-select>
        </el-form-item>
        
        <el-form-item v-if="scheduleType === 'daily'" label="推送时间">
          <el-time-picker
            v-model="dailyTimes"
            is-range
            format="HH:mm"
            value-format="HH:mm"
            placeholder="选择时间"
          />
        </el-form-item>
        
        <el-form-item v-if="scheduleType === 'daily'" label="工作日过滤">
          <el-checkbox v-model="excludeHolidays">仅工作日（排除节假日）</el-checkbox>
        </el-form-item>
        
        <el-form-item v-if="scheduleType === 'cron'" label="推送时间">
          <div class="mb-2">
            <el-tag
              v-for="(time, index) in cronTimes"
              :key="index"
              closable
              @close="removeCronTime(index)"
              class="mr-2 mb-2"
            >
              {{ time }}
            </el-tag>
          </div>
          <el-time-picker
            v-model="newCronTime"
            format="HH:mm"
            value-format="HH:mm"
            placeholder="选择推送时间"
            style="width: 150px;"
          />
          <el-button type="primary" size="small" @click="addCronTime" class="ml-2">
            添加时间
          </el-button>
          <div class="text-sm text-gray-500 mt-2">例如：08:00、09:00、18:00，系统将每天在这些时间自动推送</div>
        </el-form-item>
        
        <el-form-item v-if="scheduleType === 'cron'" label="Cron 表达式">
          <el-input v-model="cronExpression" placeholder="自动生成" readonly>
            <template #prepend>Cron</template>
          </el-input>
          <div class="text-sm text-gray-500 mt-2">根据上方选择的推送时间自动生成，格式：秒 分 时 * * ?</div>
        </el-form-item>
        
        <el-form-item v-if="scheduleType === 'cron'" label="执行周期">
          <el-checkbox-group v-model="cronWeekdays">
            <el-checkbox :value="1">周一</el-checkbox>
            <el-checkbox :value="2">周二</el-checkbox>
            <el-checkbox :value="3">周三</el-checkbox>
            <el-checkbox :value="4">周四</el-checkbox>
            <el-checkbox :value="5">周五</el-checkbox>
            <el-checkbox :value="6">周六</el-checkbox>
            <el-checkbox :value="7">周日</el-checkbox>
          </el-checkbox-group>
          <div class="text-sm text-gray-500 mt-2">不选则默认每天执行</div>
        </el-form-item>

        <!-- 步骤4: 高级配置 -->
        <h3 style="margin-top: 30px">步骤 4/4: 高级配置</h3>
        
        <el-form-item label="最大重试次数">
          <el-input-number v-model="form.max_retries" :min="0" :max="10" />
        </el-form-item>
        
        <el-form-item label="超时时间(秒)">
          <el-input-number v-model="form.timeout_seconds" :min="1" :max="60" />
        </el-form-item>
        
        <el-form-item label="启用状态">
          <el-switch v-model="form.enabled" />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '保存' : '创建' }}
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 示例对话框 -->
    <el-dialog v-model="demoVisible" title="消息模板示例" width="70%">
      <el-tabs v-model="activeDemoTab">
        <!-- Markdown 示例 -->
        <el-tab-pane label="Markdown" name="markdown">
          <div class="demo-content">
            <h4>适用场景：</h4>
            <p>适合发送富文本内容，支持标题、列表、链接、代码块等格式。</p>
            
            <h4>示例模板：</h4>
            <pre class="code-block"># 📊 日报推送

### **日期**: {{ now }}

---

## 今日工作总结
- 完成功能开发：{{ completed_tasks }} 个
- 修复 Bug：{{ fixed_bugs }} 个
- 代码审查：{{ code_reviews }} 次

## 明日计划
{% for task in tomorrow_tasks %}
- {{ task }}
{% endfor %}

---
> 发送时间：{{ now }}</pre>
            
            <h4>效果预览：</h4>
            <div class="preview-box markdown-preview">
              <h3>📊 日报推送</h3>
              <h4><strong>日期</strong>: 2026-04-22 18:00:00</h4>
              <hr>
              <h3>今日工作总结</h3>
              <ul>
                <li>完成功能开发：5 个</li>
                <li>修复 Bug：3 个</li>
                <li>代码审查：2 次</li>
              </ul>
              <h3>明日计划</h3>
              <ul>
                <li>优化性能</li>
                <li>编写测试用例</li>
              </ul>
              <hr>
              <blockquote>
                <p>发送时间：2026-04-22 18:00:00</p>
              </blockquote>
            </div>
          </div>
        </el-tab-pane>

        <!-- ActionCard 示例 -->
        <el-tab-pane label="ActionCard" name="actionCard">
          <div class="demo-content">
            <h4>适用场景：</h4>
            <p>适合需要用户交互的场景，可以添加按钮跳转到其他页面或执行操作。</p>
            
            <h4>示例模板：</h4>
            <pre class="code-block"># 🔔 告警通知

### 告警级别: <font color="#FF0000">严重</font>

**告警时间**: {{ alert_time }}
**告警对象**: {{ alert_target }}
**告警内容**: {{ alert_message }}

---

请及时处理！

[查看详情](https://example.com/alert/{{ alert_id }})
[确认处理](https://example.com/alert/{{ alert_id }}/ack)</pre>
            
            <h4>效果预览：</h4>
            <div class="preview-box actioncard-preview">
              <h3>🔔 告警通知</h3>
              <h4>告警级别: <span style="color: #FF0000">严重</span></h4>
              <p><strong>告警时间</strong>: 2026-04-22 15:30:00</p>
              <p><strong>告警对象</strong>: 服务器-001</p>
              <p><strong>告警内容</strong>: CPU 使用率超过 90%</p>
              <hr>
              <p>请及时处理！</p>
              <div class="action-buttons">
                <el-button type="primary" size="small">查看详情</el-button>
                <el-button type="success" size="small">确认处理</el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Text 示例 -->
        <el-tab-pane label="Text" name="text">
          <div class="demo-content">
            <h4>适用场景：</h4>
            <p>适合发送简单的纯文本消息，不支持富文本格式。</p>
            
            <h4>示例模板：</h4>
            <pre class="code-block">【打卡提醒】

当前时间：{{ now }}

请记得及时打卡！

温馨提示：
- 上班打卡时间：09:00 前
- 下班打卡时间：18:00 后</pre>
            
            <h4>效果预览：</h4>
            <div class="preview-box text-preview">
              <p>【打卡提醒】</p>
              <p>当前时间：2026-04-22 08:55:00</p>
              <p>请记得及时打卡！</p>
              <p>温馨提示：</p>
              <p>- 上班打卡时间：09:00 前</p>
              <p>- 下班打卡时间：18:00 后</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      
      <template #footer>
        <el-button @click="demoVisible = false">关闭</el-button>
        <el-button type="primary" @click="applyDemo">应用此示例</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const submitting = ref(false)
const isEdit = computed(() => !!route.params.id)

// 表单数据
const form = ref({
  name: '',
  description: '',
  category: 'general',
  webhook_url: '',
  at_mobiles: [],
  at_all: false,
  message_type: 'markdown',
  template_content: '',
  data_source_config: {},
  schedule_config: {},
  timezone: 'Asia/Shanghai',
  enabled: true,
  max_retries: 3,
  timeout_seconds: 10
})

// 辅助变量
const atType = ref('specific')
const newMobile = ref('')
const dataSourceType = ref('static')
const scheduleType = ref('daily')
const dailyTimes = ref([])
const excludeHolidays = ref(true)
const cronTimes = ref([])
const newCronTime = ref('')
const cronExpression = ref('')
const cronWeekdays = ref([1, 2, 3, 4, 5, 6, 7]) // 默认每天

// 示例对话框
const demoVisible = ref(false)
const activeDemoTab = ref('markdown')

// 验证规则
const rules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  webhook_url: [{ required: true, message: '请输入 Webhook URL', trigger: 'blur' }],
  template_content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }]
}

// 添加手机号
const addMobile = () => {
  if (newMobile.value && !form.value.at_mobiles.includes(newMobile.value)) {
    form.value.at_mobiles.push(newMobile.value)
    newMobile.value = ''
  }
}

// 删除手机号
const removeMobile = (index) => {
  form.value.at_mobiles.splice(index, 1)
}

// Cron 时间管理
const addCronTime = () => {
  if (!newCronTime.value) {
    ElMessage.warning('请选择时间')
    return
  }
  
  if (cronTimes.value.includes(newCronTime.value)) {
    ElMessage.warning('该时间已存在')
    return
  }
  
  cronTimes.value.push(newCronTime.value)
  cronTimes.value.sort()
  newCronTime.value = ''
}

const removeCronTime = (index) => {
  cronTimes.value.splice(index, 1)
}

// 自动生成 Cron 表达式（仅用于展示，后端不再使用）
const generateCronExpression = () => {
  if (cronTimes.value.length === 0) {
    cronExpression.value = ''
    return
  }
  
  // 仅展示第一个时间点的 Cron 格式（实际后端会为每个时间点创建独立任务）
  const firstTime = cronTimes.value[0]
  const [hour, minute] = firstTime.split(':')
  
  let dayStr, weekStr
  
  if (cronWeekdays.value.length === 0 || cronWeekdays.value.length === 7) {
    // 每天执行
    dayStr = '*'
    weekStr = '?'
  } else {
    // 指定周几
    dayStr = '?'
    weekStr = cronWeekdays.value.sort().join(',')
  }
  
  cronExpression.value = `0 ${minute} ${hour} ${dayStr} * ${weekStr}`
  if (cronTimes.value.length > 1) {
    cronExpression.value += ` (共${cronTimes.value.length}个时间点)`
  }
}

// 监听 cronTimes 和 cronWeekdays 变化，自动生成表达式
watch([cronTimes, cronWeekdays], () => {
  generateCronExpression()
}, { deep: true })

// 测试 Webhook
const testWebhook = async () => {
  if (!form.value.webhook_url) {
    ElMessage.warning('请先输入 Webhook URL')
    return
  }
  
  try {
    const res = await axios.post('/dingtalk-push/test-webhook', {
      webhook_url: form.value.webhook_url,
      secret_key: form.value.secret_key
    })
    
    if (res.data.success) {
      ElMessage.success(`测试成功！响应时间: ${res.data.data.response_time_ms}ms`)
    } else {
      ElMessage.error(res.data.msg || '测试失败')
    }
  } catch (error) {
    ElMessage.error('测试失败')
    console.error(error)
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    
    try {
      // 构建调度配置
      const scheduleConfig = buildScheduleConfig()
      
      const data = {
        ...form.value,
        at_all: atType.value === 'all',
        schedule_config: scheduleConfig,
        data_source_config: {
          type: dataSourceType.value,
          config: {}
        }
      }
      
      // 移除不需要的字段
      delete data.secret_key
      
      let res
      if (isEdit.value) {
        res = await axios.put(`/dingtalk-push/configs/${route.params.id}`, data)
      } else {
        res = await axios.post('/dingtalk-push/configs', data)
      }
      
      if (res.data.success) {
        ElMessage.success(isEdit.value ? '保存成功' : '创建成功')
        router.push('/dingtalk-push')
      } else {
        ElMessage.error(res.data.msg || '操作失败')
      }
    } catch (error) {
      ElMessage.error('操作失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 构建调度配置
const buildScheduleConfig = () => {
  if (scheduleType.value === 'daily') {
    return {
      type: 'daily',
      config: {
        times: dailyTimes.value || ['08:00'],
        weekdays: excludeHolidays.value ? [1, 2, 3, 4, 5] : [1, 2, 3, 4, 5, 6, 7],
        exclude_holidays: excludeHolidays.value
      }
    }
  }
  
  if (scheduleType.value === 'cron') {
    return {
      type: 'cron',
      config: {
        times: cronTimes.value || [],
        expression: cronExpression.value || '',
        weekdays: cronWeekdays.value.length > 0 ? cronWeekdays.value : [1, 2, 3, 4, 5, 6, 7],
        exclude_holidays: false
      }
    }
  }
  
  return { type: scheduleType.value, config: {} }
}

// 加载配置（编辑模式）
const loadConfig = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await axios.get(`/dingtalk-push/configs/${route.params.id}`)
    
    if (res.data.success) {
      const config = res.data.data
      
      // 填充表单
      Object.assign(form.value, {
        name: config.name,
        description: config.description,
        category: config.category,
        webhook_url: config.webhook_url_decrypted || '', // 使用解密后的真实地址
        at_mobiles: JSON.parse(config.at_mobiles || '[]'),
        at_all: Boolean(config.at_all), // 转换为布尔值
        message_type: config.message_type,
        template_content: config.template_content,
        enabled: Boolean(config.enabled), // 转换为布尔值
        max_retries: config.max_retries,
        timeout_seconds: config.timeout_seconds
      })
      
      // 解析调度配置
      const scheduleConfig = typeof config.schedule_config === 'string'
        ? JSON.parse(config.schedule_config)
        : config.schedule_config
      
      // 根据调度类型加载对应配置
      if (scheduleConfig.type) {
        scheduleType.value = scheduleConfig.type
        
        if (scheduleConfig.type === 'daily') {
          dailyTimes.value = scheduleConfig.config?.times || []
          excludeHolidays.value = scheduleConfig.config?.exclude_holidays ?? true
        } else if (scheduleConfig.type === 'weekly') {
          // 每周推送配置
          // TODO: 根据实际需求加载 weekly 配置
        } else if (scheduleConfig.type === 'cron') {
          // Cron 表达式配置
          cronTimes.value = scheduleConfig.config?.times || []
          cronExpression.value = scheduleConfig.config?.expression || ''
          // 加载执行周期（如果没有则默认全选）
          cronWeekdays.value = scheduleConfig.config?.weekdays || [1, 2, 3, 4, 5, 6, 7]
        }
        // once 类型不需要额外配置
      }
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
    console.error(error)
  }
}

// 返回
const goBack = () => {
  router.push('/dingtalk-push')
}

// 显示示例
const showDemo = () => {
  activeDemoTab.value = form.value.message_type
  demoVisible.value = true
}

// 应用示例
const applyDemo = () => {
  const demos = {
    markdown: `# 📊 日报推送\n\n### **日期**: {{ now }}\n\n---\n\n## 今日工作总结\n- 完成功能开发：{{ completed_tasks }} 个\n- 修复 Bug：{{ fixed_bugs }} 个\n- 代码审查：{{ code_reviews }} 次\n\n## 明日计划\n{% for task in tomorrow_tasks %}\n- {{ task }}\n{% endfor %}\n\n---\n> 发送时间：{{ now }}`,
    actionCard: `# 🔔 告警通知\n\n### 告警级别: <font color="#FF0000">严重</font>\n\n**告警时间**: {{ alert_time }}\n**告警对象**: {{ alert_target }}\n**告警内容**: {{ alert_message }}\n\n---\n\n请及时处理！\n\n[查看详情](https://example.com/alert/{{ alert_id }})\n[确认处理](https://example.com/alert/{{ alert_id }}/ack)`,
    text: `【打卡提醒】\n\n当前时间：{{ now }}\n\n请记得及时打卡！\n\n温馨提示：\n- 上班打卡时间：09:00 前\n- 下班打卡时间：18:00 后`
  }
  
  form.value.template_content = demos[activeDemoTab.value]
  form.value.message_type = activeDemoTab.value
  demoVisible.value = false
  ElMessage.success('已应用示例模板')
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.dingtalk-push-config {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #409eff;
  color: #409eff;
}

.demo-content {
  max-height: 600px;
  overflow-y: auto;
}

.demo-content h4 {
  margin-top: 20px;
  margin-bottom: 10px;
  color: #303133;
  font-weight: 600;
}

.demo-content p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}

.code-block {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  margin: 10px 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.preview-box {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  margin-top: 15px;
  background-color: #fff;
  min-height: 100px;
}

.markdown-preview h3 {
  color: #303133;
  margin-top: 15px;
  margin-bottom: 10px;
}

.markdown-preview h4 {
  color: #606266;
  margin: 10px 0;
}

.markdown-preview ul {
  padding-left: 20px;
  margin: 10px 0;
}

.markdown-preview li {
  margin: 5px 0;
  color: #606266;
}

.markdown-preview blockquote {
  border-left: 4px solid #409eff;
  padding-left: 15px;
  margin: 15px 0;
  color: #909399;
}

.actioncard-preview h3 {
  color: #303133;
  margin-bottom: 15px;
}

.actioncard-preview p {
  margin: 8px 0;
  color: #606266;
}

.action-buttons {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.text-preview p {
  margin: 8px 0;
  color: #606266;
  line-height: 1.6;
}
</style>
