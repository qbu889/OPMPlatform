<template>
  <div class="chatbot-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon :size="24"><ChatDotRound /></el-icon>
          <span style="margin-left: 10px; font-size: 18px; font-weight: 600;">智能客服</span>
        </div>
      </template>

      <div class="chat-content">
        <div class="messages-container" ref="messagesContainer">
          <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
            <div class="message-avatar">
              <el-icon v-if="msg.role === 'user'" :size="32"><UserFilled /></el-icon>
              <el-icon v-else :size="32"><ChatLineSquare /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ msg.timestamp }}</div>
            </div>
          </div>
          <div v-if="loading" class="message system">
            <div class="message-content">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>AI 正在思考...</span>
            </div>
          </div>
        </div>

        <div class="input-area">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题..."
            @keyup.enter="handleSend"
          />
          <div class="input-actions">
            <el-button type="info" @click="handleClear">清空对话</el-button>
            <el-button type="primary" :loading="loading" @click="handleSend">
              <el-icon><Promotion /></el-icon>
              发送
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { ChatDotRound, UserFilled, ChatLineSquare, Loading, Promotion } from '@element-plus/icons-vue'

const messagesContainer = ref(null)
const loading = ref(false)
const inputMessage = ref('')
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是智能客服，基于 Ollama AI。请问有什么可以帮助您的？',
    timestamp: new Date().toLocaleTimeString(),
  },
])

const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date().toLocaleTimeString(),
  }

  messages.value.push(userMessage)
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const response = await fetch('/chatbot/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: userMessage.content,
        history: messages.value.slice(0, -1),
      }),
    })
    const result = await response.json()

    if (result.success) {
      messages.value.push({
        role: 'assistant',
        content: result.response,
        timestamp: new Date().toLocaleTimeString(),
      })
    } else {
      ElMessage.error(result.message || '请求失败')
    }
  } catch (error) {
    console.error('聊天错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

const handleClear = () => {
  messages.value = [
    {
      role: 'assistant',
      content: '对话已清空。请问有什么可以帮助您的？',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.chatbot-container {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  align-items: center;
}

.chat-content {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 10px;
}

.message-content {
  max-width: 60%;
  padding: 12px 16px;
  border-radius: 8px;
}

.message.user .message-content {
  background: #409eff;
  color: white;
}

.message:not(.user) .message-content {
  background: white;
  color: #333;
}

.message.system .message-content {
  background: transparent;
  color: #909399;
  text-align: center;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  text-align: right;
}

.input-area {
  margin-top: auto;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}
</style>
