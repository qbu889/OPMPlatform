<template>
  <el-header class="header">
    <div class="header-content">
      <div class="logo" @click="goHome">
        <img src="/nokia-06.png" alt="NOKIA" class="logo-icon" />
        <span class="logo-text">诺基亚 OPM 系统</span>
      </div>

      <el-menu mode="horizontal" :ellipsis="false" @select="handleMenuSelect">
        <el-menu-item index="home" @click.prevent="goHome">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="document">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>文档</span>
          </template>
          <el-menu-item index="word-to-md">
            <el-icon><Document /></el-icon>
            <span>Word 转 Markdown</span>
          </el-menu-item>
          <el-menu-item index="markdown-upload">
            <el-icon><Files /></el-icon>
            <span>Markdown 转 Word</span>
          </el-menu-item>
          <el-menu-item index="word-to-excel">
            <el-icon><DataBoard /></el-icon>
            <span>Word 转 Excel</span>
          </el-menu-item>
          <el-menu-item index="fpa-generator">
            <el-icon><DataAnalysis /></el-icon>
            <span>FPA 预估表生成</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="smart">
          <template #title>
            <el-icon><Platform /></el-icon>
            <span>智能系统</span>
          </template>
          <el-menu-item index="spreadsheet">
            <el-icon><Grid /></el-icon>
            <span>在线表格</span>
          </el-menu-item>
          <el-menu-item index="chatbot">
            <el-icon><ChatDotRound /></el-icon>
            <span>智能客服</span>
          </el-menu-item>
          <el-menu-item index="schedule-config">
            <el-icon><Calendar /></el-icon>
            <span>排班配置管理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="tools">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>高效工具</span>
          </template>
          <el-menu-item index="clean-event-page">
            <el-icon><Edit /></el-icon>
            <span>事件数据清洗</span>
          </el-menu-item>
          <el-menu-item index="sql-formatter">
            <el-icon><DataBoard /></el-icon>
            <span>SQL ID 格式化</span>
          </el-menu-item>
          <el-menu-item index="kafka-generator">
            <el-icon><Operation /></el-icon>
            <span>Kafka 消息生成</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>

      <div class="user-menu">
        <template v-if="userStore.isLoggedIn">
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span>{{ userStore.username }}</span>
              <span v-if="userStore.isAdmin" class="admin-badge">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showChangePasswordModal = true">
                  <el-icon><Key /></el-icon>
                  <span>修改密码</span>
                </el-dropdown-item>
                <el-dropdown-item v-if="userStore.isAdmin">
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-dropdown-item>
                <el-divider />
                <el-dropdown-item @click="handleLogout">
                  <el-icon><ArrowLeft /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button size="small" @click="goTo('/login')">
            <el-icon><Avatar /></el-icon>
            <span>登录</span>
          </el-button>
          <el-button size="small" type="primary" @click="goTo('/register')">
            <el-icon><UserFilled /></el-icon>
            <span>注册</span>
          </el-button>
        </template>
      </div>
    </div>
  </el-header>

  <!-- Change Password Modal -->
  <el-dialog v-model="showChangePasswordModal" title="修改密码" width="400px">
    <el-form :model="passwordForm" ref="passwordFormRef">
      <el-form-item label="当前密码">
        <el-input v-model="passwordForm.oldPassword" type="password" />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="passwordForm.newPassword" type="password" />
        <div class="el-form-item__content">
          <el-text type="info" size="small">至少 8 位，包含字母和数字</el-text>
        </div>
      </el-form-item>
      <el-form-item label="确认新密码">
        <el-input v-model="passwordForm.confirmPassword" type="password" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showChangePasswordModal = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="handleSavePassword">
        保存更改
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Document,
  Platform,
  OfficeBuilding,
  Files,
  DataBoard,
  DataAnalysis,
  Grid,
  ChatDotRound,
  Calendar,
  UserFilled,
  Avatar,
  Key,
  Setting,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'
import { changePassword, logout } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

const showChangePasswordModal = ref(false)
const passwordFormRef = ref(null)
const saving = ref(false)

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const goHome = () => {
  router.push('/')
}

const goTo = (path) => {
  router.push(path)
}

const handleMenuSelect = (index) => {
  const pathMap = {
    home: '/',
    'word-to-md': '/word-to-md',
    'markdown-upload': '/markdown-upload',
    'word-to-excel': '/word-to-excel',
    'fpa-generator': '/fpa-generator',
    spreadsheet: '/spreadsheet',
    chatbot: '/chatbot',
    'schedule-config': '/schedule-config',
    'clean-event-page': '/clean-event-page',
    'sql-formatter': '/sql-formatter',
    'kafka-generator': '/kafka-generator',
  }

  if (pathMap[index]) {
    router.push(pathMap[index])
  }
}

const handleLogout = async () => {
  await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    type: 'warning',
  })

  try {
    await logout()
    userStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    console.error('退出登录错误:', error)
    ElMessage.error('退出登录失败')
  }
}

const handleSavePassword = async () => {
  if (!passwordForm.value.newPassword || !passwordForm.value.confirmPassword) {
    ElMessage.error('请填写完整信息')
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  if (passwordForm.value.newPassword.length < 8) {
    ElMessage.error('新密码至少 8 位')
    return
  }

  saving.value = true
  try {
    const result = await changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword,
      passwordForm.value.confirmPassword
    )

    if (result.success) {
      ElMessage.success('密码修改成功')
      showChangePasswordModal.value = false
      passwordForm.value.oldPassword = ''
      passwordForm.value.newPassword = ''
      passwordForm.value.confirmPassword = ''
    } else {
      ElMessage.error(result.message || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码错误:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 40px;
}

.logo-icon {
  height: 32px;
  margin-right: 12px;
}

.logo-text {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.el-menu {
  background: transparent;
  border: none;
  flex: 1;
}

.el-menu-item,
.el-sub-menu__title {
  color: #b0b8c4;
  height: 60px;
  line-height: 60px;
}

.el-menu-item:hover,
.el-sub-menu__title:hover {
  background: transparent;
  color: white;
}

.el-menu-item.is-active {
  color: #409eff;
}

.user-menu {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.user-info .el-icon {
  margin-right: 6px;
}

.user-info span:first-child {
  margin-right: 6px;
}

.admin-badge {
  background: #f56c6c;
  color: white;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
}

.el-button {
  color: white;
}
</style>
