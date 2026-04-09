<template>
  <div class="error-container">
    <div class="error-content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>抱歉，您访问的页面找不到</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.error-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-content {
  text-align: center;
  color: white;
}

.error-content h1 {
  font-size: 120px;
  margin: 0;
  text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
}

.error-content h2 {
  font-size: 36px;
  margin: 20px 0 10px;
}

.error-content p {
  font-size: 18px;
  margin-bottom: 30px;
  opacity: 0.9;
}
</style>
