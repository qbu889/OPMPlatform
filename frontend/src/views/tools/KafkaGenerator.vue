<template>
  <div class="kafka-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><Operation /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">Kafka 消息生成</span>
        </div>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="Topic">
          <el-input v-model="form.topic" placeholder="请输入 Kafka Topic" />
        </el-form-item>
        <el-form-item label="分区数">
          <el-input-number v-model="form.partitions" :min="1" :max="32" />
        </el-form-item>
        <el-form-item label="消息数量">
          <el-input-number v-model="form.count" :min="1" :max="10000" />
        </el-form-item>
        <el-form-item label="数据源">
          <el-select v-model="form.sourceType">
            <el-option label="ES 数据" value="es" />
            <el-option label="自定义 JSON" value="custom" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.sourceType === 'es'" label="ES Index">
          <el-input v-model="form.esIndex" placeholder="请输入 ES Index 名称" />
        </el-form-item>

        <el-form-item v-if="form.sourceType === 'custom'" label="JSON 模板">
          <el-input
            v-model="form.jsonTemplate"
            type="textarea"
            :rows="8"
            placeholder='例如：{\n  "id": "{{id}}",\n  "name": "{{name}}"\n}'
          />
          <div class="form-tip">支持 {{variable}} 占位符</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="generating" @click="handleGenerate">
            <el-icon><VideoPlay /></el-icon>
            生成 Kafka 消息
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="result" class="result-section">
        <el-divider>生成结果</el-divider>
        <el-alert
          :title="`成功生成 ${result.count} 条消息`"
          type="success"
          show-icon
          :closable="false"
        />
        <el-input
          v-model="result.preview"
          type="textarea"
          :rows="10"
          readonly
          class="mt-2"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, VideoPlay } from '@element-plus/icons-vue'

const generating = ref(false)
const result = ref(null)

const form = reactive({
  topic: '',
  partitions: 1,
  count: 100,
  sourceType: 'es',
  esIndex: '',
  jsonTemplate: '{\n  "id": "{{id}}",\n  "message": "{{message}}"\n}',
})

const handleGenerate = async () => {
  if (!form.topic) {
    ElMessage.error('请输入 Topic')
    return
  }

  generating.value = true
  result.value = null

  try {
    const response = await fetch('/kafka-generator/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    const data = await response.json()

    if (data.success) {
      result.value = {
        count: data.count,
        preview: JSON.stringify(data.messages?.slice(0, 5) || [], null, 2),
      }
      ElMessage.success(`成功生成 ${data.count} 条 Kafka 消息`)
    } else {
      ElMessage.error(data.message || '生成失败')
    }
  } catch (error) {
    console.error('生成错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.kafka-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.result-section {
  margin-top: 30px;
}

.mt-2 {
  margin-top: 15px;
}
</style>
