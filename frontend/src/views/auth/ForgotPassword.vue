<template>
  <div class="forgot-container">
    <div class="forgot-card">
      <div class="forgot-header">
        <el-icon :size="60" color="#409eff">
          <Key />
        </el-icon>
        <h2>忘记密码</h2>
        <p>输入您的邮箱，我们将发送重置密码的链接</p>
      </div>

      <el-form :model="form" ref="formRef" @submit.prevent="handleReset">
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入您的邮箱"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>

        <el-form-item style="width: 100%">
          <el-button type="primary" size="large" :loading="loading" @click="handleReset">
            <span v-if="!loading">发送重置链接</span>
            <span v-else>发送中...</span>
          </el-button>
        </el-form-item>
      </el-form>

      <div class="forgot-footer">
        <el-link :href="'/login'" underline>返回登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Key, Message } from '@element-plus/icons-vue'
import { forgotPassword } from '@/api/auth'

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  email: '',
})

const handleReset = async () => {
  if (!form.email) {
    ElMessage.error('请输入邮箱')
    return
  }

  loading.value = true
  try {
    const result = await forgotPassword(form.email)

    if (result.success) {
      ElMessage.success(result.message || '重置链接已发送到您的邮箱')
    } else {
      ElMessage.error(result.message || '发送失败')
    }
  } catch (error) {
    console.error('重置密码错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.forgot-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.forgot-header {
  text-align: center;
  margin-bottom: 30px;
}

.forgot-header h2 {
  margin: 15px 0 10px;
  color: #333;
  font-size: 24px;
}

.forgot-header p {
  color: #999;
  font-size: 14px;
}

.forgot-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
}

.forgot-footer a {
  color: #409eff;
}
</style>
